#!/usr/bin/env python
import tkinter as tk

import threading
import socket
import talk
import vxi11
import urllib.request
from utils import *
import socketserver
import config
import plot
import probe

class Console(tk.Frame,ListenerInterface):
    def  __init__(self,master):
        tk.Frame.__init__(self,master,bg=white)
        self.pack(fill=tk.BOTH,side=tk.LEFT,expand=True,padx=(1,1),pady=(1,1))
        self.master=master
        self.init_Text()
        self.init_Entry()
        self.enabled=True

    def init_Text(self):
        subframe1=tk.Frame(self,borderwidth=1,relief="sunken")
        subframe1.pack(fill=tk.BOTH,side=tk.TOP,expand=True,padx=(1,1),pady=(1,1))
        self.text=tk.Text(subframe1,relief="flat")
        self.text.configure(state=tk.DISABLED)
        self.text.bind("<1>", lambda event: self.text.focus_set())
        self.vsb=tk.Scrollbar(subframe1,orient="vertical",command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side=tk.RIGHT,fill=tk.Y)
        self.text.pack(side=tk.LEFT,fill=tk.BOTH)
##        self.text.tag_config('return',background="#e1e1e1",foreground="black")
##        self.text.tag_config('print',background="white",foreground=greenblue)

    def init_Entry(self):
        subframe2=tk.Frame(self,borderwidth=1,relief="sunken")
        subframe2.pack(fill=tk.BOTH,side=tk.TOP,expand=True,padx=(1,1),pady=(1,1))
        self.label=tk.Label(subframe2,text="cmd:")
        self.label.pack(side=tk.LEFT,padx=5,pady=5)
        self.entry=tk.Entry(subframe2)
        self.entry.pack(fill=tk.X,padx=5,expand=True)
        self.entry.insert(0,"*idn?")
        self.entry.configure(state=tk.DISABLED)
        self.on_click_id=self.entry.bind('<Button-1>',self.on_click)
        self.entry.bind('<Return>',self.on_return)

    def on_click(self,event):
        self.entry.configure(state=tk.NORMAL)
        self.entry.delete(0,tk.END)
        self.entry.unbind('<Button-1>',self.on_click_id)
    def on_return(self,event=None):
        text=self.entry.get()
        self.entry.delete(0,tk.END)
        self.master.callMessages(text)

    def addTextConsoleMessage(self,text):
        self.text.configure(state=tk.NORMAL)
        self.text.insert(tk.END,"> "+text+"\n")
        self.text.see(tk.END)
        self.text.configure(state=tk.DISABLED)

    def addTextConsoleAnswer(self,text):
        self.text.configure(state=tk.NORMAL)
        self.text.insert(tk.END,"\n")
        self.text.insert(tk.END,"& "+text+"\n")#,'return')
        self.text.see(tk.END)
        self.text.configure(state=tk.DISABLED)
    def addTextConsolePrint(self,text):
        self.text.configure(state=tk.NORMAL)
        self.text.insert(tk.END,"< "+text+"\n")#,'print')
        self.text.see(tk.END)
        self.text.configure(state=tk.DISABLED)

    def callMessage(self, textMessage):
        if(self.enabled):
            self.addTextConsoleMessage(textMessage)
    def callAnswer(self, barray):
        if(self.enabled):
            self.addTextConsoleAnswer(convertBytesToString(barray))
    def callPrint(self, text):
        if(self.enabled):
            self.addTextConsolePrint(text)

class RightWindow(tk.Frame,ListenerInterface):

    def  __init__(self,master):
        tk.Frame.__init__(self,master,bg=white)
        self.master=master
        self.instr=None
        self.initUI()
        self.initScript()

    def initUI(self):
        #Right Vertical frame with three horizontal frames
        self.pack(fill=tk.BOTH,side=tk.RIGHT)
        subframe1=tk.Frame(self,borderwidth=1,relief="sunken")
        subframe1.pack(fill=tk.BOTH,side=tk.TOP,padx=(1,1),pady=(1,1))
        subframe2=tk.Frame(self,borderwidth=1,relief="sunken")
        subframe2.pack(fill=tk.BOTH,side=tk.TOP,padx=(1,1),pady=(1,1))
        subframe3=tk.Frame(self,borderwidth=1,relief="sunken")
        subframe3.pack(fill=tk.BOTH,side=tk.TOP,padx=(1,1),pady=(1,1))

        subframe4=tk.Frame(self,bg=white)
        subframe4.pack(fill=tk.BOTH,side=tk.TOP)
        radiolayout=tk.Frame(subframe4,borderwidth=1,relief="sunken")
        radiolayout.pack(fill=tk.BOTH,side=tk.LEFT,padx=(1,1),pady=(1,1))
        options1=tk.Frame(subframe4,borderwidth=1,relief="sunken")
        options1.pack(fill=tk.BOTH,side=tk.LEFT,expand=True,padx=(1,1),pady=(1,1))

        subframe5=tk.Frame(self,borderwidth=1,relief="sunken")
        subframe5.pack(fill=tk.BOTH,side=tk.TOP,padx=(1,1),pady=(1,1))
        subframe6=tk.Frame(self,borderwidth=1,relief="sunken")
        subframe6.pack(fill=tk.BOTH,side=tk.TOP,padx=(1,1),pady=(1,1))
        empty=tk.Frame(self,borderwidth=1,relief="sunken")
        empty.pack(fill=tk.BOTH,side=tk.TOP,expand=True,padx=(1,1),pady=(1,1))
        
        # connect button
        self.connectButton=tk.Button(subframe3,text='Connect',command=self.on_returnConnect,width=8)
        self.connectButton.pack(side=tk.LEFT,padx=5,pady=5)

        # connect entry
        entry_text=tk.StringVar()
        entry_text.set("192.168.0.53")
        self.connectentry=tk.Entry(subframe3,justify='center',textvariable=entry_text)
        self.connectentry.pack(fill=tk.X,padx=5,expand=True)

        # Radio group
        self.radioLabel=tk.Label(radiolayout,text="Connection choice :")
        self.radioLabel.pack(side=tk.TOP,padx=5,pady=5)
        self.radioVar=tk.IntVar()
        self.radioVxi11=tk.Radiobutton(radiolayout,text="vxi11",variable=self.radioVar,value=1,command=self.selectRadio)
        self.radioVxi11.pack(side=tk.TOP,padx=5,pady=5)
        self.radioGPIB=tk.Radiobutton(radiolayout,text="gpib",variable=self.radioVar,value=2,command=self.selectRadio)
        self.radioGPIB.pack(side=tk.TOP,padx=5,pady=5)
        self.radioRaw=tk.Radiobutton(radiolayout,text="raw",variable=self.radioVar,value=3,command=self.selectRadio)
        self.radioRaw.pack(side=tk.TOP,padx=5,pady=5)
        self.radioVxi11.select()

        # port
        self.portLabel=tk.Label(options1,text='Port')
        self.portLabel.pack(side=tk.TOP,padx=5,pady=5)
        self.portEntry=EntryInteger(options1,justify='center',state="disabled")#,textvariable=self.portEntryText)
        self.portEntry.pack(side=tk.TOP,padx=5)
        self.portEntry.set("0")

        # gpib adress
        self.gpibLabel=tk.Label(options1,text='GPIB addr')
        self.gpibLabel.pack(side=tk.TOP,padx=5,pady=5)
        self.gpibEntry=EntryInteger(options1,justify='center',state="disabled")#,textvariable=self.gpibEntryText)
        self.gpibEntry.pack(side=tk.TOP,padx=5)
        self.gpibEntry.set("18")

        # CONFIG
        configLabel=tk.Label(subframe5,text='Config',width=8)
        configLabel.pack(side=tk.LEFT,padx=5,pady=5)

        # new config button
        newconfigButton=tk.Button(subframe5,text='New',command=self.newConfig,width=12)
        newconfigButton.pack(side=tk.LEFT,padx=5,pady=5)

        # edit config button
        editconfigButton=tk.Button(subframe5,text='Edit',command=self.editConfig,width=12)
        editconfigButton.pack(side=tk.LEFT,padx=5,pady=5)

        # PROBE
        probeLabel=tk.Label(subframe6,text='Probe',width=8)
        probeLabel.pack(side=tk.LEFT,padx=5,pady=5)

        # connect probe button
        probeButton=tk.Button(subframe6,text='Connect',command=self.enableProbe,width=12)
        probeButton.pack(side=tk.LEFT,padx=5,pady=5)

    def editConfig(self):
        self.master.configWindow=config.openfile(self.master)
    def newConfig(self):
        self.master.configWindow=config.openWindow(self.master,None)
    def enableProbe(self):
        self.master.enableProbe()


    def selectRadio(self):
        var=self.radioVar.get();
        if(var ==1):
            self.gpibEntry.configure(state=tk.DISABLED)
            self.portEntry.configure(state=tk.DISABLED)
            self.gpibEntry.set("-1")
            self.portEntry.set("0")
        elif (var==2):
            self.gpibEntry.configure(state=tk.NORMAL)
            self.portEntry.configure(state=tk.NORMAL)
            self.gpibEntry.set("18")
            self.portEntry.set("1234")
        elif (var==3):
            self.gpibEntry.configure(state=tk.DISABLED)
            self.portEntry.configure(state=tk.NORMAL)
            self.gpibEntry.set("-1")
            self.portEntry.set("9001")
    def initScript(self):
        # connect entry
        self.connectentry.bind('<Return>',self.on_returnConnect)

    def on_returnConnect(self,event=None):
        ip=self.connectentry.get()
        var=self.radioVar.get();
        gpib=int(self.gpibEntry.get());
        port=int(self.portEntry.get());

        if(var == 1):
            listip=vxi11.list_devices(ip)

            for i in listip:
                if(ip == i):
                    self.instr=talk.VXi11_Talk(ip)

                    self.setActiveConnect(2)
                    self.master.readThread.init(self.instr)
                    return
            print("Ip unreachable")
        elif(var == 2):
            self.instr=talk.GPIB_Talk(ip,port=port,gpibaddr=gpib)
            self.setActiveConnect(2)
            self.master.readThread.init(self.instr)
            return
        elif(var == 3):
            self.instr=talk.Raw_Talk(ip,port=port)
            self.setActiveConnect(2)
            self.master.readThread.init(self.instr)
            return

        self.setActiveConnect(1)




    def setActiveJoin(self,colorchoice):
        if(threading.main_thread().is_alive() and not self.master.stopBoolean):
            try:
                if(colorchoice==0):
                    self.joinEntry.configure(bg="green")
                elif(colorchoice==1):
                    self.joinEntry.configure(bg="red")
                else:
                    self.joinEntry.configure(bg="yellow")
            except (tk.TclError,RuntimeError):
                # Ignore the issue when the soft is down and where the background thread try to reach the dead main thread
                pass
    def setActiveConnect(self,colorchoice):
        if(threading.main_thread().is_alive() and not self.master.stopBoolean):
            try:
                if(colorchoice==0):
                    self.connectentry.configure(bg="green")
                elif(colorchoice==1):
                    self.connectentry.configure(bg="red")
                else:
                    self.connectentry.configure(bg="yellow")
            except (tk.TclError,RuntimeError):
                # Ignore the issue when the soft is down and where the background thread try to reach the dead main thread
                pass

    def setActiveHost(self,colorchoice):

        if(threading.main_thread().is_alive() and not self.master.stopBoolean):
            try:
                if(colorchoice==0):
                    self.entryHost.configure(readonlybackground="green")
                elif(colorchoice==1):
                    self.entryHost.configure(readonlybackground="red")
                else:
                    self.entryHost.configure(readonlybackground="yellow")
            except (tk.TclError,RuntimeError):
                # Ignore the issue when the soft is down and where the background thread try to reach the dead main thread
                pass

class ReadThread(ListenerInterface):

    def  __init__(self,master):
        self.master=master
        self.messages=[]
        self.instr=None
        self.isRunning=False
        self.thread=None
        pass
    def stop(self):
        self.messages=[]
        self.isRunning=False

    def __run(self):
        try:
            self.instr.connect()
            self.master.rightWindow.setActiveConnect(0)
            self.isRunning=True
            self.master.callMessages("*idn?")
            inc=0
            while(self.isRunning):
                if(self.instr != None):
                    try:
                        if(self.messages!=[]):
                            if("?" not in self.messages[0]):
                               self.instr.write(self.messages[0])
                            else:
                               barray= self.instr.ask(self.messages[0])
                               if(barray!=None):
                                   if type(barray) is bytes and len(barray)>0:
                                       self.master.callAnswers(barray)
                            self.messages=self.messages[1:]
                        inc+=1
                        if(inc>1000*100):
                            inc=0
                            self.master.update()
                    except Exception as err:
                        self.messages=self.messages[1:]
                        print(err)
            if self.instr != None:
                self.instr.close()
        except Exception as err:
            print("Connection failed")
            pass
        finally :
            self.master.rightWindow.setActiveConnect(1)
    def init(self,instr):
        self.instr=instr
        self.thread=threading.Thread(target=self.__run)
        self.thread.start()
    def callMessage(self, textMessage):
        if(self.isRunning):
            self.messages+=[textMessage]

class Application(tk.Frame):
    def  __init__(self,master):
        tk.Frame.__init__(self,master,bg=white)
        self.master=master
        self.pack(fill=tk.BOTH,expand=True)
        self.listeners=[]
        self.configWindow=None
        self.stopBoolean=False
        self.plot=None
        self.probe=None
        self.probeApp=None
        self.rightWindow=RightWindow(self)
        self.console=Console(self)
        self.addToListener(self.rightWindow)
        self.addToListener(self.console)
        self.readThread=ReadThread(self)
        self.addToListener(self.readThread)
    def createPlot(self):
        if(self.plot == None):
            self.plot=plot.openWindow(self.master)
    def addToListener(self,listener):
        self.listeners+=[listener]
    def callAnswers(self,barray):
        for i in self.listeners:
            i.callAnswer(barray)
    def callPrints(self,text):
        self.console.callPrint(text)
    def callMessages(self,textMessage):
        for i in self.listeners:
            i.callMessage(textMessage)
        self.update()
    def enableConsole(self,boolean):
        self.console.enabled=boolean
    def enableProbe(self):
        if(self.probe != None):
            self.probe.destroy()
            self.probe.update()
        self.probe,self.probeApp=probe.openWindow(self)



    def stop(self):
        self.stopBoolean=True
        self.readThread.stop()
        if(self.plot!=None):
            self.plot.stop()
        if(self.probe!=None):
            self.probe.destroy()
            self.probeApp.stop()
            self.probe.update()


    def on_closing(self):
        self.stop()
        self.master.destroy()

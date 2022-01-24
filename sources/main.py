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


##from tkinter import messagebox

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
        self.text.tag_config('return',background="gray",foreground="cyan")
        self.text.tag_config('print',background="white",foreground=greenblue)

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
        self.master.callMessages(text)

    def addTextConsoleMessage(self,text):
        self.text.configure(state=tk.NORMAL)
        self.text.insert(tk.END,"> "+text+"\n")
        self.text.see(tk.END)
        self.text.configure(state=tk.DISABLED)

    def addTextConsoleAnswer(self,text):
        self.text.configure(state=tk.NORMAL)
        self.text.insert(tk.END,"& "+text+"\n",'return')
        self.text.see(tk.END)
        self.text.configure(state=tk.DISABLED)
    def addTextConsolePrint(self,text):
        self.text.configure(state=tk.NORMAL)
        self.text.insert(tk.END,"< "+text+"\n",'print')
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
        # host button
        self.hostButton=tk.Button(subframe1,text='Host',command=self.host,width=8,state="disabled")
        self.hostButton.pack(side=tk.LEFT,padx=5,pady=5)

        self.labelText=tk.StringVar()
        self.labelText.set('ip of host')
        self.entryHost=tk.Entry(subframe1,textvariable=self.labelText,justify='center',readonlybackground="white",state="readonly")
        self.entryHost.pack(fill=tk.X,padx=5,pady=5,expand=True)

        # join button
        self.joinButton=tk.Button(subframe2,text='Join',command=self.join,width=8,state="disabled")
        self.joinButton.pack(side=tk.LEFT,padx=5,pady=5)

        # join entry
        self.joinEntry=tk.Entry(subframe2,justify='center',state="disabled")
        self.joinEntry.pack(side=tk.LEFT,fill=tk.X,padx=5,expand=True)
        # join entry
        self.joinportEntry=EntryInteger(subframe2,justify='center',state="disabled")
        self.joinportEntry.pack(fill=tk.X,padx=5,expand=True)


        # connect button
        self.connectButton=tk.Button(subframe3,text='Connect',command=self.on_returnConnect,width=8)
        self.connectButton.pack(side=tk.LEFT,padx=5,pady=5)

        # connect entry
        entry_text=tk.StringVar()
        entry_text.set("192.168.0.78")
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
##        self.portEntryText=tk.StringVar()
##        self.portEntryText.set("0")
        self.portLabel=tk.Label(options1,text='Port')
        self.portLabel.pack(side=tk.TOP,padx=5,pady=5)
        self.portEntry=EntryInteger(options1,justify='center',state="disabled")#,textvariable=self.portEntryText)
        self.portEntry.pack(side=tk.TOP,padx=5)
        self.portEntry.set("0")



        # gpib adress
##        self.gpibEntryText=tk.StringVar()
##        self.gpibEntryText.set("18")
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

##        probeLabel=tk.Label(subframe6,text='Com Port')
##        probeLabel.pack(side=tk.TOP,padx=5,pady=5)
##        self.probeEntry=EntryInteger(subframe6,justify='center')
##        self.probeEntry.pack(side=tk.TOP,padx=5)
##        self.probeEntry.set("6")


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
    def host(self):
        if(self.master.hostserver.isRunning):
            self.master.hostserver.stop()
            self.labelText.set("host ip")
        else:
            self.master.hostserver.init()
##            self.labelText.set(ip)
    def join(self):
        ip=self.joinEntry.get()
        port=int(self.joinportEntry.get())
        self.master.joinclient.init((ip,port))


    def on_returnConnect(self,event=None):
        ip=self.connectentry.get()
        var=self.radioVar.get();
        gpib=int(self.gpibEntry.get());
        port=int(self.portEntry.get());


##        print(str(var)+" "+self.gpibEntry.get()+" "+self.portEntry.get())
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
##
##class HostHandler(socketserver.StreamRequestHandler):
##    def handle(self):
##        try:
##            self.master.rightWindow.setActiveHost(0)
##            while(self.isRunning):
##                if self.messageToSend!=None:
##                    self.request.send(self.messageToSend.encode())
##                    self.messageToSend=None
##                try:
##                    data=self.request.recv(1024).decode()
##                    print('host received "%s"' % data)
##                    if(data==""):
##                        self.isRunning=False
##                        self.request.close()
##                        self.connected=False
##                        #closed
##                        pass
##                    if (data):
##                        self.master.callMessages(data)
##                    else:
##                        break
##                except socket.timeout:
##                    pass
##            self.request.send(b'')
##        finally:
##            self.server.close()
##            self.master.rightWindow.setActiveHost(1)
##        return
##
##class HostServer2(ListenerInterface):
##    def  __init__(self,master):
##        self.master=master
##        self.isRunning=False
##        self.messageToSend=None
##        self.connected=False
##        self.server_address=None
##        self.hostsocket=None
##
####        self.hostsocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
##    def stop(self):
##        if not self.connected and self.isRunning:
##            socket.socket(socket.AF_INET,socket.SOCK_STREAM).connect(self.address)
##        self.isRunning=False
##
##    def init(self):
##        self.master.rightWindow.setActiveHost(2)
##        external_ip=None
##        try:
##            external_ip=urllib.request.urlopen('https://v4.ident.me').read().decode('utf8')
##        except Exception:
##            external_ip=socket.gethostbyname(socket.gethostname())
##
####        print(external_ip)
##        self.address = ('127.0.0.1', 0) # let the kernel give us a port
##        self.server = socketserver.TCPServer(self.address, HostHandler)
##        self.server.allow_reuse_address=True
##        self.server.timeout=1
##        ip, port = self.server.server_address # find out what port we were given
##        t = threading.Thread(target=self.server.serve_forever)
##        t.setDaemon(False) # don't hang on exit
##        t.start()
##        self.address=(ip,port)
##        print(str(ip)+" "+str(port))
##        return external_ip
##
##    def callAnswer(self, textAnswer):
##        self.messageToSend=textAnswer
##
##    def isRunning(self):
##        return self.isRunning



class HostServer(ListenerInterface):
    def  __init__(self,master):
        self.master=master
        self.isRunning=False
        self.thread=None
        self.messageToSend=None
        self.connected=False
        self.server_address=None
        self.hostsocket=None

##        self.hostsocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    def stop(self):
        if not self.connected and self.isRunning:
            if(self.server_address!=None):
                socket.socket(socket.AF_INET,socket.SOCK_STREAM).connect(('127.0.0.1',self.server_address[1]))
        self.isRunning=False

    def __run(self):
        self.isRunning=True
        self.master.rightWindow.setActiveHost(2)
        try:
            self.hostsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.hostsocket.bind(self.server_address)
##            print(self.hostsocket.getsockname())
            ip,port=self.hostsocket.getsockname()
            external_ip=None
            if not self.isRunning:
                self.master.rightWindow.setActiveHost(1)
                self.hostsocket.close()
                return

            try:
                external_ip=urllib.request.urlopen('https://v4.ident.me').read().decode('utf8')
            except Exception:
                external_ip=socket.gethostbyname(socket.gethostname())
##            print(external_ip)
            print(str(external_ip)+" "+str(port))
            self.server_address=self.hostsocket.getsockname()
            values=setupPort(port)
            if not self.isRunning:
                self.master.rightWindow.setActiveHost(1)
                self.hostsocket.close()
                return
            if(values[1]==""):
                self.master.rightWindow.setActiveHost(1)
                self.hostsocket.close()

                self.isRunning=False
                self.master.rightWindow.labelText.set("Error")
                return
            self.master.rightWindow.labelText.set(str(external_ip)+":"+str(port))
            self.hostsocket.settimeout(1)
            self.hostsocket.listen(1)
##            self.hostsocket=socketserver.TCPServer(self.server_address)
##            print(str(self.hostsocket.server_address))
            self.master.rightWindow.setActiveHost(2)
            while(self.isRunning):
                try:
                    connection, client_address = self.hostsocket.accept()
                    self.connected=True
                except socket.timeout:
                    continue
                else:
                    if not self.isRunning:
                        break
                    try:
                        self.master.rightWindow.setActiveHost(0)
                        connection.settimeout(1)
        ##                print('client connected: '+client_address)
                        while(self.isRunning):
                            if self.messageToSend!=None:
                                connection.send(self.messageToSend.encode())
                                self.messageToSend=None
                            try:
                                data=connection.recv(1024).decode()
                                print('host received "%s"' % data)
                                if(data==""):
                                    self.isRunning=False
                                    connection.shutdown(socket.SHUT_RDWR)
                                    connection.close()
                                    self.connected=False
                                    #closed
                                    pass
                                if (data):
                                    self.master.callMessages(data)
                                else:
                                    break
                            except socket.timeout:
                                pass
                    finally:
            ##                self.master.rightWindow.setActiveHost(False)
                        connection.shutdown(socket.SHUT_RDWR)
                        connection.close()
                        self.isRunning=False
                    self.connected=False
        finally:
            self.master.rightWindow.setActiveHost(1)
##            self.hostsocket.shutdown(socket.SHUT_RDWR)
            self.hostsocket.close()
            self.hostsocket=None
            self.isRunning=False

    def init(self):
        self.master.rightWindow.setActiveHost(2)
        server_name=socket.gethostname()
##        external_ip=None
##        try:
##            external_ip=urllib.request.urlopen('https://v4.ident.me').read().decode('utf8')
##        except Exception:
##            external_ip=socket.gethostbyname(socket.gethostname())
##        print(external_ip)
        self.server_address=("127.0.0.1",0)#(server_name,1060)
##        self.server_address=(external_ip,0)#(server_name,1060)

        print(server_name)
        self.thread=threading.Thread(target=self.__run)
        self.thread.start()
##        return external_ip+" "+

##        return socket.gethostbyname(server_name)
    def callAnswer(self, textAnswer):
        self.messageToSend="1:"+convertBytesToString(textAnswer)
    def callPrint(self, text):
        self.messageToSend="2:"+text
    def isRunning(self):
        return self.isRunning

class JoinClient(ListenerInterface):
    def  __init__(self,master):
        self.master=master
        self.isRunning=False
        self.thread=None
        self.message=None
        self.server_address=None
        self.joinsocket=None
    def stop(self):
        self.isRunning=False
    def __run(self):

        self.isRunning=True
        self.master.rightWindow.setActiveJoin(2)
        try:
            self.joinsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.joinsocket.connect(self.server_address)
            self.master.rightWindow.setActiveJoin(0)
            self.joinsocket.settimeout(1)
            while(self.isRunning):
                if(self.message!=None):
                    self.joinsocket.send(self.message.encode())
                    self.message=None
                try:
    ##                    print(str(type(self.joinsocket)))
                    data=self.joinsocket.recv(1024).decode()
                    print('join received "%s"' % data)
                    if(data==""):
                        self.isRunning=False
                        #closed
                        pass

                    if (data):
                        text=data.encode()
                        if(text[:2]=="1:"):
                            self.master.callAnswers(text[2:])
                        elif (text[:2]=="1:"):
                            self.master.callPrints(text[2:])
                        else:
                           self.master.callAnswers(text)
    ##                        connection.sendall(data)
                    else:
                        break
                except socket.timeout:
                    pass
        finally :
            self.master.rightWindow.setActiveJoin(1)
            self.joinsocket.close()
    def init(self,address):
        self.master.rightWindow.setActiveJoin(2)
        self.server_address=address
##        self.server_address=(ip,1060)
        self.thread=threading.Thread(target=self.__run)
        self.thread.start()
    def callMessage(self, textMessage):
        if(self.message==None and self.isRunning):
            self.message=textMessage

    def isRunning(self):
        return self.isRunning

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
##                                   print(str(type(barray))+" "+str(len(barray)))
##                                   print("hello"+text)
                                   if type(barray) is bytes and len(barray)>0:
                                       self.master.callAnswers(barray)
                            self.messages=self.messages[1:]
                        inc+=1
                        if(inc>1000*100):
                            inc=0
                            self.master.update()
##                            print("pass")
                    except Exception as err:
##                        print("yes")
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

##        print(str(type(self.instr)))
        self.thread=threading.Thread(target=self.__run)
        self.thread.start()
    def callMessage(self, textMessage):
##        print("callMessage "+str(textMessage))
        if(self.isRunning):
            self.messages+=[textMessage]
##            self.message=textMessage

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

        self.hostserver=HostServer(self)
        self.joinclient=JoinClient(self)

        self.addToListener(self.hostserver)
        self.addToListener(self.joinclient)
##        self.plot=plot.openWindow(self.master,random=True)

##        getIpList_Windows()

##        self.configWindow=config.openWindow(self.master,None)
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
        self.hostserver.callPrint(text)
    def callMessages(self,textMessage):
##        print("callMessages "+str(textMessage))
        for i in self.listeners:
##            print("hello "+str(i))
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
        self.hostserver.stop()
        if(self.plot!=None):
            self.plot.stop()
        if(self.probe!=None):
            self.probe.destroy()
            self.probeApp.stop()
            self.probe.update()
        if(self.hostserver.thread!=None):
            self.hostserver.thread.join()
        self.joinclient.stop()
        if(self.joinclient.thread!=None):
            self.joinclient.thread.join()
##        if(self.configWindow!=None):
##            self.configWindow.destroy()


    def on_closing(self):
        self.stop()
        self.master.destroy()

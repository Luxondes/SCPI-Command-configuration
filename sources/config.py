import tkinter as tk
import tkinter.ttk  as ttk
from tkinter import filedialog as fd
import os
import xml.etree.ElementTree as ET
import utils
import struct
import plot
import time

boldfont=("Helvetica",12,"bold")


class Hint():
    def  __init__(self,text,widget,config):
        self.hinttext=text
        self.config=config
        if widget !=None:
            self.addWidget(widget)
    def addWidget(self,widget):
        widget.bind("<Enter>",self.on_enter)
        widget.bind("<Leave>",self.on_leave)        
    def on_enter(self,event):
        self.config.labelHint.configure(text=self.hinttext)
    def on_leave(self,event):
        self.config.labelHint.configure(text="Put mouse over text for get help")   

class Tag(tk.Frame,utils.ListenerInterface):
    def  __init__(self,config,title,tagname,unit=2,getterOnly=False,canDefault=True,hint=0, hinttext=None):
        tk.Frame.__init__(self,config.scrollable_frame,borderwidth=1,relief="sunken")
        self.tagname=tagname
        self.unit=None
        self.getSend=None
        self.getResponse=None
        self.setSend=None
        self.default=None
        self.checkbutton=None
        self.config=config
        self.display()
    
        self.test=False
        self.getterOnly=getterOnly
        self.unitFlag=unit

        frame2=createSubFrame(self)
        
        title=createTitleLabel(frame2,tk.LEFT,title)
        if(hinttext!=None):
            Hint(hinttext,title,self.config)

        if(hint & 1):
            self.config.addHintWidget(1,createLabel(frame2,tk.LEFT,"(1)",0,0,2))
        if(hint & 2):
            self.config.addHintWidget(2,createLabel(frame2,tk.LEFT,"(2)",0,0,2))
        if canDefault:
            self.checkbutton=createDefaultCheckbutton(frame2,tk.LEFT)
            self.checkbutton[0].configure(command=self.onClickCheckBox)
  
        self.testButton=createTestbutton(frame2,tk.RIGHT,command=self.onTestButton)

        if canDefault:
            self.nocmdFrame=createSubFrame(self)
            frame2=createSubFrame(self.nocmdFrame)
            createLabel(frame2,tk.LEFT,"Value :")
            self.default=createEntry(frame2,tk.LEFT)
            self.nocmdFrame.pack_forget()
            if(unit==1):
                createLabel(frame2,tk.LEFT,"ms")
            elif (unit==0):
                createLabel(frame2,tk.LEFT,"Hz")
                
         
        self.gettersetterFrame=createSubFrame(self)
        if(unit!=2):
            self.unit=UnitOptionMenu(self.gettersetterFrame,unit)
        frame2=createSubFrame(self.gettersetterFrame)
        self.config.addHintWidget(4,createLabel(frame2,tk.LEFT,"Get Send :"))
        self.getSend=createEntry(frame2,tk.LEFT)
##        self.config.addHintWidget(5, createLabel(frame2,tk.LEFT,"Response :"))
##        self.getResponse=createEntry(frame2,tk.LEFT)
##        self.getResponse.set("Value")
        if not getterOnly:
            frame2=createSubFrame(self.gettersetterFrame)
            self.config.addHintWidget(3,createLabel(frame2,tk.LEFT,"Set Send :"))
            self.setSend=createEntry(frame2,tk.LEFT)
        pass
    def hide(self):
        self.pack_forget()
        self.visible=False
    def display(self):
        self.pack(fill=tk.X,side=tk.TOP,expand=True,padx=(1,1),pady=(1,1))
        self.visible=True        

        
    def onTestButton(self):
        if(self.getSend.get() !=None and self.getSend.get()!=""):
            self.test=True
            self.config.master.callMessages(self.getSend.get())
            self.getSend.configure(state="alternate")

    def callAnswer(self, barray):
        if(self.test):
            textAnswer=utils.convertBytesToString(barray)
            if(self.tagname=="Start" or
               self.tagname=="Stop" or
               self.tagname=="Center" or
               self.tagname=="Span" or
               self.tagname=="Rbw" or
               self.tagname=="Vbw" or
               self.tagname=="Attenuator" or
               self.tagname=="SweepTime"
               ):
                try:
                    float(textAnswer.strip())
                    self.getSend.configure(background="green")
                except ValueError:
                    print('Got '+textAnswer+' but needed a number')
                    self.getSend.configure(background="red")
            if(self.tagname=="AmplitudeUnit"):
                if(textAnswer.lower().trim() in ["dbm","dbuv","dbmv","v","w","dbua","dbµv","dbµa"]):
                    self.getSend.configure(background="green")
                else:
                    print('Got '+textAnswer.lower()+' but required dbm, dbuv, dbmv, v, w, dbua, dbµv or dbµa')
                    self.getSend.configure(background="red")
            elif(' ' not in textAnswer.strip()):
                self.getSend.configure(background="green")
            else:
                print('Got '+textAnswer+' but needed something')
                self.getSend.configure(background="red")
            self.test=False
    def onClickCheckBox(self):
        if(self.checkbutton[1].get()):
            self.gettersetterFrame.pack_forget()
            self.nocmdFrame.pack(fill=tk.X,side=tk.TOP,expand=True)
        else:
            self.gettersetterFrame.pack(fill=tk.X,side=tk.TOP,expand=True)
            self.nocmdFrame.pack_forget()
        
    def setValues(self,xmlroot):
        tags=xmlroot.findall(self.tagname)
        if(len(tags)==0):
            if(self.default!=None):
                self.default.set("None")
                self.checkbutton[0].select()
                self.onClickCheckBox()
            return
        for tag in tags:
            if(len(tag)==0):
                self.default.set(str(tag.text))
                self.checkbutton[0].select()
                self.onClickCheckBox()
                return
            for subelem in tag:
                if(self.unit!=None):
                    self.unit.setUnit(str(subelem.text))
                if(subelem.tag.lower() == "get"):
                    for subsubelem in subelem:
                        if(subsubelem.tag.lower() == "send"):
                            self.getSend.set(subsubelem.text)  
##                        if(subsubelem.tag.lower() == "response"):
##                            self.getResponse.set(subsubelem.text)                  
                if(not self.getterOnly and subelem.tag.lower() == "set"):
                    for subsubelem in subelem:
                        if(subsubelem.tag.lower() == "send"):
                            self.setSend.set(subsubelem.text)  
        pass
    def saveValues(self,tree):
        if not self.visible:
            return
        
        boo=self.checkbutton!=None and self.checkbutton[1].get()
        #ignore the command
        if(self.default!=None and boo):
            if(utils.textEmpty(self.default.get())):
                return
        elif(utils.textEmpty(self.getSend.get()) and (self.setSend==None or utils.textEmpty(self.setSend.get()))):
            return
        
        child=ET.SubElement(tree,self.tagname)
        if(self.unit!=None):
            child1=ET.SubElement(child,self.unit.getTypeUnitTagName())
            child1.text=self.unit.getUnit()
        if(boo):
            child.text=self.default.get()
            return
        if(self.getSend!=None and not utils.textEmpty(self.getSend.get())):
            child1=ET.SubElement(child,"Get")
            child2=ET.SubElement(child1,"Send")
            child2.text=self.getSend.get()
            child2=ET.SubElement(child1,"Response")
            
            child2.text="Value"#self.getResponse.get()
##            if(utils.textEmpty(child2.text)):
##                child2.text="Value"
        if(self.setSend!=None and not utils.textEmpty(self.setSend.get())):
            child1=ET.SubElement(child,"Set")
            child2=ET.SubElement(child1,"Send")
            child2.text=self.setSend.get()
            child2=ET.SubElement(child1,"Response")
class GetPointsTag(tk.Frame,utils.ListenerInterface):
    def  __init__(self,config,title,tagname,hint=0,hinttext=None):
        tk.Frame.__init__(self,config.scrollable_frame,borderwidth=1,relief="sunken")
        self.tagname=tagname
        self.getSend=None
        self.getResponse=None
        self.config=config
        
        self.test=False
        self.testPlot=-1
        frame2=createSubFrame(self)
        self.startime=0
        self.display()
        
        
        title=createTitleLabel(frame2,tk.LEFT,title)
        if(hinttext!=None):
            Hint(hinttext,title,self.config)
        if(hint & 1):
            self.config.addHintWidget(1,createLabel(frame2,tk.LEFT,"(1)",0,0,2))
        if(hint & 2):
            self.config.addHintWidget(2,createLabel(frame2,tk.LEFT,"(2)",0,0,2))
           
        self.testButton=createTestbutton(frame2,tk.RIGHT,command=self.onTestButton)
        self.testPlotButton=createTestbutton(frame2,tk.RIGHT,command=self.onTestPlotButton,text="Plot Test")

        self.gettersetterFrame=createSubFrame(self)
        
        frame2=createSubFrame(self.gettersetterFrame)
        self.config.addHintWidget(4, createLabel(frame2,tk.LEFT,"Get Send :"))
        self.getSend=createEntry(frame2,tk.LEFT)
        createLabel(frame2,tk.LEFT,"Response :")
        

        self.listResponseLong=("Integer 16 bytes","Integer 32 bytes","Integer 64 bytes","real 32 bytes","real 64 bytes","Ascii/String")
        self.listResponseShort=("UINT:16","INT:32","INT:64","REAL:32","REAL:64","ASCII")
        self.listResponseShortBytes=(2,4,8,4,8)
        self.textResponse=tk.StringVar()
        self.textResponse.set(self.listResponseLong[3])
        self.listResponseMenu=tk.OptionMenu(frame2,self.textResponse,*self.listResponseLong,command=self.onClickListResponse)
        self.listResponseMenu.pack(side=tk.LEFT)
        
        self.asciivariables=(",",";")
        self.asciivar=tk.StringVar()
        self.asciivar.set(self.asciivariables[0])
        self.asciiResponseMenu=tk.OptionMenu(frame2,self.asciivar,*self.asciivariables)
##        self.asciiResponseMenu.pack(side=tk.LEFT)

        self.endianList=("Big endian","Little endian")
        self.endianvar=tk.StringVar()
        self.endianvar.set(self.endianList[1])
        self.endianResponseMenu=tk.OptionMenu(frame2,self.endianvar,*self.endianList)
##        self.endianResponseMenu.pack(side=tk.LEFT)
        self.onClickListResponse(self.textResponse.get())

    def setHeaderTag(self,headertag):
        self.headertag=headertag
    def setInitTag(self,inittag):
        self.inittag=inittag
    def hide(self):
        self.pack_forget()
        self.visible=False
    def display(self):
        self.pack(fill=tk.X,side=tk.TOP,expand=True,padx=(1,1),pady=(1,1))
        self.visible=True    

    def onClickListResponse(self,value):
        inc =0
        for x in self.listResponseLong:
            if x == value:
                if inc == 3 or inc == 4:
                    #enable endian
                    self.endianResponseMenu.pack(side=tk.LEFT)
                    self.asciiResponseMenu.pack_forget()
                    return
                if inc == 5:
                    # enable sub ascii

                    self.asciiResponseMenu.pack(side=tk.LEFT)
                    self.endianResponseMenu.pack_forget()
                    return
                self.endianResponseMenu.pack_forget()
                self.asciiResponseMenu.pack_forget()    
                return
            inc+=1
        inc =0
        split= value.split(':')
        if(split[0]=="ASCII"):
            value="ASCII"
            sec=","
            if(len(split)>1):
                sec=split[1]
            # enable sub ascii
            self.asciivar.set(sec)
            self.asciiResponseMenu.pack(side=tk.LEFT)
            self.endianResponseMenu.pack_forget()
            return
        
        for x in self.listResponseShort:
            if x == value:
                self.textResponse.set(self.listResponseLong[inc])
                if inc == 3 or inc == 4:
                    #enable endian
                    self.endianResponseMenu.pack(side=tk.LEFT)
                    self.asciiResponseMenu.pack_forget()
                    return
                
                self.endianResponseMenu.pack_forget()
                self.asciiResponseMenu.pack_forget()    
                return
            inc+=1

    def onTestPlotButton(self):
##        print("onTestPlotButton")
        if(self.getSend.get() !=None and self.getSend.get()!=""):
            self.testPlot=0
            self.config.master.createPlot()
            self.config.master.callPrints("Wait qew seconds")
            self.config.master.enableConsole(False)
            init=False
            self.test=False
            self.startime=round(time.time()*1000)/1000
            if(self.inittag.listLines == []):
                init=False
                
            for line in self.inittag.listLines:
                text=line[0].get()
                if not utils.textEmpty(text):
                    self.config.master.callMessages(line[0].get())
                    init=True

            if not init:
                self.config.master.callPrints("Lack of a init line for set the type (int, float, double, ascii) of the data returned")
                self.getSend.configure(background="red")
                return
            for i in range(0,plot.linesmax+1):
                self.config.master.callMessages(self.getSend.get())
            self.testPlot=plot.linesmax  
##            print(plot.linesmax+";"+self.testPlot
            self.getSend.configure(background="yellow")
        
    def onTestButton(self):
        if(self.getSend.get() !=None and self.getSend.get()!=""):
            self.test=True

            init=False
            if(self.inittag.listLines == []):
                init=False
                
            for line in self.inittag.listLines:
                text=line[0].get()
                if not utils.textEmpty(text):
                    self.config.master.callMessages(line[0].get())
                    init=True

            if not init:
                self.config.master.callPrints("Lack of a init line for set the type (int, float, double, ascii) of the data returned")
                self.getSend.configure(background="red")
                return
            self.config.master.callMessages(self.getSend.get())
            self.getSend.configure(background="yellow")
    def testPlotAnswer(self,barray):
##        print("onTestPlotButton")
        inc =0
        for x in self.listResponseLong:
            if x == self.textResponse.get():
                break
            inc+=1
        self.testPlot-=1
        if inc<5:
            nbpts=0
            if(self.headertag.textvar.get() == self.headertag.optionList[2]): #"#A"
                if(str(barray[:2]) != '#A'):
                    return
                numberHeaderBytes=struct.unpack('H'*2,barray[2,4])
            elif(self.headertag.textvar.get() == self.headertag.optionList[1]):#"IEEE 754"
                if(str(barray[:1]) != "b'#'" or str(barray[1:2]) < "b'0'" or str(barray[1:2]) > "b'9'"):
                    return
                c=str(barray[1:2])[2]
##                    self.config.master.callPrints("Number of Points1 : "+str(c))
                v=int(c)
                c=barray[2:2+v].decode('ascii')
                nbpts=int(str(c))/self.listResponseShortBytes[inc]
                listpts= utils.readPoints(barray[2+v:],int(str(c)),inc,0)
                if(self.testPlot==0):
                    delay=round(time.time()*1000)/1000-self.startime
                self.config.master.plot.setPoints(listpts,plot.linesmax-1-self.testPlot)

##                maxf=float("-inf")
##                for f in listpts:
##                    maxf=max(f,maxf)
        elif inc==5:
            listpts= utils.readPoints(barray,-1,inc,0)
            if(self.testPlot==0):
                delay=round(time.time()*1000)/1000-self.startime
            self.config.master.plot.setPoints(listpts,plot.linesmax-1-self.testPlot)
##            maxf=float("-inf")
##            for f in listpts:
##                maxf=max(f,maxf)
        if(self.testPlot==0):
            self.testPlot=-1
            self.getSend.configure(background="green")
            self.config.master.enableConsole(True)
            self.config.master.callPrints("The Plot is done")
            
            self.config.master.callPrints("Request 100 plots has costed "+str(delay)+" s, so "+str(100/delay)+" Acq/s")
            

            

    def testAnswer(self,barray):
        inc =0
        for x in self.listResponseLong:
            if x == self.textResponse.get():
                break
            inc+=1
        self.test=False
        if inc<5:
            self.config.master.callPrints("Length of the values on bytes : "+str(len(barray)))
            nbpts=0
            if(self.headertag.textvar.get() == self.headertag.optionList[2]): #"#A"
                if(str(barray[:2]) != '#A'):
                    self.config.master.callPrints("Got a header '"+utils.convertBytesToString(barray[:2])+"' but needed '#A'")
                    self.getSend.configure(background="red")
                    return
                numberHeaderBytes=struct.unpack('H'*2,barray[2,4])
                self.config.master.callPrints("#A reader not implemented : "+str(numberHeaderBytes))
                self.getSend.configure(background="red")
            elif(self.headertag.textvar.get() == self.headertag.optionList[1]):#"IEEE 754"
                if(str(barray[:1]) != "b'#'" or str(barray[1:2]) < "b'0'" or str(barray[1:2]) > "b'9'"):
                    self.config.master.callPrints("Got a header '"+utils.convertBytesToString(barray[:2])+"' but needed '#X' where X is a number")
                    self.getSend.configure(background="red")
                    return
                c=str(barray[1:2])[2]
##                    self.config.master.callPrints("Number of Points1 : "+str(c))
                v=int(c)
                c=barray[2:2+v].decode('ascii')
                nbpts=int(str(c))/self.listResponseShortBytes[inc]
                self.config.master.callPrints("Number of Points : "+str(nbpts))
                self.getSend.configure(background="green")
                listpts= utils.readPoints(barray[2+v:],int(str(c)),inc,0)
                maxf=float("-inf")
                for f in listpts:
                    maxf=max(f,maxf)
                    
                print("Max value of all points : "+str(maxf))
                self.config.master.callPrints("Max value of all points : "+str(maxf))
                

                
            else:
                self.config.master.callPrints("Number of Points : "+str(c))
                self.getSend.configure(background="red")
        elif inc==5:
            listpts= utils.readPoints(barray,-1,inc,0)
            maxf=float("-inf")
            for f in listpts:
                maxf=max(f,maxf)                  
            print("Max value of all points : "+str(maxf))
            self.config.master.callPrints("Max value of all points : "+str(maxf))
            self.getSend.configure(background="green")

    def callAnswer(self, barray):
        #Create a plot where you call the command 99 others times if the command is good on the first.
        #Then you display the acq/s of that.
##        if(self.testPlot):

        if(self.test):
            self.testAnswer(barray)
        if(self.testPlot>=0):
            self.testPlotAnswer(barray)            

    def setValues(self,xmlroot):
        tags=xmlroot.findall(self.tagname)
        if(len(tags)!=0):   
            for tag in tags:
                if(len(tag)==0):
                    return
                for subelem in tag:
                    if(subelem.tag.lower() == "get"):
                        for subsubelem in subelem:
                            if(subsubelem.tag.lower() == "send"):
                                self.getSend.set(subsubelem.text)  
                            if(subsubelem.tag.lower() == "response"):
                                self.onClickListResponse(subsubelem.text.upper())
        tags=xmlroot.findall("Endian")
        if(len(tags)==0):
            self.endianvar.set(self.endianList[1])
            return
        for tag in tags:
            if(tag.text!=None and tag.text.lower()=="big"):
                self.endianvar.set(self.endianList[0])
            else:
                self.endianvar.set(self.endianList[1])
    def saveValues(self,tree):
        if not self.visible:
            return

        inc =0
        for x in self.listResponseLong:
            if x == self.textResponse.get():
                break 
            inc+=1
        
        if(inc == 3 or inc == 4):
            child=ET.SubElement(tree,"Endian")
            if(self.endianvar.get()==self.endianList[0]):
                child.text="BIG"
            else:
                child.text="LITTLE"

        child=ET.SubElement(tree,self.tagname)

        if(self.getSend!=None and not utils.textEmpty(self.getSend.get())):
            child1=ET.SubElement(child,"Get")
            child2=ET.SubElement(child1,"Send")
            child2.text=self.getSend.get()
            child2=ET.SubElement(child1,"Response")
            child2.text=self.listResponseShort[inc]
            if(child2.text=="ASCII"):
                child2.text+=":"+self.asciivar.get()
 
class ListTag(tk.Frame):
    def  __init__(self,master,config,title,tagname,tagline,hint=0,attrs=[],hinttext=None):
        tk.Frame.__init__(self,master,borderwidth=1,relief="sunken")
        self.display()
        self.tagname=tagname
        self.listLines=[]
        self.listFrames=[]
        self.attrs=attrs
        self.tagline=tagline
        
        frame2=createSubFrame(self)
        
        title=createTitleLabel(frame2,tk.LEFT,title,width=12)
 
        button=tk.Button(frame2,text='+',command=self.onClickAdd)
        button.pack(side=tk.LEFT,padx=5,pady=5)
        button=tk.Button(frame2,text='-',command=self.onClickRemove)
        button.pack(side=tk.LEFT,padx=5,pady=5)
        if(hinttext!=None):
            Hint(hinttext,title,config) 
        if(hint & 1):
            self.config.addHintWidget(1,createLabel(frame2,tk.LEFT,"(1)",0,0,2))
        if(hint & 2):
            self.config.addHintWidget(2,createLabel(frame2,tk.LEFT,"(2)",0,0,2))

        self.listmainFrame=createSubFrame(self)

        pass
    def hide(self):
        self.pack_forget()
    def display(self):
        self.pack(fill=tk.X,side=tk.TOP,expand=True,padx=(1,1),pady=(1,1))
        
    def onClickAdd(self):
        self.add()
        pass
    def onClickRemove(self):
        if(len(self.listFrames)>0):
            self.listFrames.pop().destroy()
            self.listLines.pop()
        pass
    def add(self,attrsVal=[],textvalue=""):
        if(len(attrsVal)!=len(self.attrs)):
            attrsVal=[""]*len(self.attrs)

##        frame1=createFrame(self.scrollable_frame)
##        createTitleLabel(frame1,tk.LEFT,"Notes")
        
        frame2=createSubFrame(self.listmainFrame)
        self.listFrames+=[frame2]
        createTitleLabel(frame2,tk.LEFT,self.tagline,width=8)
        frame1=createSubFrame(frame2,side=tk.LEFT)
        frame2=createSubFrame(frame1)
        createLabel(frame2,tk.LEFT,"text",5,5,12)
        entry=createEntry(frame2,tk.LEFT,width=-1)
        entry.set(textvalue)
        line=[entry]
        inc=0
        for attr in self.attrs:
            frame2=createSubFrame(frame1)
            createLabel(frame2,tk.LEFT,attr,5,5,12)
            entry=createEntry(frame2,tk.LEFT,width=-1)
            entry.set(attrsVal[inc])
            line+=[entry]
            inc+=1
        self.listLines+=[line]
        

        
        
    def setValues(self,xmlroot):
        tags=xmlroot.findall(self.tagname)
        if(len(tags)==0):
            self.add()
            return
        for tag in tags:
##            print(str(tag.tag)+";"+str(len(tag)))
            if(len(tag)==0):
                self.add()
                return
            for subelem in tag:
                attrtext=[""]*len(self.attrs)
                inc=0
                for att in subelem.attrib:
                    if(att in self.attrs):
                        attrtext[inc]=subelem.attrib[att]
                        inc+=1
                if(subelem.text==None or inc!=len(self.attrs)):
                    # Si le texte est vide ou pas d'id, alors on l'ignore
                    continue
                self.add(attrtext,str(subelem.text))
        pass
    def saveValues(self,tree):
        child=ET.SubElement(tree,self.tagname)
        
        for line in self.listLines:
            inc=0
            child1=ET.SubElement(child,self.tagline)
            child1.text=line[inc].get()
            inc+=1
            for att in self.attrs:
                child1.set(att,line[inc].get())
                inc+=1
            
            
class ModeTag(tk.Frame):
    def  __init__(self,master,config,title,tagname,hinttext=None):
        tk.Frame.__init__(self,master,borderwidth=1,relief="sunken")
        self.display()
        self.tagname=tagname
        self.config=config;
        
        
        frame2=createSubFrame(self)

        title=createTitleLabel(frame2,tk.LEFT,title)

        if(hinttext!=None):
            Hint(hinttext,title,config) 
        self.optionList=("Spectrum","VNA","Probe","Oscilloscope")
        self.textvar=tk.StringVar()
        self.textvar.set(self.optionList[0])
        optionmenu=tk.OptionMenu(frame2,self.textvar,*self.optionList,command=self.onClick)
        optionmenu.pack(side=tk.LEFT)
    def hide(self):
        self.pack_forget()
    def display(self):
        self.pack(fill=tk.X,side=tk.TOP,expand=True,padx=(1,1),pady=(1,1))
    def onClick(self,text):
        if(text=="Spectrum"):
            self.config.mode=0
        elif(text=="VNA"):
            self.config.mode=1
        elif(text=="Probe"):
            self.config.mode=2
        elif(text=="Oscilloscope"):
            self.config.mode=3
        self.config.switchDisplay()
            
    
    def setValues(self,xmlroot):
        tags=xmlroot.findall(self.tagname)
        for tag in tags:
            text=str(tag.text)
            if(text=="Spectrum"):
                self.config.mode=0
                self.textvar.set(self.optionList[0])
            elif(text=="VNA"):
                self.config.mode=1
                self.textvar.set(self.optionList[1])
            elif(text=="Probe"):
                self.config.mode=2
                self.textvar.set(self.optionList[2])
            elif(text=="Oscilloscope"):
                self.config.mode=3
                self.textvar.set(self.optionList[3])
        self.config.switchDisplay()
        
    def saveValues(self,tree):
        child=ET.SubElement(tree,self.tagname)
        child.text=self.textvar.get()
class HeaderTag(tk.Frame):
    def  __init__(self,master,config,title,tagname,hinttext=None):
        tk.Frame.__init__(self,master,borderwidth=1,relief="sunken")
        self.display()
        self.tagname=tagname
        frame2=createSubFrame(self)

        title=createTitleLabel(frame2,tk.LEFT,title)
        if(hinttext!=None):
            Hint(hinttext,title,config) 

        self.optionList=("None","IEEE 754","#A")
        self.textvar=tk.StringVar()
        self.textvar.set(self.optionList[0])
        
        optionmenu=tk.OptionMenu(frame2,self.textvar,*self.optionList,command=self.clickValue)
        optionmenu.pack(side=tk.LEFT)
    def clickValue(self,value):
        if(value=="#A"):
            self.nbptsTag.pack_forget()
            self.nbptsTag.visible=False
        elif(value=="IEEE 754"):
            self.nbptsTag.pack_forget()
            self.nbptsTag.visible=False
        else:
            self.nbptsTag.visible=True
            self.nbptsTag.pack(fill=tk.X,side=tk.TOP,expand=True,after=self)

    def hide(self):
        self.pack_forget()
    def display(self):
        self.pack(fill=tk.X,side=tk.TOP,expand=True,padx=(1,1),pady=(1,1))
                   
    def setValues(self,xmlroot):
        tags=xmlroot.findall(self.tagname)
        for tag in tags:
            text=str(tag.text)
            if(text=="#A"):
                self.textvar.set(self.optionList[2])
            elif(text=="IEEE 754"):
                self.textvar.set(self.optionList[1])
            else:
                self.textvar.set(self.optionList[0])
        self.clickValue(self.textvar.get())
    def saveValues(self,tree):
        if(self.optionList[0]!=self.textvar.get()):
            child=ET.SubElement(tree,self.tagname)
            child.text=self.textvar.get()
    def setNbPtsTag(self,tag):
        self.nbptsTag=tag
        self.clickValue(self.textvar.get())

class UnitOptionMenu(tk.Frame):
    def  __init__(self,master,unit):
        tk.Frame.__init__(self,master)
        self.pack(fill=tk.X,side=tk.TOP,expand=True)

        
        self.unittag=["Freq-Unit","Time-Unit"]
        self.unitoptionList=["Frequency unit","Time unit"]
        self.unittextvar=tk.StringVar()
        self.unittextvar.set(self.unitoptionList[unit])
        optionmenu=tk.OptionMenu(self,self.unittextvar,*self.unitoptionList,command=self.clickValue)
        optionmenu.pack(side=tk.LEFT)

        self.freqoptionList=("Hz","KHz","MHz","GHz","THz")
        self.freqtextvar=tk.StringVar()
        self.freqtextvar.set(self.freqoptionList[0])
        self.freqoptionmenu=tk.OptionMenu(self,self.freqtextvar,*self.freqoptionList)

        self.timeoptionList=("s","ds","cs","ms","µs","ns","ps")
        self.timetextvar=tk.StringVar()
        self.timetextvar.set(self.timeoptionList[0])
        self.timeoptionmenu=tk.OptionMenu(self,self.timetextvar,*self.timeoptionList)

        if unit == 0:
            self.freqoptionmenu.pack(side=tk.LEFT)
        else:
            self.timeoptionmenu.pack(side=tk.LEFT)
        
    def clickValue(self,value):
        if(value==self.unitoptionList[0]):
            self.timeoptionmenu.pack_forget()
            self.freqoptionmenu.pack(side=tk.LEFT)
        else:
            self.freqoptionmenu.pack_forget()
            self.timeoptionmenu.pack(side=tk.LEFT)
    def getTypeUnitTagName(self):
        if(self.unittextvar.get()==self.unitoptionList[0]):
            return self.unittag[0]
        else:
            return self.unittag[1]
        pass
    def getUnit(self):
        if(self.unittextvar.get()==self.unitoptionList[0]):
            return self.freqtextvar.get()
        else:
            return self.timetextvar.get()
        pass
    def setUnit(self,text):
        if(text == None or text.strip() == ""):
            return
        loweredtext=text.lower()
        # suppose if this is frequency if contain a h
        if('h' in loweredtext):
            for x in self.freqoptionList:
                if(loweredtext == x.lower()):
                    self.freqtextvar.set(x)
            self.unittextvar.set(self.unitoptionList[0])
            return

        # suppose if this is time if contain a s
        if('s' in loweredtext):
            for x in self.timeoptionList:
                if(loweredtext == x.lower()):
                    self.timetextvar.set(x)
            self.unittextvar.set(self.unitoptionList[1])  
            return
        
        
       
class SimpleTag(tk.Frame):
    def  __init__(self,master,title,tagname):
        tk.Frame.__init__(self,master,borderwidth=1,relief="sunken")
        self.display()
        self.tagname=tagname
        createLabel(self,tk.LEFT,title,5,5,12)
        self.default=createEntry(self,tk.LEFT,width=-1)
    def hide(self):
        self.pack_forget()
    def display(self):
        self.pack(fill=tk.X,side=tk.TOP,expand=True,padx=(1,1),pady=(1,1))
            
    def setValues(self,xmlroot):
        tags=xmlroot.findall(self.tagname)
        for tag in tags:
            self.default.set(str(tag.text))
    def saveValues(self,tree):
        child=ET.SubElement(tree,self.tagname)
        child.text=self.default.get()
class Config(tk.Frame,utils.ListenerInterface):

    
    def  __init__(self,root,filename,master):
        tk.Frame.__init__(self,root)
        self.pack(fill=tk.BOTH,expand=True)
        self.master=master
        self.tags=[]
        self.mode=0
        self.tagsSpectrum=[]
        self.tagsOscilloscope=[]
        self.listeners=[]
        if(filename==''):
            filename=None
        
        self.filename=filename
        print("Filename : "+str(filename))
        self.initAllUI()
        if(filename==None):
            pass
        else:
            tree = ET.parse(filename)
            root=tree.getroot()
            for tag in self.tags:
                tag.setValues(root)
            if(self.mode==0):
                for tag in self.tagsSpectrum:
                    tag.setValues(root)
            if(self.mode==3):
                for tag in self.tagsOscilloscope:
                    tag.setValues(root) 
                        
    def initAllUI(self):
        
        self.bottomhint=tk.Frame(self,borderwidth=1,relief="sunken")
        self.labelHint=tk.Label(self.bottomhint,text="",anchor="w",justify=tk.LEFT)
        # FORM
        canvasscroll=tk.Frame(self)
        
        canvas=tk.Canvas(canvasscroll)

        
        vscrollbar= tk.Scrollbar(canvasscroll,orient=tk.VERTICAL,command=canvas.yview)
##        hscrollbar= tk.Scrollbar(self,orient=tk.HORIZONTAL,command=canvas.xview,bg=utils.white)

        self.scrollable_frame=tk.Frame(canvas)
        self.scrollable_frame.pack(fill=tk.BOTH,side=tk.TOP,expand=True)
        self.scrollable_frame.bind('<Configure>',
                                   lambda e:
                                   canvas.configure(scrollregion=canvas.bbox("all")))

        
##
        canvas_frame=canvas.create_window(0,0,window=self.scrollable_frame,anchor="nw")

        canvas.bind('<Configure>',
                                   lambda e:
                                   canvas.itemconfig(canvas_frame,width=e.width))
        self.bind_all('<MouseWheel>',
                                   lambda e:
                                   canvas.yview_scroll(int(-1*(e.delta/120)),"units"))
        canvas.configure(yscrollcommand=vscrollbar.set)
##        canvas.configure(xscrollcommand=hscrollbar.set)
        canvasscroll.pack(fill=tk.BOTH,side=tk.TOP,expand=True)
##        hscrollbar.pack(side=tk.TOP,fill=tk.X)

        canvas.pack(fill=tk.BOTH,side=tk.LEFT,expand=True)
        vscrollbar.pack(side=tk.RIGHT,fill=tk.Y)
        
    
        self.initBottomMenu()


        frame1=createFrame(self.scrollable_frame,text="Notes")
##        createTitleLabel(frame1,tk.LEFT,"Notes",width=8)
        frame2=createSubFrame(frame1)
        
        
    
        self.tags=[]
        self.tags+=[SimpleTag(frame2,"Version file","File_ver")]
        self.tags+=[SimpleTag(frame2,"Date file","Date")]
        self.tags+=[SimpleTag(frame2,"Marque","Marque")]
        
        self.tags+=[ModeTag(self.scrollable_frame,self,title="Mode",tagname="Mode"
                            ,hinttext="VNA not implemented on this software. Work on Luxondes console but experimental.")]
        
        self.tags+=[ListTag(self.scrollable_frame,self,title="Devices idn",tagname="DeviceNames",tagline="Device",attrs=["id"]
                            ,hinttext="Required for work. On id, you put the answer of the *idn?. On text a sublime text")]
        self.tags+=[ListTag(self.scrollable_frame,self,title="Device initiation",tagname="Init",tagline="Line"
                            ,hinttext="Device initiation is always required for initiate the type of data receveid per the getter of Values")]

        self.tags+=[HeaderTag(self.scrollable_frame,self,title="Header",tagname="Header"
                              ,hinttext="Read your device manual for know if you have a header. IEEE754 is a header which look like '#{1-9}{number}'. #A is '#A{2bytes}")]
        self.addToList(Tag(self,title="Number of points",tagname="NumberOfPoints",unit=2,getterOnly=True,canDefault=True,hint=1
                           ,hinttext="Tag for get the number of points if lack of a header. If no command for get it, put a fixed number"))
        self.tags[-2].setNbPtsTag(self.tags[-1])

        self.addToList(GetPointsTag(self,title="Values",tagname="GetPoints",hint=2
                                    ,hinttext="Tag for get the data, require to know the type of data received."))
        self.tags[-1].setHeaderTag(self.tags[-3])
        self.tags[-1].setInitTag(self.tags[-4])
        self.addToListOscilloscope(Tag(self,title="GetHeader",tagname="GetHeader",unit=1,getterOnly=True,hint=2))
        self.addToListSpectrum(Tag(self,title="Start",tagname="Start",unit=0,getterOnly=False,canDefault=False,hint=2))
        self.addToListSpectrum(Tag(self,title="Stop",tagname="Stop",unit=0,getterOnly=False,canDefault=False,hint=2))
        self.addToListSpectrum(Tag(self,title="Center",tagname="Center",unit=0,getterOnly=False) )      
        self.addToListSpectrum(Tag(self,title="Span",tagname="Span",unit=0,getterOnly=False))
        
        self.addToListSpectrum(Tag(self,title="Rbw",tagname="Rbw",unit=2,getterOnly=True,hint=1))
        self.addToListSpectrum(Tag(self,title="Vbw",tagname="Vbw",unit=2,getterOnly=True,hint=1))
        
        self.addToListSpectrum(Tag(self,title="Attenuator",tagname="Attenuator",unit=2,getterOnly=True,hint=1))
                           
        self.addToListSpectrum(Tag(self,title="Sweep Time",tagname="SweepTime",unit=1,getterOnly=True,hint=1))
        self.addToList(Tag(self,title="Unit Y",tagname="AmplitudeUnit",unit=2,getterOnly=True,hint=1))


    def switchDisplay(self):
        if(self.mode==0):
            for tag in self.tagsSpectrum:
                tag.display()
            for tag in self.tagsOscilloscope:
                tag.hide()
        elif(self.mode==1):
            for tag in self.tagsSpectrum:
                tag.hide()
            for tag in self.tagsOscilloscope:
                tag.hide() 
        elif(self.mode==2):
            for tag in self.tagsSpectrum:
                tag.hide()
            for tag in self.tagsOscilloscope:
                tag.hide()            
        elif(self.mode==3):
            for tag in self.tagsSpectrum:
                tag.hide()
            for tag in self.tagsOscilloscope:
                tag.display() 
                    
        

        
    def initBottomMenu(self):


        
        # Bottom Menu
        bottommenu=tk.Frame(self,borderwidth=1,relief="sunken")
        bottommenu.pack(fill=tk.X,side=tk.TOP,padx=(1,1),pady=(1,1))

        # save config button
        self.saveconfigButton=tk.Button(bottommenu,text='Save',command=self.click,width=12)
        self.saveconfigButton.pack(side=tk.LEFT,padx=5,pady=5)

        # save as config button
        self.saveasconfigButton=tk.Button(bottommenu,text='Save as',command=self.onClickSaveAs,width=12)
        self.saveasconfigButton.pack(side=tk.LEFT,padx=5,pady=5)


        # Bottom Hints

        self.bottomhint.pack(fill=tk.X,side=tk.TOP,padx=(1,1),pady=(1,1))

        
        self.hint1=Hint("(1): Default can be 'None' or empty",None,self)
        self.hint2=Hint("(2): Required for Scanphone",None,self)
        self.hint3=Hint("Setter ex: :FREQ:CENTER 1000 Mhz -> :FREQ:CENTER Value Unit, if no unit, the 1000 will be converted to Hz before",None,self)
        self.hint4=Hint("Getter: Require always a '?', always wait a answer. The answer need to be only a integer,float or a unit",None,self)
        self.hint5=Hint("Response is 'Value'",None,self)
        self.labelHint.pack(side=tk.BOTTOM,padx=0,fill=tk.X,pady=0,expand=True)        
        
    def addHintWidget(self,hint,widget):
        if hint == 1: # "(1): Default can be 'None' or empty"
            self.hint1.addWidget(widget)
        if hint == 2: # "(2): Required for Scanphone"
            self.hint2.addWidget(widget)
        if hint == 3: # "(2): Required for Scanphone"
            self.hint3.addWidget(widget)
        if hint == 4: # "(2): Required for Scanphone"
            self.hint4.addWidget(widget)        
        if hint == 5: # "(2): Required for Scanphone"
            self.hint5.addWidget(widget)          

    def onClickSaveAs(self):
        root=self.buildTree()
##        self.backup(root)
        filename=fd.asksaveasfilename(initialdir=os.getcwd(),title="Save config xml",filetypes=[("XML Files","*.xml")])
        if not filename.endswith(".xml"):
            filename+=".xml"
        root.write(open(filename,"w"),encoding='unicode')
    
    def click(self):
        root=self.buildTree()
        self.backup(root)
    def buildTree(self):
        tree = ET.Element("Cmd-SCPI")
        root=ET.ElementTree(tree)
        ET.SubElement(tree,"Copyright").text="LUXONDES"
        for tag in self.tags:
            tag.saveValues(tree)
        if(self.mode==0):
            for tag in self.tagsSpectrum:
                tag.saveValues(tree)
        if(self.mode==3):
            for tag in self.tagsOscilloscope:
                tag.saveValues(tree)            
        indent(tree)
        return root

    def backup(self,root):
        if(self.filename==None):
            fileback_up='back_up.xml'
        else:
            fileback_up=self.filename[:-4]+"_back.xml"
            
        root.write(open('back_up.xml',"w"),encoding='unicode')


## Do a backup when destroyed    
    def destroy(self):
        super().destroy()
        root=self.buildTree()
        self.backup(root)
        
    def addToList(self,listener):
        self.tags+=[listener]
        self.listeners+=[listener]
    def addToListSpectrum(self,listener):
        self.tagsSpectrum+=[listener]
        self.listeners+=[listener]
    def addToListOscilloscope(self,listener):
        self.tagsOscilloscope+=[listener]
        self.listeners+=[listener]       
        
    def callAnswers(self,barray):
        for i in self.listeners:
            i.callAnswer(barray)
    def callAnswer(self, barray):
        self.callAnswers(barray)
        

        


            

def indent(elem, level=0):
    i = "\r\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
            
def createFrame(parent,text=None):
    subframe=ttk.LabelFrame(parent,text=text,padding=(5,5))
    subframe.pack(fill=tk.X,side=tk.TOP,expand=True,padx=(1,1),pady=(1,1))
    return subframe
def createSubFrame(parent,side=tk.TOP):
    subframe=tk.Frame(parent)
    subframe.pack(fill=tk.X,side=side,expand=True)
    return subframe
def createEntry(frame,side2,width=32):
    if width == -1:
        entry=utils.EntrySimplified(frame)
        entry.pack(side=side2,fill=tk.X,padx=5,expand=True)
    else:
        entry=utils.EntrySimplified(frame,width=width)
        entry.pack(side=side2,fill=tk.X,padx=5)
    return entry
def createLabel(frame,side2,text2,padx=5,pady=5,width=8):
    label=tk.Label(frame,text=text2,width=width)
    label.pack(side=side2,padx=padx,pady=pady)
    return label
def createTitleLabel(frame,side2,text2,width=-1):
    if(width==-1):
        label=tk.Label(frame,text=text2,anchor="w",font=boldfont)   
    else:
        label=tk.Label(frame,text=text2,anchor="w",font=boldfont,width=width)
    label.pack(side=side2,padx=5,pady=5)
    return label

def createDefaultCheckbutton(frame,side2,text="lack of command"):
    var1=tk.IntVar()
    checkbutton=tk.Checkbutton(frame,text=text,variable=var1)
    checkbutton.pack(side=side2,padx=5,pady=5)
    return (checkbutton,var1)
def createTestbutton(frame,side2,command,text="test"):
    button=tk.Button(frame,text=text,command=command)
    button.pack(side=side2,padx=5,pady=5)
    return button

def openWindow(toproot,filename):
    root=tk.Toplevel(toproot.master)
    splits=toproot.master.geometry().split('+')
    pos=(int(splits[1]),int(splits[2]))
    
    screen_width=toproot.master.winfo_screenwidth()
    y=300
    width=800
    widthconfig=600
    x=pos[0]+int(splits[0].split('x')[0])+5
    if(x+widthconfig>screen_width):
        x=pos[0]-widthconfig-5

    root.geometry(str(widthconfig)+"x450+%d+%d"%(x,y))

    app=Config(root,filename,toproot)
    toproot.addToListener(app)
    root.title('Config')
##    root.style = ttk.Style(root)
    root.iconbitmap(utils.getPathIcon())
##    root.style.theme_use("forest-light")
    
    return root

def openfile(toproot):
    name=fd.askopenfilename(initialdir=os.getcwd(),title="Select a config xml",filetypes=[("XML Files","*.xml")])
    if(name==None or name.strip()==""):
        return None
    return openWindow(toproot,name)
    


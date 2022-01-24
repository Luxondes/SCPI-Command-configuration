import tkinter as tk
from tkinter import filedialog as fd
import os
import utils
import struct
import plot
import time
from ctypes import *

linesmax=100
boldfont=("Helvetica",12,"bold")

class Probe(tk.Frame,utils.ListenerInterface):

    
    def  __init__(self,root,master):
        tk.Frame.__init__(self,root,bg=utils.white)
        self.pack(fill=tk.BOTH,expand=True)
        self.master=master
        self.handle=c_long (0)
        self.status =None
        self.linesX=[]
        self.linesY=[]
        self.linesZ=[]
        self.linesXYZ=[]
        self.values=[(0,0,0,0)]*linesmax
        self.timeidx=0
        self.unit=" V/m"
        self.info=None

        self.xyzField=c_float(0)
        self.xField=c_float(0)
        self.yField=c_float(0)
        self.zField=c_float(0)
        self.continueToDraw=True
        self.maxf=float("-inf")
        self.minf=float("inf")
        self.canvas = tk.Canvas(self,bg="white")
        self.canvas.pack(fill=tk.BOTH, side=tk.RIGHT,expand=True)
       

        # Load DLL into memory.

        self.etsProbeDll = WinDLL ("ETSProbe.dll")
        self.etsProbeDll.ETS_CreateProbe.argtypes=c_char_p,POINTER(c_long),c_char_p,c_char_p
        self.etsProbeDll.ETS_CreateProbe.restype=c_int

        p4 = b'HI-Any'
        switchedToFP=False

        test_i=0
        while(True):
            p1 = ("Probe #"+str(test_i)).encode()
            p3 = ("Com"+str(test_i)).encode()
            self.status =self.etsProbeDll.ETS_CreateProbe (p1, byref(self.handle),p3, p4)
            if(self.status==0):
                break
            if(self.status==3):
                test_i+=1
                if(test_i==10):
                    if(switchedToFP):
                        print("Error, not found any probe of Com[0-10] of family HI or FP")
                        root.destroy()
                        return
                    test_i=0
                    p4 = b'FP-Any'
                    switchedToFP=True
                continue

                
            
            
            
##        print(str(type(self.status))+" s "+str(self.status))
##        print(str(type(self.handle))+" h "+str(self.handle))

        self.etsProbeDll.ETS_ReadFieldSynchronous.argtypes=c_int,POINTER(c_float),POINTER(c_float),POINTER(c_float),POINTER(c_float)
        self.etsProbeDll.ETS_ReadFieldSynchronous.restype=c_int


        self.etsProbeDll.ETS_GetUnitsString.argtypes=c_int,c_char_p,c_int
        self.etsProbeDll.ETS_GetUnitsString.restype=c_int

        self.etsProbeDll.ETS_Model.argtypes=c_int,c_char_p,c_int
        self.etsProbeDll.ETS_Model.restype=c_int
        
        self.etsProbeDll.ETS_ProbeName.argtypes=c_int,c_char_p,c_int
        self.etsProbeDll.ETS_ProbeName.restype=c_int

        length_buffer_array=120

        p1=create_string_buffer(length_buffer_array)

        self.status =self.etsProbeDll.ETS_GetUnitsString (self.handle,p1, length_buffer_array)
        self.unit=" "+p1.value.decode()
        
        self.status =self.etsProbeDll.ETS_ProbeName (self.handle,p1, length_buffer_array)
        self.info=p1.value.decode()
        
        self.status =self.etsProbeDll.ETS_Model (self.handle,p1, length_buffer_array)
        self.info+=" "+p1.value.decode()

        self.loopi()
    def loopi(self):
        if(self.continueToDraw):
            self.after(100,self.loopi)
            
            self.updateLines()
            self.timeidx+=1
            self.timeidx=self.timeidx % linesmax

    def draw(self):
        self.canvas.delete("all")
        self.canvas.create_text(5,5,anchor="nw",text=(str(self.maxf)+self.unit))
        self.canvas.create_text(5,self.canvas.winfo_height()-20,anchor="nw",text=(str(self.minf)+self.unit))
##        fl=self.xField.value*self.xField.value+self.yField.value*self.yField.value+self.zField.value*self.zField.value
##        fl=fl**(0.5)
##        print(str(fl)+" "+str(self.xyzField.value)+" V/m")
##        self.canvas.create_text(self.canvas.winfo_width()/2,5,anchor="nw",text=(str(self.xyzField.value)+self.unit))
        self.canvas.create_text(self.canvas.winfo_width()/2,self.canvas.winfo_height()-20,anchor="nw",text=self.info)

        stepy=((self.canvas.winfo_height()-20)/4.)
        self.canvas.create_text(self.canvas.winfo_width()/2,5,anchor="nw",text="x",fill="green")
        self.canvas.create_text(self.canvas.winfo_width()/2+8,5,anchor="nw",text="y",fill="red")
        self.canvas.create_text(self.canvas.winfo_width()/2+16,5,anchor="nw",text="z",fill="blue")
        self.canvas.create_text(self.canvas.winfo_width()/2+24,5,anchor="nw",text="xyz",fill="black")
        if(self.linesX!=[]):
            self.canvas.create_line(self.linesX,fill="green")
            self.canvas.create_line(self.linesY,fill="red")
            self.canvas.create_line(self.linesZ,fill="blue")
            self.canvas.create_line(self.linesXYZ,fill="black")
    def updateLines(self):
        self.status =self.etsProbeDll.ETS_ReadFieldSynchronous(self.handle,byref(self.xField),byref(self.yField),byref(self.zField),byref(self.xyzField))
        self.values[self.timeidx]=(self.xField.value,self.yField.value,self.zField.value,self.xyzField.value)
        for i in self.values[self.timeidx]:
            if(self.maxf<i):
                self.maxf=i
            if(self.minf>i):
                self.minf=i                
        w=self.canvas.winfo_width()
        h=self.canvas.winfo_height()
        sh=20
        bh=h-sh*2
        self.timeidx
        stepx=w/(linesmax-1)
        inc=0
        ptsX=[]
        ptsY=[]
        ptsZ=[]
        ptsXYZ=[]
        for i in range(0,linesmax):
            idx=(self.timeidx+i)%linesmax
            tupl=self.values[idx]
            ptsX+=[(stepx*inc,sh+(bh-(tupl[0]-self.minf)/(self.maxf-self.minf)*bh))]
            ptsY+=[(stepx*inc,sh+(bh-(tupl[1]-self.minf)/(self.maxf-self.minf)*bh))]
            ptsZ+=[(stepx*inc,sh+(bh-(tupl[2]-self.minf)/(self.maxf-self.minf)*bh))]
            ptsXYZ+=[(stepx*inc,sh+(bh-(tupl[3]-self.minf)/(self.maxf-self.minf)*bh))]
            inc+=1
        self.linesX=ptsX    
        self.linesY=ptsY
        self.linesZ=ptsZ
        self.linesXYZ=ptsXYZ
        self.draw()
        
    def stop(self):
        self.continueToDraw=False
        self.etsProbeDll.ETS_RemoveProbe.argtypes=[c_long]
        self.etsProbeDll.ETS_RemoveProbe.restype=c_int
        
        self.status =self.etsProbeDll.ETS_RemoveProbe (self.handle)
##        print(str(type(self.status))+" s "+str(self.status))
##        print(str(type(self.handle))+" h "+str(self.handle))

        

def openWindow(toproot):
    root=tk.Toplevel(toproot.master)
    root.geometry(str("400x100+300+300"))
    app=Probe(root,toproot)
    toproot.addToListener(app)
    root.title('Probe')
    return root,app
    


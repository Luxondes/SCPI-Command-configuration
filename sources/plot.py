#!/usr/bin/env python3
import tkinter as tk
import random
import tkinter.font as ft
linesmax=100

class Plot(tk.Frame):


    def __init__(self,master,random=False):
        tk.Frame.__init__(self,master)
        self.pack(fill=tk.BOTH)
        self._after_id=None
        self.lines=[[]]*linesmax
        self.values=[[]]*linesmax
        self.continueToDraw=True
        self.initUI()
        self.maxf=float("-inf")
        self.minf=float("inf")
        if random:
            self.after(100,self.random)

        self.window_w=0
        self.window_h=0
        self._after_id=False
        self.canvas.bind("<Configure>",self.on_resize)

        self.loopi()


    def on_resize(self,event):
        if event.widget.widgetName== "canvas":
            if(self.window_w!=event.width or self.window_h!=event.height):
                self.window_w,self.window_h=event.width,event.height
                self._after_id=True

    def initUI(self):
        self.pack(fill=tk.BOTH, expand=1)

        self.var=tk.IntVar()
        self.var.set(0)
        scale=tk.Scale(self,variable=self.var,orient=tk.HORIZONTAL,from_=0,to=(linesmax-1),command=self.onScaleChange)
        scale.pack(fill=tk.X, side=tk.BOTTOM)

        frame=tk.Frame(self)
        frame.pack(fill=tk.BOTH, side=tk.BOTTOM,expand=True)

        self.canvas = tk.Canvas(frame,bg="white")
        self.canvas.pack(fill=tk.BOTH, side=tk.RIGHT,expand=True)

        frame=tk.Frame(frame)
        frame.pack(fill=tk.BOTH, side=tk.LEFT)

    def onScaleChange(self,event):
        self.draw()
    def setPoints(self,listval,index):
        if(index==0):
            self.maxf=float("-inf")
            self.minf=float("inf")

        for f in listval:
            self.maxf=max(f,self.maxf)
            self.minf=min(f,self.minf)

        print(str(index)+";"+str(self.maxf)+";"+str(self.minf))
        self.values[index]=listval

        if(index==99):
            self.updateLines()


    def updateLines(self):

        w=self.canvas.winfo_width()

        h=self.canvas.winfo_height()
        sh=20
        bh=h-sh*2
        index=0

        for listval in self.values:
            stepx=w/(len(listval)-1)
            inc=0
            pts=[]
            for x in listval:
                pts+=[(stepx*inc,sh+(bh-(x-self.minf)/(self.maxf-self.minf)*bh))]
                inc+=1
            self.lines[index]=pts
            index+=1
        self.draw()

    def random(self):
        self.maxf=11
        self.minf=0
        vals=[]
        for i in range(0,100):
            vals+=[random.randrange(11)]
        self.values[0]=vals
        self.updateLines()

    def loopi(self):
        if(self.continueToDraw):
            self.after(100,self.loopi)
            if(self._after_id):
                self._after_id=False
                self.updateLines()

    def draw(self):
        self.canvas.delete("all")
        self.canvas.create_text(5,5,anchor="nw",text=str(self.maxf))
        self.canvas.create_text(5,self.canvas.winfo_height()-20,anchor="nw",text=str(self.minf))

        if(self.lines[self.var.get()]!=[]):
            l=self.lines[self.var.get()]
            self.canvas.create_line(l)


    def stop(self):
        self.continueToDraw=False


def openWindow(toproot,random=False):
    root=tk.Toplevel(toproot)
    splits=toproot.geometry().split('+')
    pos=(int(splits[1]),int(splits[2]))

    screen_width=toproot.winfo_screenwidth()
    y=300
    x=pos[0]-int(splits[0].split('x')[0])+5
    print(x)
    # Put the window to the right of the main window or left if not place

    if(x<0):
        x=pos[0]+int(splits[0].split('x')[0])-5

    root.geometry(str(400)+"x250+%d+%d"%(x,y))

    app=Plot(root,random)
    root.title('Plot')
    return app

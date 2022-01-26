import tkinter as tk
##import tkinter.ttk as ttk
from port_forwarding import setup_port_map
from port_forwarding import PortMapFailed
import struct
import os
import socket

greenblue = "#415464"
white="#ffffff"
black="#000000"
orange="#ffbb33"

class ListenerInterface:
    def callMessage(self, textMessage):
        pass
    def callAnswer(self, barray):
        pass

        
        

class EntryInteger(tk.Entry):
    def __init__(self,master=None,**kwargs):
        self.var= tk.StringVar(master)
        self.var.trace('w',self.validate)
        tk.Entry.__init__(self,master,textvariable=self.var,**kwargs)
        self.get,self.set=self.var.get,self.var.set
    def validate(self,*args):
        value=self.get()
        if not value.isdigit():
            self.set(''.join(x for x in value if x.isdigit()))
    def setBg(self,i):
        if i==0:
            self.configure(bg="white")
        elif i==1:
            self.configure(bg="red")
        elif i==2:
            self.configure(bg="yellow")
        elif i==3:
            self.configure(bg="green")
        
class EntrySimplified(tk.Entry):
    def __init__(self,master=None,**kwargs):
        self.var= tk.StringVar(master)
        self.var.trace('w',self.validate)
        tk.Entry.__init__(self,master,textvariable=self.var,**kwargs)
        self.get,self.set=self.var.get,self.var.set
    def validate(self,*args):
        value=self.get()
        self.setBg(0)
    def setBg(self,i):
        if i==0:
            self.configure(bg="white")
        elif i==1:
            self.configure(bg="red")
        elif i==2:
            self.configure(bg="yellow")
        elif i==3:
            self.configure(bg="green")
def setupPort(port):
    try:
        internal_ip, external_ip=setup_port_map(port)
    except PortMapFailed:
        print("Failed port map")
    else:
        print(f"Success internal_ip={internal_ip} "
              f"external_ip={external_ip}")
        return (internal_ip,external_ip)
    return ("","")
def convertBytesToString(barray):
    try:
        return barray.decode('ascii')
    except Exception as err:
        return str(barray)

def textEmpty(text):
    if(text==None):
        return True
    if(text==""):
        return True
    if(text.lower()=="none"):
        return True
    return False


def readPoints(barray,nbbytes,typeOf,endian=1,commma=","):
    if(typeOf<4):
        if(endian==0):
            endian="little"
        else:
            endian="big"
    elif(typeOf<6):
        if(endian==0):
            endian=""
        else:
##            endian=">"
            endian=""
    
    listpts=[]
    if(typeOf == 0):
        for inc in range(0,nbbytes,2):
            listpts += [int.from_bytes(barray[inc:inc+2],endian)*0.01]
    elif(typeOf == 1):
        for inc in range(0,nbbytes,4):
            listpts += [int.from_bytes(barray[inc:inc+4],endian)*0.001]
    elif(typeOf == 2):
        for inc in range(0,nbbytes,8):
            listpts += [int.from_bytes(barray[inc:inc+8],endian)*0.001]
    elif(typeOf == 3):
        for inc in range(0,nbbytes,4):
            listpts += [struct.unpack('f',barray[inc:inc+4])[0]]
    elif(typeOf == 4):
        for inc in range(0,nbbytes,8):
            listpts += [struct.unpack('d',barray[inc:inc+8])[0]]
    elif(typeOf == 5): #ascii
        split=convertBytesToString(barray).split(commma)
        for s in split:
            listpts +=[float(s)]

    return listpts
def getIpList_Windows():
    cmd_out=os.popen('arp -a').read()
    line_arr=cmd_out.split('\n')
    line_count=len(line_arr)
    ip=socket.gethostbyname(socket.gethostname())
    ip[:ip.rfind('.')]
                            
    
    print(socket.gethostbyname(socket.gethostname()))
    for i in range(0,line_count):
        y=line_arr[i]
        print (y)
        if(y.strip().startswith(ip)):
            print (":::"+y)

            
def getPathForest():
    return getPath()+"\\graphics\\forest-light.tcl"
def getPathIcon():
    return getPath()+"\\graphics\\app_icon_round.ico"
def getOneImage():
    return tk.PhotoImage(file=getPath()+"\\graphics\\forest-light\\border-alternate.png")

# Get the path of this script for get the correct path
def getPath():
    scriptPath = os.path.realpath(__file__)
    # reverse the string
    rev_s = scriptPath[::-1]
    # get last index of the req. character
    stri=scriptPath[0:len(scriptPath) - rev_s.index("\\") - 1]
    return stri
        
##        z=y.find(mac_address)
##    devices=[]
##    for device in os.popen('arp -a'): devices.append(device)

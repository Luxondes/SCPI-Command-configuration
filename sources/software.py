#!/usr/bin/env python
import tkinter as tk

from main import *

def main():
    
    root=tk.Tk()
    root.geometry("800x450+300+300")
    root.resizable(False,False)
    app=Application(root)
    root.protocol("WM_DELETE_WINDOW",app.on_closing)
    app.master.title('Luxondes PC Test Software')
    app.mainloop()
if __name__ == '__main__':
    main()

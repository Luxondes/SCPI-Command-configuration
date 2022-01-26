import tkinter as tk
##import tkinter.ttk as ttk
import os
from main import *
import utils

class Windows(tk.Tk):
    def __init__(self):
        super().__init__()

        # root window
        self.title('Luxondes PC Test Software')
        self.geometry("800x450+300+300")
        self.resizable(False,False)
        self.iconbitmap(utils.getPathIcon())
        
##        self.style = ttk.Style(self)
##        self.tk.call("source", utils.getPathForest())
##        self.style.theme_use("forest-light")
        
        app=Application(self)
        self.protocol("WM_DELETE_WINDOW",app.on_closing)



if __name__ == '__main__':
    windows = Windows()
    windows.mainloop()

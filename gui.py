import os
import pathlib 
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from tkinter import *

# Path: gui.py

class GUI:
    def __init__(self, master):
        self.master = master
        master.title("SteamSync")
        master.geometry("400x400")

        self.label = Label(master, text="Rocket League Settings")
        self.label.pack()

        self.greet_button = Button(master, text="Select Rocket League Folder", command=self.get_file_path)
        self.greet_button.pack()

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()

        self.label = Label(master, text="Steam")
    
    def select_folder(self):
        root = Tk()
        root.withdraw()
        folder_selected = filedialog.askdirectory()
        return folder_selected
        
    def get_file_path(self):
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename()
        return file_path
    
    
        
root = tk.Tk()
my_gui = GUI(root)
root.mainloop()

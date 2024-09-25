import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog

import os

# slashes are backward when opened with filedialog

def open_root():

    global root_path

    root_path = filedialog.askdirectory(title="Open Root Path")

    path = os.path.normpath(root_path) 

    label = tk.Label(root, text="Root Path: " + path)
    label.pack()

    print("root path: ", path)

    root_path = path

def open_zip():

    global zip_path

    zip_path = filedialog.askopenfile(title="Select Zip File")

    zip_path = zip_path.name

    zip_path = zip_path.split("/")

    path = ""

    for zip in zip_path:
        
        if zip[-1] == ":":

            zip = zip + "\\"

        path = os.path.join(path, zip)

    label = tk.Label(root, text="Zip Path: " + str(path))

    label.pack()

    print("zip path: ", path)

    zip_path = path

def open_txt(): 

    global txt_path

    txt_path = filedialog.askdirectory(title="Select txt Output")

    txt_path = txt_path.split("/")

    path = ""

    for txt in txt_path:

        path = os.path.join(path, txt)

    try:

        label = tk.Label(root, text="Txt Path" + str(root_path) + "\\" + str(path))

        label.pack()

        print("txt path", str(root_path) + "\\" + str(path))

    except NameError:
        
        label = tk.Label(root, text="Root Path Does Not Exist Yet\n[Root Path]\\" + str(path))

        label.pack()

        print("Root Path Does Not Exist Yet\n[Root Path]\\", str(path))

    txt_path = path
    
def close_app():

    root.destroy()

def on_select():

    txt_button.pack()

clicked = False

def on_default():

    global txt_path, clicked

    clicked = True

    txt_button.pack_forget()

    txt_path = "\\Txt"

    try:

        label = tk.Label(root, text="Txt Path: " + str(root_path) + "\\" + str(txt_path))

        label.pack()

        print("txt path", str(root_path) + "\\" + str(txt_path))

    except NameError:
        
        label = tk.Label(root, text="Root Path Does Not Exist Yet\n[Root Path]\\" + str(txt_path))

        label.pack()

        print("Root Path Does Not Exist Yet\n[Root Path]\\", str(txt_path))
    

    print("txt path: ", txt_path)

root = tk.Tk()

root.geometry('400x350')

root.title("File Selector")

root_button = tk.Button(root, text="Open Root Path", command=open_root)  
root_button.pack(pady=10)

zip_button = tk.Button(root, text="Select Zip File", command=open_zip)  
zip_button.pack(pady=10)

txt_button = tk.Button(root, text="Select Txt Folder", command=open_txt)  
txt_button.pack(pady=10)

var = tk.IntVar()

# select your own Checkbox
# select_button = tk.Checkbutton(root, text="Select Txt Output Folder", command=on_select, variable=var, onvalue=1)
# select_button.pack(side=tk.TOP, ipady=5)

default_button = tk.Checkbutton(root, text="Use Default Txt Output Folder", command=on_default, variable=var, onvalue=2)
default_button.pack(side=tk.TOP, ipady=5)

close_button = tk.Button(root, text="Run Application", command=close_app)
close_button.pack(pady=10)

root.mainloop()

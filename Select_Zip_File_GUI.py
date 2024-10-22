import os
import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog
from PIL import Image, ImageTk
from tkinter import filedialog, font

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
    zip_path = path
    close_app()


def close_app():
    root.destroy()


root = tk.Tk()
root.geometry('400x175')
root.title("File Selector")

original_image = Image.open('zip_icon.png')  
resized_image = original_image.resize((50, 50), Image.LANCZOS)  
zip_icon = ImageTk.PhotoImage(resized_image) 

zip_button = tk.Button(root, image=zip_icon, command=open_zip, borderwidth=0)
zip_button.pack(pady=10)

custom_font = font.Font(family="Helvetica", size=12, weight="bold")  # You can change the family, size, and weight

description_label = tk.Label(root, text="Open Zip File", font=custom_font)
description_label.pack()

root.mainloop()
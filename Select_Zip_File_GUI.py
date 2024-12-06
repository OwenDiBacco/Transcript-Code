import os
import tkinter as tk
from tkinter import filedialog, font
from tkinter import ttk
from PIL import Image, ImageTk

def open_zip():
    global zip_path
    zip_path = filedialog.askopenfile(title="Select Zip File")
    if zip_path:
        zip_path = zip_path.name
        zip_path = zip_path.split("/")

        path = ""
        for zip in zip_path:
            if zip[-1] == ":":
                zip = zip + "\\"
            path = os.path.join(path, zip)

        path_label.config(text="Zip Path: " + str(path))
        adjust_window_width(path)
        zip_path = path
        

'''
Allows you to see the zip file's entire path
'''
def adjust_window_width(path):
    text_length = len("Zip Path: " + path) * 7  
    new_width = max(500, text_length)  
    root.geometry(f"{new_width}x250")

def checkbox_action():
    global checkbox_checked
    if ai_script_var.get() == 1:
        checkbox_checked = True
        status_label.config(text="AI Script Generation: Enabled", fg="green")
    else:
        checkbox_checked = False
        status_label.config(text="AI Script Generation: Disabled", fg="red")

def close_app():
    root.destroy()


# create the main window
root = tk.Tk()
root.geometry('200x250')
root.title("File Selector")

# variables
ai_script_var = tk.IntVar()
checkbox_checked = False

# load and resize the image
original_image = Image.open('images/zip_icon.png')
resized_image = original_image.resize((50, 50), Image.LANCZOS)
zip_icon = ImageTk.PhotoImage(resized_image)

# label for file path
path_label = tk.Label(root, text="", padx=10, pady=10)
path_label.pack()

# button to open zip file with image
zip_button = tk.Button(root, image=zip_icon, command=open_zip, borderwidth=0)
zip_button.pack(pady=10)

# description label
description_label = tk.Label(root, text="Open Zip File")
description_label.pack()

# checkbutton for AI script generation
checkbox = ttk.Checkbutton(
    root,
    text="Generate AI Script",
    variable=ai_script_var,
    command=checkbox_action
)
checkbox.pack(pady=10)

# status label
status_label = tk.Label(root, text="AI Script Generation: Disabled")
status_label.pack()

# close button
close_button = tk.Button(root, text="Run", command=close_app)
close_button.pack(side=tk.BOTTOM, pady=10)

root.mainloop()
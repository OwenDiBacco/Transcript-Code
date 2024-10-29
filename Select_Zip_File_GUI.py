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
        zip_path = path

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

root = tk.Tk()
root.geometry('500x350')
root.title("File Selector")
root.configure(bg="#2e2e2e")

title_font = font.Font(family="Helvetica", size=16, weight="bold")
description_font = font.Font(family="Helvetica", size=12)

style = ttk.Style()
style.configure("TCheckbutton", font=("Helvetica", 12), foreground="white", background="#2e2e2e", padding=5)

ai_script_var = tk.IntVar()

original_image = Image.open('images/zip_icon.png')
resized_image = original_image.resize((50, 50), Image.LANCZOS)
zip_icon = ImageTk.PhotoImage(resized_image)

path_label = tk.Label(root, text="", font=description_font, bg="#2e2e2e", fg="white")
path_label.pack(pady=10)

zip_button = tk.Button(root, image=zip_icon, command=open_zip, borderwidth=0, bg="#4CAF50", activebackground="#45a049")
zip_button.pack(pady=20)

description_label = tk.Label(root, text="Open Zip File", font=title_font, bg="#2e2e2e", fg="white")
description_label.pack(pady=10)

checkbox = ttk.Checkbutton(
    root,
    text="Generate AI Script",
    variable=ai_script_var,
    onvalue=1,
    offvalue=0,
    style="TCheckbutton",
    command=checkbox_action
)
checkbox.pack(pady=10)

status_label = tk.Label(root, text="AI Script Generation: Disabled", font=description_font, fg="red", bg="#2e2e2e")
status_label.pack(pady=10)

close_button = tk.Button(root, text="Close", command=close_app, font=description_font, bg="#f44336", fg="white", borderwidth=0, padx=10, pady=5)
close_button.pack(side=tk.BOTTOM, pady=10)

root.mainloop()

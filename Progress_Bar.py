import tkinter as tk
from tkinter import ttk

class ProgressBarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Progress Bar Example")
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=20)

    def update_progress(self, current, end):

        if current < end:

            self.progress["maximum"] = end
            self.progress["value"] = current
        
        else:

            root.destroy()

if __name__ == "__main__":

    global app

    root = tk.Tk()
    app = ProgressBarApp(root)

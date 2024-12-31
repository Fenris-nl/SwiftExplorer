import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ui import FolderBrowser

def main():
    """
    Main function to initialize and run the application.
    """
    root = tb.Window(themename="cyborg")
    app = FolderBrowser(root)

    # Add dark mode toggle
    dark_mode_var = tk.BooleanVar(value=True)
    dark_mode_toggle = tb.Checkbutton(root, text="Dark Mode", variable=dark_mode_var, bootstyle="switch", command=lambda: toggle_dark_mode(root, dark_mode_var))
    dark_mode_toggle.pack(side=tk.BOTTOM, pady=10)

    root.mainloop()

def toggle_dark_mode(root, var):
    """Toggle dark mode."""
    style = ttk.Style()
    if var.get():
        root.style.theme_use("cyborg")
        # Update Treeview colors for dark mode
        style.configure("Treeview",
            background="#2b2b2b",
            foreground="white",
            fieldbackground="#2b2b2b",
            selectbackground="#404040",
            selectforeground="white"
        )
    else:
        root.style.theme_use("flatly")
        # Update Treeview colors for light mode
        style.configure("Treeview",
            background="white",
            foreground="black",
            fieldbackground="white",
            selectbackground="#0078d7",
            selectforeground="white"
        )

if __name__ == "__main__":
    main()

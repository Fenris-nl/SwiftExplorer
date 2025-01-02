import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ui import FolderBrowser
import json
from pathlib import Path
from typing import Dict, Any
import logging

CONFIG_FILE = Path("config.json")

def load_config() -> Dict[str, Any]:
    """Load application configuration."""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"Error loading config: {e}")
    return {"theme": "cyborg", "default_directory": str(Path.home())}

def save_config(config: Dict[str, Any]) -> None:
    """Save application configuration."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        logging.error(f"Error saving config: {e}")

def main() -> None:
    """Initialize and run the application."""
    try:
        config = load_config()
        root = tb.Window(themename=config["theme"])
        app = FolderBrowser(root)
        
        if config["default_directory"]:
            app.directory_entry.insert(0, config["default_directory"])

        # Add dark mode toggle
        dark_mode_var = tk.BooleanVar(value=config["theme"] == "cyborg")
        dark_mode_toggle = tb.Checkbutton(
            root, 
            text="Dark Mode", 
            variable=dark_mode_var, 
            bootstyle="switch",
            command=lambda: toggle_dark_mode(root, dark_mode_var, config)
        )
        dark_mode_toggle.pack(side=tk.BOTTOM, pady=10)

        root.mainloop()
    except Exception as e:
        logging.exception("Application error")
        messagebox.showerror("Error", f"Application error: {str(e)}")

def toggle_dark_mode(root: tb.Window, var: tk.BooleanVar, config: Dict[str, Any]) -> None:
    """Toggle dark mode and save preference."""
    theme = "cyborg" if var.get() else "flatly"
    root.style.theme_use(theme)
    config["theme"] = theme
    save_config(config)
    
    style = ttk.Style()
    if var.get():
        style.configure("Treeview",
            background="#2b2b2b",
            foreground="white",
            fieldbackground="#2b2b2b",
            selectbackground="#404040",
            selectforeground="white"
        )
    else:
        style.configure("Treeview",
            background="white",
            foreground="black",
            fieldbackground="white",
            selectbackground="#0078d7",
            selectforeground="white"
        )

if __name__ == "__main__":
    main()

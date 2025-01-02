import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ui import FolderBrowser
import json
from pathlib import Path
from typing import Dict, Any
import logging
import PIL
from PIL import Image

# Monkey-patch: allow calls to Image.CUBIC by mapping it to BICUBIC
if not hasattr(Image, "CUBIC"):
    Image.CUBIC = Image.BICUBIC

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
    """Initialize and run the application with modern styling"""
    try:
        config = load_config()
        
        # Create root window with modern styling
        root = tb.Window(
            themename=config["theme"],
            scaling=1.2  # Increase default size of widgets
        )
        
        # Configure window
        root.title("SwiftExplorer")
        # Instead of setting a fixed geometry, maximize the window
        root.state('zoomed')  # For Windows
        # For Linux/Mac uncomment the following:
        # root.attributes('-zoomed', True)
        
        # Set modern font
        default_font = ('Segoe UI', 10)
        root.option_add('*Font', default_font)
        
        # Create application
        app = FolderBrowser(root)
        
        # Add theme toggle with modern styling
        create_theme_toggle(root, config)
        
        root.mainloop()

    except Exception as e:
        logging.exception("Application error")
        messagebox.showerror("Error", f"Application error: {str(e)}")

def create_theme_toggle(root: tb.Window, config: Dict[str, Any]) -> None:
    """Create modern theme toggle"""
    toggle_frame = ttk.Frame(root)
    toggle_frame.pack(side=tk.BOTTOM, pady=10)
    
    dark_mode_var = tk.BooleanVar(value=config["theme"] == "cyborg")
    
    # Create modern toggle switch
    dark_mode_toggle = ttk.Checkbutton(
        toggle_frame,
        text="Dark Mode",
        variable=dark_mode_var,
        style='Switch.TCheckbutton',
        command=lambda: toggle_dark_mode(root, dark_mode_var, config)
    )
    dark_mode_toggle.pack(side=tk.LEFT, padx=5)

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

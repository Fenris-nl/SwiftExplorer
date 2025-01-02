from datetime import datetime
import threading
import tkinter as tk
import ttkbootstrap as tb
from tkinter import filedialog, messagebox, BooleanVar
import pyperclip
from ttkbootstrap import ttk
from ttkbootstrap.constants import *
from file_operations import search_files, perform_file_operation, select_files_by_type
from preview import preview_file, update_preview_image
import os
import logging
from typing import List  # Add this import

from utils import format_size

class FolderBrowser:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional File Browser")
        self.root.geometry("1200x800")  # Set a larger default window size

        self.selected_files = []
        self.pdf_doc = None
        self.pdf_page_number = 0
        self.zoom_level = 1.0
        self.current_preview_file = None

        # Initialize the BooleanVar for the exact match checkbox
        self.exact_match_var = BooleanVar(value=True)
        self.search_jpg_var = BooleanVar(value=False)
        self.search_png_var = BooleanVar(value=False)
        self.search_gif_var = BooleanVar(value=False)
        self.search_pdf_var = BooleanVar(value=False)

        # Add more BooleanVar for file extensions
        self.extension_vars = {
            # Images
            'jpg': BooleanVar(value=False),
            'png': BooleanVar(value=False),
            'gif': BooleanVar(value=False),
            'webp': BooleanVar(value=False),
            'svg': BooleanVar(value=False),
            # Documents
            'pdf': BooleanVar(value=False),
            'doc': BooleanVar(value=False),
            'docx': BooleanVar(value=False),
            'xls': BooleanVar(value=False),
            'xlsx': BooleanVar(value=False),
            # Code files
            'py': BooleanVar(value=False),
            'java': BooleanVar(value=False),
            'cpp': BooleanVar(value=False),
            'js': BooleanVar(value=False),
            # Other
            'txt': BooleanVar(value=False),
            'md': BooleanVar(value=False),
            'json': BooleanVar(value=False),
            'xml': BooleanVar(value=False),
        }

        # Initialize preview components first
        self.canvas = None
        self.preview_text = None
        self.preview_frame = None
        
        # Add style configuration
        self.style = ttk.Style()
        self.configure_styles()

        # Create UI components
        self.create_main_layout(root)

        # Add keyboard shortcuts
        self.root.bind('<Control-f>', lambda e: self.file_names_text.focus())
        self.root.bind('<Control-o>', lambda e: self.browse_directory())
        self.root.bind('<Control-v>', lambda e: self.paste_from_clipboard())
        self.root.bind('<F5>', lambda e: self.start_search_thread())
        self.root.bind('<Control-a>', lambda e: self.select_all_results())
        
        # Add search history
        self.search_history = []
        self.max_history = 10

        # Add menu bar
        self.create_menu_bar(root)

        self.stop_event = threading.Event()  # Event to signal stopping the search

    def configure_styles(self):
        """Configure custom styles for widgets"""
        # Frame styles
        self.style.configure('Modern.TFrame', 
            background='#2b2b2b',
            padding=10,
            relief='flat'
        )

        # Label styles
        self.style.configure('Modern.TLabel',
            font=('Segoe UI', 10),
            padding=(5, 5),
            background='#2b2b2b',
            foreground='white'
        )

        # Button styles
        self.style.configure('Modern.TButton',
            font=('Segoe UI', 10),
            padding=(15, 8),
            borderwidth=0,
            relief='flat',
            background='#0078d4'
        )

        # Entry styles
        self.style.configure('Modern.TEntry',
            padding=(10, 5),
            relief='flat',
            borderwidth=0
        )

        # Treeview styles
        self.style.configure('Modern.Treeview',
            background='#2b2b2b',
            foreground='white',
            fieldbackground='#2b2b2b',
            borderwidth=0,
            relief='flat',
            rowheight=30
        )

    def create_menu_bar(self, root):
        """Create the menu bar with settings and help menus."""
        menu_bar = tk.Menu(root)
        root.config(menu=menu_bar)

        # Settings menu
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Settings", command=self.open_settings_dialog)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)

        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Help", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

    def open_settings_dialog(self):
        """Open the settings dialog."""
        settings_dialog = tk.Toplevel(self.root)
        settings_dialog.title("Settings")
        settings_dialog.geometry("400x300")
        settings_dialog.transient(self.root)
        settings_dialog.grab_set()

        # Theme selection
        theme_label = tk.Label(settings_dialog, text="Select Theme:")
        theme_label.pack(pady=10)
        theme_var = tk.StringVar(value="cyborg")
        theme_combobox = ttk.Combobox(settings_dialog, textvariable=theme_var, values=tb.Style().theme_names(), state="readonly")
        theme_combobox.pack(pady=10)

        # Default directory
        default_dir_label = tk.Label(settings_dialog, text="Default Directory:")
        default_dir_label.pack(pady=10)
        default_dir_entry = tk.Entry(settings_dialog, width=50)
        default_dir_entry.pack(pady=10)
        default_dir_button = tk.Button(settings_dialog, text="Browse", command=lambda: self.browse_default_directory(default_dir_entry))
        default_dir_button.pack(pady=10)

        # Save settings button
        save_button = tk.Button(settings_dialog, text="Save", command=lambda: self.save_settings(theme_var.get(), default_dir_entry.get()))
        save_button.pack(pady=20)

    def browse_default_directory(self, entry):
        """Browse for the default directory."""
        directory = filedialog.askdirectory()
        if directory:
            entry.delete(0, tk.END)
            entry.insert(0, directory)

    def save_settings(self, theme, default_directory):
        """Save the settings."""
        # Save the settings to a file or apply them directly
        # For simplicity, we'll just print them here
        print(f"Theme: {theme}")
        print(f"Default Directory: {default_directory}")
        self.update_status("Settings saved")

    def show_help(self):
        """Show the help dialog."""
        messagebox.showinfo("Help", "This is the help dialog. Provide useful information here.")

    def show_about(self):
        """Show the about dialog."""
        messagebox.showinfo("About", "Professional File Browser\nVersion 1.0\nDeveloped by Your Name")

    def create_main_layout(self, root):
        """
        Create the main layout by organizing frames in a PanedWindow.
        """
        # Clear or hide any existing widgets if needed
        # ...existing code...

        # Create a vertical paned window to hold top/middle/bottom
        self.main_paned = ttk.Panedwindow(root, orient="vertical")
        self.main_paned.pack(fill="both", expand=True, padx=10, pady=10)

        # Top frame (for directory, filename, and search options)
        self.top_frame = ttk.Frame(self.main_paned)
        self.create_top_frame(self.top_frame)
        self.main_paned.add(self.top_frame, weight=0)

        # Middle frame (for results and preview)
        self.middle_frame = ttk.Frame(self.main_paned)
        self.create_middle_frame(self.middle_frame)
        self.main_paned.add(self.middle_frame, weight=1)

        # Bottom frame (status bar)
        self.bottom_frame = ttk.Frame(self.main_paned)
        self.create_status_bar(self.bottom_frame)
        self.main_paned.add(self.bottom_frame, weight=0)

    def create_top_frame(self, parent_frame):
        """
        Create top frame with directory selection, filename input, search options.
        """
        top_frame = tb.Frame(parent_frame)
        top_frame.pack(fill=tk.X)

        # Directory selection frame
        self.create_directory_frame(top_frame)

        # Filename input frame
        self.create_filename_frame(top_frame)

        # Options frame
        self.create_options_frame(top_frame)

        # Search button
        self.create_search_button(top_frame)

    def create_middle_frame(self, parent_frame):
        middle_frame = tb.Frame(parent_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 5))

        # Split frame for results and preview
        self.create_results_frame(middle_frame)
        self.create_preview_frame(middle_frame)

    def create_directory_frame(self, parent_frame):
        """Create modern directory selection frame"""
        dir_frame = ttk.Frame(parent_frame, style='Modern.TFrame')
        dir_frame.pack(fill=tk.X, pady=(0, 10))

        # Add a title label
        title_frame = ttk.Frame(dir_frame, style='Modern.TFrame')
        title_frame.pack(fill=tk.X, pady=(0, 5))
        
        title_label = ttk.Label(
            title_frame, 
            text="📁 Directory Selection",
            style='Modern.TLabel',
            font=('Segoe UI', 12, 'bold')
        )
        title_label.pack(side=tk.LEFT)

        # Create search container
        search_container = ttk.Frame(dir_frame, style='Modern.TFrame')
        search_container.pack(fill=tk.X)

        self.directory_entry = ttk.Entry(
            search_container,
            style='Modern.TEntry',
            font=('Segoe UI', 10)
        )
        self.directory_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.browse_button = ttk.Button(
            search_container,
            text="Browse",
            style='Modern.TButton',
            command=self.browse_directory
        )
        self.browse_button.pack(side=tk.RIGHT)

    def create_filename_frame(self, parent_frame):
        filename_frame = tb.Frame(parent_frame)
        filename_frame.pack(fill=tk.X, pady=(10, 5))

        self.file_names_label = tb.Label(filename_frame, text="Filenames (one per line):", font=("Helvetica", 12))
        self.file_names_label.pack(side=tk.LEFT, padx=(0, 10))

        self.file_names_text = tk.Text(filename_frame, width=50, height=5, font=("Helvetica", 12))
        self.file_names_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        button_frame = tb.Frame(filename_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))

        self.paste_button = tb.Button(button_frame, text="Paste from Clipboard", command=self.paste_from_clipboard, bootstyle=SUCCESS)
        self.paste_button.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_button = tb.Button(button_frame, text="Clear Field", command=self.clear_field, bootstyle=DANGER)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))

        # Add history button
        self.history_button = tb.Button(
            button_frame,
            text="Search History",
            command=self.show_search_history,
            bootstyle=INFO
        )
        self.history_button.pack(side=tk.LEFT, padx=(0, 10))

        # Add "Clean Text" button
        self.clean_text_button = tb.Button(
            button_frame,
            text="Remove Duplicates",
            command=self.clean_text_content,
            bootstyle=WARNING
        )
        self.clean_text_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Add word count label
        self.word_count_label = tb.Label(button_frame, text="Lines: 0")
        self.word_count_label.pack(side=tk.RIGHT, padx=(10, 0))

        # Bind text changes to update word count
        self.file_names_text.bind('<<Modified>>', self.update_line_count)

    def create_options_frame(self, parent_frame):
        """Create modern options frame with categorized sections"""
        options_frame = ttk.Frame(parent_frame, style='Modern.TFrame')
        options_frame.pack(fill=tk.X, pady=10)

        # Create sections (removed filter section)
        self.create_file_types_section(options_frame)
        self.create_search_options_section(options_frame)

    def create_file_types_section(self, parent):
        """Create modern file type selection section with grouped checkboxes."""
        section = ttk.LabelFrame(
            parent,
            text="✨ File Types",
            style='Modern.TLabelframe',
            padding=10
        )
        section.pack(fill=tk.X, pady=(0, 10))

        # Create a frame for each category
        categories = {
            "🖼️ Images": [
                ('jpg', 'JPG'), ('png', 'PNG'), ('gif', 'GIF'), 
                ('webp', 'WebP'), ('svg', 'SVG'), ('ico', 'ICO')
            ],
            "📄 Documents": [
                ('pdf', 'PDF'), ('doc', 'DOC'), ('docx', 'DOCX'),
                ('xls', 'XLS'), ('xlsx', 'XLSX'), ('txt', 'TXT')
            ],
            "👨‍💻 Code": [
                ('py', 'Python'), ('java', 'Java'), ('cpp', 'C++'),
                ('js', 'JavaScript'), ('html', 'HTML'), ('css', 'CSS')
            ],
            "📦 Other": [
                ('json', 'JSON'), ('xml', 'XML'), ('md', 'Markdown'),
                ('csv', 'CSV'), ('sql', 'SQL'), ('log', 'LOG')
            ]
        }

        # Create a frame to hold all category frames
        types_container = ttk.Frame(section)
        types_container.pack(fill=tk.X, expand=True)

        # Create a frame for each category
        for category_name, extensions in categories.items():
            category_frame = ttk.LabelFrame(
                types_container,
                text=category_name,
                padding=5
            )
            category_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

            # Add checkboxes for each extension
            for ext, label in extensions:
                if ext in self.extension_vars:
                    cb = ttk.Checkbutton(
                        category_frame,
                        text=label,
                        variable=self.extension_vars[ext],
                        style='Modern.TCheckbutton'
                    )
                    cb.pack(anchor=tk.W, padx=5, pady=2)

        # Add "Select All" and "Clear All" buttons
        button_frame = ttk.Frame(section)
        button_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(
            button_frame,
            text="Select All",
            command=self.select_all_extensions,
            style='Modern.TButton'
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Clear All",
            command=self.clear_all_extensions,
            style='Modern.TButton'
        ).pack(side=tk.LEFT, padx=5)

    def select_all_extensions(self):
        """Select all file type checkboxes."""
        for var in self.extension_vars.values():
            var.set(True)

    def clear_all_extensions(self):
        """Clear all file type checkboxes."""
        for var in self.extension_vars.values():
            var.set(False)

    def create_search_button(self, parent_frame):
        search_frame = tb.Frame(parent_frame)
        search_frame.pack(fill=tk.X, pady=(10, 5))

        self.search_button = tb.Button(search_frame, text="Search", command=self.start_search_thread, bootstyle=PRIMARY)
        self.search_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))

        self.stop_button = tb.Button(search_frame, text="Stop", command=self.stop_search, bootstyle=DANGER)
        self.stop_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        self.stop_button.config(state=tk.DISABLED)

    def create_results_frame(self, parent_frame):
        results_frame = tb.Frame(parent_frame)
        results_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        results_frame.configure(width=480)  # 40% of 1200px default width

        self.create_results_treeview(results_frame)

    def create_results_treeview(self, parent_frame):
        """Create modern results treeview"""
        # Configure Treeview style
        style = ttk.Style()
        
        # Configure colors for dark mode
        style.configure("Treeview",
            background="#2b2b2b",
            foreground="white",
            fieldbackground="#2b2b2b",
            selectbackground="#404040",
            selectforeground="white"
        )
        
        # Configure row colors
        style.configure("oddrow.Treeview",
            background="#333333",
            fieldbackground="#333333"
        )
        style.configure("evenrow.Treeview",
            background="#2b2b2b",
            fieldbackground="#2b2b2b"
        )
        
        # Configure selection colors
        style.map("Treeview",
            background=[("selected", "#404040")],
            foreground=[("selected", "white")],
        )

        # Create treeview with columns
        self.results_tree = ttk.Treeview(
            parent_frame,
            columns=("Filename", "Filepath", "Size", "Date Modified"),
            show='headings',
            selectmode='extended',
            style="Treeview"
        )

        # Configure column headings
        self.results_tree.heading("Filename", text="Filename", anchor=tk.W)
        self.results_tree.heading("Filepath", text="Filepath", anchor=tk.W)
        self.results_tree.heading("Size", text="Size", anchor=tk.E)
        self.results_tree.heading("Date Modified", text="Date Modified", anchor=tk.W)

        # Configure column properties
        self.results_tree.column("Filename", width=200, anchor=tk.W, stretch=True)
        self.results_tree.column("Filepath", width=400, anchor=tk.W, stretch=True)
        self.results_tree.column("Size", width=100, anchor=tk.E, stretch=False)
        self.results_tree.column("Date Modified", width=150, anchor=tk.W, stretch=False)

        # Configure tags for alternating row colors
        self.results_tree.tag_configure('oddrow',
            background='#333333',
            foreground='white'
        )
        self.results_tree.tag_configure('evenrow',
            background='#2b2b2b',
            foreground='white'
        )
        self.results_tree.tag_configure('selected',
            background='#404040',
            foreground='white'
        )

        # Add scrollbar
        self.results_scrollbar = ttk.Scrollbar(parent_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=self.results_scrollbar.set)
        
        # Pack the scrollbar and treeview
        self.results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind events
        self.results_tree.bind('<<TreeviewSelect>>', self.preview_file)
        self.results_tree.bind('<Double-1>', self.on_double_click)
        
        # Configure the spinner
        self.spinner = tb.Progressbar(parent_frame, mode='indeterminate')
        self.spinner.pack(side=tk.TOP, pady=10)
        self.spinner.pack_forget()

        # Add modern styling to treeview
        self.results_tree.configure(style='Modern.Treeview')
        
        # Add alternating row colors
        self.results_tree.tag_configure('oddrow',
            background='#333333',
            foreground='white'
        )
        self.results_tree.tag_configure('evenrow',
            background='#2b2b2b',
            foreground='white'
        )
        
        # Add hover effect
        self.results_tree.tag_configure('hover',
            background='#404040'
        )
        
        # Bind hover events
        self.results_tree.bind('<Enter>', self.on_tree_hover)
        self.results_tree.bind('<Leave>', self.on_tree_leave)

    def on_tree_hover(self, event):
        """Handle treeview hover effect"""
        item = self.results_tree.identify_row(event.y)
        if item:
            self.results_tree.tag_add('hover', item)

    def on_tree_leave(self, event):
        """Handle treeview hover leave"""
        for item in self.results_tree.tag_has('hover'):
            self.results_tree.tag_remove('hover', item)

    def insert_file_result(self, parent, file_path, index):
        """Insert a file result into the treeview."""
        try:
            size = format_size(os.path.getsize(file_path))
            date_modified = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            
            values = (
                os.path.basename(file_path),  # Filename
                file_path,                    # Full path
                size,                         # File size
                date_modified                 # Modified date
            )
            
            item_id = self.results_tree.insert(
                parent,
                'end',
                values=values,
                tags=(tag,)
            )
            
            return item_id
        except Exception as e:
            logging.error(f"Error inserting file result: {str(e)}")
            return None

    def display_results(self, file_paths, search_type):
        """
        Display the search results in the application's results tree.

        Parameters:
        file_paths (defaultdict): A dictionary of filenames and their corresponding file paths.
        search_type (str): The type of search to perform (e.g., All, Newest, Oldest).
        """
        if search_type == "All":
            for target, paths in file_paths.items():
                parent = self.results_tree.insert('', 'end', text=target, values=("", "", "", ""))
                for index, file_path in enumerate(paths):
                    self.insert_file_result(parent, file_path, index)
        else:
            selected_files = select_files_by_type(file_paths, search_type)

            total_files = len(selected_files)
            if total_files == 0:
                self.search_button.config(state="normal")
                self.spinner.stop()
                self.spinner.pack_forget()
                return

            sort_by = self.sort_by_var.get()
            if (sort_by == "Size"):
                selected_files.sort(key=lambda x: os.path.getsize(x))
            elif (sort_by == "Date"):
                selected_files.sort(key=os.path.getmtime)

            for index, file_path in enumerate(selected_files):
                self.insert_file_result('', file_path, index)

    def create_file_operations_frame(self, parent_frame):
        file_ops_frame = tb.Frame(parent_frame)
        file_ops_frame.pack(fill=tk.X, pady=(10, 5))

        self.copy_button = tb.Button(file_ops_frame, text="Copy Selected", command=lambda: perform_file_operation(self.results_tree, 'copy'), bootstyle=PRIMARY)
        self.copy_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.move_button = tb.Button(file_ops_frame, text="Move Selected", command=lambda: perform_file_operation(self.results_tree, 'move'), bootstyle=PRIMARY)
        self.move_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.delete_button = tb.Button(file_ops_frame, text="Delete Selected", command=lambda: perform_file_operation(self.results_tree, 'delete'), bootstyle=DANGER)
        self.delete_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Add "Select All" button
        self.select_all_button = tb.Button(file_ops_frame, text="Select All", command=self.select_all_results, bootstyle=INFO)
        self.select_all_button.pack(side=tk.LEFT, padx=(0, 10))

    def create_preview_frame(self, parent_frame):
        """
        Create preview area (canvas or text).
        """
        # Create preview frame with fixed minimum size
        self.preview_frame = tb.Frame(parent_frame)
        self.preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Set minimum size
        self.preview_frame.grid_propagate(False)
        self.preview_frame.configure(width=600, height=400)

        preview_label = tb.Label(self.preview_frame, text="File Preview:", font=("Helvetica", 12))
        preview_label.pack(side=tk.TOP, anchor=tk.W, padx=(0, 10))

        # Canvas frame with scrollbars
        canvas_frame = tb.Frame(self.preview_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbars
        y_scrollbar = tb.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        x_scrollbar = tb.Scrollbar(self.preview_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas.configure(
            xscrollcommand=x_scrollbar.set,
            yscrollcommand=y_scrollbar.set
        )

        # Navigation controls
        self.create_navigation_controls(self.preview_frame)

        # Text preview
        self.preview_text = tk.Text(self.preview_frame, wrap="none", state=tk.DISABLED)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        self.preview_text.pack_forget()  # Initially hidden

    def create_navigation_controls(self, parent_frame):
        """Create navigation controls in a separate method."""
        nav_frame = tb.Frame(parent_frame)
        nav_frame.pack(pady=(10, 5), fill=tk.X)

        # Left side controls
        left_controls = tb.Frame(nav_frame)
        left_controls.pack(side=tk.LEFT)

        self.prev_page_button = tb.Button(left_controls, text="Previous Page", 
                                        command=self.prev_pdf_page, state=tk.DISABLED)
        self.prev_page_button.pack(side=tk.LEFT, padx=5)

        self.next_page_button = tb.Button(left_controls, text="Next Page", 
                                        command=self.next_pdf_page, state=tk.DISABLED)
        self.next_page_button.pack(side=tk.LEFT, padx=5)

        # Right side controls
        right_controls = tb.Frame(nav_frame)
        right_controls.pack(side=tk.RIGHT)

        self.zoom_out_button = tb.Button(right_controls, text="Zoom Out", 
                                       command=self.zoom_out, state=tk.DISABLED)
        self.zoom_out_button.pack(side=tk.LEFT, padx=5)

        self.zoom_in_button = tb.Button(right_controls, text="Zoom In", 
                                      command=self.zoom_in, state=tk.DISABLED)
        self.zoom_in_button.pack(side=tk.LEFT, padx=5)

    def create_status_bar(self, parent_frame):
        """
        Create a status bar at the bottom.
        """
        self.status_bar = tb.Label(parent_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, message):
        """Update the status bar message."""
        self.status_bar.config(text=message)
        self.root.update_idletasks()

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.directory_entry.delete(0, tk.END)
            self.directory_entry.insert(0, directory)

    def paste_from_clipboard(self):
        """Paste and clean up clipboard content."""
        try:
            clipboard_content = pyperclip.paste()
            # Clean up the text by removing duplicates and empty lines
            lines = clipboard_content.strip().split('\n')
            # Remove empty lines and strip whitespace
            lines = [line.strip() for line in lines if line.strip()]
            # Remove duplicates while preserving order
            cleaned_lines = []
            seen = set()
            for line in lines:
                if line not in seen:
                    cleaned_lines.append(line)
                    seen.add(line)
            
            # Insert cleaned content
            self.file_names_text.delete("1.0", tk.END)
            self.file_names_text.insert(tk.END, '\n'.join(cleaned_lines))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste from clipboard: {e}")

    def clear_field(self):
        self.file_names_text.delete("1.0", tk.END)

    def start_search_thread(self):
        try:
            search_text = self.file_names_text.get("1.0", "end").strip()
            if not search_text:
                messagebox.showwarning("Warning", "Please enter at least one filename")
                return

            if search_text:
                self.add_to_search_history(search_text)
                
            # Clean up text before searching
            self.clean_text_content()
            
            self.search_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.spinner.pack()
            self.spinner.start()
            self.stop_event.clear()  # Clear the stop event before starting the search
            search_thread = threading.Thread(target=lambda: search_files(self))
            search_thread.start()
        except Exception as e:
            self.update_status(f"Search error: {str(e)}")
            self.search_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.spinner.stop()
            self.spinner.pack_forget()

    def stop_search(self):
        """Stop the search operation."""
        self.stop_event.set()
        self.update_status("Stopping search...")
        self.search_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.spinner.stop()
        self.spinner.pack_forget()

    def preview_file(self, event):
        try:
            selected_items = self.results_tree.selection()
            if not selected_items:
                return

            item = selected_items[0]
            values = self.results_tree.item(item)['values']
            
            if not values or not all(values):
                return  # Skip if it's a parent/folder item

            file_path = values[1]
            if not os.path.exists(file_path):
                messagebox.showerror("Error", f"File not found: {file_path}")
                return

            self.current_preview_file = file_path
            self.zoom_level = 1.0

            if self.canvas:
                self.canvas.delete("all")
            if self.preview_text:
                self.preview_text.config(state=tk.NORMAL)
                self.preview_text.delete("1.0", tk.END)
                self.preview_text.config(state=tk.DISABLED)
                self.preview_text.pack_forget()

            preview_file(self, file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview file: {str(e)}")
            logging.error(f"Preview error: {str(e)}")

    def sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        try:
            l.sort(key=lambda t: float(t[0]), reverse=reverse)
        except ValueError:
            l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        tv.heading(col, command=lambda: self.sort_column(tv, col, not reverse))

    def on_mouse_wheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def prev_pdf_page(self):
        if self.pdf_doc and self.pdf_page_number > 0:
            self.pdf_page_number -= 1
            preview_file(self, self.current_preview_file, self.pdf_page_number)

    def next_pdf_page(self):
        if self.pdf_doc and self.pdf_page_number < len(self.pdf_doc) - 1:
            self.pdf_page_number += 1
            preview_file(self, self.current_preview_file, self.pdf_page_number)

    def zoom_in(self):
        self.zoom_level += 0.1
        update_preview_image(self)

    def zoom_out(self):
        if self.zoom_level > 0.1:
            self.zoom_level -= 0.1
            update_preview_image(self)

    def select_all_results(self):
        for item in self.results_tree.get_children():
            self.results_tree.selection_add(item)

    def add_to_search_history(self, search_text):
        """Add search text to history and maintain max size."""
        if search_text not in self.search_history:
            self.search_history.insert(0, search_text)
            if len(self.search_history) > self.max_history:
                self.search_history.pop()

    def show_search_history(self):
        """Display search history in a popup menu."""
        if not self.search_history:
            return
            
        menu = tk.Menu(self.root, tearoff=0)
        for item in self.search_history:
            menu.add_command(
                label=item[:50] + "..." if len(item) > 50 else item,
                command=lambda x=item: self.use_history_item(x)
            )
        
        menu.post(
            self.file_names_text.winfo_rootx(),
            self.file_names_text.winfo_rooty() + self.file_names_text.winfo_height()
        )

    def use_history_item(self, text):
        """Insert history item into search field."""
        self.file_names_text.delete("1.0", tk.END)
        self.file_names_text.insert("1.0", text)

    def clean_text_content(self):
        """Remove duplicates and empty lines from the text content."""
        try:
            content = self.file_names_text.get("1.0", tk.END).strip()
            lines = [line for line in content.split('\n') if line.strip()]
            # Remove empty lines and strip whitespace
            lines = [line.strip() for line in lines if line.strip()]
            # Remove duplicates while preserving order
            cleaned_lines = []
            seen = set()
            for line in lines:
                if line not in seen:
                    cleaned_lines.append(line)
                    seen.add(line)
            
            # Update text content
            self.file_names_text.delete("1.0", tk.END)
            self.file_names_text.insert(tk.END, '\n'.join(cleaned_lines))
            
            # Show cleanup results
            duplicates_removed = len(lines) - len(cleaned_lines)
            if duplicates_removed > 0:
                self.update_status(f"Removed {duplicates_removed} duplicate lines")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clean text: {e}")

    def update_line_count(self, event=None):
        """Update the line count label."""
        try:
            content = self.file_names_text.get("1.0", tk.END).strip()
            lines = [line for line in content.split('\n') if line.strip()]
            self.word_count_label.config(text=f"Lines: {len(lines)}")
            self.file_names_text.edit_modified(False)  # Reset modified flag
        except Exception as e:
            logging.error(f"Error updating line count: {e}")

    def on_double_click(self, event):
        """Handle double-click on treeview item."""
        try:
            selected_items = self.results_tree.selection()
            if not selected_items:
                return

            item = selected_items[0]
            values = self.results_tree.item(item)['values']
            
            if not values or not all(values):
                return  # Skip if it's a parent/folder item

            file_path = values[1]
            if not os.path.exists(file_path):
                messagebox.showerror("Error", f"File not found: {file_path}")
                return

            os.startfile(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {repr(e)}")
            logging.error(f"Error opening file: {repr(e)}")

    def get_selected_extensions(self) -> List[str]:
        """
        Get list of selected file extensions.
        
        Returns:
            List[str]: List of selected file extensions with dots (e.g., ['.jpg', '.png'])
        """
        return [f'.{ext}' for ext, var in self.extension_vars.items() if var.get()]

    def create_search_options_section(self, parent):
        """Create modern search options section"""
        section = ttk.LabelFrame(
            parent,
            text="🔍 Search Options",
            style='Modern.TLabelframe',
            padding=10
        )
        section.pack(fill=tk.X, pady=(0, 10))

        # Create options container
        options_container = ttk.Frame(section, style='Modern.TFrame')
        options_container.pack(fill=tk.X, expand=True)

        # Left side - Search modes
        search_modes = ttk.Frame(options_container, style='Modern.TFrame')
        search_modes.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Search mode checkboxes
        self.exact_match_checkbox = ttk.Checkbutton(
            search_modes,
            text="Exact Match",
            variable=self.exact_match_var,
            style='Modern.TCheckbutton'
        )
        self.exact_match_checkbox.pack(anchor=tk.W, pady=2)

        self.case_sensitive_checkbox = ttk.Checkbutton(
            search_modes,
            text="Case Sensitive",
            style='Modern.TCheckbutton'
        )
        self.case_sensitive_checkbox.pack(anchor=tk.W, pady=2)

        self.search_content_checkbox = ttk.Checkbutton(
            search_modes,
            text="Search Content",
            style='Modern.TCheckbutton'
        )
        self.search_content_checkbox.pack(anchor=tk.W, pady=2)

        # Right side - Sort options
        sort_options = ttk.Frame(options_container, style='Modern.TFrame')
        sort_options.pack(side=tk.RIGHT, fill=tk.Y, padx=5)

        # Sort by dropdown
        ttk.Label(
            sort_options,
            text="Sort By:",
            style='Modern.TLabel'
        ).pack(side=tk.LEFT, padx=5)

        self.sort_by_var = tk.StringVar(value="None")
        sort_by = ttk.Combobox(
            sort_options,
            textvariable=self.sort_by_var,
            values=["None", "Size", "Date"],
            state="readonly",
            width=15
        )
        sort_by.pack(side=tk.LEFT, padx=5)

        # Search type dropdown
        ttk.Label(
            sort_options,
            text="Search Type:",
            style='Modern.TLabel'
        ).pack(side=tk.LEFT, padx=5)

        self.search_type_var = tk.StringVar(value="All")
        search_type = ttk.Combobox(
            sort_options,
            textvariable=self.search_type_var,
            values=["All", "Newest", "Oldest", "Largest", "Smallest"],
            state="readonly",
            width=15
        )
        search_type.pack(side=tk.LEFT, padx=5)


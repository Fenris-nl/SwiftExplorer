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
        # Main frame
        main_frame = tb.Frame(root)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Create all frames
        self.create_top_frame(main_frame)
        self.create_middle_frame(main_frame)
        self.create_file_operations_frame(main_frame)
        self.create_status_bar(main_frame)

    def create_status_bar(self, parent_frame):
        """Create a status bar for displaying operation feedback."""
        self.status_bar = tb.Label(parent_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, message):
        """Update the status bar message."""
        self.status_bar.config(text=message)
        self.root.update_idletasks()

    def create_top_frame(self, parent_frame):
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

    def create_middle_frame(self, parent):
        middle_frame = tb.Frame(parent)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 5))

        # Split frame for results and preview
        self.create_results_frame(middle_frame)
        self.create_preview_frame(middle_frame)

    def create_directory_frame(self, parent_frame):
        dir_frame = tb.Frame(parent_frame)
        dir_frame.pack(fill=tk.X, pady=(10, 5))

        self.directory_label = tb.Label(dir_frame, text="Select Directory:", font=("Helvetica", 12))
        self.directory_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.directory_entry = tb.Entry(dir_frame, width=50, font=("Helvetica", 12))
        self.directory_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.browse_button = tb.Button(dir_frame, text="Browse", command=self.browse_directory, bootstyle=PRIMARY)
        self.browse_button.pack(side=tk.LEFT)

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
        options_frame = tb.Frame(parent_frame)
        options_frame.pack(fill=tk.X, pady=(10, 5))

        # Create checkboxes frame with scrollbar
        extensions_frame = tb.LabelFrame(options_frame, text="File Extensions", padding=5)
        extensions_frame.pack(fill=tk.X, pady=5)

        # Create canvas and scrollbar for extensions
        canvas = tk.Canvas(extensions_frame, height=100)
        scrollbar = ttk.Scrollbar(extensions_frame, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)

        canvas.configure(xscrollcommand=scrollbar.set)

        # Group extensions by type
        extension_groups = {
            "Images": [('jpg', 'JPG'), ('png', 'PNG'), ('gif', 'GIF'), ('webp', 'WebP'), ('svg', 'SVG')],
            "Documents": [('pdf', 'PDF'), ('doc', 'DOC'), ('docx', 'DOCX'), ('xls', 'XLS'), ('xlsx', 'XLSX')],
            "Code": [('py', 'Python'), ('java', 'Java'), ('cpp', 'C++'), ('js', 'JavaScript')],
            "Other": [('txt', 'TXT'), ('md', 'MD'), ('json', 'JSON'), ('xml', 'XML')]
        }

        # Create extension checkboxes in groups
        current_x = 0
        for group_name, extensions in extension_groups.items():
            group_frame = ttk.LabelFrame(scrollable_frame, text=group_name, padding=5)
            group_frame.pack(side=tk.LEFT, padx=5, fill=tk.Y)
            
            for ext, label in extensions:
                cb = tb.Checkbutton(
                    group_frame,
                    text=label,
                    variable=self.extension_vars[ext],
                    bootstyle="round-toggle"
                )
                cb.pack(anchor=tk.W, padx=5)
                current_x += cb.winfo_reqwidth()

        # Configure canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.pack(side=tk.TOP, fill=tk.X, expand=True)
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Rest of options
        options_inner_frame = tb.Frame(options_frame)
        options_inner_frame.pack(fill=tk.X, pady=5)

        self.exact_match_checkbox = tb.Checkbutton(options_inner_frame, text="Exact Match", 
                                                 variable=self.exact_match_var, bootstyle="info-round-toggle")
        self.exact_match_checkbox.pack(side=tk.LEFT, padx=5)

        self.case_sensitive_checkbox = tb.Checkbutton(options_inner_frame, text="Case Sensitive", 
                                                    bootstyle="info-round-toggle")
        self.case_sensitive_checkbox.pack(side=tk.LEFT, padx=5)

        self.search_content_checkbox = tb.Checkbutton(options_inner_frame, text="Search Content", bootstyle=INFO)
        self.search_content_checkbox.pack(side=tk.LEFT, padx=(0, 10))

        self.sort_by_label = tb.Label(options_inner_frame, text="Sort By:", font=("Helvetica", 12))
        self.sort_by_label.pack(side=tk.LEFT, padx=(0, 10))

        self.sort_by_var = tk.StringVar()
        self.sort_by_var.set("None")
        self.sort_by_combobox = ttk.Combobox(options_inner_frame, textvariable=self.sort_by_var, values=["None", "Size", "Date"], state="readonly")
        self.sort_by_combobox.pack(side=tk.LEFT, padx=(0, 10))

        self.search_type_label = tb.Label(options_inner_frame, text="Search Type:", font=("Helvetica", 12))
        self.search_type_label.pack(side=tk.LEFT, padx=(0, 10))

        self.search_type_var = tk.StringVar()
        self.search_type_var.set("All")
        self.search_type_combobox = ttk.Combobox(options_inner_frame, textvariable=self.search_type_var, values=["All", "Newest", "Oldest", "Largest", "Smallest"], state="readonly")
        self.search_type_combobox.pack(side=tk.LEFT, padx=(0, 10))

        # Add advanced search options
        self.min_size_label = tb.Label(options_inner_frame, text="Min Size (KB):", font=("Helvetica", 12))
        self.min_size_label.pack(side=tk.LEFT, padx=(0, 10))
        self.min_size_var = tk.IntVar()
        self.min_size_entry = tb.Entry(options_inner_frame, textvariable=self.min_size_var, width=10)
        self.min_size_entry.pack(side=tk.LEFT, padx=(0, 10))

        self.max_size_label = tb.Label(options_inner_frame, text="Max Size (KB):", font=("Helvetica", 12))
        self.max_size_label.pack(side=tk.LEFT, padx=(0, 10))
        self.max_size_var = tk.IntVar()
        self.max_size_entry = tb.Entry(options_inner_frame, textvariable=self.max_size_var, width=10)
        self.max_size_entry.pack(side=tk.LEFT, padx=(0, 10))

        self.date_range_label = tb.Label(options_inner_frame, text="Date Range:", font=("Helvetica", 12))
        self.date_range_label.pack(side=tk.LEFT, padx=(0, 10))
        self.date_range_var = tk.StringVar()
        self.date_range_entry = tb.Entry(options_inner_frame, textvariable=self.date_range_var, width=20)
        self.date_range_entry.pack(side=tk.LEFT, padx=(0, 10))

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
        """Create the results treeview with proper configuration."""
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
        self.results_tree.heading("Size", text="Size", anchor=tk.W)
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
            if (self.min_size_var.get() > 0 or self.max_size_var.get() > 0) and total_files > 0:
                selected_files = [f for f in selected_files if self.min_size_var.get() <= os.path.getsize(f) / 1024 <= self.max_size_var.get()]
            if self.date_range_var.get() and total_files > 0:
                date_range = self.date_range_var.get().split('-')
                if len(date_range) == 2:
                    start_date = datetime.strptime(date_range[0].strip(), '%Y-%m-%d')
                    end_date = datetime.strptime(date_range[1].strip(), '%Y-%m-%d')
                    selected_files = [f for f in selected_files if start_date <= datetime.fromtimestamp(os.path.getmtime(f)) <= end_date]

            total_files = len(selected_files)
            if total_files == 0:
                self.search_button.config(state="normal")
                self.spinner.stop()
                self.spinner.pack_forget()
                return

            sort_by = self.sort_by_var.get()
            if sort_by == "Size":
                selected_files.sort(key=lambda x: os.path.getsize(x))
            elif sort_by == "Date":
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
            lines = content.split('\n')
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

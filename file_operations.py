import os
import shutil
import difflib
from tkinter import filedialog, messagebox
from datetime import datetime
from utils import format_size
from collections import defaultdict
import logging
import tkinter as tk
from tkinter import ttk

logging.basicConfig(level=logging.ERROR, filename='app_errors.log')

def search_files(app):
    """Search for files in the specified directory based on user input."""
    try:
        directory = app.directory_entry.get()
        exact_match = app.exact_match_var.get()
        case_sensitive = app.case_sensitive_checkbox.instate(['selected'])
        search_content = app.search_content_checkbox.instate(['selected'])
        search_type = app.search_type_var.get()

        extensions = get_extensions(app)
        filenames = app.file_names_text.get("1.0", "end").strip().split('\n')
        filenames = [filename.strip() for filename in filenames if filename.strip()]

        if not directory:
            show_error(app, "Please select a directory")
            return

        if not filenames:
            show_error(app, "Please enter filenames")
            return

        # Clear existing results
        app.results_tree.delete(*app.results_tree.get_children())
        app.selected_files = []

        print(f"Searching in directory: {directory}")  # Debug print
        print(f"Searching for files: {filenames}")  # Debug print

        # Perform the search
        found_files = defaultdict(list)
        for root, _, files in os.walk(directory):
            if app.stop_event.is_set():
                print("Search stopped")  # Debug print
                break
            for file in files:
                if app.stop_event.is_set():
                    print("Search stopped")  # Debug print
                    break
                file_name, file_extension = os.path.splitext(file)
                if not extensions or file_extension.lower() in extensions:
                    file_path = os.path.join(root, file)
                    for target in filenames:
                        if app.stop_event.is_set():
                            print("Search stopped")  # Debug print
                            break
                        if exact_match:
                            if is_exact_match(file, target, extensions, case_sensitive):
                                found_files[target].append(file_path)
                                print(f"Found exact match: {file_path}")  # Debug print
                        else:
                            if (target.lower() in file_name.lower()) or search_content and search_file_content(file_path, target):
                                found_files[target].append(file_path)
                                print(f"Found match: {file_path}")  # Debug print

        print(f"Total files found: {sum(len(files) for files in found_files.values())}")  # Debug print

        # Display results
        app.results_tree.delete(*app.results_tree.get_children())  # Clear existing results
        
        if found_files:
            for index, (target, paths) in enumerate(found_files.items()):
                for file_path in paths:
                    if app.stop_event.is_set():
                        print("Search stopped")  # Debug print
                        break
                    app.insert_file_result('', file_path, index)  # Insert directly without parent
                    print(f"Inserting file: {file_path}")  # Debug print
        
            # Update status with total files found
            total_files = sum(len(paths) for paths in found_files.values())
            app.update_status(f"Found {total_files} file(s)")
        else:
            app.update_status("No files found")

    except Exception as e:
        print(f"Search error: {str(e)}")  # Debug print
        logging.error(f"Search error: {str(e)}")
        show_error(app, f"Search error: {str(e)}")
    finally:
        app.search_button.config(state="normal")
        app.stop_button.config(state=tk.DISABLED)
        app.spinner.stop()
        app.spinner.pack_forget()

def get_extensions(app):
    """
    Get the list of file extensions to search for based on user input.

    Parameters:
    app (object): The application instance containing search parameters.

    Returns:
    list: A list of file extensions to search for.
    """
    extensions = []
    if app.search_jpg_var.get():
        extensions.append('.jpg')
    if app.search_png_var.get():
        extensions.append('.png')
    if app.search_gif_var.get():
        extensions.append('.gif')
    if app.search_pdf_var.get():
        extensions.append('.pdf')
    return extensions

def show_error(app, message):
    """
    Show an error message and reset the search button and spinner.

    Parameters:
    app (object): The application instance containing the UI elements.
    message (str): The error message to display.
    """
    messagebox.showerror("Error", message)
    app.search_button.config(state="normal")
    app.spinner.stop()
    app.spinner.pack_forget()

def search_directory(directory, filenames, extensions, exact_match, case_sensitive, search_content):
    """
    Search the specified directory for files matching the search criteria.

    Parameters:
    directory (str): The directory to search.
    filenames (list): The list of filenames to search for.
    extensions (list): The list of file extensions to search for.
    exact_match (bool): Whether to search for exact matches.
    case_sensitive (bool): Whether to perform a case-sensitive search.
    search_content (bool): Whether to search the content of the files.

    Returns:
    defaultdict: A dictionary of filenames and their corresponding file paths.
    """
    file_paths = defaultdict(list)
    for root, _, files in os.walk(directory):
        for file in files:
            file_name, file_extension = os.path.splitext(file)
            if not extensions or file_extension.lower() in extensions:
                for target in filenames:
                    if exact_match:
                        if is_exact_match(file, target, extensions, case_sensitive):
                            file_paths[target].append(os.path.join(root, file))
                            logging.info(f"Exact match found: {file}")
                    else:
                        if search_content:
                            if search_file_content(os.path.join(root, file), target):
                                file_paths[target].append(os.path.join(root, file))
                                logging.info(f"Content match found: {file}")
                        else:
                            if (target.lower() in file_name.lower()) or (difflib.SequenceMatcher(None, file_name.lower(), target.lower()).ratio() > 0.8):
                                file_paths[target].append(os.path.join(root, file))
                                logging.info(f"Partial match found: {file}")
    return file_paths

def is_exact_match(file, target, extensions, case_sensitive):
    """
    Check if the file matches the target exactly, considering case sensitivity and extensions.

    Parameters:
    file (str): The filename to check.
    target (str): The target filename to match.
    extensions (list): The list of file extensions to consider.
    case_sensitive (bool): Whether to perform a case-sensitive match.

    Returns:
    bool: True if the file matches the target exactly, False otherwise.
    """
    matched = False
    if case_sensitive:
        if file == target:
            matched = True
    else:
        if file.lower() == target.lower():
            matched = True

    if not matched and not target.endswith(tuple(extensions)):
        for ext in extensions:
            target_with_ext = f"{target}{ext}"
            if case_sensitive:
                if file == target_with_ext:
                    matched = True
            else:
                if file.lower() == target_with_ext.lower():
                    matched = True
            if matched:
                break
    return matched

def display_results(app, file_paths, search_type):
    """
    Display the search results in the application's results tree.

    Parameters:
    app (object): The application instance containing the results tree.
    file_paths (defaultdict): A dictionary of filenames and their corresponding file paths.
    search_type (str): The type of search to perform (e.g., All, Newest, Oldest).
    """
    logging.info(f"Displaying results for search type: {search_type}")
    if search_type == "All":
        for target, paths in file_paths.items():
            parent = app.results_tree.insert('', 'end', text=target, values=("", "", "", ""))
            for index, file_path in enumerate(paths):
                logging.info(f"Inserting file: {file_path}")
                app.insert_file_result(parent, file_path, index)
    else:
        selected_files = select_files_by_type(file_paths, search_type)

        total_files = len(selected_files)
        if total_files == 0:
            app.search_button.config(state="normal")
            app.spinner.stop()
            app.spinner.pack_forget()
            return

        sort_by = app.sort_by_var.get()
        if sort_by == "Size":
            selected_files.sort(key=lambda x: os.path.getsize(x))
        elif sort_by == "Date":
            selected_files.sort(key=os.path.getmtime)

        for index, file_path in enumerate(selected_files):
            logging.info(f"Inserting file: {file_path}")
            app.insert_file_result('', file_path, index)

def insert_file_result(app, parent, file_path, index):
    """Insert a file result into the results tree."""
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
        
        item_id = app.results_tree.insert(
            parent, 'end',
            values=values,
            tags=(tag,)
        )
        
        print(f"Inserted item: {values}")  # Debug print
        return item_id
        
    except Exception as e:
        print(f"Error inserting file result: {str(e)}")  # Debug print
        logging.error(f"Error inserting file result: {str(e)}")
        return None

def select_files_by_type(file_paths, search_type):
    """
    Select files based on the specified search type (e.g., Newest, Oldest).

    Parameters:
    file_paths (defaultdict): A dictionary of filenames and their corresponding file paths.
    search_type (str): The type of search to perform.

    Returns:
    list: A list of selected file paths based on the search type.
    """
    selected_files = []
    for target, paths in file_paths.items():
        if paths:
            if search_type == "Newest":
                selected_file = max(paths, key=os.path.getmtime)
            elif search_type == "Oldest":
                selected_file = min(paths, key=os.path.getmtime)
            selected_files.append(selected_file)
    return selected_files

def search_file_content(file_path, search_text):
    """
    Search for the specified text within a file.

    Parameters:
    file_path (str): The path of the file to search.
    search_text (str): The text to search for.

    Returns:
    bool: True if the text is found in the file, False otherwise.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return search_text in content
    except Exception as e:
        print(f"Error searching content in file {file_path}: {e}")
        return False

def perform_file_operation(results_tree, operation):
    try:
        selected_items = results_tree.selection()
        if not selected_items:
            messagebox.showerror("Error", "No files selected")
            return

        if operation in ['copy', 'move']:
            destination = filedialog.askdirectory()
            if not destination:
                return
            if not os.path.exists(destination):
                messagebox.showerror("Error", "Selected destination does not exist")
                return

        # Create progress window
        progress_window = create_progress_window(results_tree, len(selected_items))
        
        try:
            for i, item in enumerate(selected_items, 1):
                file_path = results_tree.item(item)['values'][1]
                if not os.path.exists(file_path):
                    logging.error(f"File not found: {file_path}")
                    continue

                update_progress(progress_window, i, len(selected_items), file_path)
                
                try:
                    if operation == 'delete':
                        delete_file(file_path)
                    elif operation == 'copy':
                        copy_file(file_path, destination)
                    elif operation == 'move':
                        move_file(file_path, destination)
                except Exception as e:
                    logging.error(f"Operation failed for {file_path}: {str(e)}")
                    
        finally:
            progress_window.destroy()
            
        messagebox.showinfo("Success", "Operation completed")
        
    except Exception as e:
        logging.error(f"File operation error: {str(e)}")
        messagebox.showerror("Error", f"Operation failed: {str(e)}")

def create_progress_window(parent, total_files):
    progress = tk.Toplevel(parent)
    progress.title("Operation Progress")
    progress.geometry("400x150")
    progress.transient(parent)
    progress.grab_set()  # Make window modal
    
    progress.label = tk.Label(progress, text="Processing files...")
    progress.label.pack(pady=10)
    
    progress.progressbar = ttk.Progressbar(progress, length=300, mode='determinate')
    progress.progressbar.pack(pady=10)
    
    progress.file_label = tk.Label(progress, text="", wraplength=380)
    progress.file_label.pack(pady=5)
    
    return progress

def update_progress(window, current, total, current_file):
    window.label.config(text=f"Processing files... ({current}/{total})")
    window.progressbar['value'] = (current / total) * 100
    window.file_label.config(text=f"Current file: {os.path.basename(current_file)}")
    window.update()

def copy_file(file_path, destination):
    """
    Copy a file to the specified destination.

    Parameters:
    file_path (str): The path of the file to copy.
    destination (str): The destination directory.
    """
    try:
        base_name = os.path.basename(file_path)
        destination_path = os.path.join(destination, base_name)

        if os.path.exists(destination_path):
            destination_path = handle_existing_file(destination_path)

        shutil.copy(file_path, destination_path)
    except Exception as e:
        print(f"Error copying file {file_path} to {destination}: {e}")

def move_file(file_path, destination):
    """
    Move a file to the specified destination.

    Parameters:
    file_path (str): The path of the file to move.
    destination (str): The destination directory.
    """
    try:
        base_name = os.path.basename(file_path)
        destination_path = os.path.join(destination, base_name)

        if os.path.exists(destination_path):
            destination_path = handle_existing_file(destination_path)

        shutil.move(file_path, destination_path)
    except Exception as e:
        print(f"Error moving file {file_path} to {destination}: {e}")

def handle_existing_file(destination_path):
    """
    Handle a file that already exists in the destination directory by renaming it.

    Parameters:
    destination_path (str): The original destination path.

    Returns:
    str: The new destination path with a unique name.
    """
    creation_time = os.path.getctime(destination_path)
    creation_date = datetime.fromtimestamp(creation_time).strftime('%Y%m%d_%H%M%S')
    base_name, extension = os.path.splitext(os.path.basename(destination_path))
    destination_path = os.path.join(os.path.dirname(destination_path), f"{base_name}_{creation_date}{extension}")

    counter = 1
    while os.path.exists(destination_path):
        destination_path = os.path.join(os.path.dirname(destination_path), f"{base_name}_{creation_date}_{counter}{extension}")
        counter += 1

    return destination_path

def delete_file(file_path):
    """
    Delete the specified file.

    Parameters:
    file_path (str): The path of the file to delete.
    """
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
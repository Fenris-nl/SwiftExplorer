import os
from tkinter import messagebox
from PIL import Image, ImageTk
import logging
import fitz  # PyMuPDF
from typing import Optional, Set
from pathlib import Path

logging.basicConfig(level=logging.ERROR, filename='app_errors.log')

# Define supported file types as frozen sets for immutability
SUPPORTED_TEXT_FILES: Set[str] = frozenset({'.txt', '.py', '.log', '.md', '.json', '.xml', '.csv', '.ini', '.yml', '.yaml', '.html', '.css', '.js'})
SUPPORTED_IMAGE_FILES: Set[str] = frozenset({'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'})
SUPPORTED_PDF_FILES: Set[str] = frozenset({'.pdf'})

def preview_file(app, file_path: str, page_number: int = 0) -> None:
    """
    Preview a file based on its type.
    
    Args:
        app: Application instance
        file_path: Path to the file to preview
        page_number: Page number for PDF files
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file type is not supported
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    extension = path.suffix.lower()
    
    try:
        if extension in SUPPORTED_TEXT_FILES:
            preview_text_file(app, file_path)
        elif extension in SUPPORTED_IMAGE_FILES:
            preview_image_file(app, file_path)
        elif extension in SUPPORTED_PDF_FILES:
            preview_pdf_file(app, file_path, page_number)
        else:
            try:
                preview_text_file(app, file_path)
            except Exception:
                raise ValueError(f"Unsupported file type: {extension}")
    except Exception as e:
        logging.exception(f"Error previewing file {file_path}")
        display_error(app, str(e))

def preview_text_file(app, file_path):
    """
    Preview a text file in the application's text widget.

    Parameters:
    app (object): The application instance containing the text widget.
    file_path (str): The path of the text file to preview.
    """
    app.preview_text.config(state="normal")
    app.preview_text.delete("1.0", "end")
    app.preview_text.pack(fill="both", expand=True)  # Show the text widget
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    app.preview_text.insert("end", content)
    app.preview_text.config(state="disabled")

def preview_image_file(app, file_path):
    """
    Preview an image file in the application's canvas.

    Parameters:
    app (object): The application instance containing the canvas.
    file_path (str): The path of the image file to preview.
    """
    app.preview_text.pack_forget()  # Hide the text widget
    img = Image.open(file_path)
    app.image = img  # Store the original image
    app.canvas.update_idletasks()  # Ensure canvas dimensions are updated
    fit_image_to_canvas(app)
    app.zoom_in_button.config(state="normal")
    app.zoom_out_button.config(state="normal")

def preview_pdf_file(app, file_path, page_number):
    """
    Preview a PDF file in the application's canvas.

    Parameters:
    app (object): The application instance containing the canvas.
    file_path (str): The path of the PDF file to preview.
    page_number (int): The page number to display.
    """
    app.preview_text.pack_forget()  # Hide the text widget
    load_pdf(app, file_path)
    show_pdf_page(app, page_number)
    app.zoom_in_button.config(state="normal")
    app.zoom_out_button.config(state="normal")

def display_error(app, error):
    """
    Display an error message in the application's text widget.

    Parameters:
    app (object): The application instance containing the text widget.
    error (Exception): The error to display.
    """
    app.preview_text.config(state="normal")
    app.preview_text.delete("1.0", "end")
    app.preview_text.insert("end", f"Error displaying file: {error}")
    app.preview_text.pack(fill="both", expand=True)  # Show the text widget
    app.preview_text.config(state="disabled")
    logging.error(f"Error displaying file: {error}")

def fit_image_to_canvas(app):
    """
    Fit the image to the canvas while maintaining aspect ratio.

    Parameters:
    app (object): The application instance containing the canvas and image.
    """
    try:
        if not hasattr(app, 'image'):
            return
            
        img = app.image.copy()
        if hasattr(app, 'rotation'):
            img = img.rotate(app.rotation)
            
        canvas_width = app.canvas.winfo_width()
        canvas_height = app.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            app.canvas.update_idletasks()
            canvas_width = app.canvas.winfo_width()
            canvas_height = app.canvas.winfo_height()
            
        img_width, img_height = img.size
        scale_factor = min(canvas_width / img_width, canvas_height / img_height)
        new_size = (int(img_width * scale_factor), int(img_height * scale_factor))
        
        try:
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        except AttributeError:
            # Fallback for older Pillow versions
            img = img.resize(new_size, Image.LANCZOS)
            
        app.canvas_img = ImageTk.PhotoImage(img)
        app.canvas.delete("all")
        app.canvas.create_image(
            canvas_width // 2, 
            canvas_height // 2,
            anchor="center",
            image=app.canvas_img
        )
        app.canvas.config(scrollregion=app.canvas.bbox("all"))
    except Exception as e:
        logging.error(f"Error fitting image to canvas: {e}")

def update_preview_image(app):
    """
    Update the preview image in the canvas based on the current zoom level.

    Parameters:
    app (object): The application instance containing the canvas and image.
    """
    if hasattr(app, 'image'):
        try:
            img = app.image.copy()
            width, height = img.size
            new_size = int(width * app.zoom_level), int(height * app.zoom_level)
            # Use LANCZOS instead of deprecated ANTIALIAS
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            app.canvas_img = ImageTk.PhotoImage(img)
            app.canvas.create_image(app.canvas.winfo_width()//2, app.canvas.winfo_height()//2, anchor="center", image=app.canvas_img)
            app.canvas.config(scrollregion=app.canvas.bbox("all"))
        except Exception as e:
            logging.error(f"Error updating preview image: {e}")
    elif app.pdf_doc:
        show_pdf_page(app, app.pdf_page_number)

def load_pdf(app, file_path):
    """
    Load a PDF document into the application.

    Parameters:
    app (object): The application instance containing the PDF document.
    file_path (str): The path of the PDF file to load.
    """
    app.pdf_doc = fitz.open(file_path)
    app.pdf_page_number = 0
    app.zoom_level = 1.0
    update_pdf_navigation_buttons(app)

def show_pdf_page(app, page_number):
    """
    Display a specific page of the loaded PDF document in the canvas.

    Parameters:
    app (object): The application instance containing the canvas and PDF document.
    page_number (int): The page number to display.
    """
    if app.pdf_doc:
        page = app.pdf_doc.load_page(page_number)
        zoom_matrix = fitz.Matrix(app.zoom_level, app.zoom_level)
        pix = page.get_pixmap(matrix=zoom_matrix)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        app.canvas.config(scrollregion=app.canvas.bbox("all"))
        display_image_on_canvas(app, img)

        update_pdf_navigation_buttons(app)

def display_image_on_canvas(app, img):
    """
    Display an image on the application's canvas.

    Parameters:
    app (object): The application instance containing the canvas.
    img (PIL.Image): The image to display.
    """
    app.canvas_img = ImageTk.PhotoImage(img)
    app.canvas.create_image(app.canvas.winfo_width()//2, app.canvas.winfo_height()//2, anchor="center", image=app.canvas_img)
    app.canvas.config(scrollregion=app.canvas.bbox("all"))

def update_pdf_navigation_buttons(app):
    """
    Update the state of the PDF navigation buttons based on the current page and zoom level.

    Parameters:
    app (object): The application instance containing the navigation buttons and PDF document.
    """
    if app.pdf_doc:
        app.prev_page_button.config(state="normal" if app.pdf_page_number > 0 else "disabled")
        app.next_page_button.config(state="normal" if app.pdf_page_number < len(app.pdf_doc) - 1 else "disabled")
        app.zoom_in_button.config(state="normal")
        app.zoom_out_button.config(state="normal")
    else:
        app.prev_page_button.config(state="disabled")
        app.next_page_button.config(state="disabled")
        app.zoom_in_button.config(state="disabled")
        app.zoom_out_button.config(state="disabled")

import logging
from datetime import datetime

logging.basicConfig(level=logging.ERROR, filename='app_errors.log')

def update_progress(app, current, total):
    """
    Update the progress bar in the application.

    Parameters:
    app (object): The application instance containing the progress bar.
    current (int): The current progress value.
    total (int): The total value representing 100% progress.
    """
    try:
        progress = int((current / total) * 100)
        app.progress_bar['value'] = progress
        app.root.update_idletasks()
    except ZeroDivisionError:
        app.progress_bar['value'] = 0
        app.root.update_idletasks()
    except Exception as e:
        logging.error(f"Error updating progress: {e}")
        update_status(app, f"Error updating progress: {e}")

def update_status(app, status):
    """
    Update the status label in the application.

    Parameters:
    app (object): The application instance containing the status label.
    status (str): The status message to display.
    """
    try:
        app.status_label.config(text=status)
    except Exception as e:
        logging.error(f"Error updating status: {e}")
        print(f"Error updating status: {e}")

def format_size(size):
    """
    Format the file size into a human-readable format (e.g., KB, MB, GB).

    Parameters:
    size (int): The file size in bytes.

    Returns:
    str: The formatted file size.
    """
    try:
        if size < 0:
            return "Invalid size"
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
    except Exception as e:
        logging.error(f"Error formatting size: {e}")
        return f"Error formatting size: {e}"

# Example usage:
# print(format_size(1024)) # Outputs: "1.00 KB"
# print(format_size(1048576)) # Outputs: "1.00 MB"

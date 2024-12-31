# SwiftExplorer

SwiftExplorer is a professional file browser application built with Python and Tkinter. It provides advanced file searching, previewing, and file operations with a user-friendly interface. The application supports dark mode, various file types, and includes features like search history, text cleaning, and more.

## Features

- **Advanced File Search**: Search for files based on name, extension, size, date, and content.
- **File Preview**: Preview text, image, and PDF files within the application.
- **File Operations**: Perform copy, move, and delete operations on selected files.
- **Dark Mode**: Toggle between dark and light themes.
- **Search History**: Maintain a history of recent searches for quick access.
- **Text Cleaning**: Remove duplicate lines and empty lines from the search input.
- **Progress and Status Updates**: Real-time progress and status updates during operations.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/SwiftExplorer.git
    cd SwiftExplorer
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the application:
    ```bash
    python main.py
    ```

## Usage

### Main Interface

- **Directory Selection**: Browse and select the directory to search.
- **Filename Input**: Enter filenames to search, one per line.
- **Options**: Configure search options like exact match, case sensitivity, file extensions, and more.
- **Search Button**: Start the search operation.
- **Results**: View search results in a treeview with details like filename, path, size, and date modified.
- **Preview**: Preview selected files in the preview pane.
- **File Operations**: Perform copy, move, and delete operations on selected files.

### Settings

- **Theme Selection**: Choose between available themes.
- **Default Directory**: Set a default directory for searches.

### Help

- **Help Dialog**: Access help information.
- **About Dialog**: View information about the application.

## Keyboard Shortcuts

- **Ctrl+F**: Focus on the filename input field.
- **Ctrl+O**: Open the directory browser.
- **Ctrl+V**: Paste from clipboard.
- **F5**: Start the search operation.
- **Ctrl+A**: Select all search results.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Tkinter](https://docs.python.org/3/library/tkinter.html) - Python's standard GUI toolkit.
- [ttkbootstrap](https://ttkbootstrap.readthedocs.io/en/latest/) - A modern theme for Tkinter.
- [Pillow](https://python-pillow.org/) - Python Imaging Library (PIL) fork.
- [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/) - Python bindings for MuPDF.

## Contact

For any inquiries or support, please contact [yourname@example.com](mailto:yourname@example.com).
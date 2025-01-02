# 🚀 SwiftExplorer

A professional-grade file management application built with Python, featuring advanced search capabilities, file preview support, and a modern dark/light theme interface.

## ✨ Key Features

### 🔍 Search Capabilities
- **Smart Search**: Find files by name, content, or pattern matching
- **Advanced Filters**: 
  - 📁 Extension-specific searching
  - 🔤 Case sensitivity options
- **📜 Search History**: Quick access to previous searches
- **⚡ Real-time Results**: Dynamic updates during search operations

### 👁️ File Preview
- **📦 Enhanced Multi-format Support**:
  - 📝 Text files with syntax highlighting: Python, Java, C++, SQL, and more
  - 🖼️ Extended image formats: PNG, JPG, HEIC, RAW, PSD, SVG
  - 📄 Documents: PDF, Office formats (doc, xls, ppt)
- **🎨 Image Enhancement Features**:
  - 🔆 Brightness and contrast controls
  - 🎨 Filters: Grayscale, Sepia, Blur, Sharpen
  - 🔄 Rotation and flip options
  - 🔍 Advanced zoom with mouse wheel support

### 🎯 Advanced Search
- **🔍 Smart Filtering**:
  - 🏷️ File type categories
  - 🔠 Regex pattern matching
- **📊 Results View**:
  - 📋 Customizable columns
  - 🔄 Sort by any attribute
  - 🎨 Color coding by file type
  - 📥 Export results to CSV/Excel

### 🛠️ File Operations
- **⚡ Batch Processing**: Perform operations on multiple files
- **📂 File Management**:
  - 📋 Copy with conflict resolution
  - 🚀 Move with automatic renaming
  - 🗑️ Secure delete
- **📊 Progress Tracking**: Real-time operation progress indicators

### 💫 User Interface
- **🎨 Theme Support**:
  - 🌙 Dark mode (Cyborg theme)
  - ☀️ Light mode (Flatly theme)
  - 💾 Persistent theme preferences
- **✨ Modern UI Elements**:
  - 📱 Responsive layout
  - 🎯 Custom styling
  - 📈 Progress indicators
  - 📢 Status updates

## ⚙️ Installation

### 📋 Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
```bash
# Clone the repository
git clone https://github.com/Fenris-nl/SwiftExplorer.git
cd SwiftExplorer

# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Dependencies
- tkinter: GUI framework
- ttkbootstrap: Modern theming
- Pillow: Image processing
- PyMuPDF: PDF handling
- pyperclip: Clipboard operations

## Usage Guide

### Search Operations
1. **Basic Search**:
   - Enter directory path or browse
   - Input search terms (one per line)
   - Click "Search" or press F5

2. **Advanced Search**:
   - Toggle "Exact Match" for precise results
   - Enable "Case Sensitive" for specific matches
   - Select file extensions to filter results

3. **Search Results**:
   - Double-click to open files
   - Select multiple files for batch operations
   - Sort by name, size, or date
   - Preview selected files

### ⌨️ Keyboard Shortcuts
| Shortcut | Action |
|----------|---------|
| `Ctrl+F` | 🔍 Focus search input |
| `Ctrl+O` | 📁 Open directory browser |
| `Ctrl+V` | 📋 Paste from clipboard |
| `F5` | 🚀 Start search |
| `Ctrl+A` | ✨ Select all results |

## ⚙️ Configuration

### 🔧 Settings
- 🎨 Theme selection
- 📁 Default directory
- 📜 Search history size
- 👁️ Preview preferences

### File Associations
The application supports various file types with custom preview handlers:
```python
SUPPORTED_TEXT_FILES = {'.txt', '.py', '.log', '.md', '.json', '.xml', '.csv', '.ini', '.yml', '.yaml', '.html', '.css', '.js'}
SUPPORTED_IMAGE_FILES = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
SUPPORTED_PDF_FILES = {'.pdf'}
```

## 🤝 Contributing

### 🛠️ Development Setup
1. Fork the repository
2. Create a feature branch
3. Set up development environment
4. Make changes following the code style
5. Submit pull request

### 📝 Code Style
- ✨ Type hints for function parameters
- 🛡️ Comprehensive error handling
- 📝 Logging for debugging
- 📚 Clear documentation

## 💬 Support

For bug reports and feature requests, please use the GitHub issues system. For direct support:
- 📧 Email: [kaanerdem3@gmail.com](mailto:kaanerdem3@gmail.com)
- 🐛 GitHub Issues: [Project Issues](https://github.com/Fenris-nl/SwiftExplorer/issues)

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
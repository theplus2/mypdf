# AGENTS.md - MyPDF Library Development Guide

## Overview
MyPDF Library is a PyQt6-based PDF library management application with built-in PDF viewer. It organizes PDFs into categories, provides reading progress tracking, and includes features like thumbnails, favorites, and dark mode reading.

## Build Commands

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Building Executable
```bash
# Windows build
powershell -ExecutionPolicy Bypass -File build_windows.ps1

# Manual PyInstaller build (Windows)
python -m PyInstaller MyPDFLibrary.spec --clean --noconfirm

# Manual PyInstaller build (macOS) 
python -m PyInstaller MyPDFLibrary_Mac.spec --clean --noconfirm
```

### Testing
No formal test framework is currently configured. Testing is done manually by running the application and verifying functionality.

### Linting/Code Quality
No linting tools are currently configured. Consider adding:
- flake8 for Python style checking
- black for code formatting
- mypy for type checking

## Code Style Guidelines

### File Organization
- `main.py` - Entry point and UI components (LibraryWidget, ReaderWidget, MainApp)
- `library_manager.py` - Data persistence and book management logic
- `pdf_engine.py` - PDF rendering and thumbnail generation using PyMuPDF
- `config.py` - Cross-platform data directory management and migration

### Import Style
Follow standard Python import organization:
1. Standard library imports
2. Third-party imports (PyQt6, fitz/Pillow)
3. Local application imports

```python
import sys
import os
import json
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QSize

import fitz  # PyMuPDF
from pdf_engine import PDFEngine
from library_manager import LibraryManager
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `LibraryWidget`, `PDFEngine`)
- **Functions/Methods**: snake_case (e.g., `load_data()`, `get_page_image()`)
- **Variables**: snake_case (e.g., `current_page`, `data_dir`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DARK_THEME`)
- **Private methods**: prefix with underscore (e.g., `_internal_method()`)

### UI Components Structure
- Use descriptive Korean labels for user-facing text
- Separate layout creation from widget initialization
- Group related UI setup into logical methods (`init_ui()`)
- Use object names for styling important buttons (`setObjectName("action_btn")`)

### Error Handling
- Use try-except blocks for file operations and PDF processing
- Show user-friendly QMessageBox for expected errors
- Log detailed errors to console for debugging
- Gracefully handle missing files and corrupted PDFs

```python
try:
    # File operation
    with open(self.filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    # Handle gracefully
    pass
except Exception as e:
    print(f"Unexpected error: {e}")
    QMessageBox.critical(self, "오류", f"작업 중 오류가 발생했습니다: {str(e)}")
```

### Data Management
- All data stored in JSON format with UTF-8 encoding
- Use `load_data()` before modifications to ensure latest data
- Call `save_data()` immediately after any changes
- Store data in OS-appropriate directories via `config.get_data_directory()`

### PDF Processing Guidelines
- Always close PDF documents when done (`doc.close()`)
- Handle PyMuPDF operations in try-except blocks
- Generate thumbnails only if they don't already exist
- Use appropriate zoom factors for different rendering needs

### Performance Considerations
- Use `setUpdatesEnabled(False)` during bulk UI updates
- Implement search debouncing (300ms delay for search bar)
- Cache thumbnails to avoid regeneration
- Use progress dialogs for batch operations

### Code Comments
- Use Korean comments for business logic explanation
- Include TODO/FIX comments for temporary solutions
- Document complex algorithms or workarounds
- Keep comments concise and relevant

### Qt/PyQt6 Best Practices
- Use `setFocusPolicy(Qt.FocusPolicy.NoFocus)` for non-interactive buttons
- Implement proper signal-slot connections
- Use appropriate layout managers (QHBoxLayout, QVBoxLayout)
- Handle window resizing and events properly
- Use `QApplication.processEvents()` during long operations

### Cross-Platform Considerations
- Use `config.py` functions for OS-specific paths
- Test on Windows and macOS (primary targets)
- Handle file path separators with `os.path.join()`
- Consider PyInstaller packaging requirements

### Internationalization
- Primary UI language: Korean
- Use UTF-8 encoding for all text files
- Consider future i18n support for English

## Development Workflow

### Adding New Features
1. Identify the appropriate file (main.py for UI, library_manager.py for data)
2. Follow existing code patterns and naming conventions
3. Add Korean UI text appropriate for user understanding
4. Test with various PDF files and edge cases
5. Update data schema if needed (handle backward compatibility)

### Modifying PDF Engine
- PyMuPDF (fitz) is the core library for PDF operations
- Handle memory carefully - always close documents
- Test with different PDF versions and formats
- Consider performance impact of rendering operations

### UI Modifications
- Follow the dark theme styling established in `DARK_THEME`
- Maintain consistent spacing and widget sizing
- Use appropriate Korean labels and descriptions
- Test window resizing and responsiveness

## Important Notes

- This is a desktop application targeting Korean-speaking users
- Data migration logic handles transition from older versions
- No formal testing framework - manual testing required
- Application supports both Windows and macOS via PyInstaller
- PDF files are not copied - only references and thumbnails are stored
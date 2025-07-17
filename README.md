# DocGenius - Document Creator Toolkit 📄

A powerful, modular toolkit for converting data sources (CSV, JSON, APIs) into beautifully formatted documents (Markdown, PDF, Word).

## 🚀 Quick Start

### Installation
```bash
# Install dependencies
python tools/install_deps.py

# Or run full setup
python tools/setup.py
```

### Basic Usage
```bash
# Launch the interactive menu
python app.py

# Or use the document creator directly
python document_creator.py --input data.csv --output report.md --format markdown
```

## 🏗️ Architecture

DocGenius uses a clean, modular architecture:

```
📁 Project Structure
├── 📄 app.py                    # Main launcher with menu system
├── 📄 document_creator.py       # Core document creation functionality  
├── 📄 dev_tools.py             # Developer tools interface
├── 📄 system_tools.py          # System management tools
├── 📄 compat.py                # Backward compatibility layer
├── 📁 logic/                   # Core business logic
│   ├── 📁 models/              # Data structures and validation
│   ├── 📁 data_sources/        # Input loading (CSV, JSON, APIs)
│   ├── 📁 exporters/           # Document generation (MD, PDF, Word)
│   └── 📁 utilities/           # Supporting functions
├── 📁 assets/                  # Static assets and examples
│   └── 📁 examples/            # Usage examples and demos
├── 📁 tools/                   # Development and build tools
├── 📁 tests/                   # Test suite
└── 📁 .dev/                   # Development files and logs
```

## 🎯 Features

### Data Sources
- **CSV Files**: Advanced parsing with custom delimiters, encoding detection
- **JSON Files**: Nested object support with flattening options
- **APIs**: RESTful API integration with authentication
- **Validation**: Comprehensive data validation and error handling

### Export Formats
- **Markdown**: YAML front matter, custom templates, table formatting
- **PDF**: Professional formatting, headers/footers, custom styling
- **Word**: Template support, styling, metadata integration

### Utilities
- **File Operations**: Backup management, temporary files, path validation
- **GUI Dialogs**: File selection, progress tracking, user interaction
- **Validation**: Data integrity, business logic, file format validation
- **Configuration**: Environment management, settings persistence
- **Logging**: Session tracking, performance monitoring, error reporting
- **System Tools**: Dependency checking, environment detection

## 📋 Usage Examples

### Command Line Interface
```bash
# Interactive mode
python app.py

# Direct export
python document_creator.py --input employees.csv --output report.md --format markdown

# With template
python document_creator.py --input data.json --output document.pdf --format pdf --template custom.template
```

### Python API
```python
from logic.data_sources import CSVLoader
from logic.exporters import MarkdownExporter
from logic.models import DataObject, DocumentConfig

# Load data
loader = CSVLoader()
result = loader.load('employees.csv')

# Export to markdown
exporter = MarkdownExporter()
data_obj = DataObject(result.data)
config = DocumentConfig(output_path='employees.md')

export_result = exporter.export(data_obj, config)
```

## 🛠️ Development Tools

Located in the `tools/` directory:

- **`install_deps.py`**: Quick dependency installation
- **`setup.py`**: Complete development environment setup
- **`run_tests.py`**: Comprehensive test runner
- **`build_exe.py`**: Standalone executable builder

## 🧪 Testing

```bash
# Run all tests
python tools/run_tests.py

# Run specific test module
python -m pytest tests/test_markdown_export.py

# Run with coverage
python tools/run_tests.py --coverage
```

## 📦 Building Executable

```bash
# Build standalone EXE
python tools/build_exe.py

# The executable will be created in dist/DocGenius.exe
```

## 🔧 Configuration

DocGenius supports various configuration options:

- **Environment files**: `.env` support for settings
- **Configuration files**: JSON/YAML configuration files  
- **Command line options**: Override any setting via CLI
- **Interactive setup**: Guided configuration through menus

## 📚 Examples

Check the `assets/examples/` directory for:
- **`demo_toolkit.py`**: Comprehensive feature demonstration
- Sample data files and templates
- Usage patterns and best practices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python tools/run_tests.py`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- Check the examples in `assets/examples/`
- Review the development logs in `.dev/logs/`
- Run the dependency checker: `python tools/install_deps.py`
- Use the interactive help: `python app.py` and select help options

---

**DocGenius** - Transforming data into documents with elegance and efficiency. 🎨✨

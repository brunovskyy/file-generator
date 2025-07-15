# Document Creator Toolkit

A modular Python toolkit for converting data sources (CSV, JSON, APIs) into various document formats (Markdown, PDF, Word). Supports both interactive and argument-based CLI usage with advanced features like YAML front matter key selection for Markdown exports.

## Features

✅ **Multi-format Data Loading**: CSV, JSON, and API endpoints  
✅ **Multiple Export Formats**: Markdown, PDF, Word documents  
✅ **Interactive CLI**: User-friendly prompts and file selection  
✅ **Argument-based CLI**: Scriptable command-line interface  
✅ **YAML Front Matter**: Interactive key selection for Markdown exports  
✅ **Template Support**: Word/PDF generation from templates  
✅ **Modular Design**: Clean, extensible architecture  
✅ **Error Handling**: Comprehensive error reporting and validation  
✅ **Downloads Folder Default**: Automatically saves to user's Downloads folder  
✅ **Folder Selection Dialog**: GUI folder picker for output directory  

## Quick Start

### Installation

```bash
# Clone or download the project
cd "PY Document Creator"

# Install dependencies
pip install -r requirements.txt
```

### Interactive Mode

```bash
python main_cli.py
```

The interactive mode will guide you through:
1. **Data Source Selection**: Choose file, URL, or API endpoint
2. **Export Format Selection**: Select from Markdown, PDF, Word
3. **Output Configuration**: Set output directory and options with GUI folder picker
4. **YAML Key Selection**: Interactive tree view for Markdown front matter (if enabled)

**Default Output**: Files are saved to your Downloads folder in timestamped subdirectories.

### Command Line Mode

```bash
# Basic usage
python main_cli.py --source data.json --export-types markdown pdf

# Advanced usage with all options
python main_cli.py \
  --source https://api.example.com/data \
  --export-types markdown word \
  --output-dir ./exports \
  --yaml-front-matter \
  --yaml-key-selection select \
  --filename-key name \
  --verbose
```

## Project Structure

```
PY Document Creator/
├── json_to_file/                 # Core toolkit modules
│   ├── __init__.py              # Package initialization
│   ├── source_to_json.py        # Data loading and normalization
│   ├── markdown_export.py       # Markdown export with YAML front matter
│   ├── pdf_export.py           # PDF export (direct and template-based)
│   ├── word_export.py          # Word export (direct and template-based)
│   └── utils.py                 # Shared utility functions
├── main_cli.py                  # Unified CLI entry point
├── tests/                       # Comprehensive test suite
├── requirements.txt             # Project dependencies
├── README.md                    # This file
└── output/                      # Default output directory (legacy)
```

**Note**: The default output directory is now `~/Downloads/` for better user experience.

## Usage Examples

### Data Sources

**Local Files:**
```bash
python main_cli.py --source data.csv --export-types markdown
python main_cli.py --source data.json --export-types pdf word
```

**URLs:**
```bash
python main_cli.py --source https://example.com/data.json --export-types markdown
```

**APIs:**
```bash
python main_cli.py --source https://api.example.com/users --export-types markdown pdf
```

### Export Formats

**Markdown with YAML Front Matter:**
```bash
python main_cli.py --source data.json --export-types markdown --yaml-front-matter --yaml-key-selection select
```

**PDF (requires reportlab):**
```bash
python main_cli.py --source data.csv --export-types pdf
```

**Word Documents (requires python-docx):**
```bash
python main_cli.py --source data.json --export-types word
```

**Multiple Formats:**
```bash
python main_cli.py --source data.json --export-types markdown pdf word
```

## Advanced Features

### YAML Front Matter Key Selection

For Markdown exports, the toolkit provides an interactive tree view to select which keys should be included in the YAML front matter:

```
==================================================
YAML FRONT MATTER KEY SELECTION
==================================================

Available keys in your data:
 1. name                           (e.g., John Doe)
 2. email                          (e.g., john@example.com)
 3. profile.age                    (e.g., 30)
 4. profile.location               (e.g., New York)
 5. skills                         (e.g., ['Python', 'JavaScript'])

Selection options:
  - Enter numbers separated by spaces (e.g., 1 3 5)
  - Enter 'all' to select all keys
  - Enter 'none' to skip YAML front matter

Enter your selection: 1 2 3
```

### Template-Based Exports

The toolkit supports template-based document generation for Word and PDF formats:

```python
from json_to_file.word_export import export_to_word

# Using a template URL
export_to_word(
    data_list,
    output_directory="./output",
    template_url="https://example.com/template.docx",
    use_template=True
)
```

### API Integration

Load data from APIs with custom headers and parameters:

```python
from json_to_file.source_to_json import load_normalized_data

data = load_normalized_data(
    source_path_or_url="https://api.example.com/data",
    file_format="api",
    api_method="GET",
    api_headers={"Authorization": "Bearer token"},
    api_query={"limit": 100}
)
```

## Dependencies

### Core Dependencies
- `requests`: HTTP requests for APIs and URLs
- `pathlib`: Modern path handling (built-in)
- `json`, `csv`: Data format support (built-in)

### Optional Dependencies
- `PyYAML`: Enhanced YAML front matter support
- `reportlab`: Direct PDF generation
- `python-docx`: Word document creation
- `docxtpl`: Advanced Word templating
- `docx2pdf`: Word to PDF conversion

Install all dependencies:
```bash
pip install -r requirements.txt
```

Or install selectively:
```bash
# For basic functionality
pip install requests

# For Markdown with YAML
pip install PyYAML

# For PDF export
pip install reportlab

# For Word export
pip install python-docx docxtpl docx2pdf
```

## API Reference

### Data Loading

```python
from json_to_file.source_to_json import load_normalized_data

# Load from any source
data = load_normalized_data(
    source_path_or_url="data.json",
    file_format="json",  # auto-detected if None
    encoding="utf-8",
    api_method="GET",
    api_headers={"Authorization": "Bearer token"},
    api_query={"limit": 100}
)
```

### Markdown Export

```python
from json_to_file.markdown_export import export_to_markdown

files = export_to_markdown(
    data_list=data,
    output_directory="./output",
    filename_key="name",
    include_yaml_front_matter=True,
    selected_yaml_keys={"name", "email", "profile.age"},
    flatten_yaml_values=True
)
```

### PDF Export

```python
from json_to_file.pdf_export import export_to_pdf

files = export_to_pdf(
    data_list=data,
    output_directory="./output",
    filename_key="name",
    template_url="https://example.com/template.docx",
    use_template=True
)
```

### Word Export

```python
from json_to_file.word_export import export_to_word

files = export_to_word(
    data_list=data,
    output_directory="./output",
    filename_key="name",
    template_path="./template.docx",
    use_template=True
)
```

## Error Handling

The toolkit provides comprehensive error handling with custom exceptions:

```python
from json_to_file import (
    DataSourceError,
    MarkdownExportError,
    PDFExportError,
    WordExportError
)

try:
    data = load_normalized_data("invalid_source.json")
except DataSourceError as e:
    print(f"Data loading failed: {e}")

try:
    export_to_pdf(data, "./output")
except PDFExportError as e:
    print(f"PDF export failed: {e}")
```

## Extending the Toolkit

### Adding New Data Sources

1. Extend `source_to_json.py` with new format detection
2. Add loading logic for the new format
3. Update the CLI to support the new source type

### Adding New Export Formats

1. Create a new module in `json_to_file/` (e.g., `excel_export.py`)
2. Implement the export function following the existing pattern
3. Add the new format to the CLI choices
4. Update the main CLI to handle the new format

### Example: Adding Excel Export

```python
# json_to_file/excel_export.py
def export_to_excel(data_list, output_directory, **kwargs):
    """Export data to Excel format."""
    # Implementation here
    pass
```

Then update `main_cli.py` to include 'excel' in the export choices.

## Contributing

1. Follow the existing code structure and patterns
2. Add comprehensive docstrings to all functions
3. Include error handling with custom exceptions
4. Update this README with new features
5. Test with various data sources and formats

## License

This project is provided as-is for educational and development purposes.

---

**Need help?** Check the docstrings in each module or run `python main_cli.py --help` for usage information.

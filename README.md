# DocGenius - Document Creator Toolkit 📄

A powerful, easy-to-use toolkit that transforms your data (CSV files, JSON data, APIs) into professional documents (Markdown, PDF, Word) with just a few clicks.

**Author**: https://github.com/brunovskyy/

## 🚀 Quick Start

### For End Users (Recommended)
1. Download the latest release from [GitHub Releases](https://github.com/brunovskyy/file-generator/releases)
2. Extract and run `DocGenius.exe`
3. Follow the interactive menu to convert your files

### For Developers
```bash
# Install dependencies
python tools/deps_installer_tool.py

# Or run full setup
python tools/setup_installer_tool.py
```

### Basic Usage
```bash
# Launch the interactive menu
python app_launcher_cli.py

# Or use the document creator directly
python -m docgenius.core.document_creator --input data.csv --output report.md --format markdown
```

## 📖 How to Use DocGenius

### Step-by-Step Guide

#### 1. Converting a CSV File to Markdown Report
**What you need**: A CSV file with your data (e.g., employee list, sales data, inventory)

**Steps**:
1. Run DocGenius (either the `.exe` or `python app_launcher_cli.py`)
2. Select "Create Document from Data"
3. Choose your CSV file
4. Select "Markdown" as output format
5. Choose where to save your report

**Example Input** (`employees.csv`):
```csv
Name,Department,Salary,Start_Date
John Smith,Engineering,75000,2023-01-15
Jane Doe,Marketing,65000,2023-02-20
Mike Johnson,Sales,55000,2023-03-10
```

**Expected Output** (`employee_report.md`):
```markdown
# Data Report

## Summary
- Total Records: 3
- Generated: 2025-07-17

## Employee Data

| Name | Department | Salary | Start Date |
|------|------------|--------|------------|
| John Smith | Engineering | $75,000 | 2023-01-15 |
| Jane Doe | Marketing | $65,000 | 2023-02-20 |
| Mike Johnson | Sales | $55,000 | 2023-03-10 |

## Export Statistics
- Unique Data Fields: 4
- Successfully Processed: 3 records
- Export Format: Markdown
```

#### 2. Converting JSON Data to PDF Report
**What you need**: A JSON file with structured data

**Steps**:
1. Launch DocGenius
2. Select "Create Document from Data"
3. Choose your JSON file
4. Select "PDF" as output format
5. Optionally customize the template

**Example Input** (`sales_data.json`):
```json
{
  "quarter": "Q1 2025",
  "sales": [
    {"product": "Widget A", "revenue": 15000, "units": 150},
    {"product": "Widget B", "revenue": 22000, "units": 110}
  ],
  "total_revenue": 37000
}
```

**Expected Output**: A professional PDF report with:
- Header with quarter information
- Formatted tables showing sales data
- Export metadata and processing information
- Professional styling and document structure

#### 3. Batch Processing Multiple Files
**What you need**: Multiple CSV/JSON files in a folder

**Steps**:
1. Launch DocGenius
2. Select "Batch Process Files"
3. Choose your input folder
4. Select output format (Markdown, PDF, or Word)
5. Choose output directory
6. Let DocGenius process all files automatically

**Use Cases**:
- Monthly sales reports → Professional PDF document formatting
- Employee data → Formatted team directories
- Inventory lists → Searchable markdown catalogs
- Survey results → Structured data reports

### Common File Types Supported

**Input Formats**:
- `.csv` - Comma-separated values
- `.json` - JavaScript Object Notation
- `.xlsx` - Excel spreadsheets (coming soon)
- REST APIs (with authentication)

**Output Formats**:
- `.md` - Markdown (great for documentation, GitHub)
- `.pdf` - PDF (professional reports, printing)
- `.docx` - Word documents (editable reports)

---

## 🏗️ Technical Documentation & Architecture

*This section is intended for developers, contributors, and users who want to understand the technical details.*

### Project Architecture

DocGenius uses a clean, modular architecture with clear separation of concerns:

```
📁 Project Structure
├── 📄 app_launcher_cli.py        # Main application launcher
├── 📁 docgenius/                 # Core package
│   ├── 📁 cli/                   # Command-line interfaces
│   │   ├── dev_tools.py          # Developer tools
│   │   └── system_tools.py       # System management
│   ├── � core/                  # Core functionality
│   │   └── document_creator.py   # Main document creation engine
│   ├── 📁 logic/                 # Business logic modules
│   │   ├── � data_sources/      # Input handlers (CSV, JSON, API)
│   │   ├── 📁 exporters/         # Output generators (MD, PDF, Word)
│   │   ├── � models/            # Data structures and validation
│   │   └── 📁 utilities/         # Supporting functions
│   └── � compat/                # Backward compatibility
├── 📁 tools/                     # Development and build tools
├── 📁 tests/                     # Comprehensive test suite
├── 📁 assets/                    # Examples and static resources
└── 📁 build/                     # Build artifacts and executables
```

### Advanced Usage & API

#### Command Line Interface
```bash
# Interactive mode with full menu
python app_launcher_cli.py

# Direct document creation
python -m docgenius.core.document_creator \
    --input employees.csv \
    --output report.md \
    --format markdown \
    --template custom_template.yaml

# Batch processing
python -m docgenius.cli.system_tools \
    --batch-process \
    --input-dir ./data/ \
    --output-dir ./reports/ \
    --format pdf

# Developer tools
python -m docgenius.cli.dev_tools --run-tests --coverage
```

#### Python API Examples
```python
from docgenius.logic.data_sources import CSVDataLoader, JSONDataLoader
from docgenius.logic.exporters import MarkdownExporter, PDFExporter
from docgenius.logic.models import DataObject, DocumentConfig
from docgenius.logic.utilities import FileHelper, ValidationHelper

# Advanced CSV processing with custom configuration
loader = CSVDataLoader()
config = {
    'delimiter': ';',
    'encoding': 'utf-8',
    'skip_rows': 2,
    'custom_headers': ['ID', 'Name', 'Department', 'Salary']
}
result = loader.load('complex_data.csv', config)

# Data validation and transformation
validator = ValidationHelper()
if validator.validate_data_structure(result.data):
    # Transform data before export
    transformed_data = validator.transform_data(result.data)
    
    # Create data object with metadata
    data_obj = DataObject(
        data=transformed_data,
        metadata={
            'source_file': 'complex_data.csv',
            'processing_date': '2025-07-17',
            'total_records': len(transformed_data)
        }
    )
    
    # Advanced export configuration
    export_config = DocumentConfig(
        output_path='advanced_report.pdf',
        template_path='templates/corporate_template.yaml',
        styling={
            'font_family': 'Arial',
            'primary_color': '#2E86AB',
            'include_charts': True,
            'page_orientation': 'landscape'
        }
    )
    
    # Export with error handling
    exporter = PDFExporter()
    try:
        export_result = exporter.export(data_obj, export_config)
        print(f"Export successful: {export_result.output_path}")
    except Exception as e:
        print(f"Export failed: {e}")
```

### Development Tools & Testing

#### Available Development Tools
Located in the `tools/` directory:

```bash
# Dependency management
python tools/deps_installer_tool.py          # Install required packages
python tools/setup_installer_tool.py        # Complete dev environment setup

# Testing and quality assurance
python tools/test_runner_tool.py            # Run comprehensive test suite
python tools/test_runner_tool.py --coverage # Run tests with coverage report
python tools/test_runner_tool.py --integration # Run integration tests only

# Build and distribution
python tools/build_exe_tool.py             # Create standalone executable
python tools/rename_files_with_imports.py  # Refactor imports (development)
```

#### Testing Framework
```bash
# Run all tests with verbose output
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_integration_e2e.py     # End-to-end tests
python -m pytest tests/test_export_markdown.py     # Markdown export tests
python -m pytest tests/test_data_source_json.py    # JSON handling tests

# Run with coverage and HTML report
python -m pytest tests/ --cov=docgenius --cov-report=html

# Performance testing
python tests/test_runner_organized.py --performance
```

#### Building Executable
```bash
# Build standalone executable
python tools/build_exe_tool.py

# The executable will be created in:
# - dist/DocGenius.exe (Windows)
# - dist/DocGenius (Linux/macOS)

# Advanced build options
python tools/build_exe_tool.py --debug          # Debug build with console
python tools/build_exe_tool.py --onefile        # Single file executable
python tools/build_exe_tool.py --windowed       # GUI-only (no console)
```

## ✨ What DocGenius Can Do for You

### 📊 Input Sources
- **CSV Files**: Excel exports, database dumps, survey data
- **JSON Data**: API responses, configuration files, structured data
- **API Integration**: Connect directly to REST APIs (coming soon)

### 📄 Output Formats
- **Markdown**: Perfect for documentation, GitHub, technical writing
- **PDF**: Professional reports, presentations, printable documents
- **Word Documents**: Editable reports, collaborative documents

### 🎯 Perfect For
- **Business Reports**: Transform sales data into formatted business documents
- **Data Documentation**: Convert datasets into readable documentation
- **Team Updates**: Create formatted reports from project data
- **Academic Work**: Convert research data into formatted papers
- **Personal Projects**: Transform hobby data into shareable formats

---

### 🔧 Technical Features

*For developers and advanced users*

#### Data Processing Capabilities
- **Advanced CSV Parsing**: Custom delimiters, encoding detection, header mapping
- **JSON Processing**: Nested object flattening, array handling, schema validation
- **Data Validation**: Type checking, required field validation, business rule enforcement
- **Error Handling**: Graceful failure recovery, detailed error reporting

#### Export Engine Features
- **Markdown Engine**: YAML front matter, custom templates, table formatting, TOC generation
- **PDF Generator**: Professional styling, headers/footers, page numbering, custom fonts
- **Word Integration**: Template support, style inheritance, metadata embedding

#### System Utilities
- **File Management**: Automatic backups, temporary file handling, path validation
- **User Interface**: GUI dialogs, progress tracking, interactive menus
- **Configuration**: Environment management, settings persistence, profile support
- **Monitoring**: Session logging, performance metrics, error tracking
- **Development Tools**: Dependency checking, environment detection, build automation



### Configuration & Customization

#### Environment Configuration
```bash
# Create .env file for custom settings
echo "DEFAULT_OUTPUT_FORMAT=pdf" > .env
echo "TEMP_DIR=/custom/temp/path" >> .env
echo "LOG_LEVEL=DEBUG" >> .env
```

#### Custom Templates
```yaml
# custom_template.yaml
document:
  title: "{{metadata.title}}"
  author: "{{metadata.author}}"
  date: "{{current_date}}"
  
styling:
  primary_color: "#2E86AB"
  font_family: "Arial"
  page_size: "A4"
  
sections:
  - type: "header"
    content: "{{document.title}}"
  - type: "data_table"
    source: "main_data"
    columns: ["Name", "Department", "Salary"]
  - type: "summary"
    statistics: true
```

#### Command Line Configuration
```bash
# Override any setting via CLI
python -m docgenius.core.document_creator \
    --config-file ./custom_config.yaml \
    --output-format pdf \
    --template ./templates/corporate.yaml \
    --log-level DEBUG \
    --temp-dir ./temp/
```

### Integration Examples

#### CI/CD Pipeline Integration
```yaml
# .github/workflows/generate-reports.yml
name: Generate Reports
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install DocGenius
        run: |
          pip install -r requirements.txt
          
      - name: Generate Weekly Report
        run: |
          python -m docgenius.core.document_creator \
            --input data/weekly_sales.csv \
            --output reports/weekly_report.pdf \
            --format pdf \
            --template templates/weekly_template.yaml
```

#### Automated Data Processing Script
```python
#!/usr/bin/env python3
"""
Automated report generation script
Run this daily to process new data files
"""
import os
import glob
from datetime import datetime
from docgenius.core.document_creator import DocumentCreator
from docgenius.logic.utilities import FileHelper

def process_daily_files():
    """Process all CSV files from today and generate reports"""
    today = datetime.now().strftime('%Y-%m-%d')
    input_pattern = f"./data/{today}_*.csv"
    
    creator = DocumentCreator()
    file_helper = FileHelper()
    
    for csv_file in glob.glob(input_pattern):
        # Generate output filename
        base_name = os.path.basename(csv_file).replace('.csv', '')
        output_file = f"./reports/{base_name}_report.pdf"
        
        # Create backup
        file_helper.create_backup(csv_file)
        
        # Generate report
        try:
            result = creator.create_document(
                input_path=csv_file,
                output_path=output_file,
                format='pdf',
                template='./templates/daily_report.yaml'
            )
            print(f"✅ Generated: {output_file}")
        except Exception as e:
            print(f"❌ Failed to process {csv_file}: {e}")

if __name__ == "__main__":
    process_daily_files()
```

### Example Projects & Demos

The `assets/examples/` directory contains complete working examples:

#### `demo_toolkit.py` - Comprehensive Demo
```python
# Run the full feature demonstration
python assets/examples/demo_toolkit.py

# This demo shows:
# - Loading different data types
# - Multiple export formats
# - Custom templates
# - Error handling
# - Performance monitoring
```

#### Sample Data Files
- `tests/sample_companies.csv` - Business data example
- `tests/sample_employees.json` - Employee records
- `tests/data/test_data.csv` - General test dataset

#### Template Examples
```bash
# View available templates
ls assets/examples/templates/

# business_report.yaml     - Corporate report template
# academic_paper.yaml      - Research document template  
# data_summary.yaml        - Statistical summary template
# newsletter.yaml          - Newsletter format template
```

---

## 🤝 Contributing & Development

### For Contributors

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/file-generator.git
   cd file-generator
   ```

2. **Set up development environment**
   ```bash
   python tools/setup_installer_tool.py
   python tools/deps_installer_tool.py
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make your changes and test**
   ```bash
   # Run tests before committing
   python tools/test_runner_tool.py
   
   # Check code style
   python -m flake8 docgenius/
   python -m black docgenius/
   ```

5. **Submit a pull request**
   - Ensure all tests pass
   - Add tests for new features
   - Update documentation if needed

### Development Guidelines

#### Code Structure
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Add unit tests for new functionality

#### Testing Requirements
```bash
# All tests must pass
python tools/test_runner_tool.py

# Coverage should be > 80%
python tools/test_runner_tool.py --coverage

# Integration tests must pass
python -m pytest tests/test_integration_e2e.py
```

#### Adding New Features
1. Create tests first (TDD approach)
2. Implement feature in appropriate module
3. Update relevant documentation
4. Add example usage if applicable
5. Test with multiple data formats

## 📄 License & Support

### License
This project is licensed under the MIT License - see the LICENSE file for details.

### Getting Help

**For End Users**:
- 📖 Check the user examples above
- 🎮 Try the interactive demo: `python app_launcher_cli.py`
- 📁 Review sample files in `assets/examples/`
- 🐛 Report issues on [GitHub Issues](https://github.com/brunovskyy/file-generator/issues)

**For Developers**:
- 🔧 Run dependency checker: `python tools/deps_installer_tool.py`
- 📋 Review development logs in build artifacts
- 🧪 Check test results: `python tools/test_runner_tool.py`
- 📚 Review API documentation in source code docstrings

### Common Issues & Solutions

**Issue**: "Module not found" errors
**Solution**: Run `python tools/deps_installer_tool.py` to install dependencies

**Issue**: Executable won't build
**Solution**: Check `build/` directory for detailed error logs

**Issue**: CSV parsing errors
**Solution**: Check file encoding and delimiter settings

**Issue**: PDF generation fails
**Solution**: Ensure required fonts are installed on your system

---

**DocGenius** - Making data transformation simple for everyone. 🎨✨

*Transform your data into professional documents with just a few clicks!*

# Logic Directory - DocGenius Core Components

This directory contains the core business logic and supporting models for DocGenius. The structure is organized to provide clear separation of concerns and maintainable code architecture.

## 📁 Directory Structure

```
logic/
├── models/           # Data models and structures
├── exporters/        # Document export implementations  
├── data_sources/     # Data loading and processing
├── utilities/        # Shared utility functions
└── README.md         # This file
```

---

## 🏗️ Architecture Overview

### 📊 **Data Flow:**
```
Data Sources → Models → Processing → Exporters → Output Files
```

1. **Data Sources** load and validate input data (CSV, JSON, APIs)
2. **Models** represent the data structures and configuration
3. **Processing** normalizes and transforms the data
4. **Exporters** generate the final document formats
5. **Utilities** provide shared functionality across components

---

## 📋 Component Details

### 🗃️ **Models (`models/`)**
Core data structures and configuration classes:

- **`document_config.py`** - Configuration settings for document generation
- **`export_settings.py`** - Export-specific settings and validation
- **`data_structures.py`** - Data models for normalized content
- **`template_models.py`** - Template and formatting models
- **`validation_models.py`** - Input validation and error handling

**Purpose:** Define the structure and validation rules for all data flowing through the system.

### 📤 **Exporters (`exporters/`)**
Document format generators:

- **`markdown_exporter.py`** - Markdown file generation with YAML front matter
- **`pdf_exporter.py`** - PDF document creation and formatting
- **`word_exporter.py`** - Word document generation and templates
- **`base_exporter.py`** - Abstract base class for all exporters
- **`export_factory.py`** - Factory pattern for exporter creation

**Purpose:** Convert normalized data into specific document formats with consistent interfaces.

### 📥 **Data Sources (`data_sources/`)**
Input data handlers:

- **`csv_loader.py`** - CSV file parsing and validation
- **`json_loader.py`** - JSON data loading and normalization
- **`api_client.py`** - REST API data fetching
- **`base_loader.py`** - Abstract base class for data loaders
- **`data_validator.py`** - Input data validation and sanitization

**Purpose:** Handle various input formats and normalize them into consistent data structures.

### 🛠️ **Utilities (`utilities/`)**
Shared functionality:

- **`file_operations.py`** - File system operations and path handling
- **`formatting_helpers.py`** - Text formatting and template utilities
- **`dialog_managers.py`** - GUI file/folder selection dialogs
- **`logging_config.py`** - Logging setup and configuration
- **`error_handlers.py`** - Error handling and user feedback

**Purpose:** Provide reusable functionality that doesn't belong to specific components.

---

## 🔗 Component Relationships

### **Primary Dependencies:**
```
App Layer (app.py, document_creator.py)
    ↓
Logic Layer (this directory)
    ↓
External Libraries (requests, PyYAML, etc.)
```

### **Internal Dependencies:**
```
Exporters → Models + Utilities
Data Sources → Models + Utilities  
Models → Utilities (validation only)
Utilities → External Libraries only
```

### **Key Interfaces:**
1. **`BaseLoader`** - Standard interface for all data sources
2. **`BaseExporter`** - Standard interface for all exporters
3. **`DocumentConfig`** - Central configuration object
4. **`ExportSettings`** - Format-specific settings container

---

## 🚀 Usage Examples

### **Loading Data:**
```python
from logic.data_sources import CSVLoader, JSONLoader
from logic.models import DocumentConfig

# Load configuration
config = DocumentConfig(source="data.csv", formats=["markdown"])

# Load data using appropriate loader
if config.source.endswith('.csv'):
    loader = CSVLoader()
    data = loader.load(config.source)
```

### **Exporting Documents:**
```python
from logic.exporters import MarkdownExporter
from logic.models import ExportSettings

# Configure export settings
settings = ExportSettings(
    include_yaml=True,
    output_dir="./output"
)

# Export documents
exporter = MarkdownExporter(settings)
files = exporter.export(data, settings)
```

---

## 🔄 Migration from `json_to_file/`

The existing `json_to_file/` directory is being restructured:

### **File Mapping:**
- `source_to_json.py` → `data_sources/json_loader.py` + `data_sources/csv_loader.py`
- `markdown_export.py` → `exporters/markdown_exporter.py`
- `pdf_export.py` → `exporters/pdf_exporter.py`
- `word_export.py` → `exporters/word_exporter.py`
- `utils.py` → `utilities/` (split into specific files)

### **Backwards Compatibility:**
The old `json_to_file/` imports will continue to work during the transition period through import redirects.

---

## 🎯 Benefits of This Structure

### **For Developers:**
- **Clear separation of concerns** - easy to find and modify specific functionality
- **Consistent interfaces** - predictable patterns across components
- **Easy testing** - isolated components with clear dependencies
- **Scalable architecture** - simple to add new exporters or data sources

### **For Contributors:**
- **Self-documenting structure** - directory names explain purpose
- **Focused files** - each file has a single responsibility
- **Clear dependencies** - easy to understand what imports what
- **Comprehensive documentation** - README files explain each component

### **For Maintenance:**
- **Isolated changes** - modifications don't ripple across the system
- **Easy debugging** - problems can be traced to specific components
- **Version control friendly** - smaller files with focused changes
- **Future-proof** - structure supports adding new formats and features

---

## 📚 Next Steps

1. **Review existing code** in `json_to_file/` directory
2. **Create model classes** for configuration and data structures
3. **Refactor exporters** to use consistent interfaces
4. **Split data loading** into specialized loader classes
5. **Update imports** throughout the application
6. **Add comprehensive tests** for each component
7. **Create migration guide** for external users

---

**💡 Remember:** This structure is designed to grow with the project while maintaining clean, readable, and maintainable code.

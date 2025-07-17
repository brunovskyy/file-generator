# Exporters - Document Generation Engines

This directory contains the specialized export engines that transform normalized data into various document formats. Each exporter provides format-specific optimizations and features.

## 📋 Files Overview

### 📄 **Format Exporters**

#### `markdown_exporter.py`
**Purpose:** Generate Markdown files with YAML front matter and structured content  
**Responsibilities:**
- Convert data objects to Markdown format
- Generate YAML front matter headers
- Handle Markdown-specific formatting (tables, lists, links)
- Support custom templates and styling
- Manage file naming and organization

**Key Classes:**
- `MarkdownExporter` - Main markdown generation engine
- `YAMLFrontMatterGenerator` - YAML header creation
- `MarkdownFormatter` - Content formatting utilities

**Supported Features:**
- YAML front matter with configurable keys
- Table generation from structured data
- Custom template support
- Link generation and validation
- Image embedding and references

---

#### `pdf_exporter.py`
**Purpose:** Generate professional PDF documents with layout control  
**Responsibilities:**
- Convert data to PDF format with precise layout
- Handle fonts, styling, and page layouts
- Support headers, footers, and page numbering
- Generate tables, charts, and graphics
- Manage PDF metadata and properties

**Key Classes:**
- `PDFExporter` - Main PDF generation engine
- `PDFLayoutManager` - Page layout and positioning
- `PDFStyleManager` - Font and styling control
- `PDFTableGenerator` - Table creation and formatting

**Supported Features:**
- Custom page sizes and orientations
- Advanced table layouts with styling
- Header and footer customization
- Font embedding and management
- Metadata and document properties

---

#### `word_exporter.py`
**Purpose:** Generate Microsoft Word documents with rich formatting  
**Responsibilities:**
- Create Word documents with native formatting
- Handle styles, templates, and themes
- Generate tables, lists, and structured content
- Support document sections and page breaks
- Manage Word-specific features

**Key Classes:**
- `WordExporter` - Main Word document generator
- `WordStyleManager` - Style and formatting control
- `WordTableGenerator` - Table creation utilities
- `WordTemplateProcessor` - Template handling

**Supported Features:**
- Native Word formatting and styles
- Template-based document generation
- Table creation with custom styling
- Section management and page breaks
- Header and footer customization

---

### 🎯 **Base Classes**

#### `base_exporter.py`
**Purpose:** Abstract base class defining the common exporter interface  
**Responsibilities:**
- Define standard exporter methods and properties
- Provide common validation and error handling
- Handle file naming and path management
- Support progress tracking and logging

**Key Classes:**
- `BaseExporter` - Abstract exporter interface
- `ExportContext` - Shared context and settings
- `ExportResult` - Result status and metadata

---

#### `template_processor.py`
**Purpose:** Template loading, validation, and processing utilities  
**Responsibilities:**
- Load and validate template files
- Process template variables and placeholders
- Handle template inheritance and includes
- Support custom template functions

**Key Classes:**
- `TemplateProcessor` - Main template engine
- `TemplateLoader` - Template file management
- `TemplateValidator` - Template validation logic
- `VariableResolver` - Variable substitution

---

## 🔗 Exporter Relationships

```
BaseExporter (Abstract)
    ├── MarkdownExporter
    │   ├── YAMLFrontMatterGenerator
    │   └── MarkdownFormatter
    ├── PDFExporter
    │   ├── PDFLayoutManager
    │   ├── PDFStyleManager
    │   └── PDFTableGenerator
    └── WordExporter
        ├── WordStyleManager
        ├── WordTableGenerator
        └── WordTemplateProcessor

TemplateProcessor (Shared)
    ├── TemplateLoader
    ├── TemplateValidator
    └── VariableResolver
```

---

## 🎯 Design Principles

### **Interface Consistency**
All exporters implement the same base interface for seamless format switching and batch processing.

### **Format Optimization**
Each exporter leverages format-specific features and best practices for optimal output quality.

### **Template Support**
Comprehensive template system allows customization without code changes.

### **Error Handling**
Robust error handling with detailed feedback for troubleshooting and debugging.

---

## 📝 Common Interface

All exporters implement the following interface:

```python
class BaseExporter:
    def validate_settings(self) -> ValidationResult:
        """Validate exporter configuration."""
        
    def export_single(self, data_object: DataObject) -> ExportResult:
        """Export single data object to file."""
        
    def export_batch(self, data_collection: DataCollection) -> List[ExportResult]:
        """Export multiple data objects."""
        
    def get_output_path(self, data_object: DataObject) -> Path:
        """Generate output file path for data object."""
        
    def preview_export(self, data_object: DataObject) -> str:
        """Generate preview of export output."""
```

---

## 🚀 Usage Examples

### **Basic Export:**
```python
from logic.exporters import MarkdownExporter
from logic.models import DataObject, MarkdownSettings

# Configure exporter
settings = MarkdownSettings(
    include_yaml_front_matter=True,
    yaml_keys=["title", "date", "author"]
)

exporter = MarkdownExporter(settings)

# Export single object
data_obj = DataObject({"name": "John", "role": "Developer"})
result = exporter.export_single(data_obj)

if result.success:
    print(f"Exported to: {result.output_path}")
else:
    print(f"Export failed: {result.error}")
```

### **Batch Export:**
```python
from logic.exporters import PDFExporter
from logic.models import DataCollection, PDFSettings

# Configure PDF export
settings = PDFSettings(
    page_size="A4",
    include_header=True,
    include_footer=True
)

exporter = PDFExporter(settings)

# Export collection
collection = DataCollection([obj1, obj2, obj3])
results = exporter.export_batch(collection)

for result in results:
    if result.success:
        print(f"✓ {result.output_path}")
    else:
        print(f"✗ {result.error}")
```

### **Template-Based Export:**
```python
from logic.exporters import WordExporter
from logic.models import WordSettings

# Configure with custom template
settings = WordSettings(
    template_path="templates/employee_report.docx",
    custom_styles=True
)

exporter = WordExporter(settings)

# Export with template
result = exporter.export_single(employee_data)
```

---

## 🔧 Adding New Exporters

To add support for a new format:

1. **Create exporter class** inheriting from `BaseExporter`
2. **Implement required methods** following the interface
3. **Add format-specific settings** model
4. **Create unit tests** for the new exporter
5. **Update documentation** and examples

Example structure:
```python
class NewFormatExporter(BaseExporter):
    def __init__(self, settings: NewFormatSettings):
        super().__init__(settings)
        
    def validate_settings(self) -> ValidationResult:
        # Format-specific validation
        
    def export_single(self, data_object: DataObject) -> ExportResult:
        # Format-specific export logic
        
    def _format_content(self, data: dict) -> str:
        # Private formatting methods
```

---

## 📊 Performance Considerations

### **Memory Management**
- Stream large datasets to avoid memory issues
- Use generators for batch processing
- Clean up temporary resources

### **File I/O Optimization**
- Batch file operations when possible
- Use efficient file writing methods
- Handle concurrent access properly

### **Format-Specific Optimizations**
- Leverage native libraries for best performance
- Cache reusable resources (fonts, styles)
- Optimize template processing

---

## 🔄 Migration Notes

When migrating from the existing `json_to_file` structure:

1. **`markdown_export.py`** → `MarkdownExporter` class
2. **`pdf_export.py`** → `PDFExporter` class  
3. **`word_export.py`** → `WordExporter` class
4. **Shared utilities** → `BaseExporter` and helper classes

Benefits of the new structure:
- **Consistent interface** across all formats
- **Better error handling** and validation
- **Template support** for customization
- **Easier testing** and maintenance

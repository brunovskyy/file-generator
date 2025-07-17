# Models - Data Structures and Configuration

This directory contains the core data models and configuration classes that define the structure and behavior of data throughout DocGenius.

## 📋 Files Overview

### 🔧 **Configuration Models**

#### `document_config.py`
**Purpose:** Central configuration object for document generation process  
**Responsibilities:**
- Store user preferences (source, output directory, formats)
- Validate configuration consistency
- Provide default values and validation rules
- Handle configuration persistence

**Key Classes:**
- `DocumentConfig` - Main configuration container
- `ConfigValidator` - Configuration validation logic

**Usage Example:**
```python
config = DocumentConfig(
    source="data.csv",
    export_types=["markdown", "pdf"],
    output_dir="./output",
    yaml_front_matter=True
)
```

---

#### `export_settings.py`
**Purpose:** Format-specific export settings and validation  
**Responsibilities:**
- Define settings for each export format
- Validate format-specific options
- Handle export customization options
- Manage template settings

**Key Classes:**
- `ExportSettings` - Base settings class
- `MarkdownSettings` - Markdown-specific options
- `PDFSettings` - PDF-specific options  
- `WordSettings` - Word document options

---

### 📊 **Data Models**

#### `data_structures.py`
**Purpose:** Data models for normalized content representation  
**Responsibilities:**
- Define standard data object structure
- Handle data normalization and validation
- Provide data transformation utilities
- Manage field mapping and aliases

**Key Classes:**
- `DataObject` - Single data record representation
- `DataCollection` - Collection of data objects
- `FieldMapping` - Field name mapping and transformation
- `DataNormalizer` - Data standardization logic

---

#### `template_models.py`
**Purpose:** Template and formatting models for document generation  
**Responsibilities:**
- Define template structure and variables
- Handle template validation and loading
- Manage formatting options and styles
- Support custom template creation

**Key Classes:**
- `DocumentTemplate` - Base template class
- `MarkdownTemplate` - Markdown template with YAML
- `PDFTemplate` - PDF layout and styling
- `WordTemplate` - Word document template

---

### ✅ **Validation Models**

#### `validation_models.py`
**Purpose:** Input validation and error handling models  
**Responsibilities:**
- Define validation rules and constraints
- Handle error collection and reporting
- Provide validation result structures
- Support custom validation logic

**Key Classes:**
- `ValidationResult` - Validation outcome container
- `ValidationRule` - Individual validation rule
- `ErrorCollector` - Error aggregation and reporting
- `DataValidator` - Comprehensive data validation

---

## 🔗 Model Relationships

```
DocumentConfig
    ├── ExportSettings (multiple formats)
    │   ├── MarkdownSettings
    │   ├── PDFSettings
    │   └── WordSettings
    ├── DataCollection
    │   └── DataObject (multiple records)
    └── ValidationResult
        └── ValidationRule (multiple rules)

DocumentTemplate
    ├── MarkdownTemplate
    ├── PDFTemplate
    └── WordTemplate
```

---

## 🎯 Design Principles

### **Immutability**
Models are designed to be immutable where possible to prevent accidental modifications and ensure thread safety.

### **Validation**
All models include built-in validation to catch errors early and provide clear feedback to users.

### **Serialization**
Models support JSON serialization for configuration persistence and API communication.

### **Extensibility**
Base classes and interfaces allow easy addition of new formats and validation rules.

---

## 📝 Implementation Guidelines

### **Creating New Models:**
1. Inherit from appropriate base class
2. Define clear validation rules
3. Include comprehensive docstrings
4. Add serialization support
5. Write unit tests

### **Model Naming Conventions:**
- Classes: `PascalCase` (e.g., `DocumentConfig`)
- Methods: `snake_case` (e.g., `validate_settings`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_OUTPUT_DIR`)

### **Validation Patterns:**
```python
def validate(self) -> ValidationResult:
    """Validate model state and return result."""
    errors = []
    
    if not self.source:
        errors.append("Source is required")
    
    if not self.export_types:
        errors.append("At least one export type required")
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors
    )
```

---

## 🚀 Usage Examples

### **Basic Configuration:**
```python
from logic.models import DocumentConfig, ExportSettings

# Create configuration
config = DocumentConfig(
    source="employees.csv",
    export_types=["markdown", "pdf"]
)

# Validate configuration
result = config.validate()
if not result.is_valid:
    print(f"Errors: {result.errors}")
```

### **Advanced Settings:**
```python
from logic.models import MarkdownSettings, PDFSettings

# Configure markdown export
md_settings = MarkdownSettings(
    include_yaml_front_matter=True,
    yaml_keys=["title", "date", "author"],
    template="custom_template.md"
)

# Configure PDF export
pdf_settings = PDFSettings(
    page_size="A4",
    margin={"top": 1, "bottom": 1, "left": 1, "right": 1},
    font_family="Arial"
)
```

---

## 🔄 Migration Notes

When migrating from the existing `json_to_file` structure:

1. **Configuration objects** replace scattered parameter passing
2. **Validation models** centralize error handling
3. **Data structures** standardize data representation
4. **Export settings** replace format-specific parameters

This provides better maintainability, consistency, and extensibility for the entire system.

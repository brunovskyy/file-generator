# Utilities - Supporting Functions and Helpers

This directory contains utility functions, helper classes, and common functionality used throughout the DocGenius application. These utilities provide reusable components for file operations, validation, formatting, and system interactions.

## 📋 Files Overview

### 🗂️ **File Operations**

#### `file_utils.py`
**Purpose:** File system operations, path handling, and file management utilities  
**Responsibilities:**
- Safe file and directory operations
- Path validation and normalization
- File type detection and validation
- Backup and recovery operations
- Temporary file management

**Key Functions:**
- `safe_create_directory()` - Create directories with proper error handling
- `validate_file_path()` - Path validation and security checks
- `get_file_extension()` - File type detection
- `backup_file()` - Create file backups before operations
- `cleanup_temp_files()` - Temporary file management

**Key Classes:**
- `PathManager` - Path handling and validation
- `FileOperations` - Safe file system operations
- `BackupManager` - File backup and recovery

---

#### `dialog_utils.py`
**Purpose:** GUI dialog utilities for file and folder selection  
**Responsibilities:**
- File selection dialogs with proper window management
- Folder selection with validation
- Dialog customization and configuration
- Cross-platform dialog support
- Error handling for dialog operations

**Key Functions:**
- `select_file_dialog()` - File selection with filters
- `select_folder_dialog()` - Directory selection
- `save_file_dialog()` - Save location selection
- `show_message_dialog()` - User messaging
- `confirm_dialog()` - User confirmation prompts

**Key Classes:**
- `DialogManager` - Centralized dialog handling
- `DialogConfig` - Dialog configuration options

---

### ✅ **Validation and Checking**

#### `validation_utils.py`
**Purpose:** Data validation, format checking, and constraint verification  
**Responsibilities:**
- Data type validation and conversion
- Format validation (email, URL, date patterns)
- Business rule validation
- Collection validation utilities
- Custom validation rule support

**Key Functions:**
- `validate_email()` - Email format validation
- `validate_url()` - URL format and accessibility
- `validate_date_format()` - Date string validation
- `validate_data_structure()` - Object structure validation
- `apply_validation_rules()` - Custom rule application

**Key Classes:**
- `DataValidator` - Comprehensive data validation
- `ValidationRule` - Individual validation rules
- `ValidationChain` - Chained validation processing

---

#### `format_utils.py`
**Purpose:** Text formatting, string manipulation, and content processing  
**Responsibilities:**
- String cleaning and normalization
- Text formatting for different output types
- Template variable processing
- Content transformation utilities
- Encoding and character handling

**Key Functions:**
- `clean_text()` - Text sanitization and normalization
- `format_for_filename()` - Safe filename generation
- `escape_special_chars()` - Format-specific escaping
- `normalize_whitespace()` - Whitespace handling
- `convert_encoding()` - Character encoding conversion

**Key Classes:**
- `TextProcessor` - Advanced text processing
- `FormatConverter` - Format-specific conversion
- `TemplateEngine` - Template processing utilities

---

### 🔧 **Configuration and Settings**

#### `config_utils.py`
**Purpose:** Configuration management, settings persistence, and environment handling  
**Responsibilities:**
- Configuration file loading and saving
- Environment variable handling
- Settings validation and defaults
- Configuration migration and versioning
- Secure settings management

**Key Functions:**
- `load_config()` - Configuration file loading
- `save_config()` - Configuration persistence
- `get_env_setting()` - Environment variable access
- `merge_configs()` - Configuration merging
- `validate_config()` - Configuration validation

**Key Classes:**
- `ConfigManager` - Central configuration handling
- `SettingsStore` - Persistent settings storage
- `EnvironmentHandler` - Environment configuration

---

### 📊 **Logging and Monitoring**

#### `logging_utils.py`
**Purpose:** Structured logging, monitoring, and debugging utilities  
**Responsibilities:**
- Application logging configuration
- Structured log formatting
- Performance monitoring and metrics
- Debug information collection
- Log rotation and management

**Key Functions:**
- `setup_logging()` - Logger configuration
- `log_operation()` - Operation logging with context
- `measure_performance()` - Performance timing
- `log_error_with_context()` - Enhanced error logging
- `create_debug_report()` - Debug information collection

**Key Classes:**
- `LogManager` - Centralized logging control
- `PerformanceMonitor` - Performance tracking
- `DebugCollector` - Debug information gathering

---

### 🌐 **System Integration**

#### `system_utils.py`
**Purpose:** System information, platform detection, and environment utilities  
**Responsibilities:**
- Operating system detection and adaptation
- System resource monitoring
- Environment setup and validation
- Cross-platform compatibility
- System command execution

**Key Functions:**
- `get_system_info()` - System information collection
- `check_dependencies()` - Dependency validation
- `get_available_memory()` - Resource monitoring
- `execute_system_command()` - Safe command execution
- `setup_environment()` - Environment preparation

**Key Classes:**
- `SystemInfo` - System information container
- `ResourceMonitor` - Resource usage tracking
- `PlatformHandler` - Platform-specific operations

---

### 🎯 **Data Processing**

#### `data_utils.py`
**Purpose:** Data manipulation, transformation, and analysis utilities  
**Responsibilities:**
- Data structure manipulation
- Statistical analysis and summarization
- Data type conversion and normalization
- Collection operations and filtering
- Data quality assessment

**Key Functions:**
- `flatten_nested_dict()` - Dictionary flattening
- `normalize_field_names()` - Field name standardization
- `detect_data_types()` - Automatic type detection
- `summarize_data()` - Data summary statistics
- `filter_data()` - Data filtering and selection

**Key Classes:**
- `DataProcessor` - Advanced data manipulation
- `StatisticsCalculator` - Statistical analysis
- `DataQualityAnalyzer` - Data quality assessment

---

## 🔗 Utility Relationships

```
Core Utilities
├── FileOperations
│   ├── PathManager
│   ├── BackupManager
│   └── DialogManager
├── DataProcessor
│   ├── DataValidator
│   ├── TextProcessor
│   └── StatisticsCalculator
├── ConfigManager
│   ├── SettingsStore
│   └── EnvironmentHandler
└── SystemInfo
    ├── ResourceMonitor
    └── PlatformHandler

Shared Components
├── LogManager (used by all)
├── ValidationChain (used by validators)
└── PerformanceMonitor (used by processors)
```

---

## 🎯 Design Principles

### **Reusability**
Utilities are designed to be generic and reusable across different parts of the application.

### **Error Handling**
Comprehensive error handling with meaningful error messages and recovery options.

### **Performance**
Optimized implementations for common operations with minimal overhead.

### **Cross-Platform**
Platform-agnostic implementations with platform-specific adaptations where needed.

---

## 🚀 Usage Examples

### **File Operations:**
```python
from logic.utilities import file_utils

# Safe directory creation
result = file_utils.safe_create_directory("/path/to/output")
if not result.success:
    print(f"Failed to create directory: {result.error}")

# File validation
if file_utils.validate_file_path("data.csv"):
    print("File path is valid and accessible")

# Create backup before operations
backup_path = file_utils.backup_file("important.json")
```

### **Dialog Operations:**
```python
from logic.utilities import dialog_utils

# File selection with filters
file_path = dialog_utils.select_file_dialog(
    title="Select Data File",
    filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json")]
)

if file_path:
    print(f"Selected file: {file_path}")

# Folder selection
output_dir = dialog_utils.select_folder_dialog(
    title="Select Output Directory"
)
```

### **Data Validation:**
```python
from logic.utilities import validation_utils

# Email validation
if validation_utils.validate_email("user@example.com"):
    print("Valid email address")

# Data structure validation
data = {"name": "John", "age": 30}
result = validation_utils.validate_data_structure(
    data, 
    required_fields=["name", "age"],
    field_types={"name": str, "age": int}
)

if result.is_valid:
    print("Data structure is valid")
```

### **Configuration Management:**
```python
from logic.utilities import config_utils

# Load configuration
config = config_utils.load_config("settings.json")

# Get setting with default
output_dir = config_utils.get_setting(
    "output_directory", 
    default="./output"
)

# Save updated configuration
config_utils.save_config(config, "settings.json")
```

### **Logging Setup:**
```python
from logic.utilities import logging_utils

# Setup application logging
logging_utils.setup_logging(
    level="INFO",
    log_file="docgenius.log",
    include_console=True
)

# Log operation with context
logging_utils.log_operation(
    "document_export",
    {"format": "pdf", "count": 10},
    duration=2.5
)
```

### **System Information:**
```python
from logic.utilities import system_utils

# Get system information
sys_info = system_utils.get_system_info()
print(f"OS: {sys_info.platform}")
print(f"Memory: {sys_info.memory_gb} GB")

# Check dependencies
deps_ok = system_utils.check_dependencies([
    "pandas", "reportlab", "python-docx"
])

if not deps_ok:
    print("Missing required dependencies")
```

---

## 🔧 Creating New Utilities

When adding new utility functions:

1. **Choose appropriate module** based on functionality
2. **Follow naming conventions** (snake_case for functions)
3. **Include comprehensive docstrings** with examples
4. **Add error handling** and validation
5. **Write unit tests** for all functions
6. **Update documentation** and examples

Example utility function:
```python
def process_data_safely(data: dict, processor_func: callable) -> ProcessResult:
    """
    Safely process data with error handling and logging.
    
    Args:
        data: Input data dictionary
        processor_func: Function to process the data
        
    Returns:
        ProcessResult with success status and result/error
        
    Example:
        result = process_data_safely(
            {"name": "John"}, 
            lambda x: x["name"].upper()
        )
        if result.success:
            print(f"Result: {result.data}")
    """
    try:
        logging_utils.log_operation_start("data_processing")
        
        # Validate input
        if not isinstance(data, dict):
            return ProcessResult(False, None, "Invalid data type")
            
        # Process data
        result = processor_func(data)
        
        logging_utils.log_operation_success("data_processing")
        return ProcessResult(True, result, None)
        
    except Exception as e:
        logging_utils.log_operation_error("data_processing", str(e))
        return ProcessResult(False, None, str(e))
```

---

## 📊 Performance Utilities

### **Memory Management:**
```python
from logic.utilities import system_utils

# Monitor memory usage
memory_info = system_utils.get_memory_usage()
if memory_info.available_mb < 100:
    print("Low memory warning")

# Process large datasets in chunks
for chunk in data_utils.chunk_data(large_dataset, chunk_size=1000):
    process_chunk(chunk)
```

### **Performance Monitoring:**
```python
from logic.utilities import logging_utils

# Measure operation performance
with logging_utils.measure_performance("data_export"):
    export_data_to_files(data)

# Get performance metrics
metrics = logging_utils.get_performance_metrics()
print(f"Average export time: {metrics['data_export']['avg_duration']}")
```

---

## 🔄 Migration Notes

When migrating from the existing `json_to_file` structure:

1. **`utils.py`** functions → Organized into specific utility modules
2. **Scattered helper functions** → Centralized in appropriate modules
3. **Error handling** → Consistent patterns across utilities
4. **Configuration handling** → Centralized configuration management

Benefits of the new structure:
- **Better organization** with focused utility modules
- **Reusable components** across the entire application
- **Consistent error handling** and logging patterns
- **Improved testing** with isolated utility functions
- **Enhanced documentation** with clear examples and usage patterns

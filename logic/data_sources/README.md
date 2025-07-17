# Data Sources - Input Loading and Processing

This directory contains specialized loaders for different data source types. Each loader handles format-specific parsing, validation, and normalization to provide consistent data structures for export processing.

## 📋 Files Overview

### 📊 **Source Loaders**

#### `csv_loader.py`
**Purpose:** Load and process CSV files with comprehensive parsing options  
**Responsibilities:**
- Parse CSV files with configurable delimiters and encoding
- Handle headers, data types, and missing values
- Validate data integrity and structure
- Support custom field mapping and aliases
- Process large files with streaming support

**Key Classes:**
- `CSVLoader` - Main CSV processing engine
- `CSVOptions` - Configuration for CSV parsing
- `CSVValidator` - Data validation and quality checks
- `CSVFieldMapper` - Column mapping and transformation

**Supported Features:**
- Multiple delimiters (comma, semicolon, tab, custom)
- Character encoding detection and conversion
- Header row detection and validation
- Data type inference and conversion
- Missing value handling strategies
- Large file streaming and chunking

---

#### `json_loader.py`
**Purpose:** Load and process JSON files and data structures  
**Responsibilities:**
- Parse JSON files and nested data structures
- Handle arrays and object hierarchies
- Flatten nested structures for document generation
- Validate JSON schema and data consistency
- Support JSONLines and multi-document formats

**Key Classes:**
- `JSONLoader` - Main JSON processing engine
- `JSONFlattener` - Nested structure flattening
- `JSONValidator` - Schema validation and checking
- `JSONPathProcessor` - JSONPath queries and extraction

**Supported Features:**
- Standard JSON and JSONLines formats
- Nested object flattening with configurable depth
- JSONPath queries for data extraction
- Schema validation and type checking
- Array processing and normalization
- Custom deserialization handlers

---

#### `api_loader.py`
**Purpose:** Load data from REST APIs and web services  
**Responsibilities:**
- Make HTTP requests to API endpoints
- Handle authentication and headers
- Process paginated responses
- Parse various response formats (JSON, XML, CSV)
- Implement retry logic and error handling
- Cache responses for efficiency

**Key Classes:**
- `APILoader` - Main API client and processor
- `APIConfig` - Configuration for API requests
- `ResponseParser` - Response format handling
- `PaginationHandler` - Paginated data processing
- `AuthManager` - Authentication handling

**Supported Features:**
- REST API integration with various auth methods
- Pagination support (offset, cursor, page-based)
- Response caching and rate limiting
- Multiple response formats
- Custom headers and request configuration
- Retry logic with exponential backoff

---

#### `database_loader.py`
**Purpose:** Load data from database connections  
**Responsibilities:**
- Connect to various database types (PostgreSQL, MySQL, SQLite)
- Execute queries and process results
- Handle connection pooling and management
- Support parameterized queries for security
- Process large result sets efficiently

**Key Classes:**
- `DatabaseLoader` - Main database interface
- `QueryBuilder` - SQL query construction
- `ConnectionManager` - Database connection handling
- `ResultProcessor` - Query result processing

**Supported Features:**
- Multiple database engine support
- Secure parameterized queries
- Connection pooling and reuse
- Large result set streaming
- Transaction management
- Custom query building

---

### 🎯 **Base Classes**

#### `base_loader.py`
**Purpose:** Abstract base class defining the common loader interface  
**Responsibilities:**
- Define standard loading methods and properties
- Provide common validation and error handling
- Handle data normalization and transformation
- Support progress tracking and logging

**Key Classes:**
- `BaseLoader` - Abstract loader interface
- `LoaderConfig` - Base configuration class
- `LoadResult` - Result status and metadata
- `DataNormalizer` - Common data transformation

---

#### `source_detector.py`
**Purpose:** Automatic source type detection and loader selection  
**Responsibilities:**
- Analyze input sources to determine type
- Select appropriate loader based on source characteristics
- Validate source accessibility and format
- Provide loader recommendations and options

**Key Classes:**
- `SourceDetector` - Main detection engine
- `SourceAnalyzer` - Format analysis utilities
- `LoaderSelector` - Loader recommendation logic

---

## 🔗 Loader Relationships

```
BaseLoader (Abstract)
    ├── CSVLoader
    │   ├── CSVOptions
    │   ├── CSVValidator
    │   └── CSVFieldMapper
    ├── JSONLoader
    │   ├── JSONFlattener
    │   ├── JSONValidator
    │   └── JSONPathProcessor
    ├── APILoader
    │   ├── APIConfig
    │   ├── ResponseParser
    │   ├── PaginationHandler
    │   └── AuthManager
    └── DatabaseLoader
        ├── QueryBuilder
        ├── ConnectionManager
        └── ResultProcessor

SourceDetector (Shared)
    ├── SourceAnalyzer
    └── LoaderSelector

DataNormalizer (Shared)
    └── Used by all loaders
```

---

## 🎯 Design Principles

### **Interface Consistency**
All loaders implement the same base interface for seamless source switching and processing.

### **Format Specialization**
Each loader is optimized for its specific data format with tailored parsing and validation.

### **Performance Optimization**
Support for streaming, chunking, and efficient processing of large datasets.

### **Error Resilience**
Comprehensive error handling with recovery options and detailed diagnostics.

---

## 📝 Common Interface

All loaders implement the following interface:

```python
class BaseLoader:
    def validate_source(self) -> ValidationResult:
        """Validate data source accessibility and format."""
        
    def load_data(self) -> DataCollection:
        """Load and normalize data from source."""
        
    def preview_data(self, limit: int = 5) -> List[DataObject]:
        """Preview first few records from source."""
        
    def get_metadata(self) -> dict:
        """Get metadata about the data source."""
        
    def estimate_size(self) -> int:
        """Estimate number of records in source."""
```

---

## 🚀 Usage Examples

### **CSV Loading:**
```python
from logic.data_sources import CSVLoader
from logic.models import CSVOptions

# Configure CSV loader
options = CSVOptions(
    delimiter=",",
    encoding="utf-8",
    header_row=True,
    skip_empty_rows=True
)

loader = CSVLoader("employees.csv", options)

# Validate and load
if loader.validate_source().is_valid:
    data = loader.load_data()
    print(f"Loaded {len(data)} records")
```

### **JSON Loading:**
```python
from logic.data_sources import JSONLoader

# Load JSON data
loader = JSONLoader("data.json")

# Preview data structure
preview = loader.preview_data(3)
for obj in preview:
    print(f"Sample: {obj.data}")

# Load all data
collection = loader.load_data()
```

### **API Loading:**
```python
from logic.data_sources import APILoader, APIConfig

# Configure API access
config = APIConfig(
    base_url="https://api.example.com",
    endpoint="/users",
    auth_type="bearer",
    auth_token="your-token-here",
    pagination="offset"
)

loader = APILoader(config)

# Load paginated data
data = loader.load_data()
print(f"Loaded {len(data)} records from API")
```

### **Database Loading:**
```python
from logic.data_sources import DatabaseLoader

# Configure database connection
loader = DatabaseLoader(
    connection_string="postgresql://user:pass@localhost/db",
    query="SELECT * FROM employees WHERE active = true"
)

# Load query results
data = loader.load_data()
```

---

## 🔧 Auto-Detection

Use the source detector for automatic loader selection:

```python
from logic.data_sources import SourceDetector

# Analyze source and get recommended loader
detector = SourceDetector()
recommendation = detector.analyze_source("data.csv")

print(f"Detected format: {recommendation.format}")
print(f"Recommended loader: {recommendation.loader_class}")
print(f"Confidence: {recommendation.confidence}")

# Create loader automatically
loader = recommendation.create_loader()
data = loader.load_data()
```

---

## 📊 Performance Features

### **Streaming Support**
```python
# Process large files in chunks
loader = CSVLoader("large_file.csv")
for chunk in loader.stream_data(chunk_size=1000):
    process_chunk(chunk)
```

### **Caching**
```python
# Cache API responses
api_loader = APILoader(config, cache_duration=3600)
data = api_loader.load_data()  # Cached for 1 hour
```

### **Parallel Processing**
```python
# Load multiple sources in parallel
loaders = [CSVLoader(f"file_{i}.csv") for i in range(5)]
results = DataLoader.load_parallel(loaders)
```

---

## 🛠️ Adding New Loaders

To add support for a new data source type:

1. **Create loader class** inheriting from `BaseLoader`
2. **Implement required methods** following the interface
3. **Add source-specific configuration** class
4. **Update source detector** to recognize the new format
5. **Create unit tests** and documentation

Example structure:
```python
class NewSourceLoader(BaseLoader):
    def __init__(self, source: str, config: NewSourceConfig):
        super().__init__(source, config)
        
    def validate_source(self) -> ValidationResult:
        # Source-specific validation
        
    def load_data(self) -> DataCollection:
        # Source-specific loading logic
        
    def _parse_source(self) -> List[dict]:
        # Private parsing methods
```

---

## 🔄 Migration Notes

When migrating from the existing `json_to_file` structure:

1. **`source_to_json.py`** functions → Specialized loader classes
2. **Data loading logic** → Centralized in loader classes
3. **Format detection** → `SourceDetector` class
4. **Error handling** → Consistent across all loaders

Benefits of the new structure:
- **Format specialization** with optimized parsers
- **Consistent interface** across all source types
- **Better error handling** and validation
- **Performance optimizations** for large datasets
- **Automatic source detection** and loader selection

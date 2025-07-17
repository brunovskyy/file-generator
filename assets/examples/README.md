# DocGenius Examples

This directory contains example scripts and sample data to demonstrate the DocGenius toolkit features.

## Files

### `demo_toolkit.py`
Comprehensive demonstration script showing:
- Data loading from CSV and JSON
- Markdown, PDF, and Word export
- Validation features
- Error handling

**Usage:**
```bash
cd assets/examples
python demo_toolkit.py
```

### Sample Data
The demo script creates sample employee data in multiple formats to showcase the toolkit's capabilities.

## Features Demonstrated

1. **Data Loading**
   - CSV file loading with validation
   - JSON data processing
   - Error handling for malformed data

2. **Document Export**
   - Markdown export with YAML front matter
   - PDF generation with formatting
   - Word document creation with styling

3. **Validation**
   - File path validation
   - Data structure validation
   - Business logic validation

4. **Error Handling**
   - Graceful failure handling
   - Comprehensive error reporting
   - Logging and monitoring

## Output
Generated files are created in the `output/` directory:
- `employees.md` - Markdown format
- `employees.pdf` - PDF format  
- `employees.docx` - Word format

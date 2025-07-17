"""
CSV data source loader with comprehensive parsing options.

This module provides CSV loading capabilities with configurable delimiters,
encoding options, data type inference, and large file support.
"""

import csv
import io
from typing import Any, Dict, List, Optional, Union, Iterator
from pathlib import Path
from datetime import datetime
import requests

# Optional encoding detection
try:
    import chardet
    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False

from .data_loader_base import BaseLoader, LoadContext, DataSourceError
from ..models import DataObject, DataCollection, ValidationResult


class CSVOptions:
    """Configuration options for CSV parsing."""
    
    def __init__(
        self,
        delimiter: str = ",",
        quotechar: str = '"',
        escapechar: Optional[str] = None,
        header_row: bool = True,
        skip_empty_rows: bool = True,
        max_field_size: int = 131072,  # Default CSV field size limit
        detect_types: bool = True,
        type_conversion_errors: str = "ignore",  # ignore, warn, error
        null_values: Optional[List[str]] = None
    ):
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.escapechar = escapechar
        self.header_row = header_row
        self.skip_empty_rows = skip_empty_rows
        self.max_field_size = max_field_size
        self.detect_types = detect_types
        self.type_conversion_errors = type_conversion_errors
        self.null_values = null_values or ['', 'NULL', 'null', 'None', 'N/A', 'n/a']


class CSVFieldMapper:
    """Handles field name mapping and nested structure conversion."""
    
    def __init__(self, create_nested: bool = True, separator: str = '_'):
        self.create_nested = create_nested
        self.separator = separator
    
    def convert_row_to_nested(self, row_dict: Dict[str, str]) -> Dict[str, Any]:
        """
        Convert flat CSV row to nested structure based on field names.
        
        Args:
            row_dict: Flat dictionary from CSV row
            
        Returns:
            Nested dictionary structure
        """
        if not self.create_nested:
            return row_dict
        
        nested_object = {}
        
        for column_name, column_value in row_dict.items():
            if not column_name:  # Skip empty column names
                continue
            
            if self.separator in column_name:
                self._set_nested_value(nested_object, column_name, column_value)
            else:
                nested_object[column_name] = column_value
        
        return nested_object
    
    def _set_nested_value(self, obj: Dict[str, Any], key_path: str, value: Any) -> None:
        """Set nested value using separator-delimited key path."""
        keys = key_path.split(self.separator)
        current = obj
        
        # Navigate to parent of target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set final value
        current[keys[-1]] = value


class CSVValidator:
    """Validates CSV data and performs quality checks."""
    
    def __init__(self, options: CSVOptions):
        self.options = options
    
    def validate_csv_structure(self, file_path: Path) -> ValidationResult:
        """Validate CSV file structure and format."""
        result = ValidationResult(is_valid=True)
        
        try:
            with open(file_path, 'r', encoding='utf-8', newline='') as f:
                # Check if file is empty
                if f.read(1) == '':
                    result.add_error("CSV file is empty")
                    return result
                
                f.seek(0)
                
                # Try to detect dialect
                sample = f.read(8192)
                f.seek(0)
                
                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
                    if dialect.delimiter != self.options.delimiter:
                        result.add_warning(
                            f"Detected delimiter '{dialect.delimiter}' differs from configured '{self.options.delimiter}'"
                        )
                except csv.Error:
                    result.add_warning("Could not detect CSV dialect")
                
                # Check first few rows
                reader = csv.reader(f, delimiter=self.options.delimiter, quotechar=self.options.quotechar)
                
                rows_checked = 0
                field_counts = []
                
                for row in reader:
                    field_counts.append(len(row))
                    rows_checked += 1
                    
                    if rows_checked >= 10:  # Check first 10 rows
                        break
                
                # Check for consistent field counts
                if field_counts:
                    expected_fields = field_counts[0]
                    inconsistent_rows = [i for i, count in enumerate(field_counts) if count != expected_fields]
                    
                    if inconsistent_rows:
                        result.add_warning(
                            f"Inconsistent field counts in rows: {inconsistent_rows} (expected {expected_fields} fields)"
                        )
        
        except Exception as e:
            result.add_error(f"CSV validation failed: {str(e)}")
        
        return result
    
    def analyze_data_quality(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze data quality and provide statistics."""
        if not data:
            return {"total_rows": 0, "empty_rows": 0, "field_analysis": {}}
        
        total_rows = len(data)
        empty_rows = sum(1 for row in data if not any(str(v).strip() for v in row.values()))
        
        # Analyze fields
        field_analysis = {}
        all_fields = set()
        for row in data:
            all_fields.update(row.keys())
        
        for field in all_fields:
            values = [row.get(field, '') for row in data]
            non_empty_values = [v for v in values if str(v).strip()]
            
            field_analysis[field] = {
                "total_values": len(values),
                "non_empty_values": len(non_empty_values),
                "empty_percentage": (len(values) - len(non_empty_values)) / len(values) * 100,
                "unique_values": len(set(str(v) for v in non_empty_values)),
                "sample_values": list(set(str(v) for v in non_empty_values))[:5]
            }
        
        return {
            "total_rows": total_rows,
            "empty_rows": empty_rows,
            "empty_row_percentage": empty_rows / total_rows * 100,
            "total_fields": len(all_fields),
            "field_analysis": field_analysis
        }


class CSVLoader(BaseLoader):
    """
    CSV file loader with comprehensive parsing and validation.
    
    Supports local files and URLs with configurable parsing options,
    data type inference, and memory-efficient streaming.
    """
    
    def __init__(self, source: str, context: LoadContext, **kwargs):
        """Initialize CSV loader with options."""
        super().__init__(source, context, **kwargs)
        
        # Parse CSV-specific options
        self.csv_options = CSVOptions(**{
            k: v for k, v in kwargs.items() 
            if k in CSVOptions.__init__.__code__.co_varnames
        })
        
        self.field_mapper = CSVFieldMapper(
            create_nested=kwargs.get('create_nested', True),
            separator=kwargs.get('field_separator', '_')
        )
        
        self.validator = CSVValidator(self.csv_options)
        self._headers = None
        self._estimated_rows = None
    
    def _get_source_type(self) -> str:
        """Return the source type identifier."""
        return "csv"
    
    def validate_source(self) -> ValidationResult:
        """Validate CSV source accessibility and format."""
        result = self._validate_basic_requirements()
        
        if not result.is_valid:
            return result
        
        try:
            if self.source.startswith(('http://', 'https://')):
                # Validate URL accessibility
                response = requests.head(self.source, timeout=self.context.timeout)
                response.raise_for_status()
                
                content_type = response.headers.get('content-type', '').lower()
                if content_type and 'text/csv' not in content_type and 'text/plain' not in content_type:
                    result.add_warning(f"URL content type '{content_type}' may not be CSV")
            
            else:
                # Validate file existence and format
                file_path = Path(self.source)
                
                if not file_path.exists():
                    result.add_error(f"CSV file not found: {self.source}")
                    return result
                
                if not file_path.is_file():
                    result.add_error(f"Source is not a file: {self.source}")
                    return result
                
                # Validate CSV structure
                csv_result = self.validator.validate_csv_structure(file_path)
                result = result.combine(csv_result)
        
        except requests.RequestException as e:
            result.add_error(f"Cannot access CSV URL: {str(e)}")
        except Exception as e:
            result.add_error(f"CSV validation failed: {str(e)}")
        
        return result
    
    def estimate_size(self) -> Optional[int]:
        """Estimate number of records in CSV."""
        if self._estimated_rows is not None:
            return self._estimated_rows
        
        try:
            if self.source.startswith(('http://', 'https://')):
                # For URLs, we can't easily estimate without downloading
                return None
            
            file_path = Path(self.source)
            
            # Quick estimation by counting lines
            with open(file_path, 'r', encoding=self.context.encoding) as f:
                line_count = sum(1 for _ in f)
            
            # Subtract header row if present
            if self.csv_options.header_row:
                line_count -= 1
            
            self._estimated_rows = max(0, line_count)
            return self._estimated_rows
        
        except Exception:
            return None
    
    def preview_data(self, limit: int = 5) -> List[DataObject]:
        """Preview first few records from CSV."""
        try:
            preview_objects = []
            
            with self._open_csv_source() as csv_file:
                reader = self._create_csv_reader(csv_file)
                
                for i, row_data in enumerate(reader):
                    if i >= limit:
                        break
                    
                    # Convert and create data object
                    nested_data = self.field_mapper.convert_row_to_nested(row_data)
                    data_object = self._create_data_object(nested_data, i)
                    preview_objects.append(data_object)
            
            return preview_objects
        
        except Exception as e:
            self.context.log_error(f"CSV preview failed: {str(e)}")
            return []
    
    def load_data(self) -> DataCollection:
        """Load complete CSV data."""
        start_time = datetime.now()
        data_objects = []
        
        try:
            self.context.log_info(f"Loading CSV data from: {self.source}")
            
            with self._open_csv_source() as csv_file:
                reader = self._create_csv_reader(csv_file)
                
                total_estimated = self.estimate_size()
                
                for i, row_data in enumerate(reader):
                    # Check record limit
                    if self.context.max_records and i >= self.context.max_records:
                        self.context.log_info(f"Reached maximum record limit: {self.context.max_records}")
                        break
                    
                    # Report progress
                    if i % 100 == 0:  # Report every 100 rows
                        self.context.report_progress(i, total_estimated, f"Loading row {i}")
                    
                    # Process row
                    try:
                        nested_data = self.field_mapper.convert_row_to_nested(row_data)
                        
                        # Apply type conversion if enabled
                        if self.csv_options.detect_types:
                            nested_data = self._convert_data_types(nested_data)
                        
                        data_object = self._create_data_object(nested_data, i)
                        data_objects.append(data_object)
                    
                    except Exception as e:
                        if self.csv_options.type_conversion_errors == "error":
                            raise DataSourceError(f"Error processing row {i}: {str(e)}")
                        elif self.csv_options.type_conversion_errors == "warn":
                            self.context.log_warning(f"Error processing row {i}: {str(e)}")
            
            # Create collection
            collection = self._create_data_collection(data_objects)
            
            # Add quality analysis
            quality_analysis = self.validator.analyze_data_quality([obj.data for obj in data_objects])
            collection.metadata['quality_analysis'] = quality_analysis
            
            load_duration = (datetime.now() - start_time).total_seconds()
            collection.metadata['load_duration'] = load_duration
            
            self.context.log_info(f"Loaded {len(data_objects)} records in {load_duration:.2f}s")
            
            return collection
        
        except Exception as e:
            raise DataSourceError(f"Failed to load CSV data: {str(e)}")
    
    def stream_data(self, chunk_size: Optional[int] = None) -> Iterator[List[DataObject]]:
        """Stream CSV data in chunks for memory efficiency."""
        chunk_size = chunk_size or self.context.batch_size
        
        try:
            with self._open_csv_source() as csv_file:
                reader = self._create_csv_reader(csv_file)
                
                chunk = []
                for i, row_data in enumerate(reader):
                    # Check record limit
                    if self.context.max_records and i >= self.context.max_records:
                        break
                    
                    # Process row
                    nested_data = self.field_mapper.convert_row_to_nested(row_data)
                    
                    if self.csv_options.detect_types:
                        nested_data = self._convert_data_types(nested_data)
                    
                    data_object = self._create_data_object(nested_data, i)
                    chunk.append(data_object)
                    
                    # Yield chunk when full
                    if len(chunk) >= chunk_size:
                        yield chunk
                        chunk = []
                
                # Yield remaining items
                if chunk:
                    yield chunk
        
        except Exception as e:
            raise DataSourceError(f"Failed to stream CSV data: {str(e)}")
    
    def _open_csv_source(self):
        """Open CSV source (file or URL) and return file-like object."""
        if self.source.startswith(('http://', 'https://')):
            # Download from URL
            response = requests.get(self.source, timeout=self.context.timeout, stream=True)
            response.raise_for_status()
            
            # Detect encoding if not specified
            if self.context.encoding == 'utf-8' and CHARDET_AVAILABLE:
                content_sample = response.content[:8192]
                detected = chardet.detect(content_sample)
                if detected['encoding'] and detected['confidence'] > 0.7:
                    encoding = detected['encoding']
                else:
                    encoding = 'utf-8'
            else:
                encoding = self.context.encoding
            
            # Return text stream
            return io.StringIO(response.content.decode(encoding))
        
        else:
            # Open local file
            return open(self.source, 'r', encoding=self.context.encoding, newline='')
    
    def _create_csv_reader(self, csv_file):
        """Create appropriate CSV reader."""
        # Set field size limit
        csv.field_size_limit(self.csv_options.max_field_size)
        
        if self.csv_options.header_row:
            reader = csv.DictReader(
                csv_file,
                delimiter=self.csv_options.delimiter,
                quotechar=self.csv_options.quotechar,
                escapechar=self.csv_options.escapechar
            )
            
            # Store headers for metadata
            if hasattr(reader, 'fieldnames') and reader.fieldnames:
                self._headers = reader.fieldnames
        
        else:
            # No headers - create numbered field names
            raw_reader = csv.reader(
                csv_file,
                delimiter=self.csv_options.delimiter,
                quotechar=self.csv_options.quotechar,
                escapechar=self.csv_options.escapechar
            )
            
            # Convert to DictReader with auto-generated field names
            first_row = next(raw_reader, None)
            if first_row:
                fieldnames = [f"field_{i+1}" for i in range(len(first_row))]
                csv_file.seek(0)
                reader = csv.DictReader(
                    csv_file,
                    fieldnames=fieldnames,
                    delimiter=self.csv_options.delimiter,
                    quotechar=self.csv_options.quotechar,
                    escapechar=self.csv_options.escapechar
                )
                self._headers = fieldnames
            else:
                raise DataSourceError("CSV file appears to be empty")
        
        return reader
    
    def _convert_data_types(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert string values to appropriate data types."""
        converted = {}
        
        for key, value in data.items():
            if isinstance(value, dict):
                # Recursively convert nested dictionaries
                converted[key] = self._convert_data_types(value)
            else:
                converted[key] = self._convert_single_value(value)
        
        return converted
    
    def _convert_single_value(self, value: str) -> Any:
        """Convert a single string value to appropriate type."""
        if not isinstance(value, str):
            return value
        
        value = value.strip()
        
        # Check for null values
        if value in self.csv_options.null_values:
            return None
        
        if not value:
            return None
        
        # Try integer conversion
        try:
            if '.' not in value and 'e' not in value.lower():
                return int(value)
        except ValueError:
            pass
        
        # Try float conversion
        try:
            return float(value)
        except ValueError:
            pass
        
        # Try boolean conversion
        lower_value = value.lower()
        if lower_value in ('true', 'yes', '1', 'on'):
            return True
        elif lower_value in ('false', 'no', '0', 'off'):
            return False
        
        # Return as string
        return value
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get CSV-specific metadata."""
        metadata = super().get_metadata()
        metadata.update({
            'csv_options': {
                'delimiter': self.csv_options.delimiter,
                'header_row': self.csv_options.header_row,
                'detect_types': self.csv_options.detect_types
            },
            'headers': self._headers,
            'estimated_rows': self._estimated_rows
        })
        return metadata


# Register CSV loader
from .data_loader_base import loader_registry
loader_registry.register_loader('csv', CSVLoader, ['.csv', '.tsv', '.txt'])

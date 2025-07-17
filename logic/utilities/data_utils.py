"""
Data processing and transformation utilities for DocGenius.

This module provides utilities for data manipulation, transformation,
and processing operations common across different modules.
"""

import json
import csv
import re
from typing import Any, Dict, List, Optional, Union, Callable, Iterator, Tuple
from pathlib import Path
from datetime import datetime, date
import logging
from collections import defaultdict, OrderedDict
import copy


class DataTransformer:
    """Data transformation and manipulation utilities."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def flatten_nested_dict(self, data: Dict[str, Any], 
                           separator: str = ".", 
                           prefix: str = "") -> Dict[str, Any]:
        """
        Flatten a nested dictionary into a single-level dictionary.
        
        Args:
            data: Dictionary to flatten
            separator: Separator for nested keys
            prefix: Prefix for all keys
            
        Returns:
            Flattened dictionary
        """
        result = {}
        
        for key, value in data.items():
            new_key = f"{prefix}{separator}{key}" if prefix else key
            
            if isinstance(value, dict):
                result.update(self.flatten_nested_dict(value, separator, new_key))
            elif isinstance(value, list):
                # Handle lists by converting to indexed keys
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        result.update(self.flatten_nested_dict(item, separator, f"{new_key}[{i}]"))
                    else:
                        result[f"{new_key}[{i}]"] = item
            else:
                result[new_key] = value
        
        return result
    
    def unflatten_dict(self, data: Dict[str, Any], separator: str = ".") -> Dict[str, Any]:
        """
        Convert a flattened dictionary back to nested structure.
        
        Args:
            data: Flattened dictionary
            separator: Separator used in flattened keys
            
        Returns:
            Nested dictionary
        """
        result = {}
        
        for key, value in data.items():
            keys = key.split(separator)
            current = result
            
            for k in keys[:-1]:
                # Handle array indices
                if '[' in k and ']' in k:
                    base_key, index_part = k.split('[', 1)
                    index = int(index_part.rstrip(']'))
                    
                    if base_key not in current:
                        current[base_key] = []
                    
                    # Extend list if necessary
                    while len(current[base_key]) <= index:
                        current[base_key].append({})
                    
                    current = current[base_key][index]
                else:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
            
            # Set the final value
            final_key = keys[-1]
            if '[' in final_key and ']' in final_key:
                base_key, index_part = final_key.split('[', 1)
                index = int(index_part.rstrip(']'))
                
                if base_key not in current:
                    current[base_key] = []
                
                while len(current[base_key]) <= index:
                    current[base_key].append(None)
                
                current[base_key][index] = value
            else:
                current[final_key] = value
        
        return result
    
    def normalize_field_names(self, data: Dict[str, Any], 
                             style: str = "snake_case") -> Dict[str, Any]:
        """
        Normalize field names to a consistent style.
        
        Args:
            data: Dictionary with fields to normalize
            style: Naming style ('snake_case', 'camelCase', 'PascalCase', 'kebab-case')
            
        Returns:
            Dictionary with normalized field names
        """
        def to_snake_case(name: str) -> str:
            # Handle camelCase and PascalCase
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
            # Handle consecutive capitals
            s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
            # Replace spaces and hyphens with underscores
            s3 = re.sub(r'[-\s]+', '_', s2)
            return s3.lower()
        
        def to_camel_case(name: str) -> str:
            # Convert to snake_case first, then to camelCase
            snake = to_snake_case(name)
            components = snake.split('_')
            return components[0] + ''.join(word.capitalize() for word in components[1:])
        
        def to_pascal_case(name: str) -> str:
            # Convert to snake_case first, then to PascalCase
            snake = to_snake_case(name)
            components = snake.split('_')
            return ''.join(word.capitalize() for word in components)
        
        def to_kebab_case(name: str) -> str:
            # Convert to snake_case first, then replace underscores with hyphens
            return to_snake_case(name).replace('_', '-')
        
        transform_functions = {
            'snake_case': to_snake_case,
            'camelCase': to_camel_case,
            'PascalCase': to_pascal_case,
            'kebab-case': to_kebab_case
        }
        
        if style not in transform_functions:
            self.logger.warning(f"Unknown naming style: {style}. Using snake_case.")
            style = 'snake_case'
        
        transform_func = transform_functions[style]
        result = {}
        
        for key, value in data.items():
            new_key = transform_func(key)
            
            # Recursively normalize nested dictionaries
            if isinstance(value, dict):
                result[new_key] = self.normalize_field_names(value, style)
            elif isinstance(value, list):
                result[new_key] = [
                    self.normalize_field_names(item, style) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[new_key] = value
        
        return result
    
    def extract_fields(self, data: Dict[str, Any], 
                      field_paths: List[str], 
                      default_value: Any = None) -> Dict[str, Any]:
        """
        Extract specific fields from nested data using dot notation paths.
        
        Args:
            data: Source data dictionary
            field_paths: List of field paths (e.g., ['profile.name', 'contact.email'])
            default_value: Default value for missing fields
            
        Returns:
            Dictionary with extracted fields
        """
        result = {}
        
        for path in field_paths:
            value = self.get_nested_value(data, path)
            if value is not None:
                result[path] = value
            elif default_value is not None:
                result[path] = default_value
        
        return result
    
    def get_nested_value(self, data: Dict[str, Any], path: str, 
                        separator: str = ".") -> Any:
        """
        Get value from nested dictionary using dot notation path.
        
        Args:
            data: Source data dictionary
            path: Dot notation path (e.g., 'profile.contact.email')
            separator: Path separator
            
        Returns:
            Value at the specified path, or None if not found
        """
        try:
            keys = path.split(separator)
            current = data
            
            for key in keys:
                # Handle array indices
                if '[' in key and ']' in key:
                    base_key, index_part = key.split('[', 1)
                    index = int(index_part.rstrip(']'))
                    
                    if base_key in current and isinstance(current[base_key], list):
                        if 0 <= index < len(current[base_key]):
                            current = current[base_key][index]
                        else:
                            return None
                    else:
                        return None
                else:
                    if isinstance(current, dict) and key in current:
                        current = current[key]
                    else:
                        return None
            
            return current
        
        except (KeyError, IndexError, ValueError, TypeError):
            return None
    
    def set_nested_value(self, data: Dict[str, Any], path: str, value: Any, 
                        separator: str = ".") -> None:
        """
        Set value in nested dictionary using dot notation path.
        
        Args:
            data: Target data dictionary
            path: Dot notation path
            value: Value to set
            separator: Path separator
        """
        keys = path.split(separator)
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value


class DataValidator:
    """Data validation and quality checking utilities."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_data_structure(self, data: List[Dict[str, Any]], 
                               required_fields: Optional[List[str]] = None,
                               expected_types: Optional[Dict[str, type]] = None) -> Dict[str, Any]:
        """
        Validate data structure and quality.
        
        Args:
            data: List of data records
            required_fields: List of required field names
            expected_types: Dictionary mapping field names to expected types
            
        Returns:
            Validation report
        """
        report = {
            'total_records': len(data),
            'valid_records': 0,
            'errors': [],
            'warnings': [],
            'field_statistics': {},
            'unique_fields': set()
        }
        
        if not data:
            report['errors'].append("No data to validate")
            return report
        
        # Collect all unique fields
        for record in data:
            if isinstance(record, dict):
                report['unique_fields'].update(record.keys())
        
        # Initialize field statistics
        for field in report['unique_fields']:
            report['field_statistics'][field] = {
                'present_count': 0,
                'null_count': 0,
                'empty_count': 0,
                'unique_values': set(),
                'data_types': set()
            }
        
        # Validate each record
        for i, record in enumerate(data):
            record_errors = []
            
            if not isinstance(record, dict):
                record_errors.append(f"Record {i}: Not a dictionary")
                continue
            
            # Check required fields
            if required_fields:
                for field in required_fields:
                    if field not in record:
                        record_errors.append(f"Record {i}: Missing required field '{field}'")
                    elif record[field] is None:
                        record_errors.append(f"Record {i}: Required field '{field}' is null")
            
            # Check field types
            if expected_types:
                for field, expected_type in expected_types.items():
                    if field in record and record[field] is not None:
                        if not isinstance(record[field], expected_type):
                            record_errors.append(
                                f"Record {i}: Field '{field}' should be {expected_type.__name__}, "
                                f"got {type(record[field]).__name__}"
                            )
            
            # Update field statistics
            for field in report['unique_fields']:
                stats = report['field_statistics'][field]
                
                if field in record:
                    stats['present_count'] += 1
                    value = record[field]
                    
                    if value is None:
                        stats['null_count'] += 1
                    elif isinstance(value, str) and not value.strip():
                        stats['empty_count'] += 1
                    else:
                        stats['unique_values'].add(str(value))
                        stats['data_types'].add(type(value).__name__)
            
            if not record_errors:
                report['valid_records'] += 1
            else:
                report['errors'].extend(record_errors)
        
        # Convert sets to lists for JSON serialization
        for field_stats in report['field_statistics'].values():
            field_stats['unique_values'] = list(field_stats['unique_values'])
            field_stats['data_types'] = list(field_stats['data_types'])
        
        report['unique_fields'] = list(report['unique_fields'])
        
        # Generate warnings
        total_records = report['total_records']
        for field, stats in report['field_statistics'].items():
            missing_rate = (total_records - stats['present_count']) / total_records
            if missing_rate > 0.1:  # More than 10% missing
                report['warnings'].append(
                    f"Field '{field}' is missing in {missing_rate:.1%} of records"
                )
        
        return report
    
    def detect_data_types(self, data: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Detect the most likely data type for each field.
        
        Args:
            data: List of data records
            
        Returns:
            Dictionary mapping field names to detected types
        """
        field_types = defaultdict(lambda: defaultdict(int))
        
        for record in data:
            if isinstance(record, dict):
                for field, value in record.items():
                    if value is not None:
                        python_type = type(value).__name__
                        field_types[field][python_type] += 1
        
        # Determine most common type for each field
        detected_types = {}
        for field, type_counts in field_types.items():
            if type_counts:
                most_common_type = max(type_counts, key=type_counts.get)
                detected_types[field] = most_common_type
        
        return detected_types


class DataAggregator:
    """Data aggregation and summary utilities."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def group_by_field(self, data: List[Dict[str, Any]], 
                      field: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group data records by a specific field value.
        
        Args:
            data: List of data records
            field: Field name to group by
            
        Returns:
            Dictionary mapping field values to lists of records
        """
        groups = defaultdict(list)
        
        for record in data:
            if isinstance(record, dict) and field in record:
                key = str(record[field]) if record[field] is not None else "null"
                groups[key].append(record)
        
        return dict(groups)
    
    def aggregate_numeric_fields(self, data: List[Dict[str, Any]], 
                                numeric_fields: Optional[List[str]] = None) -> Dict[str, Dict[str, float]]:
        """
        Calculate aggregations for numeric fields.
        
        Args:
            data: List of data records
            numeric_fields: List of numeric field names (auto-detected if None)
            
        Returns:
            Dictionary with aggregation statistics
        """
        if numeric_fields is None:
            # Auto-detect numeric fields
            numeric_fields = []
            for record in data[:10]:  # Sample first 10 records
                if isinstance(record, dict):
                    for field, value in record.items():
                        if isinstance(value, (int, float)) and field not in numeric_fields:
                            numeric_fields.append(field)
        
        aggregations = {}
        
        for field in numeric_fields:
            values = []
            for record in data:
                if isinstance(record, dict) and field in record:
                    value = record[field]
                    if isinstance(value, (int, float)):
                        values.append(value)
            
            if values:
                aggregations[field] = {
                    'count': len(values),
                    'sum': sum(values),
                    'mean': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'median': sorted(values)[len(values) // 2]
                }
        
        return aggregations
    
    def count_unique_values(self, data: List[Dict[str, Any]], 
                           field: str) -> Dict[str, int]:
        """
        Count unique values for a specific field.
        
        Args:
            data: List of data records
            field: Field name to analyze
            
        Returns:
            Dictionary mapping unique values to their counts
        """
        value_counts = defaultdict(int)
        
        for record in data:
            if isinstance(record, dict) and field in record:
                value = record[field]
                key = str(value) if value is not None else "null"
                value_counts[key] += 1
        
        return dict(value_counts)


class DataConverter:
    """Data format conversion utilities."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def to_csv_rows(self, data: List[Dict[str, Any]], 
                   field_order: Optional[List[str]] = None) -> Tuple[List[str], List[List[str]]]:
        """
        Convert data to CSV format (headers and rows).
        
        Args:
            data: List of data records
            field_order: Optional field ordering
            
        Returns:
            Tuple of (headers, rows)
        """
        if not data:
            return [], []
        
        # Collect all unique fields
        all_fields = set()
        for record in data:
            if isinstance(record, dict):
                all_fields.update(record.keys())
        
        # Use provided order or alphabetical
        if field_order:
            headers = [f for f in field_order if f in all_fields]
            # Add any remaining fields
            headers.extend(sorted(f for f in all_fields if f not in headers))
        else:
            headers = sorted(all_fields)
        
        # Convert records to rows
        rows = []
        for record in data:
            if isinstance(record, dict):
                row = []
                for field in headers:
                    value = record.get(field, "")
                    # Convert complex types to strings
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value)
                    elif value is None:
                        value = ""
                    else:
                        value = str(value)
                    row.append(value)
                rows.append(row)
        
        return headers, rows
    
    def from_csv_rows(self, headers: List[str], 
                     rows: List[List[str]]) -> List[Dict[str, Any]]:
        """
        Convert CSV format back to data records.
        
        Args:
            headers: List of column headers
            rows: List of data rows
            
        Returns:
            List of data records
        """
        data = []
        
        for row in rows:
            record = {}
            for i, header in enumerate(headers):
                value = row[i] if i < len(row) else ""
                
                # Try to parse JSON for complex types
                if value.startswith('{') or value.startswith('['):
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        pass  # Keep as string
                
                record[header] = value
            
            data.append(record)
        
        return data
    
    def apply_data_transformations(self, data: List[Dict[str, Any]], 
                                  transformations: List[Callable]) -> List[Dict[str, Any]]:
        """
        Apply a series of transformations to data.
        
        Args:
            data: List of data records
            transformations: List of transformation functions
            
        Returns:
            Transformed data
        """
        result = copy.deepcopy(data)
        
        for transform_func in transformations:
            try:
                result = transform_func(result)
            except Exception as e:
                self.logger.error(f"Transformation failed: {str(e)}")
                break
        
        return result


# Convenience functions for common operations
def flatten_data(data: Dict[str, Any], separator: str = ".") -> Dict[str, Any]:
    """Convenience function to flatten nested data."""
    transformer = DataTransformer()
    return transformer.flatten_nested_dict(data, separator)


def normalize_field_names(data: Dict[str, Any], style: str = "snake_case") -> Dict[str, Any]:
    """Convenience function to normalize field names."""
    transformer = DataTransformer()
    return transformer.normalize_field_names(data, style)


def validate_data_quality(data: List[Dict[str, Any]], 
                         required_fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """Convenience function for data validation."""
    validator = DataValidator()
    return validator.validate_data_structure(data, required_fields)


def group_data_by_field(data: List[Dict[str, Any]], field: str) -> Dict[str, List[Dict[str, Any]]]:
    """Convenience function to group data by field."""
    aggregator = DataAggregator()
    return aggregator.group_by_field(data, field)


def convert_to_csv(data: List[Dict[str, Any]]) -> Tuple[List[str], List[List[str]]]:
    """Convenience function to convert data to CSV format."""
    converter = DataConverter()
    return converter.to_csv_rows(data)

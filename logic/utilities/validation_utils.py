"""
Validation utilities for data verification and error checking.

This module provides comprehensive validation functions for different
data types, file formats, and business logic validation.
"""

import re
import json
from typing import Any, Dict, List, Optional, Union, Callable, Pattern
from pathlib import Path
from datetime import datetime
import logging

from ..models.base_models import ValidationResult, ValidationRule


class DataTypeValidator:
    """Validators for different data types."""
    
    @staticmethod
    def is_email(value: str) -> bool:
        """Validate email address format."""
        if not isinstance(value, str):
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, value))
    
    @staticmethod
    def is_phone(value: str, pattern: Optional[str] = None) -> bool:
        """
        Validate phone number format.
        
        Args:
            value: Phone number to validate
            pattern: Custom regex pattern (optional)
        """
        if not isinstance(value, str):
            return False
        
        if pattern:
            return bool(re.match(pattern, value))
        
        # Default: allow various phone formats
        clean_value = re.sub(r'[^\d]', '', value)
        return len(clean_value) >= 10
    
    @staticmethod
    def is_url(value: str) -> bool:
        """Validate URL format."""
        if not isinstance(value, str):
            return False
        
        pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$'
        return bool(re.match(pattern, value))
    
    @staticmethod
    def is_date(value: str, format_string: str = "%Y-%m-%d") -> bool:
        """
        Validate date format.
        
        Args:
            value: Date string to validate
            format_string: Expected date format
        """
        if not isinstance(value, str):
            return False
        
        try:
            datetime.strptime(value, format_string)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def is_numeric(value: Any, allow_negative: bool = True, allow_decimal: bool = True) -> bool:
        """
        Validate numeric value.
        
        Args:
            value: Value to validate
            allow_negative: Whether negative numbers are allowed
            allow_decimal: Whether decimal numbers are allowed
        """
        if isinstance(value, (int, float)):
            if not allow_negative and value < 0:
                return False
            if not allow_decimal and isinstance(value, float) and value != int(value):
                return False
            return True
        
        if isinstance(value, str):
            try:
                num_value = float(value) if '.' in value else int(value)
                if not allow_negative and num_value < 0:
                    return False
                if not allow_decimal and '.' in value:
                    return False
                return True
            except ValueError:
                return False
        
        return False
    
    @staticmethod
    def is_in_range(value: Union[int, float], min_value: Optional[Union[int, float]] = None, 
                   max_value: Optional[Union[int, float]] = None) -> bool:
        """
        Validate value is within range.
        
        Args:
            value: Value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
        """
        if not isinstance(value, (int, float)):
            return False
        
        if min_value is not None and value < min_value:
            return False
        
        if max_value is not None and value > max_value:
            return False
        
        return True
    
    @staticmethod
    def matches_pattern(value: str, pattern: Union[str, Pattern]) -> bool:
        """
        Validate value matches regex pattern.
        
        Args:
            value: Value to validate
            pattern: Regex pattern to match
        """
        if not isinstance(value, str):
            return False
        
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        
        return bool(pattern.match(value))


class FileValidator:
    """Validators for file and file format validation."""
    
    @staticmethod
    def file_exists(file_path: Union[str, Path]) -> bool:
        """Validate file exists."""
        try:
            return Path(file_path).exists()
        except Exception:
            return False
    
    @staticmethod
    def is_readable(file_path: Union[str, Path]) -> bool:
        """Validate file is readable."""
        try:
            path = Path(file_path)
            return path.exists() and path.is_file() and path.stat().st_size >= 0
        except Exception:
            return False
    
    @staticmethod
    def has_extension(file_path: Union[str, Path], extensions: Union[str, List[str]]) -> bool:
        """
        Validate file has one of the specified extensions.
        
        Args:
            file_path: File path to validate
            extensions: Allowed extension(s)
        """
        try:
            path = Path(file_path)
            if isinstance(extensions, str):
                extensions = [extensions]
            
            # Normalize extensions (ensure they start with .)
            normalized_extensions = []
            for ext in extensions:
                if not ext.startswith('.'):
                    ext = '.' + ext
                normalized_extensions.append(ext.lower())
            
            return path.suffix.lower() in normalized_extensions
        except Exception:
            return False
    
    @staticmethod
    def validate_csv_format(file_path: Union[str, Path], delimiter: str = ',') -> ValidationResult:
        """
        Validate CSV file format.
        
        Args:
            file_path: Path to CSV file
            delimiter: Expected delimiter
            
        Returns:
            ValidationResult with validation details
        """
        try:
            import csv
            
            path = Path(file_path)
            if not path.exists():
                return ValidationResult(
                    is_valid=False,
                    errors=[f"File not found: {path}"]
                )
            
            errors = []
            warnings = []
            
            with open(path, 'r', encoding='utf-8') as file:
                # Try to detect dialect
                try:
                    sample = file.read(1024)
                    file.seek(0)
                    sniffer = csv.Sniffer()
                    dialect = sniffer.sniff(sample)
                    
                    if dialect.delimiter != delimiter:
                        warnings.append(f"Detected delimiter '{dialect.delimiter}' differs from expected '{delimiter}'")
                except Exception:
                    warnings.append("Could not detect CSV dialect")
                
                # Read first few rows to validate structure
                reader = csv.reader(file, delimiter=delimiter)
                rows = []
                for i, row in enumerate(reader):
                    rows.append(row)
                    if i >= 10:  # Check first 10 rows
                        break
                
                if not rows:
                    errors.append("File appears to be empty")
                else:
                    # Check for consistent column count
                    first_row_length = len(rows[0])
                    for i, row in enumerate(rows[1:], 1):
                        if len(row) != first_row_length:
                            warnings.append(f"Row {i + 1} has {len(row)} columns, expected {first_row_length}")
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings
            )
        
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Failed to validate CSV: {str(e)}"]
            )
    
    @staticmethod
    def validate_json_format(file_path: Union[str, Path]) -> ValidationResult:
        """
        Validate JSON file format.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            ValidationResult with validation details
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return ValidationResult(
                    is_valid=False,
                    errors=[f"File not found: {path}"]
                )
            
            with open(path, 'r', encoding='utf-8') as file:
                json.load(file)
            
            return ValidationResult(is_valid=True)
        
        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Invalid JSON format: {str(e)}"]
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Failed to validate JSON: {str(e)}"]
            )


class BusinessLogicValidator:
    """Validators for business logic and data integrity."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> ValidationResult:
        """
        Validate that all required fields are present and not empty.
        
        Args:
            data: Data dictionary to validate
            required_fields: List of required field names
            
        Returns:
            ValidationResult with validation details
        """
        errors = []
        
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
            elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
                errors.append(f"Required field is empty: {field}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_field_types(self, data: Dict[str, Any], field_types: Dict[str, type]) -> ValidationResult:
        """
        Validate field data types.
        
        Args:
            data: Data dictionary to validate
            field_types: Dictionary mapping field names to expected types
            
        Returns:
            ValidationResult with validation details
        """
        errors = []
        
        for field, expected_type in field_types.items():
            if field in data and data[field] is not None:
                if not isinstance(data[field], expected_type):
                    errors.append(f"Field '{field}' should be {expected_type.__name__}, got {type(data[field]).__name__}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_unique_values(self, data_list: List[Dict[str, Any]], field: str) -> ValidationResult:
        """
        Validate that values in a field are unique across records.
        
        Args:
            data_list: List of data dictionaries
            field: Field name to check for uniqueness
            
        Returns:
            ValidationResult with validation details
        """
        errors = []
        seen_values = set()
        duplicates = set()
        
        for i, record in enumerate(data_list):
            if field in record and record[field] is not None:
                value = record[field]
                if value in seen_values:
                    duplicates.add(value)
                else:
                    seen_values.add(value)
        
        if duplicates:
            errors.append(f"Duplicate values found in field '{field}': {', '.join(map(str, duplicates))}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
    
    def validate_relationships(self, data_list: List[Dict[str, Any]], 
                             parent_field: str, child_field: str) -> ValidationResult:
        """
        Validate referential integrity between fields.
        
        Args:
            data_list: List of data dictionaries
            parent_field: Field containing parent values
            child_field: Field containing child values that should reference parent
            
        Returns:
            ValidationResult with validation details
        """
        errors = []
        
        # Collect all parent values
        parent_values = set()
        for record in data_list:
            if parent_field in record and record[parent_field] is not None:
                parent_values.add(record[parent_field])
        
        # Check child references
        orphaned_children = set()
        for record in data_list:
            if child_field in record and record[child_field] is not None:
                child_value = record[child_field]
                if child_value not in parent_values:
                    orphaned_children.add(child_value)
        
        if orphaned_children:
            errors.append(f"Orphaned references in '{child_field}': {', '.join(map(str, orphaned_children))}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )


class ValidationEngine:
    """Main validation engine that coordinates different validators."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_validator = DataTypeValidator()
        self.file_validator = FileValidator()
        self.business_validator = BusinessLogicValidator()
        self.custom_rules: List[ValidationRule] = []
    
    def add_custom_rule(self, rule: ValidationRule):
        """Add a custom validation rule."""
        self.custom_rules.append(rule)
    
    def validate_data_object(self, data: Dict[str, Any], rules: List[ValidationRule]) -> ValidationResult:
        """
        Validate a data object against a list of rules.
        
        Args:
            data: Data to validate
            rules: List of validation rules to apply
            
        Returns:
            Combined ValidationResult
        """
        all_errors = []
        all_warnings = []
        
        for rule in rules:
            try:
                result = rule.validate(data)
                if not result.is_valid:
                    all_errors.extend(result.errors)
                if result.warnings:
                    all_warnings.extend(result.warnings)
            except Exception as e:
                self.logger.error(f"Validation rule failed: {str(e)}")
                all_errors.append(f"Validation rule error: {str(e)}")
        
        return ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings
        )
    
    def validate_file(self, file_path: Union[str, Path]) -> ValidationResult:
        """
        Validate a file based on its extension.
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            ValidationResult with validation details
        """
        try:
            path = Path(file_path)
            
            if not self.file_validator.file_exists(path):
                return ValidationResult(
                    is_valid=False,
                    errors=[f"File not found: {path}"]
                )
            
            if not self.file_validator.is_readable(path):
                return ValidationResult(
                    is_valid=False,
                    errors=[f"File is not readable: {path}"]
                )
            
            # Validate based on file extension
            extension = path.suffix.lower()
            
            if extension == '.csv':
                return self.file_validator.validate_csv_format(path)
            elif extension == '.json':
                return self.file_validator.validate_json_format(path)
            else:
                return ValidationResult(
                    is_valid=True,
                    warnings=[f"No specific validation available for {extension} files"]
                )
        
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"File validation failed: {str(e)}"]
            )
    
    def create_field_validator(self, field_name: str, validator_func: Callable, 
                             error_message: str) -> ValidationRule:
        """
        Create a validation rule for a specific field.
        
        Args:
            field_name: Name of field to validate
            validator_func: Function that validates the field value
            error_message: Error message if validation fails
            
        Returns:
            ValidationRule for the field
        """
        def validate_field(data: Dict[str, Any]) -> ValidationResult:
            if field_name not in data:
                return ValidationResult(is_valid=True)  # Field not present is OK
            
            value = data[field_name]
            if value is None:
                return ValidationResult(is_valid=True)  # None value is OK
            
            try:
                is_valid = validator_func(value)
                if is_valid:
                    return ValidationResult(is_valid=True)
                else:
                    return ValidationResult(
                        is_valid=False,
                        errors=[f"{field_name}: {error_message}"]
                    )
            except Exception as e:
                return ValidationResult(
                    is_valid=False,
                    errors=[f"{field_name}: Validation error - {str(e)}"]
                )
        
        return ValidationRule(
            name=f"validate_{field_name}",
            description=f"Validate {field_name} field",
            validate_func=validate_field
        )


# Convenience functions for common validations
def validate_email_field(field_name: str) -> ValidationRule:
    """Create a validation rule for email fields."""
    engine = ValidationEngine()
    return engine.create_field_validator(
        field_name,
        DataTypeValidator.is_email,
        "Invalid email address format"
    )


def validate_phone_field(field_name: str, pattern: Optional[str] = None) -> ValidationRule:
    """Create a validation rule for phone fields."""
    engine = ValidationEngine()
    validator_func = lambda value: DataTypeValidator.is_phone(value, pattern)
    return engine.create_field_validator(
        field_name,
        validator_func,
        "Invalid phone number format"
    )


def validate_numeric_field(field_name: str, allow_negative: bool = True, 
                          allow_decimal: bool = True) -> ValidationRule:
    """Create a validation rule for numeric fields."""
    engine = ValidationEngine()
    validator_func = lambda value: DataTypeValidator.is_numeric(value, allow_negative, allow_decimal)
    return engine.create_field_validator(
        field_name,
        validator_func,
        "Invalid numeric value"
    )


def validate_required_field(field_name: str) -> ValidationRule:
    """Create a validation rule for required fields."""
    def validate_required(data: Dict[str, Any]) -> ValidationResult:
        if field_name not in data or data[field_name] is None:
            return ValidationResult(
                is_valid=False,
                errors=[f"Required field missing: {field_name}"]
            )
        
        # Check for empty strings
        if isinstance(data[field_name], str) and not data[field_name].strip():
            return ValidationResult(
                is_valid=False,
                errors=[f"Required field is empty: {field_name}"]
            )
        
        return ValidationResult(is_valid=True)
    
    return ValidationRule(
        name=f"required_{field_name}",
        description=f"Validate {field_name} is required",
        validate_func=validate_required
    )

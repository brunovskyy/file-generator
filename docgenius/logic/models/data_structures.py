"""
Data structures and models for normalized content representation.

This module defines the core data models used throughout DocGenius
for representing loaded data in a standardized format.
"""

from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass, field
from pathlib import Path
import json
from datetime import datetime

from .base_models import BaseModel, ValidationResult, FieldValidator, ModelValidator


@dataclass
class DataObject(BaseModel):
    """
    Single data record representation with metadata and validation.
    
    Represents a single data object loaded from any source (CSV row,
    JSON object, API response item, etc.) in a normalized format.
    """
    
    data: Dict[str, Any]
    source_info: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize metadata with defaults."""
        if 'created_at' not in self.metadata:
            self.metadata['created_at'] = datetime.now().isoformat()
        if 'object_id' not in self.metadata:
            self.metadata['object_id'] = id(self)
    
    def get_field(self, field_path: str, default: Any = None) -> Any:
        """
        Get a field value using dot notation for nested access.
        
        Args:
            field_path: Field path like 'user.profile.name'
            default: Default value if field not found
            
        Returns:
            Field value or default
        """
        current = self.data
        for part in field_path.split('.'):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current
    
    def set_field(self, field_path: str, value: Any) -> None:
        """
        Set a field value using dot notation for nested access.
        
        Args:
            field_path: Field path like 'user.profile.name'
            value: Value to set
        """
        parts = field_path.split('.')
        current = self.data
        
        # Navigate to parent of target field
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set the final value
        current[parts[-1]] = value
    
    def flatten(self, separator: str = '_') -> Dict[str, Any]:
        """
        Flatten nested dictionary structure.
        
        Args:
            separator: Separator for flattened keys
            
        Returns:
            Flattened dictionary
        """
        def _flatten_dict(d: Dict[str, Any], prefix: str = '') -> Dict[str, Any]:
            result = {}
            for key, value in d.items():
                new_key = f"{prefix}{separator}{key}" if prefix else key
                
                if isinstance(value, dict):
                    result.update(_flatten_dict(value, new_key))
                else:
                    result[new_key] = value
            
            return result
        
        return _flatten_dict(self.data)
    
    def get_all_keys(self, prefix: str = '') -> Set[str]:
        """
        Get all available keys including nested ones.
        
        Args:
            prefix: Prefix for nested keys
            
        Returns:
            Set of all available key paths
        """
        keys = set()
        
        def _extract_keys(d: Dict[str, Any], current_prefix: str = ''):
            for key, value in d.items():
                full_key = f"{current_prefix}.{key}" if current_prefix else key
                keys.add(full_key)
                
                if isinstance(value, dict):
                    _extract_keys(value, full_key)
        
        _extract_keys(self.data, prefix)
        return keys
    
    def validate(self) -> ValidationResult:
        """Validate the data object."""
        result = ValidationResult(is_valid=True)
        
        if not isinstance(self.data, dict):
            result.add_error("Data must be a dictionary")
        
        if not self.data:
            result.add_warning("Data object is empty")
        
        return result


@dataclass
class DataCollection(BaseModel):
    """
    Collection of data objects with metadata and bulk operations.
    
    Represents a collection of DataObject instances loaded from
    a data source, with methods for bulk operations and analysis.
    """
    
    objects: List[DataObject] = field(default_factory=list)
    source_info: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize metadata with defaults."""
        if 'created_at' not in self.metadata:
            self.metadata['created_at'] = datetime.now().isoformat()
        if 'collection_id' not in self.metadata:
            self.metadata['collection_id'] = id(self)
        
        # Update count
        self.metadata['object_count'] = len(self.objects)
    
    def __len__(self) -> int:
        """Return the number of objects in the collection."""
        return len(self.objects)
    
    def __iter__(self):
        """Allow iteration over the objects."""
        return iter(self.objects)
    
    def __getitem__(self, index: int) -> DataObject:
        """Allow indexing into the collection."""
        return self.objects[index]
    
    def add_object(self, data_object: DataObject) -> None:
        """Add a data object to the collection."""
        self.objects.append(data_object)
        self.metadata['object_count'] = len(self.objects)
    
    def add_data(self, data: Dict[str, Any], source_info: Optional[Dict[str, Any]] = None) -> DataObject:
        """
        Add raw data as a new DataObject.
        
        Args:
            data: Raw data dictionary
            source_info: Optional source information
            
        Returns:
            Created DataObject
        """
        data_object = DataObject(
            data=data,
            source_info=source_info or {},
            metadata={}
        )
        self.add_object(data_object)
        return data_object
    
    def get_all_keys(self) -> Set[str]:
        """
        Get all unique keys across all objects in the collection.
        
        Returns:
            Set of all unique key paths
        """
        all_keys = set()
        for obj in self.objects:
            all_keys.update(obj.get_all_keys())
        return all_keys
    
    def get_common_keys(self, threshold: float = 1.0) -> Set[str]:
        """
        Get keys that appear in a certain percentage of objects.
        
        Args:
            threshold: Percentage threshold (0.0 to 1.0)
            
        Returns:
            Set of common key paths
        """
        if not self.objects:
            return set()
        
        key_counts = {}
        total_objects = len(self.objects)
        
        for obj in self.objects:
            for key in obj.get_all_keys():
                key_counts[key] = key_counts.get(key, 0) + 1
        
        min_count = int(total_objects * threshold)
        return {key for key, count in key_counts.items() if count >= min_count}
    
    def filter_objects(self, filter_func: callable) -> 'DataCollection':
        """
        Filter objects based on a predicate function.
        
        Args:
            filter_func: Function that takes DataObject and returns bool
            
        Returns:
            New DataCollection with filtered objects
        """
        filtered_objects = [obj for obj in self.objects if filter_func(obj)]
        
        return DataCollection(
            objects=filtered_objects,
            source_info=self.source_info.copy(),
            metadata={
                **self.metadata,
                'filtered_from': self.metadata.get('collection_id'),
                'filter_applied_at': datetime.now().isoformat(),
                'original_count': len(self.objects),
                'filtered_count': len(filtered_objects)
            }
        )
    
    def get_field_values(self, field_path: str) -> List[Any]:
        """
        Get all values for a specific field across all objects.
        
        Args:
            field_path: Field path using dot notation
            
        Returns:
            List of field values
        """
        return [obj.get_field(field_path) for obj in self.objects]
    
    def get_unique_values(self, field_path: str) -> Set[Any]:
        """
        Get unique values for a specific field across all objects.
        
        Args:
            field_path: Field path using dot notation
            
        Returns:
            Set of unique field values
        """
        values = self.get_field_values(field_path)
        return {v for v in values if v is not None}
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistical information about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        return {
            'object_count': len(self.objects),
            'unique_keys': len(self.get_all_keys()),
            'common_keys': len(self.get_common_keys(0.5)),  # Keys in 50%+ of objects
            'source_info': self.source_info,
            'created_at': self.metadata.get('created_at'),
            'memory_usage_mb': sum(
                len(str(obj.data)) for obj in self.objects
            ) / (1024 * 1024)  # Rough estimate
        }
    
    def validate(self) -> ValidationResult:
        """Validate the data collection."""
        result = ValidationResult(is_valid=True)
        
        if not isinstance(self.objects, list):
            result.add_error("Objects must be a list")
            return result
        
        if not self.objects:
            result.add_warning("Data collection is empty")
        
        # Validate each object
        invalid_objects = []
        for i, obj in enumerate(self.objects):
            obj_result = obj.validate()
            if not obj_result.is_valid:
                invalid_objects.append(i)
                for error in obj_result.errors:
                    result.add_error(f"Object {i}: {error}")
        
        if invalid_objects:
            result.add_error(f"Found {len(invalid_objects)} invalid objects: {invalid_objects}")
        
        return result


class FieldMapping:
    """
    Field name mapping and transformation utilities.
    
    Handles mapping between source field names and target field names,
    with support for transformations and aliases.
    """
    
    def __init__(self, mappings: Optional[Dict[str, str]] = None):
        """
        Initialize field mapping.
        
        Args:
            mappings: Dictionary of source_field -> target_field mappings
        """
        self.mappings = mappings or {}
        self.aliases = {}  # Additional aliases for fields
        self.transformations = {}  # Field transformation functions
    
    def add_mapping(self, source_field: str, target_field: str) -> None:
        """Add a field mapping."""
        self.mappings[source_field] = target_field
    
    def add_alias(self, field: str, alias: str) -> None:
        """Add an alias for a field."""
        self.aliases[alias] = field
    
    def add_transformation(self, field: str, transform_func: callable) -> None:
        """Add a transformation function for a field."""
        self.transformations[field] = transform_func
    
    def map_field_name(self, source_field: str) -> str:
        """
        Map a source field name to target field name.
        
        Args:
            source_field: Original field name
            
        Returns:
            Mapped field name
        """
        # Check direct mapping
        if source_field in self.mappings:
            return self.mappings[source_field]
        
        # Check aliases
        if source_field in self.aliases:
            return self.aliases[source_field]
        
        # Return original if no mapping found
        return source_field
    
    def transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply field mappings and transformations to data.
        
        Args:
            data: Original data dictionary
            
        Returns:
            Transformed data dictionary
        """
        transformed = {}
        
        for source_field, value in data.items():
            target_field = self.map_field_name(source_field)
            
            # Apply transformation if available
            if target_field in self.transformations:
                try:
                    value = self.transformations[target_field](value)
                except Exception as e:
                    # If transformation fails, use original value
                    pass
            
            transformed[target_field] = value
        
        return transformed


class DataNormalizer:
    """
    Data standardization and normalization utilities.
    
    Provides methods for cleaning, standardizing, and normalizing
    data objects for consistent processing.
    """
    
    def __init__(self):
        self.field_mapping = FieldMapping()
        self.type_converters = {}
        self.default_values = {}
    
    def add_type_converter(self, field: str, converter_func: callable) -> None:
        """Add a type converter for a specific field."""
        self.type_converters[field] = converter_func
    
    def set_default_value(self, field: str, default_value: Any) -> None:
        """Set a default value for a field."""
        self.default_values[field] = default_value
    
    def normalize_object(self, data_object: DataObject) -> DataObject:
        """
        Normalize a data object.
        
        Args:
            data_object: Original data object
            
        Returns:
            Normalized data object
        """
        # Apply field mappings
        normalized_data = self.field_mapping.transform_data(data_object.data)
        
        # Apply type conversions
        for field, converter in self.type_converters.items():
            if field in normalized_data:
                try:
                    normalized_data[field] = converter(normalized_data[field])
                except Exception:
                    # Keep original value if conversion fails
                    pass
        
        # Apply default values for missing fields
        for field, default_value in self.default_values.items():
            if field not in normalized_data:
                normalized_data[field] = default_value
        
        # Create new normalized object
        return DataObject(
            data=normalized_data,
            source_info=data_object.source_info.copy(),
            metadata={
                **data_object.metadata,
                'normalized_at': datetime.now().isoformat(),
                'original_keys': list(data_object.data.keys()),
                'normalized_keys': list(normalized_data.keys())
            }
        )
    
    def normalize_collection(self, collection: DataCollection) -> DataCollection:
        """
        Normalize all objects in a collection.
        
        Args:
            collection: Original data collection
            
        Returns:
            Normalized data collection
        """
        normalized_objects = [
            self.normalize_object(obj) for obj in collection.objects
        ]
        
        return DataCollection(
            objects=normalized_objects,
            source_info=collection.source_info.copy(),
            metadata={
                **collection.metadata,
                'normalized_at': datetime.now().isoformat(),
                'normalization_applied': True
            }
        )

"""
Abstract base loader class and common interfaces.

This module defines the base loader interface that all data source
loaders must implement, ensuring consistency across all data sources.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import logging

from ..models import DataObject, DataCollection, ValidationResult, BaseModel


@dataclass
class LoadResult:
    """
    Result container for data loading operations.
    
    Contains the loaded data, metadata, and any errors or warnings
    from the loading process.
    """
    
    success: bool
    data_collection: Optional[DataCollection] = None
    load_duration: Optional[float] = None
    records_loaded: int = 0
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize metadata with defaults."""
        if 'load_timestamp' not in self.metadata:
            self.metadata['load_timestamp'] = datetime.now().isoformat()
    
    @classmethod
    def success_result(
        cls,
        data_collection: DataCollection,
        load_duration: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'LoadResult':
        """Create a successful load result."""
        return cls(
            success=True,
            data_collection=data_collection,
            load_duration=load_duration,
            records_loaded=len(data_collection),
            metadata=metadata or {}
        )
    
    @classmethod
    def failure_result(
        cls,
        error_message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'LoadResult':
        """Create a failed load result."""
        return cls(
            success=False,
            error_message=error_message,
            metadata=metadata or {}
        )
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message to the result."""
        self.warnings.append(warning)


@dataclass
class LoadContext:
    """
    Shared context for data loading operations.
    
    Contains common settings and utilities used across
    multiple loading operations within a session.
    """
    
    encoding: str = "utf-8"
    batch_size: int = 1000
    max_records: Optional[int] = None
    timeout: int = 30
    progress_callback: Optional[callable] = None
    logger: Optional[logging.Logger] = None
    
    def __post_init__(self):
        """Initialize context with defaults."""
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
    
    def log_info(self, message: str) -> None:
        """Log an info message."""
        if self.logger:
            self.logger.info(message)
    
    def log_warning(self, message: str) -> None:
        """Log a warning message."""
        if self.logger:
            self.logger.warning(message)
    
    def log_error(self, message: str) -> None:
        """Log an error message."""
        if self.logger:
            self.logger.error(message)
    
    def report_progress(self, current: int, total: Optional[int] = None, message: str = "") -> None:
        """Report progress if callback is available."""
        if self.progress_callback:
            self.progress_callback(current, total, message)


class BaseLoader(ABC):
    """
    Abstract base class for all data source loaders.
    
    Defines the standard interface that all source-specific loaders
    must implement, ensuring consistency and interoperability.
    """
    
    def __init__(self, source: str, context: LoadContext, **kwargs):
        """
        Initialize the loader with source and context.
        
        Args:
            source: Data source identifier (file path, URL, etc.)
            context: Shared loading context
            **kwargs: Loader-specific options
        """
        self.source = source
        self.context = context
        self.options = kwargs
        self.source_type = self._get_source_type()
        self._metadata = {}
    
    @abstractmethod
    def _get_source_type(self) -> str:
        """Return the source type identifier."""
        pass
    
    @abstractmethod
    def validate_source(self) -> ValidationResult:
        """
        Validate data source accessibility and format.
        
        Returns:
            ValidationResult indicating if the source is valid and accessible
        """
        pass
    
    @abstractmethod
    def load_data(self) -> DataCollection:
        """
        Load and normalize data from source.
        
        Returns:
            DataCollection containing loaded data objects
        """
        pass
    
    @abstractmethod
    def estimate_size(self) -> Optional[int]:
        """
        Estimate number of records in source.
        
        Returns:
            Estimated record count, or None if unknown
        """
        pass
    
    def preview_data(self, limit: int = 5) -> List[DataObject]:
        """
        Preview first few records from source.
        
        Args:
            limit: Maximum number of records to preview
            
        Returns:
            List of preview DataObject instances
        """
        try:
            # Default implementation - load all and slice
            # Specific loaders should override for efficiency
            collection = self.load_data()
            return collection.objects[:limit]
        except Exception as e:
            self.context.log_error(f"Preview failed: {str(e)}")
            return []
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the data source.
        
        Returns:
            Dictionary containing source metadata
        """
        base_metadata = {
            'source': self.source,
            'source_type': self.source_type,
            'loader_class': self.__class__.__name__,
            'options': self.options
        }
        base_metadata.update(self._metadata)
        return base_metadata
    
    def stream_data(self, chunk_size: Optional[int] = None) -> Iterator[List[DataObject]]:
        """
        Stream data in chunks for memory-efficient processing.
        
        Args:
            chunk_size: Size of each chunk
            
        Yields:
            Chunks of DataObject instances
        """
        chunk_size = chunk_size or self.context.batch_size
        
        # Default implementation - specific loaders should override
        collection = self.load_data()
        
        for i in range(0, len(collection), chunk_size):
            yield collection.objects[i:i + chunk_size]
    
    def _validate_basic_requirements(self) -> ValidationResult:
        """Validate basic loader requirements."""
        result = ValidationResult(is_valid=True)
        
        if not self.source:
            result.add_error("Source cannot be empty")
        
        return result
    
    def _create_data_object(
        self,
        data: Dict[str, Any],
        index: Optional[int] = None
    ) -> DataObject:
        """
        Create a DataObject from raw data.
        
        Args:
            data: Raw data dictionary
            index: Optional record index
            
        Returns:
            DataObject instance
        """
        source_info = {
            'source': self.source,
            'source_type': self.source_type,
            'index': index
        }
        
        metadata = {
            'loaded_at': datetime.now().isoformat(),
            'loader': self.__class__.__name__
        }
        
        return DataObject(
            data=data,
            source_info=source_info,
            metadata=metadata
        )
    
    def _create_data_collection(
        self,
        data_objects: List[DataObject]
    ) -> DataCollection:
        """
        Create a DataCollection from data objects.
        
        Args:
            data_objects: List of DataObject instances
            
        Returns:
            DataCollection instance
        """
        source_info = self.get_metadata()
        
        metadata = {
            'loaded_at': datetime.now().isoformat(),
            'loader': self.__class__.__name__,
            'total_records': len(data_objects)
        }
        
        return DataCollection(
            objects=data_objects,
            source_info=source_info,
            metadata=metadata
        )


class DataSourceError(Exception):
    """Exception raised for data source related errors."""
    pass


class LoaderRegistry:
    """
    Registry for data source loaders.
    
    Manages registration and discovery of loader classes
    for different data source types.
    """
    
    def __init__(self):
        self._loaders = {}
        self._source_patterns = {}
    
    def register_loader(
        self,
        source_type: str,
        loader_class: type,
        patterns: Optional[List[str]] = None
    ) -> None:
        """
        Register a loader for a source type.
        
        Args:
            source_type: Source type identifier
            loader_class: Loader class
            patterns: Optional file/URL patterns for auto-detection
        """
        self._loaders[source_type] = loader_class
        
        if patterns:
            for pattern in patterns:
                self._source_patterns[pattern] = source_type
    
    def get_loader_class(self, source_type: str) -> Optional[type]:
        """Get loader class for source type."""
        return self._loaders.get(source_type)
    
    def detect_source_type(self, source: str) -> Optional[str]:
        """
        Detect source type from source string.
        
        Args:
            source: Source identifier
            
        Returns:
            Detected source type, or None if unknown
        """
        source_lower = source.lower()
        
        # Check URL patterns
        if source_lower.startswith(('http://', 'https://')):
            # Check file extension in URL
            for pattern, source_type in self._source_patterns.items():
                if pattern in source_lower:
                    return source_type
            # Default to API if no specific pattern matches
            return 'api'
        
        # Check file patterns
        for pattern, source_type in self._source_patterns.items():
            if source_lower.endswith(pattern):
                return source_type
        
        return None
    
    def create_loader(
        self,
        source: str,
        context: LoadContext,
        source_type: Optional[str] = None,
        **kwargs
    ) -> BaseLoader:
        """
        Create appropriate loader for source.
        
        Args:
            source: Source identifier
            context: Loading context
            source_type: Optional explicit source type
            **kwargs: Loader-specific options
            
        Returns:
            Configured loader instance
        """
        if source_type is None:
            source_type = self.detect_source_type(source)
        
        if source_type is None:
            raise DataSourceError(f"Cannot determine source type for: {source}")
        
        loader_class = self.get_loader_class(source_type)
        if loader_class is None:
            raise DataSourceError(f"No loader available for source type: {source_type}")
        
        return loader_class(source, context, **kwargs)
    
    def list_available_loaders(self) -> Dict[str, type]:
        """Get all available loaders."""
        return self._loaders.copy()


# Global loader registry instance
loader_registry = LoaderRegistry()

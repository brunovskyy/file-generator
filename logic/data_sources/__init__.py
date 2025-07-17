"""
Data sources package initialization for DocGenius.

This package contains all data source loaders for loading and
processing data from various input formats and sources.
"""

# Base loader classes
from .data_loader_base import (
    BaseLoader,
    LoadResult,
    LoadContext,
    DataSourceError,
    LoaderRegistry,
    loader_registry
)

# CSV loader
from .data_loader_csv import (
    CSVLoader,
    CSVOptions,
    CSVFieldMapper,
    CSVValidator
)

__all__ = [
    # Base classes
    "BaseLoader",
    "LoadResult",
    "LoadContext", 
    "DataSourceError",
    "LoaderRegistry",
    "loader_registry",
    
    # CSV loader
    "CSVLoader",
    "CSVOptions",
    "CSVFieldMapper",
    "CSVValidator"
]

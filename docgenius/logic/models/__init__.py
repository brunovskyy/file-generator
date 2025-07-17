"""
Models package initialization for DocGenius.

This package contains all the core data models and configuration
classes used throughout the DocGenius application.
"""

# Base models and validation
from .base_models import (
    BaseModel,
    ValidationResult,
    ValidationRule,
    FieldValidator,
    ModelValidator
)

# Data structures
from .data_structures import (
    DataObject,
    DataCollection,
    FieldMapping,
    DataNormalizer
)

# Configuration models
from .document_config import (
    DocumentConfig,
    ExportSettings,
    MarkdownSettings,
    PDFSettings,
    WordSettings,
    ExportFormat,
    YAMLKeySelection,
    ConfigValidator
)

__all__ = [
    # Base models
    "BaseModel",
    "ValidationResult", 
    "ValidationRule",
    "FieldValidator",
    "ModelValidator",
    
    # Data structures
    "DataObject",
    "DataCollection",
    "FieldMapping",
    "DataNormalizer",
    
    # Configuration
    "DocumentConfig",
    "ExportSettings",
    "MarkdownSettings", 
    "PDFSettings",
    "WordSettings",
    "ExportFormat",
    "YAMLKeySelection",
    "ConfigValidator"
]

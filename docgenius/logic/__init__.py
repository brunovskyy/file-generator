"""
DocGenius Logic Package

This package contains the core business logic for the DocGenius document creation toolkit.
It provides a modular architecture with clear separation of concerns:

- models: Core data structures and validation
- data_sources: Input loading and processing
- exporters: Document generation engines
- utilities: Supporting functions and helpers

Example usage:
    from logic.models import DataObject, DocumentConfig
    from logic.data_sources import CSVLoader
    from logic.exporters import MarkdownExporter
    
    # Load data
    loader = CSVLoader()
    result = loader.load('data.csv')
    
    # Create document
    exporter = MarkdownExporter()
    data_obj = DataObject(result.data)
    config = DocumentConfig(output_path='output.md')
    
    export_result = exporter.export(data_obj, config)
"""

__version__ = "1.0.0"
__author__ = "DocGenius Team"

# Import key classes for easy access
try:
    from .models import (
        BaseModel, ValidationResult, DataObject, 
        DataCollection, DocumentConfig, ExportSettings
    )
    from .data_sources import BaseLoader, LoadResult, CSVLoader
    from .exporters import (
        BaseExporter, ExportResult, create_template_processor as TemplateProcessor,
        MarkdownExporter, PDFExporter, WordExporter
    )
    from .utilities import (
        DialogResult, FileDialogs, MessageDialogs,
        ValidationEngine, FileOperations, LoggingConfigurator
    )
    
    __all__ = [
        # Models
        'BaseModel', 'ValidationResult', 'DataObject', 
        'DataCollection', 'DocumentConfig', 'ExportSettings',
        
        # Data Sources
        'BaseLoader', 'LoadResult', 'CSVLoader',
        
        # Exporters
        'BaseExporter', 'ExportResult', 'TemplateProcessor',
        'MarkdownExporter', 'PDFExporter', 'WordExporter',
        
        # Utilities
        'DialogResult', 'FileDialogs', 'MessageDialogs',
        'ValidationEngine', 'FileOperations', 'LoggingConfigurator'
    ]
    
except ImportError as e:
    # Handle graceful degradation if some modules aren't available
    print(f"Warning: Some logic modules could not be imported: {e}")
    __all__ = []

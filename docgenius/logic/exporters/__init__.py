"""
Exporters package initialization for DocGenius.

This package contains all document export engines for converting
data objects to various document formats.
"""

# Base exporter classes
from .export_handler_base import (
    BaseExporter,
    ExportResult,
    ExportContext
)

# Template processing
from .template_processor import (
    BaseTemplate,
    TextTemplate,
    TemplateLoader,
    TemplateValidator,
    VariableResolver,
    TemplateError,
    create_template_processor,
    render_template_with_data
)

# Format-specific exporters
from .export_handler_markdown import (
    MarkdownExporter,
    YAMLFrontMatterGenerator,
    MarkdownFormatter,
    MarkdownExportError,
    export_to_markdown  # Compatibility function
)

# PDF exporter
try:
    from .export_handler_pdf import (
        PDFExporter,
        PDFExportError,
        export_to_pdf  # Compatibility function
    )
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    PDFExporter = None
    PDFExportError = Exception
    export_to_pdf = None

# Word exporter  
try:
    from .export_handler_word import (
        WordExporter,
        WordExportError,
        export_to_word  # Compatibility function
    )
    WORD_AVAILABLE = True
except ImportError:
    WORD_AVAILABLE = False
    WordExporter = None
    WordExportError = Exception
    export_to_word = None

__all__ = [
    # Base classes
    "BaseExporter",
    "ExportResult", 
    "ExportContext",
    
    # Template processing
    "BaseTemplate",
    "TextTemplate",
    "TemplateLoader",
    "TemplateValidator",
    "VariableResolver",
    "TemplateError",
    "create_template_processor",
    "render_template_with_data",
    
    # Markdown exporter
    "MarkdownExporter",
    "YAMLFrontMatterGenerator",
    "MarkdownFormatter", 
    "MarkdownExportError",
    "export_to_markdown",
    
    # PDF exporter (if available)
    "PDFExporter",
    "PDFExportError", 
    "export_to_pdf",
    
    # Word exporter (if available)
    "WordExporter",
    "WordExportError",
    "export_to_word",
    
    # Availability flags
    "PDF_AVAILABLE",
    "WORD_AVAILABLE"
]

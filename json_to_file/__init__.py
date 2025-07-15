"""
Document Creator Toolkit

A modular Python toolkit for converting data sources (CSV, JSON, APIs) 
into various document formats (Markdown, PDF, Word).
"""

__version__ = "1.0.0"
__author__ = "Document Creator Team"

from .source_to_json import load_normalized_data, DataSourceError
from .markdown_export import export_to_markdown, MarkdownExportError
from .pdf_export import export_to_pdf, PDFExportError
from .word_export import export_to_word, WordExportError
from .utils import DocumentCreatorError

__all__ = [
    "load_normalized_data",
    "export_to_markdown", 
    "export_to_pdf",
    "export_to_word",
    "DataSourceError",
    "MarkdownExportError",
    "PDFExportError", 
    "WordExportError",
    "DocumentCreatorError"
]

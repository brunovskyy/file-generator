"""
DocGenius - Document Creator Toolkit

A professional document generation toolkit that converts data sources 
to various document formats with modular, extensible architecture.

Main Components:
- Core: Document creation engine
- CLI: Command-line interfaces
- Logic: Modular business logic (data sources, exporters, utilities)
- Compat: Legacy compatibility layers

Entry Points:
- app_launcher_cli.py: Main application launcher
- docgenius.core.document_creator: Core document creation functionality
"""

__version__ = "1.0.0"
__author__ = "Bruno Pineda"

# Main package imports for convenience
from .core.document_creator import main as create_documents
from .cli.dev_tools import DevToolsInterface
from .cli.system_tools import SystemToolsInterface

__all__ = [
    'create_documents',
    'DevToolsInterface', 
    'SystemToolsInterface'
]

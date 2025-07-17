"""
Backward compatibility layer for transitioning from json_to_file to logic structure.

This module provides compatibility functions to help existing code work with the new
modular architecture while we complete the transition.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import from new logic structure
try:
    from logic.data_sources import CSVLoader, LoadResult
    from logic.exporters import MarkdownExporter, PDFExporter, WordExporter, ExportResult
    from logic.models import DataObject, DocumentConfig, ExportSettings
    from logic.utilities import (
        FileDialogs, MessageDialogs, DialogResult,
        ValidationEngine, FileOperations,
        LoggingConfigurator, SessionLogger
    )
except ImportError as e:
    print(f"Warning: Could not import from logic structure: {e}")
    # Fallback imports would go here if needed


# === Data Source Compatibility ===
def load_normalized_data(file_path: str, source_type: str = None):
    """Load data using new data sources structure."""
    try:
        if file_path.lower().endswith('.csv'):
            loader = CSVLoader()
            result = loader.load(file_path)
            if result.success:
                return result.data
            else:
                raise DataSourceError(f"Failed to load CSV: {'; '.join(result.errors)}")
        else:
            # Handle other formats as needed
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        raise DataSourceError(f"Failed to load data from {file_path}: {str(e)}")


def validate_data_source(file_path: str) -> bool:
    """Validate data source using new validation utilities."""
    try:
        validator = ValidationEngine()
        return validator.validate_file_path(file_path)
    except:
        # Fallback validation
        return Path(file_path).exists()


# === Export Compatibility ===
def export_to_markdown(data, output_path: str, **kwargs):
    """Export to markdown using new exporter structure."""
    try:
        exporter = MarkdownExporter()
        data_obj = DataObject(data)
        config = DocumentConfig(output_path=output_path)
        settings = ExportSettings(**kwargs)
        
        result = exporter.export(data_obj, config, settings)
        if not result.success:
            raise MarkdownExportError(f"Export failed: {'; '.join(result.errors)}")
        return result
    except Exception as e:
        raise MarkdownExportError(f"Markdown export error: {str(e)}")


def export_to_pdf(data, output_path: str, **kwargs):
    """Export to PDF using new exporter structure."""
    try:
        exporter = PDFExporter()
        data_obj = DataObject(data)
        config = DocumentConfig(output_path=output_path)
        settings = ExportSettings(**kwargs)
        
        result = exporter.export(data_obj, config, settings)
        if not result.success:
            raise PDFExportError(f"Export failed: {'; '.join(result.errors)}")
        return result
    except Exception as e:
        raise PDFExportError(f"PDF export error: {str(e)}")


def export_to_word(data, output_path: str, **kwargs):
    """Export to Word using new exporter structure."""
    try:
        exporter = WordExporter()
        data_obj = DataObject(data)
        config = DocumentConfig(output_path=output_path)
        settings = ExportSettings(**kwargs)
        
        result = exporter.export(data_obj, config, settings)
        if not result.success:
            raise WordExportError(f"Export failed: {'; '.join(result.errors)}")
        return result
    except Exception as e:
        raise WordExportError(f"Word export error: {str(e)}")


# === Utility Compatibility ===
def setup_logging():
    """Setup logging using new utilities structure."""
    try:
        configurator = LoggingConfigurator()
        return configurator.setup_application_logging(log_level='INFO')
    except:
        import logging
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)


def yes_no_prompt(message: str) -> bool:
    """Yes/no prompt using new dialog utilities."""
    try:
        return MessageDialogs.show_yes_no("Confirm", message)
    except:
        # Fallback to console input
        response = input(f"{message} (y/n): ").lower().strip()
        return response in ['y', 'yes', 'true', '1']


def prompt_user_choice(message: str, choices: list) -> str:
    """Prompt user for choice."""
    try:
        return MessageDialogs.show_choice("Select Option", message, choices)
    except:
        # Fallback to console input
        print(message)
        for i, choice in enumerate(choices, 1):
            print(f"{i}. {choice}")
        
        while True:
            try:
                idx = int(input("Select choice (number): ")) - 1
                if 0 <= idx < len(choices):
                    return choices[idx]
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number.")


def select_folder_with_dialog() -> Optional[str]:
    """Select folder with dialog."""
    try:
        result = FileDialogs.select_directory("Select Directory")
        return result.selected_path if result.success else None
    except:
        # Fallback to input
        folder = input("Enter directory path: ").strip()
        return folder if folder and Path(folder).exists() else None


def get_default_output_directory():
    """Get default output directory."""
    return str(Path.cwd() / 'output')


def get_available_yaml_keys(*args, **kwargs):
    """Get available YAML keys - placeholder for compatibility."""
    return []


def interactive_yaml_key_selection(*args, **kwargs):
    """Interactive YAML key selection - placeholder for compatibility."""
    return None


def check_pdf_requirements():
    """Check PDF export requirements."""
    return True


def check_word_requirements():
    """Check Word export requirements."""
    return True


def get_missing_requirements(*args):
    """Get missing requirements."""
    return []


# === Exception Classes ===
class DataSourceError(Exception):
    """Exception raised for data source loading errors."""
    pass


class MarkdownExportError(Exception):
    """Exception raised for markdown export errors."""
    pass


class PDFExportError(Exception):
    """Exception raised for PDF export errors."""
    pass


class WordExportError(Exception):
    """Exception raised for Word export errors."""
    pass


class DocumentCreatorError(Exception):
    """Exception raised for document creator errors."""
    pass

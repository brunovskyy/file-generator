"""
Document Creator: Convert data sources to various document formats.

This module handles the document creation functionality for the DocGenius toolkit.
It provides both interactive and argument-based usage for converting
data sources (CSV, JSON, APIs) to various document formats.
"""

import argparse
import sys
import logging
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# Import toolkit modules from new package structure
from ..logic.data_sources import CSVLoader, LoadResult
from ..logic.exporters import MarkdownExporter, PDFExporter, WordExporter, ExportResult
from ..logic.models import DataObject, DocumentConfig, ExportSettings
from ..logic.utilities import (
    FileDialogs, MessageDialogs, DialogResult,
    ValidationEngine, FileOperations,
    LoggingConfigurator, SessionLogger
)

# Backward compatibility functions
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
            # Handle JSON and other formats
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if not content.strip():
                    raise DataSourceError(f"File is empty: {file_path}")
                return json.loads(content)
    except json.JSONDecodeError as e:
        # Provide helpful JSON error messages
        error_msg = f"Invalid JSON format in {file_path}:\n"
        error_msg += f"Error at line {e.lineno}, column {e.colno}: {e.msg}\n"
        error_msg += "💡 Common fixes:\n"
        error_msg += "  - Check for missing quotes around property names\n"
        error_msg += "  - Check for trailing commas\n"
        error_msg += "  - Validate JSON format at jsonlint.com"
        raise DataSourceError(error_msg)
    except FileNotFoundError:
        raise DataSourceError(f"File not found: {file_path}")
    except PermissionError:
        raise DataSourceError(f"Permission denied accessing: {file_path}")
    except Exception as e:
        raise DataSourceError(f"Failed to load data from {file_path}: {str(e)}")

def validate_data_source(file_path: str) -> bool:
    """Validate data source using new validation utilities."""
    validator = ValidationEngine()
    return validator.validate_file_path(file_path)

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

def interactive_yaml_key_selection(sample_data: Dict[str, Any], all_keys: List[str]) -> Dict[str, Any]:
    """
    Interactive YAML key selection with live preview.
    
    Args:
        sample_data: Sample data object to show previews
        all_keys: All available keys from the data
        
    Returns:
        Dictionary with selection configuration:
        - mode: 'all', 'select', 'flatten', 'none', or 'exit'
        - selected_keys: List of selected keys
        - flatten_nested: Boolean for flattening nested objects
    """
    try:
        from ..cli.enhanced_ui import EnhancedCLI, YAMLKeySelector
        
        cli = EnhancedCLI()
        selector = YAMLKeySelector(cli)
        
        # Show current data preview
        cli.format_info("Sample data preview:")
        print(json.dumps(sample_data, indent=2)[:500] + "..." if len(str(sample_data)) > 500 else json.dumps(sample_data, indent=2))
        
        return selector.select_keys_interactive(sample_data, all_keys)
        
    except ImportError:
        # Fallback to basic selection if enhanced UI is not available
        print("\n🔧 Enhanced UI not available, using basic selection...")
        return _basic_yaml_key_selection(sample_data, all_keys)


def _basic_yaml_key_selection(sample_data: Dict[str, Any], all_keys: List[str]) -> Dict[str, Any]:
    """Basic fallback YAML key selection without enhanced UI."""
    print("\n📋 Available keys in your data:")
    for i, key in enumerate(all_keys, 1):
        value = sample_data.get(key, "N/A")
        preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
        print(f"  {i}. {key}: {preview}")
    
    while True:
        choice = input(f"\nSelect keys (e.g., 1,3,5 for specific keys or 'all' for all keys): ").strip().lower()
        
        if choice == 'all':
            return {
                "mode": "all",
                "selected_keys": all_keys,
                "flatten_nested": False
            }
        elif choice == 'none':
            return {
                "mode": "none", 
                "selected_keys": [],
                "flatten_nested": False
            }
        
        try:
            # Parse specific key selection
            indices = [int(x.strip()) - 1 for x in choice.split(',')]
            selected_keys = [all_keys[i] for i in indices if 0 <= i < len(all_keys)]
            
            if selected_keys:
                return {
                    "mode": "select",
                    "selected_keys": selected_keys,
                    "flatten_nested": False
                }
            else:
                print("❌ No valid keys selected. Please try again.")
                
        except (ValueError, IndexError):
            print("❌ Invalid input. Use numbers separated by commas (e.g., 1,3,5) or 'all'.")
            continue

def check_pdf_requirements():
    """Check PDF export requirements."""
    return True  # Simplified for now

def get_missing_requirements(*args):
    """Get missing requirements."""
    return []  # Simplified for now

def check_word_requirements():
    """Check Word export requirements."""
    return True  # Simplified for now

def get_pdf_missing_requirements():
    """Get missing PDF requirements."""
    return []

def get_word_missing_requirements():
    """Get missing Word requirements.""" 
    return []

def setup_logging(log_level='INFO'):
    """Setup logging using new utilities structure."""
    configurator = LoggingConfigurator()
    return configurator.setup_application_logging(log_level=log_level)

def generate_transaction_id():
    """Generate transaction ID."""
    import uuid
    return str(uuid.uuid4())[:8]

def get_default_output_directory():
    """Get default output directory."""
    return str(Path.cwd() / 'output')

def yes_no_prompt(message: str, default: bool = True) -> bool:
    """Yes/no prompt using new dialog utilities."""
    dialogs = MessageDialogs()
    result = dialogs.confirm("Confirm", message)
    return result.value if result.success else default

def prompt_user_choice(message: str, choices: list, default: str = None) -> str:
    """Prompt user for choice."""
    print(f"\n{message}")
    for i, choice in enumerate(choices, 1):
        marker = " (default)" if choice == default else ""
        print(f"{i}. {choice}{marker}")
    
    while True:
        try:
            user_input = input(f"\nChoose 1-{len(choices)} (or 'help'/'back'): ").strip()
            
            if user_input.lower() == 'help':
                print("\nValid commands:")
                print("- Type a number (1-{}) to select an option".format(len(choices)))
                print("- Type 'help' to see this message")
                print("- Type 'back' to return to previous step")
                continue
            elif user_input.lower() == 'back':
                return "back"
            
            choice_index = int(user_input) - 1
            if 0 <= choice_index < len(choices):
                return choices[choice_index]
            else:
                print(f"❌ Invalid option. Please choose 1-{len(choices)}.")
        except ValueError:
            print(f"❌ Please enter a number (1-{len(choices)}) or 'help'/'back'.")
        except KeyboardInterrupt:
            return "back"

def select_folder_with_dialog(title: str = "Select Output Directory") -> Optional[str]:
    """Select folder with dialog using direct tkinter."""
    print(f"Opening folder selection dialog...")
    try:
        import tkinter as tk
        from tkinter import filedialog
        
        # Create a temporary root window
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        root.attributes('-topmost', True)  # Bring to front
        
        # Open folder dialog
        folder_path = filedialog.askdirectory(
            title=title
        )
        
        root.destroy()  # Clean up
        
        if folder_path:
            print(f"Selected folder: {folder_path}")
            return folder_path
        else:
            print("No folder selected.")
            return None
            
    except Exception as e:
        print(f"❌ Folder dialog failed: {e}")
        print("Please enter folder path manually instead.")
        return None

# Exception classes for backward compatibility
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


def select_file_with_dialog() -> Optional[str]:
    """
    Open a file selection dialog using direct tkinter.
    
    Returns:
        Selected file path or None if cancelled/failed
    """
    print("Opening file selection dialog...")
    try:
        import tkinter as tk
        from tkinter import filedialog
        
        # Create a temporary root window
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        root.attributes('-topmost', True)  # Bring to front
        
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select your data file",
            filetypes=[
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"), 
                ("All files", "*.*")
            ]
        )
        
        root.destroy()  # Clean up
        
        if file_path:
            print(f"Selected file: {file_path}")
            return file_path
        else:
            print("No file selected.")
            return None
            
    except Exception as e:
        print(f"❌ File dialog failed: {e}")
        print("Please enter file path manually instead.")
        return None


def validate_export_requirements(export_types: List[str]) -> bool:
    """
    Validate that required packages are available for selected export types.
    
    Args:
        export_types: List of export types to validate
        
    Returns:
        True if all requirements are met, False otherwise
    """
    missing_packages = []
    
    for export_type in export_types:
        if export_type == 'pdf':
            pdf_reqs = check_pdf_requirements()
            if not pdf_reqs['direct_pdf'] and not pdf_reqs['template_pdf']:
                missing_packages.extend(get_pdf_missing_requirements())
        elif export_type == 'word':
            word_reqs = check_word_requirements()
            if not word_reqs['word_export']:
                missing_packages.extend(get_word_missing_requirements())
    
    if missing_packages:
        print(f"\n❌ Missing required packages for selected export types:")
        for package in set(missing_packages):
            print(f"  - {package}")
        print(f"\nInstall with: pip install {' '.join(set(missing_packages))}")
        return False
    
    return True


def show_input_help(step_name: str, options: List[str] = None) -> None:
    """Show help for current input step."""
    help_messages = {
        "source_method": "Choose 1 or 2. Type the number and press Enter.",
        "source_path": "Enter a valid file path (e.g., data.json) or URL (e.g., https://api.example.com/data).",
        "export_formats": "Enter one or more numbers separated by spaces (e.g., '1' for markdown only, or '1 2 3' for all formats).",
        "output_method": "Choose 1, 2, or 3. Type the number and press Enter.",
        "yaml_front_matter": "Type 'y' for yes or 'n' for no.",
        "yaml_keys": "Choose 1 or 2. Type the number and press Enter."
    }
    
    print(f"\n💡 Help for {step_name}:")
    if step_name in help_messages:
        print(f"   {help_messages[step_name]}")
    if options:
        print(f"   Valid options: {', '.join(str(i+1) for i in range(len(options)))}")
    print("   Type 'help' anytime to see this message again.")
    print("   Type 'back' to return to previous step.")


def get_user_input_with_navigation() -> Dict[str, Any]:
    """
    Get user input with enhanced navigation and error handling.
    Uses enhanced CLI with arrow key navigation when available.
    
    Returns:
        Dictionary containing user configuration
    """
    try:
        from ..cli.enhanced_ui import EnhancedCLI
        
        cli = EnhancedCLI()
        cli.show_banner()
        
        # Use enhanced navigation
        return _get_input_with_enhanced_ui(cli)
        
    except ImportError:
        # Fallback to basic CLI
        print("\n🔧 Enhanced UI not available, using basic interface...")
        return _get_input_basic_ui()


def _get_input_with_enhanced_ui(cli) -> Dict[str, Any]:
    """Enhanced UI flow with unified step navigation and dynamic step calculation."""
    try:
        from ..cli.step_manager import StepManager
        
        step_manager = StepManager()
        config = {}
        current_step_key = "data_source"
        
        while True:
            # Update current step in config for progress tracking
            config['current_step'] = current_step_key
            
            # Get current step information
            step_num, total_steps, step_title = step_manager.get_step_progress(current_step_key, config)
            
            # Show progress
            cli.show_step_progress(step_title, total_steps, step_num)
            
            # Execute the current step
            step_result = None
            
            if current_step_key == "data_source":
                step_result = _step_data_source(cli, config)
            elif current_step_key == "template_selection":
                step_result = _step_template_selection(cli, config)
            elif current_step_key == "export_formats":
                step_result = _step_export_formats(cli, config)
            elif current_step_key == "output_directory":
                step_result = _step_output_directory(cli, config)
            elif current_step_key == "markdown_config":
                step_result = _step_markdown_config(cli, config)
            elif current_step_key == "markdown_yaml_keys":
                step_result = _step_markdown_yaml_keys(cli, config)
            elif current_step_key == "pdf_config":
                step_result = _step_pdf_config(cli, config)
            elif current_step_key == "word_config":
                step_result = _step_word_config(cli, config)
            elif current_step_key == "template_variables":
                step_result = _step_template_variables(cli, config)
            elif current_step_key == "final_review":
                step_result = _step_final_review(cli, config)
            else:
                cli.format_error(f"Unknown step: {current_step_key}")
                return None
            
            # Handle step result
            if step_result is None:
                return None  # User wants to exit
            elif step_result.get('action') == 'back':
                # Go to previous step
                prev_step = step_manager.get_previous_step(current_step_key, config)
                if prev_step:
                    current_step_key = prev_step
                    # Remove any config that depends on the current step
                    config = _cleanup_step_config(current_step_key, config)
                else:
                    return None  # No previous step, exit
            elif step_result.get('action') == 'exit':
                return None
            elif step_result.get('action') == 'restart':
                # Restart from beginning
                config.clear()
                current_step_key = "data_source"
            elif step_result.get('action') == 'continue':
                # Update config with step results
                config.update(step_result.get('data', {}))
                
                # Check if this is the final step
                if current_step_key == "final_review":
                    # Remove internal tracking data
                    config.pop('current_step', None)
                    return config
                
                # Move to next step
                next_step = step_manager.get_next_step(current_step_key, config)
                if next_step:
                    current_step_key = next_step
                else:
                    # No more steps, go to final review
                    current_step_key = "final_review"
                    
        return config
        
    except ImportError:
        cli.format_warning("Step manager not available, using basic fallback")
        return _get_input_basic_ui()


def _step_data_source(cli, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle data source selection step."""
    source_options = [
        "📁 Browse for file - Use file dialog to select data file",
        "⌨️ Type path manually - Enter file path or URL directly"
    ]
    
    def source_preview_func(selected_indices: List[int], config: Dict[str, Any]) -> str:
        if not selected_indices:
            return "No source method selected"
        
        method_index = selected_indices[0]
        if method_index == 0:
            return "File dialog will open to browse for:\n• CSV files (.csv)\n• JSON files (.json)\n• Text files (.txt)"
        else:
            return "Manual entry supports:\n• Local file paths\n• URLs (http/https)\n• Relative paths\n\nExample: data.json"
    
    action_code, selected_options, action_type = cli.multi_select_step(
        "Choose data source method",
        source_options,
        config,
        preview_func=source_preview_func,
        allow_multiple=False,
        required=True,
        back_option=False  # First step, no back option
    )
    
    if action_code == -1 or action_type == "exit":
        return None
    
    # Handle data source selection
    if "Browse for file" in selected_options[0]:
        file_path = select_file_with_dialog()
        if not file_path:
            cli.format_error("No file selected")
            return {"action": "continue", "data": {}}  # Stay on same step
    else:
        file_path = input("\n🔗 Enter file path or URL: ").strip()
        if not file_path or not validate_data_source(file_path):
            cli.format_error("Invalid file path or URL")
            return {"action": "continue", "data": {}}  # Stay on same step
    
    return {
        "action": "continue",
        "data": {
            "source": file_path,
            "source_method": "dialog" if "Browse" in selected_options[0] else "manual"
        }
    }


def _step_template_selection(cli, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle template selection step."""
    template_options = [
        "📄 No template - Generate documents from data directly",
        "📋 Use template file - Apply custom template to data",
        "🎨 Browse templates - Select from built-in templates"
    ]
    
    def template_preview_func(selected_indices: List[int], config: Dict[str, Any]) -> str:
        if not selected_indices:
            return "No template option selected"
        
        template_index = selected_indices[0]
        if template_index == 0:
            return "Direct generation:\n• Simple data-to-document conversion\n• No custom formatting\n• Fast processing"
        elif template_index == 1:
            return "Custom template:\n• Use your own template files\n• Variable substitution\n• Custom formatting"
        else:
            return "Built-in templates:\n• Professional layouts\n• Pre-designed formats\n• Industry standards\n\n(Coming soon!)"
    
    action_code, selected_options, action_type = cli.multi_select_step(
        "Template options",
        template_options,
        config,
        preview_func=template_preview_func,
        allow_multiple=False,
        required=True,
        back_option=True
    )
    
    if action_code == -1:
        return {"action": "exit" if action_type == "exit" else "back"}
    
    step_data = {}
    
    if "Use template file" in selected_options[0]:
        template_path = input("\n📁 Enter template file path: ").strip()
        if template_path and Path(template_path).exists():
            step_data['template_path'] = template_path
            cli.format_success(f"Template selected: {template_path}")
        else:
            cli.format_warning("Template file not found, continuing without template")
    elif "Browse templates" in selected_options[0]:
        cli.format_info("Built-in templates feature coming soon!")
    
    return {"action": "continue", "data": step_data}


def _step_export_formats(cli, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle export format selection step."""
    format_options = [
        "📝 Markdown - Best for notes, documentation, Obsidian",
        "📄 PDF - Professional documents, reports", 
        "📊 Word - Editable documents, templates"
    ]
    
    def format_preview_func(selected_indices: List[int], config: Dict[str, Any]) -> str:
        if not selected_indices:
            return "No formats selected"
        
        selected_formats = [format_options[i].split(' - ')[0].split(' ')[1].lower() for i in selected_indices]
        
        preview_lines = ["Selected formats:\n"]
        for fmt in selected_formats:
            if fmt == "markdown":
                preview_lines.append("📝 Markdown:")
                preview_lines.append("  • YAML front matter support")
                preview_lines.append("  • Perfect for Obsidian")
                preview_lines.append("  • Plain text format\n")
            elif fmt == "pdf":
                preview_lines.append("📄 PDF:")
                preview_lines.append("  • Professional appearance")
                preview_lines.append("  • Print-ready format")
                preview_lines.append("  • Universal compatibility\n")
            elif fmt == "word":
                preview_lines.append("📊 Word:")
                preview_lines.append("  • Editable documents")
                preview_lines.append("  • Template support")
                preview_lines.append("  • Rich formatting\n")
        
        if len(selected_formats) > 1:
            preview_lines.append(f"✨ All {len(selected_formats)} formats will be generated")
        
        return "".join(preview_lines)
    
    action_code, selected_options, action_type = cli.multi_select_step(
        "Choose output formats",
        format_options,
        config,
        preview_func=format_preview_func,
        allow_multiple=True,
        required=True,
        back_option=True
    )
    
    if action_code == -1:
        return {"action": "exit" if action_type == "exit" else "back"}
    
    # Extract format names from selected options
    export_types = []
    for option in selected_options:
        format_name = option.split(' - ')[0].split(' ')[1].lower()
        export_types.append(format_name)
    
    return {
        "action": "continue",
        "data": {"export_types": export_types}
    }


def _step_output_directory(cli, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle output directory selection step."""
    output_options = [
        "📁 Browse for folder - Use folder dialog",
        "📂 Current directory - Use current working directory", 
        "⌨️ Type path manually - Enter custom output path"
    ]
    
    def output_preview_func(selected_indices: List[int], config: Dict[str, Any]) -> str:
        if not selected_indices:
            return "No output method selected"
        
        method_index = selected_indices[0]
        current_dir = str(Path.cwd())
        
        if method_index == 0:
            return f"Folder dialog will open\nCurrent directory: {current_dir}"
        elif method_index == 1:
            export_types = config.get('export_types', ['markdown'])
            preview_lines = [f"Files will be saved to:\n{current_dir}\n\nExample output files:"]
            for fmt in export_types:
                preview_lines.append(f"• document_1.{fmt}")
                preview_lines.append(f"• document_2.{fmt}")
            return "\n".join(preview_lines)
        else:
            return "Manual path entry\nEnter absolute or relative path\nExample: ./output or C:\\Documents\\Output"
    
    action_code, selected_options, action_type = cli.multi_select_step(
        "Choose output location",
        output_options,
        config,
        preview_func=output_preview_func,
        allow_multiple=False,
        required=True,
        back_option=True
    )
    
    if action_code == -1:
        return {"action": "exit" if action_type == "exit" else "back"}
    
    # Handle output directory selection
    if "Browse for folder" in selected_options[0]:
        output_dir = select_folder_with_dialog()
        if not output_dir:
            output_dir = str(Path.cwd())
    elif "Current directory" in selected_options[0]:
        output_dir = str(Path.cwd())
    else:
        output_dir = input("\n📁 Enter output directory: ").strip()
        if not output_dir:
            output_dir = str(Path.cwd())
    
    return {
        "action": "continue",
        "data": {"output_dir": output_dir}
    }


def _step_markdown_config(cli, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle Markdown-specific configuration step."""
    yaml_options = [
        "✅ Include YAML front matter - Structured metadata at top",
        "📝 Include as plain text - Metadata mixed with content",
        "❌ No metadata - Content only"
    ]
    
    def yaml_preview_func(selected_indices: List[int], config: Dict[str, Any]) -> str:
        if not selected_indices:
            return "No YAML option selected"
        
        yaml_index = selected_indices[0]
        
        if yaml_index == 0:  # YAML front matter
            return """Example with YAML front matter:
---
title: Sample Document
author: John Doe
tags: [example, test]
---
# Document Content
This is the main content..."""
        elif yaml_index == 1:  # Plain text
            return """Example with plain text metadata:
Title: Sample Document
Author: John Doe
Tags: example, test

# Document Content  
This is the main content..."""
        else:  # No metadata
            return """Example content only:
# Document Content
This is the main content without any metadata..."""
    
    action_code, selected_options, action_type = cli.multi_select_step(
        "How should metadata be included in Markdown?",
        yaml_options,
        config,
        preview_func=yaml_preview_func,
        allow_multiple=False,
        required=True,
        back_option=True
    )
    
    if action_code == -1:
        return {"action": "exit" if action_type == "exit" else "back"}
    
    yaml_choice = selected_options[0]
    step_data = {}
    
    if "Include YAML front matter" in yaml_choice:
        step_data['yaml_front_matter'] = True
        step_data['yaml_key_selection'] = 'select'  # Will trigger key selection step
    elif "Include as plain text" in yaml_choice:
        step_data['yaml_front_matter'] = False
        step_data['yaml_key_selection'] = 'all'
    else:  # No metadata
        step_data['yaml_front_matter'] = False
        step_data['yaml_key_selection'] = 'none'
    
    return {"action": "continue", "data": step_data}


def _step_markdown_yaml_keys(cli, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle YAML key selection step."""
    try:
        # Load sample data for key selection
        sample_data_list = load_normalized_data(config['source'])
        sample_data = sample_data_list[0] if sample_data_list else {}
        all_keys = list(sample_data.keys()) if sample_data else []
        
        # Use the enhanced YAML key selector
        yaml_result = interactive_yaml_key_selection(sample_data, all_keys)
        
        if yaml_result.get('mode') == 'exit':
            return {"action": "back"}
        
        return {"action": "continue", "data": yaml_result}
        
    except Exception as e:
        cli.format_error(f"Error loading sample data: {e}")
        # Continue with basic configuration
        return {
            "action": "continue", 
            "data": {"yaml_key_selection": "all"}
        }


def _step_pdf_config(cli, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle PDF-specific configuration step."""
    pdf_options = [
        "📄 Standard layout - Default PDF formatting",
        "📊 Report layout - Professional report style",
        "📋 Letter layout - Business letter format"
    ]
    
    def pdf_preview_func(selected_indices: List[int], config: Dict[str, Any]) -> str:
        if not selected_indices:
            return "No PDF layout selected"
        
        layout_index = selected_indices[0]
        
        layouts = [
            "Standard layout:\n• Simple formatting\n• Basic headers\n• Plain styling",
            "Report layout:\n• Professional headers\n• Page numbers\n• Corporate styling", 
            "Letter layout:\n• Business formatting\n• Letterhead space\n• Formal styling"
        ]
        
        return layouts[layout_index]
    
    action_code, selected_options, action_type = cli.multi_select_step(
        "Choose PDF layout style",
        pdf_options,
        config,
        preview_func=pdf_preview_func,
        allow_multiple=False,
        required=True,
        back_option=True
    )
    
    if action_code == -1:
        return {"action": "exit" if action_type == "exit" else "back"}
    
    layout_choice = selected_options[0]
    pdf_layout = "standard"
    if "Report layout" in layout_choice:
        pdf_layout = "report"
    elif "Letter layout" in layout_choice:
        pdf_layout = "letter"
    
    return {
        "action": "continue",
        "data": {"pdf_layout": pdf_layout}
    }


def _step_word_config(cli, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle Word-specific configuration step."""
    word_options = [
        "📝 Simple document - Basic Word formatting",
        "📊 Professional template - Enhanced styling",
        "🎨 Custom template - Use existing Word template"
    ]
    
    def word_preview_func(selected_indices: List[int], config: Dict[str, Any]) -> str:
        if not selected_indices:
            return "No Word option selected"
        
        word_index = selected_indices[0]
        
        options = [
            "Simple document:\n• Basic formatting\n• Default styles\n• Quick generation",
            "Professional template:\n• Enhanced styling\n• Consistent formatting\n• Corporate appearance",
            "Custom template:\n• Use your template\n• Variable substitution\n• Custom branding"
        ]
        
        return options[word_index]
    
    action_code, selected_options, action_type = cli.multi_select_step(
        "Choose Word document style",
        word_options,
        config,
        preview_func=word_preview_func,
        allow_multiple=False,
        required=True,
        back_option=True
    )
    
    if action_code == -1:
        return {"action": "exit" if action_type == "exit" else "back"}
    
    word_choice = selected_options[0]
    step_data = {}
    
    if "Professional template" in word_choice:
        step_data['word_style'] = 'professional'
    elif "Custom template" in word_choice:
        step_data['word_style'] = 'custom'
        template_path = input("\n📁 Enter Word template path (.docx): ").strip()
        if template_path and Path(template_path).exists():
            step_data['word_template'] = template_path
    else:
        step_data['word_style'] = 'simple'
    
    return {"action": "continue", "data": step_data}


def _step_template_variables(cli, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle template variable mapping step."""
    # TODO: Implement template variable mapping
    cli.format_info("Template variable mapping coming soon!")
    
    return {"action": "continue", "data": {}}


def _step_final_review(cli, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle final configuration review step."""
    # Generate configuration summary
    summary_lines = [
        "📋 Configuration Summary:",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"📊 Source: {Path(config['source']).name}",
        f"🎯 Formats: {', '.join(config['export_types'])}",
        f"📁 Output: {config['output_dir']}"
    ]
    
    if config.get('template_path'):
        summary_lines.append(f"🎨 Template: {Path(config['template_path']).name}")
    
    if 'markdown' in config['export_types']:
        yaml_mode = config.get('mode', 'all')
        summary_lines.append(f"📝 YAML: {yaml_mode} mode")
        if yaml_mode == 'select':
            summary_lines.append(f"   Selected {len(config.get('selected_keys', []))} keys")
    
    if 'pdf' in config['export_types']:
        pdf_layout = config.get('pdf_layout', 'standard')
        summary_lines.append(f"📄 PDF: {pdf_layout} layout")
    
    if 'word' in config['export_types']:
        word_style = config.get('word_style', 'simple')
        summary_lines.append(f"📊 Word: {word_style} style")
    
    summary = "\n".join(summary_lines)
    
    review_options = [
        "✅ Continue - Start document generation",
        "🔄 Restart - Start over with new configuration",
        "🔙 Back - Modify current settings"
    ]
    
    def review_preview_func(selected_indices: List[int], config: Dict[str, Any]) -> str:
        if not selected_indices:
            return summary
        
        choice_index = selected_indices[0]
        if choice_index == 0:
            return "Ready to generate documents!\nAll files will be created in the output directory."
        elif choice_index == 1:
            return "Restart configuration from the beginning.\nAll current settings will be lost."
        else:
            return "Go back to modify settings.\nYou can change any previous configuration."
    
    action_code, selected_options, action_type = cli.multi_select_step(
        "Ready to proceed?",
        review_options,
        config,
        preview_func=review_preview_func,
        allow_multiple=False,
        required=True,
        back_option=False  # Back option is built into the choices
    )
    
    if action_code == -1 or action_type == "exit":
        return {"action": "exit"}
    
    choice = selected_options[0]
    
    if "Continue" in choice:
        return {"action": "continue", "data": {}}
    elif "Restart" in choice:
        return {"action": "restart"}
    else:  # Back
        return {"action": "back"}


def _cleanup_step_config(step_key: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Clean up configuration when going back to a previous step."""
    # Define what config keys depend on each step
    step_dependencies = {
        "data_source": [],
        "template_selection": ["template_path"],
        "export_formats": ["export_types", "markdown_config", "pdf_config", "word_config"],
        "output_directory": ["output_dir"],
        "markdown_config": ["yaml_front_matter", "yaml_key_selection", "mode", "selected_keys", "flatten_nested"],
        "markdown_yaml_keys": ["mode", "selected_keys", "flatten_nested"],
        "pdf_config": ["pdf_layout"],
        "word_config": ["word_style", "word_template"],
        "template_variables": ["template_variables"],
        "final_review": []
    }
    
    # Remove dependent config when going back
    cleaned_config = config.copy()
    keys_to_remove = step_dependencies.get(step_key, [])
    
    for key in keys_to_remove:
        cleaned_config.pop(key, None)
    
    return cleaned_config


def _get_input_basic_ui() -> Dict[str, Any]:
    """Fallback basic UI when enhanced features aren't available."""
    config = {}
    current_step = "source_method"
    
    while True:
        try:
            if current_step == "source_method":
                current_step = handle_source_selection(config)
            elif current_step == "source_path":
                current_step = handle_source_path(config)
            elif current_step == "export_formats":
                current_step = handle_export_formats(config)
            elif current_step == "output_method":
                current_step = handle_output_selection(config)
            elif current_step == "markdown_config":
                current_step = handle_markdown_config(config)
            elif current_step == "complete":
                break
            elif current_step == "exit_to_menu":
                return None
            elif current_step == "restart":
                config.clear()
                current_step = "source_method"
                print("\n🔄 Restarting configuration...")
                
        except KeyboardInterrupt:
            if yes_no_prompt("\n⚠️ Do you want to exit?", default=False):
                sys.exit(0)
            continue
    
    return config


def handle_source_selection(config: Dict[str, Any]) -> str:
    """Handle data source selection step."""
    print("\n" + "="*50)
    print("DATA SOURCE SELECTION")
    print("="*50)
    
    options = ["Type file path/URL manually", "Browse for file"]
    
    while True:
        try:
            choice = prompt_user_choice(
                "Choose input method:",
                options,
                default="Type file path/URL manually"
            )
            
            if choice == "back":
                # User wants to go back to main menu
                return "exit_to_menu"
            elif choice == "Browse for file":
                config['source_method'] = 'dialog'
                return "source_path"
            else:
                config['source_method'] = 'manual'
                return "source_path"
                
        except Exception as e:
            print(f"❌ Invalid input: {e}")
            print("Please choose option 1 or 2.")
            continue


def handle_source_path(config: Dict[str, Any]) -> str:
    """Handle source path input step."""
    while True:
        try:
            if config['source_method'] == 'dialog':
                config['source'] = select_file_with_dialog()
                if not config['source']:
                    if yes_no_prompt("No file selected. Try again?", default=True):
                        continue
                    else:
                        return "source_method"
                return "export_formats"
            else:
                user_input = input("\nEnter file path or URL (or 'help'/'back'): ").strip()
                
                if user_input.lower() == 'help':
                    show_input_help("source_path")
                    continue
                elif user_input.lower() == 'back':
                    return "source_method"
                elif not user_input:
                    print("❌ Please enter a file path or URL.")
                    continue
                elif validate_data_source(user_input):
                    config['source'] = user_input
                    return "export_formats"
                else:
                    print("❌ Invalid path or URL. Please check the file exists and is accessible.")
                    show_input_help("source_path")
                    continue
                    
        except Exception as e:
            print(f"❌ Error: {e}")
            continue


def handle_export_formats(config: Dict[str, Any]) -> str:
    """Handle export format selection step."""
    print("\n" + "="*50)
    print("OUTPUT FORMAT SELECTION")
    print("="*50)
    
    available_formats = ["markdown", "pdf", "word"]
    
    while True:
        try:
            print("Choose output formats:")
            for i, fmt in enumerate(available_formats, 1):
                print(f"  {i}. {fmt.title()}")
            
            user_input = input("\nEnter format numbers (space-separated, e.g. 1 2) or 'help'/'back': ").strip()
            
            if user_input.lower() == 'help':
                show_input_help("export_formats", available_formats)
                continue
            elif user_input.lower() == 'back':
                return "source_path"
            elif not user_input:
                print("❌ Please select at least one format.")
                continue
            
            try:
                indices = [int(x) - 1 for x in user_input.split()]
                if all(0 <= i < len(available_formats) for i in indices):
                    selected_formats = [available_formats[i] for i in indices]
                    config['export_types'] = selected_formats
                    
                    # Validate export requirements
                    if not validate_export_requirements(selected_formats):
                        print("\n❌ Cannot proceed without required packages.")
                        if yes_no_prompt("Continue with format selection?", default=True):
                            continue
                        else:
                            return "back"
                    
                    return "output_method"
                else:
                    print("❌ Invalid numbers. Choose from 1-3.")
                    show_input_help("export_formats", available_formats)
                    continue
            except ValueError:
                print("❌ Invalid input. Enter numbers separated by spaces.")
                show_input_help("export_formats", available_formats)
                continue
                
        except Exception as e:
            print(f"❌ Error: {e}")
            continue


def handle_output_selection(config: Dict[str, Any]) -> str:
    """Handle output directory selection step."""
    print("\n" + "="*50)
    print("OUTPUT CONFIGURATION")
    print("="*50)
    
    transaction_id = generate_transaction_id()
    default_output = get_default_output_directory()
    
    options = [f"Use default ({default_output})", "Type custom path", "Browse for folder"]
    
    while True:
        try:
            choice = prompt_user_choice(
                "Choose output directory method:",
                options,
                default=options[0]
            )
            
            if choice == "back":
                return "export_formats"
            
            selected_path = None
            
            if choice == options[0]:  # Use default
                selected_path = str(default_output)
                print(f"Using default directory: {selected_path}")
                
            elif choice == options[1]:  # Type custom path
                while True:
                    custom_path = input("\nEnter output directory path (or 'back'): ").strip()
                    if custom_path.lower() == 'back':
                        break
                    if custom_path:
                        selected_path = custom_path
                        break
                    else:
                        print("❌ Please enter a valid path.")
                
                if not selected_path:  # User typed 'back'
                    continue
                    
            elif choice == options[2]:  # Browse for folder
                print("\nOpening folder selection dialog...")
                selected_path = select_folder_with_dialog("Select Output Folder")
                if not selected_path:
                    print("❌ No folder selected.")
                    continue
            
            # Validate and confirm the selected path
            if selected_path:
                # Normalize the path
                try:
                    from pathlib import Path
                    path_obj = Path(selected_path)
                    normalized_path = str(path_obj.resolve())
                    
                    # Check if path exists or can be created
                    if path_obj.exists():
                        if not path_obj.is_dir():
                            print(f"❌ Error: '{selected_path}' exists but is not a directory.")
                            continue
                        status = "✅ Directory exists"
                    else:
                        status = "📁 Directory will be created"
                    
                    # Show confirmation
                    print(f"\n{status}")
                    print(f"Output directory: {normalized_path}")
                    
                    if yes_no_prompt("Use this directory?", default=True):
                        config['output_dir'] = normalized_path
                        config['transaction_id'] = transaction_id
                        return "markdown_config" if 'markdown' in config['export_types'] else "complete"
                    else:
                        continue
                        
                except Exception as e:
                    print(f"❌ Invalid path: {e}")
                    continue
            
        except Exception as e:
            print(f"❌ Error: {e}")
            continue


def handle_markdown_config(config: Dict[str, Any]) -> str:
    """Handle Markdown-specific configuration."""
    if 'markdown' not in config['export_types']:
        return "complete"
    
    print("\n" + "="*50)
    print("MARKDOWN CONFIGURATION")
    print("="*50)
    
    print("\n📝 Example Obsidian note with YAML front matter:")
    print("---")
    print("title: My Note")
    print("tags: [work, project]")
    print("---")
    print("## Title")
    print("wow this is a text")
    print()
    
    # Step 1: Content selection
    content_options = [
        "Content only (c) - Just the text without metadata",
        "Metadata only (m) - Just the YAML properties", 
        "Both (b) - Metadata + content together"
    ]
    
    while True:
        try:
            choice = prompt_user_choice(
                "What do you want to include in the output?",
                content_options,
                default=content_options[2]
            )
            
            if choice == "back":
                return "output_method"
            elif choice == content_options[0]:  # Content only
                config['include_content'] = 'content'
                config['yaml_front_matter'] = False
                return "complete"
            elif choice == content_options[1]:  # Metadata only
                config['include_content'] = 'metadata'
                config['yaml_front_matter'] = True
                break
            elif choice == content_options[2]:  # Both
                config['include_content'] = 'both'
                break
                
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
    
    # Step 2: YAML front matter configuration (only if including metadata)
    if config['include_content'] in ['metadata', 'both']:
        yaml_options = [
            "Include YAML front matter - Structured metadata at top",
            "Include as plain text - Metadata mixed with content"
        ]
        
        while True:
            try:
                choice = prompt_user_choice(
                    "How should metadata be included?",
                    yaml_options,
                    default=yaml_options[0]
                )
                
                if choice == "back":
                    continue  # Go back to content selection
                elif choice == yaml_options[0]:  # YAML front matter
                    config['yaml_front_matter'] = True
                    break
                elif choice == yaml_options[1]:  # Plain text
                    config['yaml_front_matter'] = False
                    config['yaml_key_selection'] = 'all'
                    return "complete"
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
    
    # Step 3: YAML key selection (only if using YAML front matter)
    if config.get('yaml_front_matter', False):
        print("\n🔧 For nested objects like:")
        print("user:")
        print("  name: John")
        print("  age: 30")
        
        key_options = [
            "Include all keys - Everything in YAML front matter",
            "Select specific keys - Choose which properties to include",
            "Flatten nested objects - Convert nested data to simple keys"
        ]
        
        while True:
            try:
                choice = prompt_user_choice(
                    "How should YAML keys be handled?",
                    key_options,
                    default=key_options[0]
                )
                
                if choice == "back":
                    continue  # Go back to YAML format question
                elif choice == key_options[0]:  # All keys
                    config['yaml_key_selection'] = 'all'
                    config['flatten_nested'] = False
                    return "complete"
                elif choice == key_options[1]:  # Select specific
                    config['yaml_key_selection'] = 'select'
                    config['flatten_nested'] = False
                    return "complete"
                elif choice == key_options[2]:  # Flatten nested
                    config['yaml_key_selection'] = 'all'
                    config['flatten_nested'] = True
                    return "complete"
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
    
    return "complete"


def show_post_processing_menu(results: Dict[str, Any]) -> str:
    """Show post-processing options menu."""
    print("\n" + "="*50)
    print("WHAT'S NEXT?")
    print("="*50)
    print("1. Exit (save results)")
    print("2. Reconfigure and run again")
    print("3. Change output directory only")
    print("4. Change export formats only")
    print("5. Process different data source")
    
    while True:
        try:
            choice = input("\nChoose option (1-5): ").strip()
            
            if choice == '1':
                return "exit"
            elif choice == '2':
                return "restart"
            elif choice == '3':
                return "output_only"
            elif choice == '4':
                return "formats_only"
            elif choice == '5':
                return "source_only"
            else:
                print("❌ Please choose a number from 1-5.")
                continue
                
        except Exception as e:
            print(f"❌ Error: {e}")
            continue


def preview_processing_plan(data_list: List[Dict[str, Any]], config: Dict[str, Any]) -> None:
    """
    Show a preview of what will be processed.
    
    Args:
        data_list: Normalized data to process
        config: User configuration
    """
    print("\n" + "="*50)
    print("PROCESSING PREVIEW")
    print("="*50)
    
    total_objects = len(data_list)
    total_files = total_objects * len(config['export_types'])
    
    print(f"📊 Data objects found: {total_objects}")
    print(f"📄 Output formats: {', '.join(config['export_types'])}")
    print(f"📁 Output directory: {config['output_dir']}")
    print(f"🎯 Total files to create: {total_files}")
    
    # Show sample of data structure
    if data_list:
        print(f"\n📋 Sample data structure:")
        sample = data_list[0]
        for key in list(sample.keys())[:5]:  # Show first 5 keys
            value = str(sample[key])[:50]  # Truncate long values
            if len(str(sample[key])) > 50:
                value += "..."
            print(f"  • {key}: {value}")
        if len(sample.keys()) > 5:
            print(f"  • ... and {len(sample.keys()) - 5} more fields")
    
    # Confirm before proceeding
    if not yes_no_prompt("\nProceed with processing?", default=True):
        print("❌ Processing cancelled by user.")
        sys.exit(0)


def show_processing_summary(results: Dict[str, Any]) -> None:
    """
    Show a summary of processing results.
    
    Args:
        results: Processing results dictionary
    """
    print("\n" + "="*50)
    print("PROCESSING SUMMARY")
    print("="*50)
    
    total_success = results.get('total_success', 0)
    total_failed = results.get('total_failed', 0)
    total_processed = total_success + total_failed
    
    print(f"📊 Objects processed: {total_processed}")
    print(f"✅ Successful: {total_success}")
    print(f"❌ Failed: {total_failed}")
    
    if results.get('created_files'):
        print(f"📄 Files created: {len(results['created_files'])}")
        print(f"📁 Output directory: {results.get('output_dir', 'Unknown')}")
    
    # Show failures if any
    if results.get('failures'):
        print(f"\n❌ Failures:")
        for failure in results['failures'][:5]:  # Show first 5 failures
            print(f"  • {failure}")
        if len(results['failures']) > 5:
            print(f"  • ... and {len(results['failures']) - 5} more")
    
    # Show created files
    if results.get('created_files'):
        print(f"\n📄 Created files:")
        for file_path in results['created_files'][:10]:  # Show first 10 files
            print(f"  • {file_path.name}")
        if len(results['created_files']) > 10:
            print(f"  • ... and {len(results['created_files']) - 10} more")


def execute_exports(config: Dict[str, Any], data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Execute the selected export operations.
    
    Args:
        config: User configuration dictionary
        data_list: Normalized data to export
        
    Returns:
        Dictionary with processing results
    """
    results = {
        'created_files': [],
        'failures': [],
        'total_success': 0,
        'total_failed': 0,
        'output_dir': config['output_dir']
    }
    
    for export_type in config['export_types']:
        try:
            print(f"\n📄 Exporting to {export_type.upper()}...")
            
            if export_type == 'markdown':
                # Handle new YAML configuration structure
                yaml_settings = {}
                
                # Map new config structure to export parameters
                mode = config.get('mode', 'all')
                selected_keys = config.get('selected_keys', [])
                flatten_nested = config.get('flatten_nested', False)
                
                if mode == 'none':
                    yaml_settings['include_yaml_front_matter'] = False
                elif mode == 'select' and selected_keys:
                    yaml_settings['include_yaml_front_matter'] = True
                    yaml_settings['selected_yaml_keys'] = selected_keys
                elif mode == 'flatten':
                    yaml_settings['include_yaml_front_matter'] = True
                    yaml_settings['flatten_nested'] = True
                else:  # mode == 'all' or fallback
                    yaml_settings['include_yaml_front_matter'] = True
                
                files = export_to_markdown(
                    data_list,
                    config['output_dir'],
                    filename_key=config.get('filename_key'),
                    transaction_id=config.get('transaction_id'),
                    **yaml_settings
                )
                
            elif export_type == 'pdf':
                files = export_to_pdf(
                    data_list,
                    config['output_dir'],
                    filename_key=config.get('filename_key'),
                    pdf_title=config.get('pdf_title'),
                    pdf_author=config.get('pdf_author')
                )
                
            elif export_type == 'word':
                files = export_to_word(
                    data_list,
                    config['output_dir'],
                    filename_key=config.get('filename_key'),
                    document_title=config.get('document_title'),
                    document_author=config.get('document_author')
                )
            
            results['created_files'].extend(files)
            results['total_success'] += len(files)
            print(f"✅ {export_type.title()} export completed - {len(files)} files created")
            
        except (MarkdownExportError, PDFExportError, WordExportError) as e:
            error_msg = f"{export_type.title()} export failed: {str(e)}"
            print(f"❌ {error_msg}")
            results['failures'].append(error_msg)
            results['total_failed'] += len(data_list)  # All objects failed for this format
            continue
        except Exception as e:
            error_msg = f"{export_type.title()} export unexpected error: {str(e)}"
            print(f"❌ {error_msg}")
            results['failures'].append(error_msg)
            results['total_failed'] += len(data_list)
            continue
    
    return results


def main():
    """Main entry point for the Document Creator CLI."""
    parser = argparse.ArgumentParser(
        description="Document Creator: Convert data sources to various document formats.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --source data.json --export-types markdown pdf
  %(prog)s --source https://api.example.com/data --export-types word
  %(prog)s  # Interactive mode
        """
    )
    
    parser.add_argument(
        '--source', 
        type=str, 
        help='Path or URL to the input data (CSV, JSON, or API)'
    )
    parser.add_argument(
        '--export-types', 
        type=str, 
        nargs='+', 
        choices=['markdown', 'pdf', 'word'],
        help='One or more export types'
    )
    parser.add_argument(
        '--output-dir', 
        type=str, 
        help='Directory to save exported files'
    )
    parser.add_argument(
        '--filename-key', 
        type=str, 
        help='Key to use for filename generation'
    )
    parser.add_argument(
        '--yaml-front-matter', 
        action='store_true',
        help='Include YAML front matter in Markdown export'
    )
    parser.add_argument(
        '--yaml-key-selection', 
        choices=['all', 'select', 'none'],
        default='all',
        help='YAML front matter key selection mode'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)
    
    try:
        # Get configuration
        if args.source and args.export_types:
            # Use command-line arguments
            config = {
                'source': args.source,
                'export_types': args.export_types,
                'output_dir': args.output_dir or str(get_default_output_directory()),
                'filename_key': args.filename_key,
                'yaml_front_matter': args.yaml_front_matter,
                'yaml_key_selection': args.yaml_key_selection,
                'transaction_id': generate_transaction_id()
            }
            
            # Validate source
            if not validate_data_source(config['source']):
                print(f"❌ Invalid data source: {config['source']}")
                sys.exit(1)
            
            # Validate export requirements
            if not validate_export_requirements(config['export_types']):
                sys.exit(1)
            
            # Load and normalize data
            print(f"\n📊 Loading data from: {config['source']}")
            data_list = load_normalized_data(config['source'])
            
            if not data_list:
                print("❌ No data found in source.")
                sys.exit(1)
            
            print(f"✅ Loaded {len(data_list)} data objects")
            
            # Show processing preview
            preview_processing_plan(data_list, config)
            
            # Execute exports
            results = execute_exports(config, data_list)
            
            # Show final summary
            show_processing_summary(results)
            
            if results['total_success'] > 0:
                print("\n🎉 Export process completed successfully!")
            else:
                print("\n⚠️ Export process completed with issues.")
                sys.exit(1)
                
        else:
            # Interactive mode
            print("🚀 Document Creator - Interactive Mode")
            
            while True:
                config = get_user_input_with_navigation()
                
                # Check if user wants to exit to main menu
                if config is None:
                    print("🔙 Returning to main menu...")
                    return  # Return to main menu
                
                # Load and normalize data
                print(f"\n📊 Loading data from: {config['source']}")
                data_list = load_normalized_data(config['source'])
                
                if not data_list:
                    print("❌ No data found in source.")
                    if yes_no_prompt("Try different data source?", default=True):
                        continue
                    else:
                        sys.exit(1)
                
                print(f"✅ Loaded {len(data_list)} data objects")
                
                # Show processing preview
                preview_processing_plan(data_list, config)
                
                # Execute exports
                results = execute_exports(config, data_list)
                
                # Show final summary
                show_processing_summary(results)
                
                # Post-processing menu
                next_action = show_post_processing_menu(results)
                
                if next_action == "exit":
                    if results['total_success'] > 0:
                        print("\n🎉 Export process completed successfully!")
                    else:
                        print("\n⚠️ Export process completed with issues.")
                        sys.exit(1)
                    break
                elif next_action == "restart":
                    continue
                elif next_action == "output_only":
                    # Keep all settings except output directory
                    config.pop('output_dir', None)
                    config.pop('transaction_id', None)
                    continue
                elif next_action == "formats_only":
                    # Keep all settings except export formats and dependent settings
                    config.pop('export_types', None)
                    config.pop('yaml_front_matter', None)
                    config.pop('yaml_key_selection', None)
                    continue
                elif next_action == "source_only":
                    # Keep only non-source-dependent settings
                    source_method = config.get('source_method')
                    config.clear()
                    if source_method:
                        config['source_method'] = source_method
                    continue
        
    except DataSourceError as e:
        print(f"❌ Data source error: {str(e)}")
        sys.exit(1)
    except DocumentCreatorError as e:
        print(f"❌ Export error: {str(e)}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        logging.exception("Unexpected error occurred")
        sys.exit(1)


if __name__ == '__main__':
    main()

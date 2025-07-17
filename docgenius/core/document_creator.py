"""
Document Creator: Convert data sources to various document formats.

This module handles the document creation functionality for the DocGenius toolkit.
It provides both interactive and argument-based usage for converting
data sources (CSV, JSON, APIs) to various document formats.
"""

import argparse
import sys
import logging
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
            # Handle other formats as needed
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
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

def interactive_yaml_key_selection(*args, **kwargs):
    """Backward compatibility function for YAML key selection."""
    return None  # Simplified for now

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

def setup_logging():
    """Setup logging using new utilities structure."""
    configurator = LoggingConfigurator()
    return configurator.setup_application_logging(log_level='INFO')

def generate_transaction_id():
    """Generate transaction ID."""
    import uuid
    return str(uuid.uuid4())[:8]

def get_default_output_directory():
    """Get default output directory."""
    return str(Path.cwd() / 'output')

def yes_no_prompt(message: str) -> bool:
    """Yes/no prompt using new dialog utilities."""
    return MessageDialogs.show_yes_no("Confirm", message)

def prompt_user_choice(message: str, choices: list) -> str:
    """Prompt user for choice."""
    return MessageDialogs.show_choice("Select Option", message, choices)

def select_folder_with_dialog() -> Optional[str]:
    """Select folder with dialog."""
    result = FileDialogs.select_directory("Select Output Directory")
    return result.selected_path if result.success else None

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
    Open a file selection dialog using new dialog utilities.
    
    Returns:
        Selected file path or None if cancelled/failed
    """
    print("Opening file selection dialog...")
    try:
        result = FileDialogs.select_file(
            title="Select your data file",
            file_types=[
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"), 
                ("All files", "*.*")
            ]
        )
        
        if result.success and result.selected_path:
            print(f"Selected file: {result.selected_path}")
            return result.selected_path
        else:
            print("No file selected.")
            return None
            
    except Exception as e:
        print(f"❌ Error opening file dialog: {e}")
        logging.error(f"Error opening file dialog: {e}")
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
    
    Returns:
        Dictionary containing user configuration
    """
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
            show_input_help("source_method", options)
            
            choice = prompt_user_choice(
                "Choose input method:",
                options,
                default="Type file path/URL manually"
            )
            
            if choice == "Browse for file":
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
    default_output = get_default_output_directory(transaction_id)
    
    options = [f"Use default ({default_output})", "Type custom path", "Browse for folder"]
    
    while True:
        try:
            user_input = input("\nChoose output directory (1/2/3) or 'help'/'back': ").strip()
            
            if user_input.lower() == 'help':
                show_input_help("output_method", options)
                continue
            elif user_input.lower() == 'back':
                return "export_formats"
            elif user_input == '1':
                config['output_dir'] = str(default_output)
                config['transaction_id'] = transaction_id
                return "markdown_config" if 'markdown' in config['export_types'] else "complete"
            elif user_input == '2':
                custom_path = input("Enter output directory path: ").strip()
                if custom_path:
                    config['output_dir'] = custom_path
                    config['transaction_id'] = transaction_id
                    return "markdown_config" if 'markdown' in config['export_types'] else "complete"
                else:
                    print("❌ Please enter a valid path.")
                    continue
            elif user_input == '3':
                print("\nOpening folder selection dialog...")
                selected_folder = select_folder_with_dialog("Select Output Folder")
                if selected_folder:
                    print(f"✅ Selected folder: {selected_folder}")
                    config['output_dir'] = selected_folder
                    config['transaction_id'] = transaction_id
                    return "markdown_config" if 'markdown' in config['export_types'] else "complete"
                else:
                    print("❌ No folder selected.")
                    continue
            else:
                print("❌ Please choose 1, 2, or 3.")
                show_input_help("output_method", options)
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
    
    while True:
        try:
            user_input = input("\nInclude YAML front matter? (y/n) or 'help'/'back': ").strip().lower()
            
            if user_input == 'help':
                show_input_help("yaml_front_matter")
                continue
            elif user_input == 'back':
                return "output_method"
            elif user_input in ['y', 'yes', '1']:
                config['yaml_front_matter'] = True
                break
            elif user_input in ['n', 'no', '0']:
                config['yaml_front_matter'] = False
                config['yaml_key_selection'] = 'none'
                return "complete"
            else:
                print("❌ Please enter 'y' for yes or 'n' for no.")
                continue
                
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
    
    # YAML key selection
    if config['yaml_front_matter']:
        options = ["All keys", "Select specific keys"]
        
        while True:
            try:
                user_input = input("\nYAML front matter keys (1/2) or 'help'/'back': ").strip()
                
                if user_input == 'help':
                    show_input_help("yaml_keys", options)
                    continue
                elif user_input == 'back':
                    continue  # Go back to YAML front matter question
                elif user_input == '1':
                    config['yaml_key_selection'] = 'all'
                    return "complete"
                elif user_input == '2':
                    config['yaml_key_selection'] = 'select'
                    return "complete"
                else:
                    print("❌ Please choose 1 or 2.")
                    show_input_help("yaml_keys", options)
                    continue
                    
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
                # Handle YAML key selection for Markdown
                selected_yaml_keys = None
                if config.get('yaml_key_selection') == 'select':
                    selected_yaml_keys = interactive_yaml_key_selection(data_list)
                
                files = export_to_markdown(
                    data_list,
                    config['output_dir'],
                    filename_key=config.get('filename_key'),
                    include_yaml_front_matter=config.get('yaml_front_matter', True),
                    selected_yaml_keys=selected_yaml_keys,
                    transaction_id=config.get('transaction_id')
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

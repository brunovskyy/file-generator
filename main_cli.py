"""
Document Creator CLI: Convert data sources to various document formats.

This is the main CLI entry point for the Document Creator toolkit.
It provides both interactive and argument-based usage for converting
data sources (CSV, JSON, APIs) to various document formats.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Import toolkit modules
from json_to_file.source_to_json import (
    load_normalized_data,
    validate_data_source,
    DataSourceError
)
from json_to_file.markdown_export import (
    export_to_markdown,
    interactive_yaml_key_selection,
    MarkdownExportError
)
from json_to_file.pdf_export import (
    export_to_pdf,
    check_pdf_requirements,
    get_missing_requirements as get_pdf_missing_requirements,
    PDFExportError
)
from json_to_file.word_export import (
    export_to_word,
    check_word_requirements,
    get_missing_requirements as get_word_missing_requirements,
    WordExportError
)
from json_to_file.utils import (
    setup_logging,
    generate_transaction_id,
    get_default_output_directory,
    yes_no_prompt,
    prompt_user_choice,
    select_folder_with_dialog,
    DocumentCreatorError
)


def select_file_with_dialog() -> Optional[str]:
    """
    Open a file selection dialog using tkinter.
    
    Returns:
        Selected file path or None if cancelled/failed
    """
    try:
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(
            title="Select your data file",
            filetypes=[
                ("All supported", "*.json;*.csv"),
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        root.destroy()
        return file_path if file_path else None
        
    except Exception as e:
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


def get_user_input_interactive() -> Dict[str, Any]:
    """
    Get user input through interactive prompts.
    
    Returns:
        Dictionary containing user configuration
    """
    config = {}
    
    # Get data source
    print("\n" + "="*50)
    print("DATA SOURCE SELECTION")
    print("="*50)
    
    source_method = prompt_user_choice(
        "How would you like to provide your data source?",
        ["Enter path or URL", "Select file using dialog"],
        default="Enter path or URL"
    )
    
    if source_method == "Select file using dialog":
        config['source'] = select_file_with_dialog()
        if not config['source']:
            print("❌ No file selected. Exiting.")
            sys.exit(1)
    else:
        while True:
            source_input = input("\nEnter the path or URL to your data source: ").strip()
            if validate_data_source(source_input):
                config['source'] = source_input
                break
            else:
                print("❌ Invalid path or URL. Please try again.")
    
    # Get export types
    print("\n" + "="*50)
    print("EXPORT FORMAT SELECTION")
    print("="*50)
    
    available_formats = ["markdown", "pdf", "word"]
    selected_formats = []
    
    print("Available export formats:")
    for i, fmt in enumerate(available_formats, 1):
        print(f"  {i}. {fmt.title()}")
    
    while True:
        selection = input("\nEnter format numbers separated by spaces (e.g., 1 2): ").strip()
        try:
            indices = [int(x) - 1 for x in selection.split()]
            if all(0 <= i < len(available_formats) for i in indices):
                selected_formats = [available_formats[i] for i in indices]
                break
            else:
                print("❌ Invalid selection. Please enter valid numbers.")
        except ValueError:
            print("❌ Invalid input. Please enter numbers separated by spaces.")
    
    config['export_types'] = selected_formats
    
    # Validate export requirements
    if not validate_export_requirements(selected_formats):
        print("\n❌ Cannot proceed without required packages.")
        sys.exit(1)
    
    # Get output directory
    print("\n" + "="*50)
    print("OUTPUT CONFIGURATION")
    print("="*50)
    
    transaction_id = generate_transaction_id()
    default_output = get_default_output_directory(transaction_id)
    
    output_choice = prompt_user_choice(
        f"Output directory:",
        [f"Use default ({default_output})", "Enter custom path", "Browse for folder"],
        default=f"Use default ({default_output})"
    )
    
    if output_choice.startswith("Use default"):
        config['output_dir'] = str(default_output)
    elif output_choice == "Browse for folder":
        print("\n🔍 Opening folder selection dialog...")
        print("💡 If no dialog appears, check that tkinter is installed and you're not in a headless environment.")
        
        selected_folder = select_folder_with_dialog("Select Output Folder")
        if selected_folder:
            print(f"✅ Selected folder: {selected_folder}")
            config['output_dir'] = selected_folder
        else:
            print("❌ No folder selected or dialog failed.")
            print("💡 Falling back to default Downloads folder.")
            config['output_dir'] = str(default_output)
    else:
        config['output_dir'] = input("Enter output directory path: ").strip()
    
    config['transaction_id'] = transaction_id
    
    # Configure Markdown-specific options
    if 'markdown' in selected_formats:
        print("\n" + "="*50)
        print("MARKDOWN CONFIGURATION")
        print("="*50)
        
        config['yaml_front_matter'] = yes_no_prompt(
            "Include YAML front matter in Markdown files?",
            default=True
        )
        
        if config['yaml_front_matter']:
            yaml_selection = prompt_user_choice(
                "YAML front matter keys:",
                ["All keys", "Select specific keys"],
                default="All keys"
            )
            
            config['yaml_key_selection'] = 'all' if yaml_selection == "All keys" else 'select'
        else:
            config['yaml_key_selection'] = 'none'
    
    return config


def execute_exports(config: Dict[str, Any], data_list: List[Dict[str, Any]]) -> None:
    """
    Execute the selected export operations.
    
    Args:
        config: User configuration dictionary
        data_list: Normalized data to export
    """
    created_files = []
    
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
            
            created_files.extend(files)
            print(f"✅ {export_type.title()} export completed - {len(files)} files created")
            
        except (MarkdownExportError, PDFExportError, WordExportError) as e:
            print(f"❌ {export_type.title()} export failed: {str(e)}")
            continue
    
    # Summary
    print("\n" + "="*50)
    print("EXPORT SUMMARY")
    print("="*50)
    print(f"Total files created: {len(created_files)}")
    print(f"Output directory: {config['output_dir']}")
    
    if created_files:
        print("\nCreated files:")
        for file_path in created_files:
            print(f"  - {file_path.name}")


def main():
    """Main entry point for the Document Creator CLI."""
    parser = argparse.ArgumentParser(
        description="Document Creator CLI: Convert data sources to various document formats.",
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
                
        else:
            # Interactive mode
            print("🚀 Document Creator CLI - Interactive Mode")
            config = get_user_input_interactive()
        
        # Load and normalize data
        print(f"\n📊 Loading data from: {config['source']}")
        data_list = load_normalized_data(config['source'])
        
        if not data_list:
            print("❌ No data found in source.")
            sys.exit(1)
        
        print(f"✅ Loaded {len(data_list)} data objects")
        
        # Execute exports
        execute_exports(config, data_list)
        
        print("\n🎉 Export process completed successfully!")
        
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

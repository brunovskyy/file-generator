"""
Markdown export functionality for the Document Creator toolkit.

This module provides functions to export normalized data to Markdown format,
including support for YAML front matter with interactive key selection.
"""

import json
try:
    import yaml
except ImportError:
    yaml = None
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import logging
from datetime import datetime

from .utils import (
    sanitize_filename, 
    ensure_directory_exists, 
    is_simple_yaml_value, 
    get_nested_value,
    DocumentCreatorError,
    get_available_filename
)


class MarkdownExportError(DocumentCreatorError):
    """Exception for Markdown export related errors."""
    pass


def export_to_markdown(
    data_list: List[Dict[str, Any]],
    output_directory: str,
    filename_key: Optional[str] = None,
    include_yaml_front_matter: bool = True,
    selected_yaml_keys: Optional[Set[str]] = None,
    flatten_yaml_values: bool = True,
    transaction_id: Optional[str] = None
) -> List[Path]:
    """
    Export a list of dictionaries to individual Markdown files.
    
    Args:
        data_list: List of dictionaries to export
        output_directory: Directory to save Markdown files
        filename_key: Key to use for filename generation
        include_yaml_front_matter: Whether to include YAML front matter
        selected_yaml_keys: Set of keys to include in YAML front matter
        flatten_yaml_values: Whether to flatten complex values in YAML
        transaction_id: Transaction identifier for summary file
        
    Returns:
        List of Path objects for created files
        
    Raises:
        MarkdownExportError: If export fails
    """
    try:
        # Ensure output directory exists
        output_path = ensure_directory_exists(output_directory)
        
        # Validate input data
        if not isinstance(data_list, list):
            raise MarkdownExportError("Data must be a list of dictionaries")
        
        if not data_list:
            raise MarkdownExportError("No data provided for export")
        
        created_files = []
        
        # Export each data object to a Markdown file
        for index, data_object in enumerate(data_list):
            if not isinstance(data_object, dict):
                logging.warning(f"Skipping non-dictionary item at index {index}")
                continue
            
            # Generate filename
            filename = generate_markdown_filename(
                data_object, 
                filename_key, 
                index
            )
            
            # Create markdown content
            markdown_content = create_markdown_content(
                data_object,
                include_yaml_front_matter=include_yaml_front_matter,
                selected_yaml_keys=selected_yaml_keys,
                flatten_yaml_values=flatten_yaml_values
            )
            
            # Write file
            file_path = get_available_filename(output_path / filename, "md")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            created_files.append(file_path)
            logging.info(f"✅ Created: {file_path.name}")
        
        # Create summary file if transaction_id provided
        if transaction_id:
            summary_file = create_summary_file(
                output_path,
                data_list,
                transaction_id,
                {
                    'filename_key': filename_key,
                    'include_yaml_front_matter': include_yaml_front_matter,
                    'selected_yaml_keys': list(selected_yaml_keys) if selected_yaml_keys else None,
                    'flatten_yaml_values': flatten_yaml_values
                }
            )
            created_files.append(summary_file)
        
        return created_files
        
    except Exception as e:
        raise MarkdownExportError(f"Failed to export to Markdown: {str(e)}")


def generate_markdown_filename(
    data_object: Dict[str, Any],
    filename_key: Optional[str],
    index: int
) -> str:
    """
    Generate a filename for a Markdown file based on data object.
    
    Args:
        data_object: Dictionary containing data
        filename_key: Key to use for filename generation
        index: Index of the object in the list
        
    Returns:
        Sanitized filename without extension
    """
    base_filename = None
    
    # Try to get filename from specified key
    if filename_key:
        base_filename = data_object.get(filename_key)
    
    # Try common fallback keys
    if not base_filename:
        fallback_keys = ["name", "title", "filename", "id"]
        for key in fallback_keys:
            if key in data_object and data_object[key]:
                base_filename = data_object[key]
                break
    
    # Use timestamp + index as final fallback
    if not base_filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{timestamp}_{index + 1}"
    
    return sanitize_filename(str(base_filename))


def create_markdown_content(
    data_object: Dict[str, Any],
    include_yaml_front_matter: bool = True,
    selected_yaml_keys: Optional[Set[str]] = None,
    flatten_yaml_values: bool = True
) -> str:
    """
    Create Markdown content from a data object.
    
    Args:
        data_object: Dictionary containing data
        include_yaml_front_matter: Whether to include YAML front matter
        selected_yaml_keys: Set of keys to include in YAML front matter
        flatten_yaml_values: Whether to flatten complex values in YAML
        
    Returns:
        Formatted Markdown content string
    """
    content_parts = []
    
    if include_yaml_front_matter:
        yaml_content = create_yaml_front_matter(
            data_object,
            selected_yaml_keys,
            flatten_yaml_values
        )
        content_parts.append(yaml_content)
    
    # Create main content sections for complex data
    markdown_sections = create_markdown_sections(
        data_object,
        selected_yaml_keys if include_yaml_front_matter else None,
        flatten_yaml_values
    )
    
    if markdown_sections:
        content_parts.extend(markdown_sections)
    
    return "\n".join(content_parts)


def create_yaml_front_matter(
    data_object: Dict[str, Any],
    selected_keys: Optional[Set[str]] = None,
    flatten_complex_values: bool = True
) -> str:
    """
    Create YAML front matter from a data object.
    
    Args:
        data_object: Dictionary containing data
        selected_keys: Set of keys to include (None for all)
        flatten_complex_values: Whether to flatten complex values
        
    Returns:
        YAML front matter string
    """
    yaml_data = {}
    
    # Select which keys to include
    if selected_keys:
        for key in selected_keys:
            value = get_nested_value(data_object, key)
            if value is not None:
                yaml_data[key] = value
    else:
        yaml_data = data_object.copy()
    
    # Process values for YAML compatibility
    processed_yaml_data = {}
    
    for key, value in yaml_data.items():
        if flatten_complex_values and is_simple_yaml_value(value):
            processed_yaml_data[key] = value
        elif not flatten_complex_values:
            processed_yaml_data[key] = value
        # Complex values are excluded when flattening is enabled
    
    # Generate YAML content
    if processed_yaml_data:
        if yaml:
            yaml_content = yaml.dump(
                processed_yaml_data,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=True
            )
        else:
            # Fallback to JSON if PyYAML is not available
            yaml_content = json.dumps(processed_yaml_data, indent=2, ensure_ascii=False)
        return f"---\n{yaml_content}---\n"
    else:
        return "---\n---\n"


def create_markdown_sections(
    data_object: Dict[str, Any],
    excluded_keys: Optional[Set[str]] = None,
    flatten_complex_values: bool = True
) -> List[str]:
    """
    Create Markdown sections for complex data not included in YAML front matter.
    
    Args:
        data_object: Dictionary containing data
        excluded_keys: Keys already included in YAML front matter
        flatten_complex_values: Whether complex values were flattened in YAML
        
    Returns:
        List of Markdown section strings
    """
    sections = []
    
    for key, value in data_object.items():
        # Skip if key was included in YAML front matter
        if excluded_keys and key in excluded_keys:
            continue
        
        # Skip simple values if they should have been in YAML
        if flatten_complex_values and is_simple_yaml_value(value):
            continue
        
        # Create section for complex values
        section_title = key.replace('_', ' ').title()
        sections.append(f"## {section_title}\n")
        
        if isinstance(value, (dict, list)):
            # Format as JSON for complex structures
            json_content = json.dumps(value, indent=2, ensure_ascii=False)
            sections.append(f"```json\n{json_content}\n```\n")
        else:
            # Format as text
            sections.append(f"{str(value)}\n")
    
    return sections


def create_summary_file(
    output_path: Path,
    data_list: List[Dict[str, Any]],
    transaction_id: str,
    export_settings: Dict[str, Any]
) -> Path:
    """
    Create a summary README file for the export.
    
    Args:
        output_path: Directory where files were exported
        data_list: Original data list
        transaction_id: Transaction identifier
        export_settings: Settings used for export
        
    Returns:
        Path to created summary file
    """
    summary_content = [
        "# Markdown Export Summary\n",
        f"**Transaction ID:** {transaction_id}",
        f"**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Files Created:** {len(data_list)}",
        f"**Output Directory:** {output_path}\n",
        "## Export Settings\n"
    ]
    
    for key, value in export_settings.items():
        if value is not None:
            summary_content.append(f"- **{key.replace('_', ' ').title()}:** {value}")
    
    summary_content.append("\n## Files Created\n")
    
    for i, data_object in enumerate(data_list):
        filename = generate_markdown_filename(data_object, export_settings.get('filename_key'), i)
        summary_content.append(f"- {filename}.md")
    
    summary_file = output_path / "README.md"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(summary_content))
    
    return summary_file


def get_available_yaml_keys(data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze data to find all available keys for YAML front matter selection.
    
    Args:
        data_list: List of dictionaries to analyze
        
    Returns:
        Dictionary mapping key paths to example values
    """
    all_keys = {}
    
    for data_object in data_list:
        keys = extract_all_keys(data_object)
        all_keys.update(keys)
    
    return all_keys


def extract_all_keys(data_object: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """
    Extract all keys from a nested dictionary with dot notation.
    
    Args:
        data_object: Dictionary to extract keys from
        prefix: Current key prefix
        
    Returns:
        Dictionary mapping key paths to example values
    """
    keys = {}
    
    for key, value in data_object.items():
        full_key = f"{prefix}.{key}" if prefix else key
        
        if isinstance(value, dict):
            keys.update(extract_all_keys(value, full_key))
        else:
            keys[full_key] = value
    
    return keys


def display_yaml_key_selection_ui(available_keys: Dict[str, Any]) -> Set[str]:
    """
    Display an interactive UI for selecting YAML keys.
    
    Args:
        available_keys: Dictionary of available keys with example values
        
    Returns:
        Set of selected key paths
    """
    print("\n" + "="*50)
    print("YAML FRONT MATTER KEY SELECTION")
    print("="*50)
    print("\nAvailable keys in your data:")
    
    key_list = list(available_keys.keys())
    
    # Display keys with examples
    for i, key in enumerate(key_list, 1):
        example_value = available_keys[key]
        value_preview = str(example_value)[:50] + "..." if len(str(example_value)) > 50 else str(example_value)
        print(f"{i:2d}. {key:30} (e.g., {value_preview})")
    
    print("\nSelection options:")
    print("  - Enter numbers separated by spaces (e.g., 1 3 5)")
    print("  - Enter 'all' to select all keys")
    print("  - Enter 'none' to skip YAML front matter")
    print("  - Enter 'quit' to exit")
    
    while True:
        user_input = input("\nEnter your selection: ").strip()
        
        if user_input.lower() == 'quit':
            exit(0)
        elif user_input.lower() == 'none':
            return set()
        elif user_input.lower() == 'all':
            return set(key_list)
        else:
            try:
                # Parse number selections
                selected_indices = [int(x) - 1 for x in user_input.split()]
                
                # Validate indices
                if all(0 <= i < len(key_list) for i in selected_indices):
                    selected_keys = {key_list[i] for i in selected_indices}
                    
                    # Show selection for confirmation
                    print("\nYou selected:")
                    for key in selected_keys:
                        print(f"  - {key}")
                    
                    confirm = input("\nConfirm selection? (y/n): ").strip().lower()
                    if confirm in ['y', 'yes']:
                        return selected_keys
                    else:
                        print("Please make a new selection.")
                else:
                    print("Invalid selection. Please enter valid numbers.")
            except ValueError:
                print("Invalid input. Please enter numbers separated by spaces.")


def interactive_yaml_key_selection(data_list: List[Dict[str, Any]]) -> Optional[Set[str]]:
    """
    Interactive selection of YAML keys from data.
    
    Args:
        data_list: List of dictionaries to analyze
        
    Returns:
        Set of selected keys, or None if YAML front matter is disabled
    """
    if not data_list:
        return None
    
    available_keys = get_available_yaml_keys(data_list)
    
    if not available_keys:
        print("No keys found in data for YAML front matter.")
        return None
    
    return display_yaml_key_selection_ui(available_keys)

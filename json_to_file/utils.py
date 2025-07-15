"""
Shared utility functions for the Document Creator toolkit.

This module provides common functionality used across different export modules,
including validation, file handling, and data processing utilities.
"""

import re
import os
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import datetime
import json


class DocumentCreatorError(Exception):
    """Base exception for Document Creator related errors."""
    pass


def setup_logging(level: str = "INFO") -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='[%(levelname)s] %(message)s'
    )


def validate_file_path(file_path: str) -> bool:
    """
    Validate if a file path exists and is accessible.
    
    Args:
        file_path: Path to validate
        
    Returns:
        True if path is valid and accessible, False otherwise
    """
    try:
        path = Path(file_path).expanduser().resolve()
        return path.exists() and path.is_file()
    except Exception:
        return False


def validate_url(url: str) -> bool:
    """
    Validate if a URL is properly formatted.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def validate_output_directory(directory_path: str) -> bool:
    """
    Validate if an output directory can be created or already exists.
    
    Args:
        directory_path: Path to validate
        
    Returns:
        True if directory is valid, False otherwise
    """
    if not directory_path:
        return False
    
    try:
        path = Path(directory_path).expanduser().resolve()
        return path.parent.exists() or path.exists()
    except Exception:
        return False


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize a filename to be safe for cross-platform filesystem use.
    
    Args:
        filename: Original filename
        max_length: Maximum length for the filename
        
    Returns:
        Sanitized filename safe for filesystem use
    """
    if not filename:
        return "untitled"
    
    # Convert to string and remove illegal characters
    filename = str(filename)
    filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
    
    # Remove control characters and extra whitespace
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    filename = filename.strip()
    
    # Ensure filename is not empty after sanitization
    if not filename:
        filename = "untitled"
    
    # Truncate to max length while preserving extension
    if len(filename) > max_length:
        name_part, ext_part = os.path.splitext(filename)
        max_name_length = max_length - len(ext_part)
        filename = name_part[:max_name_length] + ext_part
    
    return filename


def ensure_directory_exists(directory_path: str) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        Path object for the created/existing directory
        
    Raises:
        DocumentCreatorError: If directory cannot be created
    """
    try:
        path = Path(directory_path).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path
    except Exception as e:
        raise DocumentCreatorError(f"Cannot create directory {directory_path}: {str(e)}")


def generate_transaction_id() -> str:
    """
    Generate a unique transaction identifier based on current timestamp.
    
    Returns:
        Formatted timestamp string suitable for use as an identifier
    """
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def get_default_output_directory(transaction_id: Optional[str] = None) -> Path:
    """
    Get the default output directory path.
    
    Args:
        transaction_id: Optional transaction identifier for subdirectory
        
    Returns:
        Path object for the default output directory
    """
    user_home = Path.home()
    downloads_dir = user_home / "Downloads"
    
    if transaction_id:
        return downloads_dir / str(transaction_id)
    else:
        return downloads_dir / "document_creator_output"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def get_file_extension(filename: str) -> str:
    """
    Get the file extension from a filename.
    
    Args:
        filename: Name of the file
        
    Returns:
        File extension (without the dot)
    """
    return Path(filename).suffix.lstrip('.')


def is_simple_yaml_value(value: Any) -> bool:
    """
    Check if a value is simple enough to be embedded directly in YAML front matter.
    
    Args:
        value: Value to check
        
    Returns:
        True if value is simple enough for YAML, False otherwise
    """
    # Simple scalar types
    if isinstance(value, (str, int, float, bool, type(None))):
        return True
    
    # Simple lists (short and containing only simple values)
    if isinstance(value, list):
        return (len(value) <= 5 and 
                all(isinstance(item, (str, int, float, bool, type(None))) for item in value))
    
    # Simple dictionaries (short and containing only simple values)
    if isinstance(value, dict):
        return (len(value) <= 5 and 
                all(is_simple_yaml_value(val) for val in value.values()))
    
    return False


def get_nested_value(data: Dict[str, Any], key_path: str) -> Any:
    """
    Get a value from a nested dictionary using dot-separated key path.
    
    Args:
        data: Dictionary to search in
        key_path: Dot-separated path to the desired value (e.g., 'user.profile.name')
        
    Returns:
        The value at the specified path, or None if not found
    """
    if not key_path:
        return data
    
    keys = key_path.split('.')
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    
    return current


def flatten_dict(data: Dict[str, Any], prefix: str = "", separator: str = "_") -> Dict[str, Any]:
    """
    Flatten a nested dictionary into a single-level dictionary.
    
    Args:
        data: Dictionary to flatten
        prefix: Prefix for keys
        separator: Separator between nested keys
        
    Returns:
        Flattened dictionary
    """
    flattened = {}
    
    for key, value in data.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key
        
        if isinstance(value, dict):
            flattened.update(flatten_dict(value, new_key, separator))
        else:
            flattened[new_key] = value
    
    return flattened


def build_curl_command(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    query_params: Optional[Dict[str, Any]] = None,
    body: Optional[Dict[str, Any]] = None
) -> str:
    """
    Build a cURL command string from request parameters.
    
    Args:
        url: Request URL
        method: HTTP method
        headers: HTTP headers
        query_params: Query parameters
        body: Request body
        
    Returns:
        Formatted cURL command string
    """
    curl_parts = [f"curl -X {method.upper()}"]
    
    # Add headers
    if headers:
        for header_name, header_value in headers.items():
            curl_parts.append(f'-H "{header_name}: {header_value}"')
    
    # Add query parameters to URL
    if query_params:
        query_string = "&".join(f"{k}={v}" for k, v in query_params.items())
        url = f"{url}?{query_string}"
    
    # Add body for POST/PUT requests
    if body and method.upper() in ["POST", "PUT", "PATCH"]:
        json_body = json.dumps(body)
        curl_parts.append(f'-d \'{json_body}\'')
        curl_parts.append('-H "Content-Type: application/json"')
    
    # Add URL (always last)
    curl_parts.append(f'"{url}"')
    
    return " ".join(curl_parts)


def prompt_user_choice(
    prompt: str,
    choices: List[str],
    default: Optional[str] = None,
    case_sensitive: bool = False
) -> str:
    """
    Prompt user to select from a list of choices.
    
    Args:
        prompt: Question to display to user
        choices: List of valid choices
        default: Default choice if user enters nothing
        case_sensitive: Whether choices are case-sensitive
        
    Returns:
        Selected choice
    """
    if not case_sensitive:
        choices_lower = [choice.lower() for choice in choices]
    
    while True:
        print(f"\n{prompt}")
        for i, choice in enumerate(choices):
            marker = " (default)" if choice == default else ""
            print(f"  {i+1}. {choice}{marker}")
        
        user_input = input("Enter your choice: ").strip()
        
        if not user_input and default:
            return default
        
        # Check if input is a number
        try:
            choice_index = int(user_input) - 1
            if 0 <= choice_index < len(choices):
                return choices[choice_index]
        except ValueError:
            pass
        
        # Check if input matches a choice
        if case_sensitive:
            if user_input in choices:
                return user_input
        else:
            if user_input.lower() in choices_lower:
                return choices[choices_lower.index(user_input.lower())]
        
        print("Invalid choice. Please try again.")


def yes_no_prompt(prompt: str, default: bool = True) -> bool:
    """
    Prompt user for a yes/no answer.
    
    Args:
        prompt: Question to display to user
        default: Default answer if user enters nothing
        
    Returns:
        True for yes, False for no
    """
    default_text = "y" if default else "n"
    full_prompt = f"{prompt} (y/n) [{default_text}]: "
    
    while True:
        user_input = input(full_prompt).strip().lower()
        
        if not user_input:
            return default
        
        if user_input in ['y', 'yes']:
            return True
        elif user_input in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' or 'n'.")


def get_available_filename(base_path: Path, extension: str = "") -> Path:
    """
    Get an available filename by appending numbers if file exists.
    
    Args:
        base_path: Base path for the file
        extension: File extension to append
        
    Returns:
        Available Path object
    """
    if extension and not extension.startswith('.'):
        extension = f'.{extension}'
    
    counter = 1
    current_path = base_path.with_suffix(extension)
    
    while current_path.exists():
        stem = base_path.stem
        current_path = base_path.with_name(f"{stem}_{counter}").with_suffix(extension)
        counter += 1
    
    return current_path


def select_folder_with_dialog(title: str = "Select Output Folder") -> Optional[str]:
    """
    Open a folder selection dialog using tkinter.
    
    Args:
        title: Title for the dialog window
        
    Returns:
        Selected folder path or None if cancelled/failed
    """
    print(f"🔍 [DEBUG] Attempting to open folder dialog: '{title}'")
    
    try:
        print("🔍 [DEBUG] Importing tkinter...")
        import tkinter as tk
        from tkinter import filedialog
        print("🔍 [DEBUG] tkinter imported successfully")
        
        print("🔍 [DEBUG] Creating tkinter root window...")
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        print("🔍 [DEBUG] Root window created and hidden")
        
        print("🔍 [DEBUG] Opening folder dialog...")
        folder_path = filedialog.askdirectory(
            title=title,
            mustexist=False  # Allow selection of new folders
        )
        
        print(f"🔍 [DEBUG] Dialog returned: '{folder_path}'")
        
        print("🔍 [DEBUG] Destroying root window...")
        root.destroy()
        
        if folder_path:
            print(f"✅ [SUCCESS] Folder selected: {folder_path}")
            return folder_path
        else:
            print("ℹ️  [INFO] User cancelled folder selection")
            return None
        
    except ImportError as e:
        print(f"❌ [ERROR] tkinter not available: {e}")
        print("💡 [HINT] Try: pip install tk")
        logging.error(f"tkinter import failed: {e}")
        return None
    except Exception as e:
        print(f"❌ [ERROR] Unexpected error opening folder dialog: {e}")
        print(f"🔍 [DEBUG] Error type: {type(e).__name__}")
        logging.error(f"Error opening folder dialog: {e}")
        return None


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

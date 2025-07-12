"""
Validation utilities for the Document Creator application.
"""

import re
from pathlib import Path
from urllib.parse import urlparse

def file_or_url_validator(path: str) -> bool:
    """Validate if the given path is a file or a URL."""
    if path.startswith("http://") or path.startswith("https://"):
        return True
    try:
        p = Path(path).expanduser().resolve()
        return p.exists()
    except Exception:
        return False

def output_dir_validator(path: str) -> bool:
    """Validate if the output directory path is valid and can be created."""
    try:
        p = Path(path).expanduser().resolve()
        # Try to create the path to test validity
        p.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False

def filename_validator(filename: str) -> bool:
    """Validate if a filename is safe for filesystem use."""
    if not filename or len(filename) > 255:
        return False
    
    # Check for invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    if re.search(invalid_chars, filename):
        return False
        
    # Check for reserved names on Windows
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5',
        'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4',
        'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    if filename.upper() in reserved_names:
        return False
        
    return True

# Validate if a string is a valid URL.
def url_validator(url: str) -> bool:
    """Validate if a string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

# Validate if an HTTP method is valid.
def api_method_validator(method: str) -> bool:
    """Validate if an HTTP method is valid."""
    valid_methods = {'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'}
    return method.upper() in valid_methods

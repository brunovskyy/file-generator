# Configuration constants and settings for the Document Creator

import datetime
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class AppSettings:
    """Application-wide settings"""
    default_output_base: str = "Downloads"
    default_timestamp_format: str = "%Y-%m-%d_%H-%M-%S"
    log_format: str = '[%(levelname)s] %(message)s'
    max_filename_length: int = 255
    
@dataclass 
class ExportConfig:
    """Configuration for JSON to Markdown export process"""
    json_input_path_or_url: Optional[str] = None
    output_directory_path: Optional[str] = None
    flatten_repetition: bool = True
    filename_key: Optional[str] = None
    transaction_identifier: Optional[str] = None
    yaml_key_path: Optional[str] = None
    api_method: Optional[str] = None
    api_headers: Optional[Dict[str, str]] = None
    api_query: Optional[Dict[str, str]] = None
    api_body: Optional[str] = None
    summary_dict: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default values after creation"""
        if self.api_headers is None:
            self.api_headers = {}
        if self.api_query is None:
            self.api_query = {}

# Application constants
APP_SETTINGS = AppSettings()

# Default filename alternatives when no filename_key is provided
DEFAULT_FILENAME_KEYS = ["name", "title", "id", "slug"]

# File extensions to attempt when detecting JSON files
JSON_EXTENSIONS = [".json", ".jsonl"]

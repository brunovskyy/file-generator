"""
Data source normalization module for the Document Creator toolkit.

This module provides functions to load and normalize data from various sources 
(CSV, JSON, APIs) into a standardized list of Python dictionaries format.
"""

import json
import csv
import requests
from io import StringIO
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import logging


class DataSourceError(Exception):
    """Custom exception for data source related errors."""
    pass


def load_normalized_data(
    source_path_or_url: str,
    file_format: Optional[str] = None,
    encoding: str = "utf-8",
    api_method: Optional[str] = None,
    api_headers: Optional[Dict[str, str]] = None,
    api_query: Optional[Dict[str, Any]] = None,
    api_body: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Load and normalize data from various sources into a list of dictionaries.
    
    Args:
        source_path_or_url: Path to local file or URL to remote data source
        file_format: File format ('json', 'csv', 'api'). Auto-detected if None
        encoding: File encoding for local files
        api_method: HTTP method for API calls ('GET', 'POST', etc.)
        api_headers: HTTP headers for API calls
        api_query: Query parameters for API calls
        api_body: Request body for API calls
        
    Returns:
        List of dictionaries containing normalized data
        
    Raises:
        DataSourceError: If data cannot be loaded or normalized
    """
    try:
        # Auto-detect format if not specified
        if file_format is None:
            file_format = detect_source_format(source_path_or_url)
        
        # Load data based on format
        if file_format == "json":
            return load_json_objects(source_path_or_url, encoding=encoding)
        elif file_format == "csv":
            return load_csv_objects(source_path_or_url, encoding=encoding)
        elif file_format == "api":
            return load_api_objects(
                source_path_or_url, 
                method=api_method,
                headers=api_headers,
                query=api_query,
                body=api_body
            )
        else:
            raise DataSourceError(f"Unsupported file format: {file_format}")
            
    except Exception as e:
        raise DataSourceError(f"Failed to load data from {source_path_or_url}: {str(e)}")


def detect_source_format(source_path_or_url: str) -> str:
    """
    Detect the format of a data source based on its characteristics.
    
    Args:
        source_path_or_url: Path or URL to analyze
        
    Returns:
        String indicating the detected format ('json', 'csv', 'api')
    """
    if not source_path_or_url:
        raise DataSourceError("No data source provided")
    
    # Convert Path objects to strings for compatibility
    source_str = str(source_path_or_url)
    
    # Check for URLs
    if source_str.startswith(("http://", "https://")):
        if "/api/" in source_str or source_str.rstrip("/").endswith("/api"):
            return "api"
        elif source_str.lower().endswith(".json"):
            return "json"
        elif source_str.lower().endswith(".csv"):
            return "csv"
        else:
            return "api"  # Default to API for unknown URLs
    
    # Check local file extensions
    if source_str.lower().endswith(".json"):
        return "json"
    elif source_str.lower().endswith(".csv"):
        return "csv"
    else:
        raise DataSourceError(f"Cannot detect format for: {source_path_or_url}")


def load_json_objects(
    json_path_or_url: str, 
    encoding: str = "utf-8"
) -> List[Dict[str, Any]]:
    """
    Load JSON data from a file or URL.
    
    Args:
        json_path_or_url: Path to JSON file or URL
        encoding: File encoding for local files
        
    Returns:
        List of dictionaries from JSON data
        
    Raises:
        DataSourceError: If JSON cannot be loaded or is not a list
    """
    try:
        # Convert Path objects to strings for compatibility
        json_str = str(json_path_or_url)
        
        if json_str.startswith(("http://", "https://")):
            response = requests.get(json_str)
            response.raise_for_status()
            data = response.json()
        else:
            with open(json_str, encoding=encoding) as f:
                data = json.load(f)
        
        if not isinstance(data, list):
            raise DataSourceError("JSON root must be a list of objects")
        
        return data
        
    except requests.RequestException as e:
        raise DataSourceError(f"Failed to fetch JSON from URL: {str(e)}")
    except json.JSONDecodeError as e:
        raise DataSourceError(f"Invalid JSON format: {str(e)}")
    except FileNotFoundError:
        raise DataSourceError(f"JSON file not found: {json_path_or_url}")


def load_csv_objects(
    csv_path_or_url: str, 
    encoding: str = "utf-8"
) -> List[Dict[str, Any]]:
    """
    Load CSV data from a file or URL and convert to normalized dictionaries.
    
    Args:
        csv_path_or_url: Path to CSV file or URL
        encoding: File encoding for local files
        
    Returns:
        List of dictionaries with nested structure based on underscore-separated columns
        
    Raises:
        DataSourceError: If CSV cannot be loaded or processed
    """
    try:
        # Convert Path objects to strings for compatibility
        csv_str = str(csv_path_or_url)
        
        if csv_str.startswith(("http://", "https://")):
            response = requests.get(csv_str)
            response.raise_for_status()
            csvfile = StringIO(response.text)
        else:
            csvfile = open(csv_str, newline='', encoding=encoding)
        
        reader = csv.DictReader(csvfile)
        object_list = [convert_csv_row_to_nested_object(row) for row in reader]
        
        if not csv_str.startswith(("http://", "https://")):
            csvfile.close()
        
        return object_list
        
    except requests.RequestException as e:
        raise DataSourceError(f"Failed to fetch CSV from URL: {str(e)}")
    except FileNotFoundError:
        raise DataSourceError(f"CSV file not found: {csv_path_or_url}")
    except Exception as e:
        raise DataSourceError(f"Error processing CSV: {str(e)}")


def load_api_objects(
    api_url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    query: Optional[Dict[str, Any]] = None,
    body: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Load data from an API endpoint.
    
    Args:
        api_url: URL of the API endpoint
        method: HTTP method (GET, POST, etc.)
        headers: HTTP headers to include in request
        query: Query parameters to include in request
        body: Request body for POST/PUT requests
        
    Returns:
        List of dictionaries from API response
        
    Raises:
        DataSourceError: If API request fails or returns invalid data
    """
    try:
        response = requests.request(
            method=method or "GET",
            url=api_url,
            headers=headers or {},
            params=query or {},
            json=body if body else None
        )
        response.raise_for_status()
        
        data = response.json()
        
        if not isinstance(data, list):
            raise DataSourceError("API response must be a list of objects")
        
        return data
        
    except requests.RequestException as e:
        raise DataSourceError(f"API request failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise DataSourceError(f"Invalid JSON response from API: {str(e)}")


def convert_csv_row_to_nested_object(csv_row_dict: Dict[str, str]) -> Dict[str, Any]:
    """
    Convert a flat CSV row dictionary into a nested dictionary.
    
    Column names with underscores are converted to nested structure.
    Example: {"company_name": "Acme"} -> {"company": {"name": "Acme"}}
    
    Args:
        csv_row_dict: Dictionary representing a single CSV row
        
    Returns:
        Nested dictionary with structure based on underscore-separated keys
    """
    nested_object = {}
    
    for column_name, column_value in csv_row_dict.items():
        if not column_name:  # Skip empty column names
            continue
            
        key_path = column_name.split('_')
        current_level = nested_object
        
        for key_index, key_part in enumerate(key_path):
            if key_index == len(key_path) - 1:
                # Last key in path - assign the value
                current_level[key_part] = column_value
            else:
                # Intermediate key - create nested dict if needed
                if key_part not in current_level:
                    current_level[key_part] = {}
                current_level = current_level[key_part]
    
    return nested_object


def validate_data_source(source_path_or_url: str) -> bool:
    """
    Validate if a data source path or URL is accessible.
    
    Args:
        source_path_or_url: Path or URL to validate
        
    Returns:
        True if source is accessible, False otherwise
    """
    try:
        if source_path_or_url.startswith(("http://", "https://")):
            response = requests.head(source_path_or_url, timeout=10)
            return response.status_code == 200
        else:
            return Path(source_path_or_url).exists()
    except:
        return False

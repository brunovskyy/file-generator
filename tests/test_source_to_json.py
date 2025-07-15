"""
Unit tests for the source_to_json module.

Unit tests focus on testing individual functions in isolation.
They test specific functionality without dependencies on external systems.
"""

import unittest
import json
import csv
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

# Import the modules we're testing
from json_to_file.source_to_json import (
    load_normalized_data,
    detect_source_format,
    load_json_objects,
    load_csv_objects,
    load_api_objects,
    convert_csv_row_to_nested_object,
    validate_data_source,
    DataSourceError
)


class TestSourceToJson(unittest.TestCase):
    """Test cases for data source loading and normalization."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_json_data = [
            {"name": "John", "age": 30, "city": "New York"},
            {"name": "Jane", "age": 25, "city": "San Francisco"}
        ]
        
        self.sample_csv_data = [
            {"name": "John", "profile_age": "30", "address_city": "New York"},
            {"name": "Jane", "profile_age": "25", "address_city": "San Francisco"}
        ]
        
        self.expected_nested_data = [
            {"name": "John", "profile": {"age": "30"}, "address": {"city": "New York"}},
            {"name": "Jane", "profile": {"age": "25"}, "address": {"city": "San Francisco"}}
        ]
    
    def test_detect_source_format_json_file(self):
        """Test detecting JSON file format."""
        self.assertEqual(detect_source_format("data.json"), "json")
        self.assertEqual(detect_source_format("DATA.JSON"), "json")
    
    def test_detect_source_format_csv_file(self):
        """Test detecting CSV file format."""
        self.assertEqual(detect_source_format("data.csv"), "csv")
        self.assertEqual(detect_source_format("DATA.CSV"), "csv")
    
    def test_detect_source_format_api_url(self):
        """Test detecting API URL format."""
        self.assertEqual(detect_source_format("https://api.example.com/data"), "api")
        self.assertEqual(detect_source_format("http://example.com/api/users"), "api")
        self.assertEqual(detect_source_format("https://example.com/some/api"), "api")
    
    def test_detect_source_format_json_url(self):
        """Test detecting JSON URL format."""
        self.assertEqual(detect_source_format("https://example.com/data.json"), "json")
    
    def test_detect_source_format_csv_url(self):
        """Test detecting CSV URL format."""
        self.assertEqual(detect_source_format("https://example.com/data.csv"), "csv")
    
    def test_detect_source_format_empty_source(self):
        """Test error handling for empty source."""
        with self.assertRaises(DataSourceError):
            detect_source_format("")
    
    def test_detect_source_format_unknown(self):
        """Test error handling for unknown format."""
        with self.assertRaises(DataSourceError):
            detect_source_format("unknown.xyz")
    
    def test_convert_csv_row_to_nested_object_basic(self):
        """Test basic CSV row to nested object conversion."""
        csv_row = {"name": "John", "age": "30"}
        expected = {"name": "John", "age": "30"}
        result = convert_csv_row_to_nested_object(csv_row)
        self.assertEqual(result, expected)
    
    def test_convert_csv_row_to_nested_object_nested(self):
        """Test nested CSV row conversion."""
        csv_row = {"name": "John", "profile_age": "30", "address_city": "New York"}
        expected = {
            "name": "John",
            "profile": {"age": "30"},
            "address": {"city": "New York"}
        }
        result = convert_csv_row_to_nested_object(csv_row)
        self.assertEqual(result, expected)
    
    def test_convert_csv_row_to_nested_object_deep_nested(self):
        """Test deep nested CSV row conversion."""
        csv_row = {"user_profile_personal_name": "John", "user_profile_personal_age": "30"}
        expected = {
            "user": {
                "profile": {
                    "personal": {
                        "name": "John",
                        "age": "30"
                    }
                }
            }
        }
        result = convert_csv_row_to_nested_object(csv_row)
        self.assertEqual(result, expected)
    
    def test_convert_csv_row_to_nested_object_empty_column(self):
        """Test handling of empty column names."""
        csv_row = {"name": "John", "": "empty", "age": "30"}
        expected = {"name": "John", "age": "30"}
        result = convert_csv_row_to_nested_object(csv_row)
        self.assertEqual(result, expected)
    
    @patch('json_to_file.source_to_json.Path.exists')
    def test_validate_data_source_local_file_exists(self, mock_exists):
        """Test validating existing local file."""
        mock_exists.return_value = True
        self.assertTrue(validate_data_source("data.json"))
    
    @patch('json_to_file.source_to_json.Path.exists')
    def test_validate_data_source_local_file_not_exists(self, mock_exists):
        """Test validating non-existent local file."""
        mock_exists.return_value = False
        self.assertFalse(validate_data_source("nonexistent.json"))
    
    @patch('json_to_file.source_to_json.requests.head')
    def test_validate_data_source_url_valid(self, mock_head):
        """Test validating valid URL."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_head.return_value = mock_response
        
        self.assertTrue(validate_data_source("https://example.com/data.json"))
    
    @patch('json_to_file.source_to_json.requests.head')
    def test_validate_data_source_url_invalid(self, mock_head):
        """Test validating invalid URL."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_head.return_value = mock_response
        
        self.assertFalse(validate_data_source("https://example.com/nonexistent.json"))
    
    @patch('json_to_file.source_to_json.requests.head')
    def test_validate_data_source_url_exception(self, mock_head):
        """Test handling of URL validation exceptions."""
        mock_head.side_effect = Exception("Network error")
        
        self.assertFalse(validate_data_source("https://example.com/data.json"))
    
    @patch('builtins.open', new_callable=mock_open, read_data='[{"name": "John", "age": 30}]')
    def test_load_json_objects_local_file(self, mock_file):
        """Test loading JSON from local file."""
        result = load_json_objects("data.json")
        expected = [{"name": "John", "age": 30}]
        self.assertEqual(result, expected)
    
    @patch('json_to_file.source_to_json.requests.get')
    def test_load_json_objects_url(self, mock_get):
        """Test loading JSON from URL."""
        mock_response = MagicMock()
        mock_response.json.return_value = [{"name": "John", "age": 30}]
        mock_get.return_value = mock_response
        
        result = load_json_objects("https://example.com/data.json")
        expected = [{"name": "John", "age": 30}]
        self.assertEqual(result, expected)
    
    @patch('builtins.open', new_callable=mock_open, read_data='{"name": "John", "age": 30}')
    def test_load_json_objects_not_list(self, mock_file):
        """Test error handling for non-list JSON."""
        with self.assertRaises(DataSourceError):
            load_json_objects("data.json")
    
    @patch('json_to_file.source_to_json.requests.get')
    def test_load_api_objects_success(self, mock_get):
        """Test successful API data loading."""
        mock_response = MagicMock()
        mock_response.json.return_value = [{"name": "John", "age": 30}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = load_api_objects("https://api.example.com/users")
        expected = [{"name": "John", "age": 30}]
        self.assertEqual(result, expected)
    
    @patch('json_to_file.source_to_json.requests.get')
    def test_load_api_objects_with_params(self, mock_get):
        """Test API data loading with parameters."""
        mock_response = MagicMock()
        mock_response.json.return_value = [{"name": "John", "age": 30}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = load_api_objects(
            "https://api.example.com/users",
            method="GET",
            headers={"Authorization": "Bearer token"},
            query={"limit": 10}
        )
        
        # Verify the request was made with correct parameters
        mock_get.assert_called_once_with(
            method="GET",
            url="https://api.example.com/users",
            headers={"Authorization": "Bearer token"},
            params={"limit": 10},
            json=None
        )
    
    @patch('json_to_file.source_to_json.requests.get')
    def test_load_api_objects_not_list(self, mock_get):
        """Test error handling for non-list API response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"name": "John", "age": 30}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with self.assertRaises(DataSourceError):
            load_api_objects("https://api.example.com/user")


class TestIntegrationSourceToJson(unittest.TestCase):
    """Integration tests for source_to_json module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_json_file = os.path.join(self.test_dir, "test.json")
        self.test_csv_file = os.path.join(self.test_dir, "test.csv")
        
        # Create test JSON file
        json_data = [
            {"name": "John", "age": 30, "city": "New York"},
            {"name": "Jane", "age": 25, "city": "San Francisco"}
        ]
        with open(self.test_json_file, 'w') as f:
            json.dump(json_data, f)
        
        # Create test CSV file
        csv_data = [
            {"name": "John", "profile_age": "30", "address_city": "New York"},
            {"name": "Jane", "profile_age": "25", "address_city": "San Francisco"}
        ]
        with open(self.test_csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["name", "profile_age", "address_city"])
            writer.writeheader()
            writer.writerows(csv_data)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_load_normalized_data_json_file(self):
        """Test loading normalized data from JSON file."""
        result = load_normalized_data(self.test_json_file)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "John")
        self.assertEqual(result[1]["name"], "Jane")
    
    def test_load_normalized_data_csv_file(self):
        """Test loading normalized data from CSV file."""
        result = load_normalized_data(self.test_csv_file)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "John")
        self.assertEqual(result[0]["profile"]["age"], "30")
        self.assertEqual(result[0]["address"]["city"], "New York")
    
    def test_load_normalized_data_auto_detect(self):
        """Test auto-detection of file format."""
        # Test JSON auto-detection
        json_result = load_normalized_data(self.test_json_file)
        self.assertEqual(len(json_result), 2)
        
        # Test CSV auto-detection
        csv_result = load_normalized_data(self.test_csv_file)
        self.assertEqual(len(csv_result), 2)
        self.assertIn("profile", csv_result[0])
    
    def test_load_normalized_data_invalid_file(self):
        """Test error handling for invalid file."""
        with self.assertRaises(DataSourceError):
            load_normalized_data("nonexistent.json")


if __name__ == '__main__':
    unittest.main()

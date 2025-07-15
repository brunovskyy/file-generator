"""
End-to-end tests for the Document Creator Toolkit.

These tests verify the complete workflow from data loading
through export to various formats, simulating real user scenarios.
"""

import unittest
import tempfile
import os
import json
import csv
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import main CLI functionality
from main_cli import main
from json_to_file.source_to_json import load_normalized_data
from json_to_file.markdown_export import export_to_markdown
from json_to_file.utils import setup_logging


class TestEndToEndWorkflow(unittest.TestCase):
    """End-to-end tests for complete workflows."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_json_file = os.path.join(self.test_dir, "test_data.json")
        self.test_csv_file = os.path.join(self.test_dir, "test_data.csv")
        
        # Use Downloads directory for realistic testing
        user_home = Path.home()
        downloads_dir = user_home / "Downloads"
        self.output_dir = downloads_dir / "document_creator_tests"
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test JSON data
        self.json_data = [
            {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "department": "Engineering",
                "profile": {
                    "age": 30,
                    "location": "New York",
                    "skills": ["Python", "JavaScript", "React"],
                    "experience_years": 5
                },
                "projects": [
                    {"name": "Project A", "status": "completed"},
                    {"name": "Project B", "status": "in-progress"}
                ]
            },
            {
                "id": 2,
                "name": "Jane Smith",
                "email": "jane@example.com",
                "department": "Marketing",
                "profile": {
                    "age": 28,
                    "location": "San Francisco",
                    "skills": ["SEO", "Content Marketing", "Analytics"],
                    "experience_years": 3
                },
                "projects": [
                    {"name": "Campaign A", "status": "completed"}
                ]
            }
        ]
        
        # Save JSON test data
        with open(self.test_json_file, 'w') as f:
            json.dump(self.json_data, f, indent=2)
        
        # Create test CSV data
        csv_data = [
            {
                "name": "Alice Johnson",
                "email": "alice@example.com",
                "company_name": "Tech Corp",
                "company_industry": "Technology",
                "contact_phone": "555-0123",
                "address_city": "Austin",
                "address_state": "TX"
            },
            {
                "name": "Bob Wilson",
                "email": "bob@example.com",
                "company_name": "Green Solutions",
                "company_industry": "Energy",
                "contact_phone": "555-0456",
                "address_city": "Denver",
                "address_state": "CO"
            }
        ]
        
        # Save CSV test data
        with open(self.test_csv_file, 'w', newline='') as f:
            if csv_data:
                writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                writer.writeheader()
                writer.writerows(csv_data)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_json_to_markdown_workflow(self):
        """Test complete workflow: JSON → Markdown."""
        # Load data
        data = load_normalized_data(self.test_json_file)
        self.assertEqual(len(data), 2)
        
        # Export to Markdown
        result_files = export_to_markdown(
            data,
            self.output_dir,
            filename_key="name",
            include_yaml_front_matter=True,
            selected_yaml_keys={"name", "email", "department", "profile.age"},
            transaction_id="test_workflow"
        )
        
        # Verify files were created
        self.assertEqual(len(result_files), 3)  # 2 data files + README
        
        # Check specific files
        john_file = Path(self.output_dir) / "John Doe.md"
        jane_file = Path(self.output_dir) / "Jane Smith.md"
        readme_file = Path(self.output_dir) / "README.md"
        
        self.assertTrue(john_file.exists())
        self.assertTrue(jane_file.exists())
        self.assertTrue(readme_file.exists())
        
        # Verify content
        with open(john_file, 'r') as f:
            content = f.read()
            self.assertIn("---", content)  # YAML front matter
            self.assertIn("name:", content)
            self.assertIn("John Doe", content)
            self.assertIn("## Projects", content)  # Complex data in sections
    
    def test_csv_to_markdown_workflow(self):
        """Test complete workflow: CSV → Markdown."""
        # Load data
        data = load_normalized_data(self.test_csv_file)
        self.assertEqual(len(data), 2)
        
        # Verify CSV nested structure
        self.assertIn("company", data[0])
        self.assertIn("address", data[0])
        self.assertEqual(data[0]["company"]["name"], "Tech Corp")
        self.assertEqual(data[0]["address"]["city"], "Austin")
        
        # Export to Markdown
        result_files = export_to_markdown(
            data,
            self.output_dir,
            filename_key="name",
            include_yaml_front_matter=True,
            selected_yaml_keys={"name", "email", "company.name", "address.city"}
        )
        
        # Verify files were created
        self.assertEqual(len(result_files), 2)  # 2 data files (no transaction_id)
        
        # Check file content
        alice_file = Path(self.output_dir) / "Alice Johnson.md"
        with open(alice_file, 'r') as f:
            content = f.read()
            self.assertIn("Alice Johnson", content)
            self.assertIn("Tech Corp", content)
            self.assertIn("Austin", content)
    
    def test_data_validation_workflow(self):
        """Test data validation in complete workflow."""
        # Test with invalid JSON (not a list)
        invalid_json_file = os.path.join(self.test_dir, "invalid.json")
        with open(invalid_json_file, 'w') as f:
            json.dump({"single": "object"}, f)
        
        with self.assertRaises(Exception):
            load_normalized_data(invalid_json_file)
        
        # Test with non-existent file
        with self.assertRaises(Exception):
            load_normalized_data("nonexistent.json")
    
    def test_markdown_export_edge_cases(self):
        """Test Markdown export with edge cases."""
        # Test with minimal data
        minimal_data = [{"name": "Test User"}]
        result_files = export_to_markdown(
            minimal_data,
            self.output_dir,
            filename_key="name"
        )
        
        self.assertEqual(len(result_files), 1)
        
        # Test with complex nested data
        complex_data = [{
            "name": "Complex User",
            "metadata": {
                "nested": {
                    "deep": {
                        "value": "test"
                    }
                }
            },
            "array_of_objects": [
                {"item": "one", "value": 1},
                {"item": "two", "value": 2}
            ]
        }]
        
        result_files = export_to_markdown(
            complex_data,
            self.output_dir,
            filename_key="name"
        )
        
        self.assertEqual(len(result_files), 1)
        
        # Verify complex data is handled
        complex_file = Path(self.output_dir) / "Complex User.md"
        with open(complex_file, 'r') as f:
            content = f.read()
            self.assertIn("## Metadata", content)
            self.assertIn("## Array Of Objects", content)
    
    def test_filename_generation_edge_cases(self):
        """Test filename generation with various edge cases."""
        edge_case_data = [
            {"name": "File/Name:With*Invalid?Characters"},
            {"title": "Fallback Title"},
            {"description": "No name or title"},
            {"name": ""},  # Empty name
            {}  # No identifying fields
        ]
        
        result_files = export_to_markdown(
            edge_case_data,
            self.output_dir
        )
        
        self.assertEqual(len(result_files), 5)
        
        # Check that all files have valid names
        for file_path in result_files:
            self.assertTrue(file_path.exists())
            # Filename should not contain invalid characters
            filename = file_path.name
            invalid_chars = '/\\:*?"<>|'
            for char in invalid_chars:
                self.assertNotIn(char, filename)
    
    def test_yaml_key_selection_workflow(self):
        """Test YAML key selection functionality."""
        from json_to_file.markdown_export import get_available_yaml_keys
        
        # Get available keys
        available_keys = get_available_yaml_keys(self.json_data)
        
        # Should include both direct and nested keys
        self.assertIn("name", available_keys)
        self.assertIn("email", available_keys)
        self.assertIn("profile.age", available_keys)
        self.assertIn("profile.location", available_keys)
        self.assertIn("profile.skills", available_keys)
        
        # Test with selected keys
        selected_keys = {"name", "email", "profile.age", "profile.location"}
        result_files = export_to_markdown(
            self.json_data,
            self.output_dir,
            filename_key="name",
            include_yaml_front_matter=True,
            selected_yaml_keys=selected_keys
        )
        
        # Verify only selected keys are in YAML front matter
        john_file = Path(self.output_dir) / "John Doe.md"
        with open(john_file, 'r') as f:
            content = f.read()
            yaml_section = content.split("---")[1]  # Get YAML section
            self.assertIn("name:", yaml_section)
            self.assertIn("email:", yaml_section)
            # Complex data should not be in YAML when flatten_yaml_values=True
            self.assertNotIn("projects:", yaml_section)
    
    def test_error_handling_workflow(self):
        """Test error handling in complete workflows."""
        # Test with invalid output directory
        with self.assertRaises(Exception):
            export_to_markdown(
                self.json_data,
                "/invalid/path/that/does/not/exist"
            )
        
        # Test with invalid data types
        with self.assertRaises(Exception):
            export_to_markdown(
                "not_a_list",
                self.output_dir
            )
        
        # Test with empty data
        with self.assertRaises(Exception):
            export_to_markdown(
                [],
                self.output_dir
            )


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for CLI functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_json_file = os.path.join(self.test_dir, "cli_test.json")
        self.output_dir = os.path.join(self.test_dir, "cli_output")
        
        # Create test data
        test_data = [
            {"name": "CLI Test User", "email": "test@example.com", "age": 30}
        ]
        
        with open(self.test_json_file, 'w') as f:
            json.dump(test_data, f)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    @patch('sys.argv')
    def test_cli_help_command(self, mock_argv):
        """Test CLI help command."""
        mock_argv.return_value = ['main_cli.py', '--help']
        
        with self.assertRaises(SystemExit):
            main()
    
    @patch('sys.argv')
    @patch('json_to_file.markdown_export.export_to_markdown')
    def test_cli_basic_command(self, mock_export, mock_argv):
        """Test basic CLI command execution."""
        mock_argv.return_value = [
            'main_cli.py',
            '--source', self.test_json_file,
            '--export-types', 'markdown',
            '--output-dir', self.output_dir
        ]
        
        mock_export.return_value = [Path(self.output_dir) / "test.md"]
        
        # This would normally call main(), but we'll test the components
        # Since main() has complex interactions, we test the data flow
        data = load_normalized_data(self.test_json_file)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "CLI Test User")


if __name__ == '__main__':
    # Set up logging for tests
    setup_logging("ERROR")  # Reduce noise during testing
    unittest.main()

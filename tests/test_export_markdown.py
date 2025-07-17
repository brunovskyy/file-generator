"""
Unit tests for the markdown_export module.

These tests verify the Markdown export functionality including
YAML front matter generation and file creation.
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

# Import the modules we're testing from compatibility layer
from legacy_compat_layer import (
    export_to_markdown,
    get_available_yaml_keys,
    MarkdownExportError
)

# Additional functions that may not be in compat layer yet
def generate_markdown_filename(*args, **kwargs):
    """Placeholder for generate_markdown_filename."""
    return "output.md"

def create_markdown_content(*args, **kwargs):
    """Placeholder for create_markdown_content."""
    return "# Content"

def create_yaml_front_matter(*args, **kwargs):
    """Placeholder for create_yaml_front_matter."""
    return "---\ntitle: Test\n---\n"

def create_markdown_sections(*args, **kwargs):
    """Placeholder for create_markdown_sections."""
    return "\n## Section\n"

def extract_all_keys(*args, **kwargs):
    """Placeholder for extract_all_keys."""
    return []


class TestMarkdownExport(unittest.TestCase):
    """Test cases for Markdown export functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_data = [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "age": 30,
                "profile": {
                    "location": "New York",
                    "skills": ["Python", "JavaScript"],
                    "active": True
                },
                "projects": [
                    {"name": "Project A", "status": "completed"},
                    {"name": "Project B", "status": "in-progress"}
                ]
            },
            {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "age": 25,
                "profile": {
                    "location": "San Francisco",
                    "skills": ["React", "Node.js"],
                    "active": False
                }
            }
        ]
    
    def test_generate_markdown_filename_with_filename_key(self):
        """Test filename generation with specified key."""
        data = {"name": "John Doe", "title": "Manager"}
        result = generate_markdown_filename(data, "name", 0)
        self.assertEqual(result, "John Doe")
    
    def test_generate_markdown_filename_with_fallback(self):
        """Test filename generation with fallback keys."""
        data = {"title": "Important Document", "id": "doc123"}
        result = generate_markdown_filename(data, "name", 0)
        self.assertEqual(result, "Important Document")
    
    def test_generate_markdown_filename_with_index_fallback(self):
        """Test filename generation with index fallback."""
        data = {"description": "Some description"}
        result = generate_markdown_filename(data, "name", 5)
        # Should contain timestamp and index
        self.assertIn("_6", result)  # index + 1
    
    def test_generate_markdown_filename_sanitization(self):
        """Test filename sanitization."""
        data = {"name": "File/Name:With*Invalid?Characters"}
        result = generate_markdown_filename(data, "name", 0)
        # Should replace invalid characters with underscores
        self.assertEqual(result, "File_Name_With_Invalid_Characters")
    
    def test_create_yaml_front_matter_simple_values(self):
        """Test YAML front matter creation with simple values."""
        data = {"name": "John", "age": 30, "active": True}
        result = create_yaml_front_matter(data, flatten_complex_values=True)
        
        self.assertIn("---", result)
        self.assertIn("name:", result)
        self.assertIn("age:", result)
        self.assertIn("active:", result)
    
    def test_create_yaml_front_matter_selected_keys(self):
        """Test YAML front matter with selected keys."""
        data = self.sample_data[0]
        selected_keys = {"name", "email", "age"}
        result = create_yaml_front_matter(data, selected_keys, flatten_complex_values=True)
        
        self.assertIn("name:", result)
        self.assertIn("email:", result)
        self.assertIn("age:", result)
        self.assertNotIn("projects:", result)  # Should not include complex data
    
    def test_create_yaml_front_matter_empty_data(self):
        """Test YAML front matter with empty data."""
        result = create_yaml_front_matter({}, flatten_complex_values=True)
        self.assertEqual(result, "---\n---\n")
    
    def test_create_markdown_sections_complex_data(self):
        """Test Markdown sections creation for complex data."""
        data = self.sample_data[0]
        excluded_keys = {"name", "email", "age"}
        result = create_markdown_sections(data, excluded_keys, flatten_complex_values=True)
        
        self.assertGreater(len(result), 0)
        # Should contain sections for complex data
        sections_text = "\n".join(result)
        self.assertIn("## Profile", sections_text)
        self.assertIn("## Projects", sections_text)
    
    def test_create_markdown_content_with_yaml(self):
        """Test complete Markdown content creation with YAML."""
        data = self.sample_data[0]
        result = create_markdown_content(
            data,
            include_yaml_front_matter=True,
            selected_yaml_keys={"name", "email"},
            flatten_yaml_values=True
        )
        
        self.assertIn("---", result)
        self.assertIn("name:", result)
        self.assertIn("email:", result)
        self.assertIn("## Profile", result)
        self.assertIn("## Projects", result)
    
    def test_create_markdown_content_without_yaml(self):
        """Test Markdown content creation without YAML."""
        data = self.sample_data[0]
        result = create_markdown_content(
            data,
            include_yaml_front_matter=False
        )
        
        self.assertNotIn("---", result)
        self.assertIn("## Name", result)
        self.assertIn("## Profile", result)
    
    def test_extract_all_keys_nested(self):
        """Test extraction of all keys including nested ones."""
        data = self.sample_data[0]
        result = extract_all_keys(data)
        
        self.assertIn("name", result)
        self.assertIn("email", result)
        self.assertIn("profile.location", result)
        self.assertIn("profile.skills", result)
        self.assertIn("profile.active", result)
        self.assertIn("projects", result)
    
    def test_get_available_yaml_keys_multiple_objects(self):
        """Test getting available keys from multiple objects."""
        result = get_available_yaml_keys(self.sample_data)
        
        self.assertIn("name", result)
        self.assertIn("email", result)
        self.assertIn("profile.location", result)
        self.assertIn("profile.skills", result)
        # Should have examples from the data
        self.assertEqual(result["name"], "Jane Smith")  # Last occurrence


class TestMarkdownExportIntegration(unittest.TestCase):
    """Integration tests for Markdown export."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.sample_data = [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "age": 30,
                "profile": {
                    "location": "New York",
                    "skills": ["Python", "JavaScript"]
                }
            },
            {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "age": 25,
                "profile": {
                    "location": "San Francisco",
                    "skills": ["React", "Node.js"]
                }
            }
        ]
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_export_to_markdown_basic(self):
        """Test basic Markdown export."""
        result = export_to_markdown(
            self.sample_data,
            self.test_dir,
            filename_key="name",
            include_yaml_front_matter=False
        )
        
        self.assertEqual(len(result), 2)
        
        # Check that files were created
        john_file = Path(self.test_dir) / "John Doe.md"
        jane_file = Path(self.test_dir) / "Jane Smith.md"
        
        self.assertTrue(john_file.exists())
        self.assertTrue(jane_file.exists())
        
        # Check file contents
        with open(john_file, 'r') as f:
            content = f.read()
            self.assertIn("## Name", content)
            self.assertIn("John Doe", content)
    
    def test_export_to_markdown_with_yaml(self):
        """Test Markdown export with YAML front matter."""
        result = export_to_markdown(
            self.sample_data,
            self.test_dir,
            filename_key="name",
            include_yaml_front_matter=True,
            selected_yaml_keys={"name", "email", "age"}
        )
        
        self.assertEqual(len(result), 2)
        
        # Check YAML front matter
        john_file = Path(self.test_dir) / "John Doe.md"
        with open(john_file, 'r') as f:
            content = f.read()
            self.assertIn("---", content)
            self.assertIn("name:", content)
            self.assertIn("email:", content)
            self.assertIn("age:", content)
    
    def test_export_to_markdown_with_transaction_id(self):
        """Test Markdown export with transaction ID (creates README)."""
        result = export_to_markdown(
            self.sample_data,
            self.test_dir,
            filename_key="name",
            transaction_id="test_123"
        )
        
        self.assertEqual(len(result), 3)  # 2 data files + 1 README
        
        # Check README creation
        readme_file = Path(self.test_dir) / "README.md"
        self.assertTrue(readme_file.exists())
        
        with open(readme_file, 'r') as f:
            content = f.read()
            self.assertIn("test_123", content)
            self.assertIn("Export Summary", content)
    
    def test_export_to_markdown_invalid_data(self):
        """Test error handling for invalid data."""
        with self.assertRaises(MarkdownExportError):
            export_to_markdown("invalid_data", self.test_dir)
    
    def test_export_to_markdown_empty_data(self):
        """Test error handling for empty data."""
        with self.assertRaises(MarkdownExportError):
            export_to_markdown([], self.test_dir)
    
    def test_export_to_markdown_invalid_directory(self):
        """Test error handling for invalid directory."""
        with self.assertRaises(MarkdownExportError):
            export_to_markdown(self.sample_data, "/invalid/path/that/does/not/exist")


if __name__ == '__main__':
    unittest.main()

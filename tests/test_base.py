"""
Base Test Class for Document Creator Toolkit
===========================================

This module provides a unified base class for all tests, ensuring consistent
test data management and reducing code duplication.
"""

import unittest
import tempfile
import shutil
import json
import csv
from pathlib import Path
from typing import List, Dict, Any


class DocumentCreatorTestBase(unittest.TestCase):
    """
    Base class for all Document Creator tests.
    
    This class provides:
    - Consistent test data setup
    - Temporary directory management
    - Common test utilities
    - Shared test data fixtures
    """
    
    @classmethod
    def setUpClass(cls):
        """Set up test class with shared resources."""
        # Get the directory where tests are located
        cls.test_dir = Path(__file__).parent
        cls.test_data_dir = cls.test_dir / "data"
        cls.test_output_dir = cls.test_dir / "output"
        
        # Ensure test directories exist
        cls.test_data_dir.mkdir(exist_ok=True)
        cls.test_output_dir.mkdir(exist_ok=True)
        
        # Create standard test data files
        cls._create_test_data_files()
    
    def setUp(self):
        """Set up individual test with temporary directory."""
        # Create temporary directory for this test
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Standard test data (same for all tests)
        self.sample_data = [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "profile": {
                    "age": 30,
                    "location": "New York"
                },
                "department": "Engineering",
                "projects": [
                    {"name": "Project A", "status": "completed"},
                    {"name": "Project B", "status": "in-progress"}
                ]
            },
            {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "profile": {
                    "age": 25,
                    "location": "San Francisco"
                },
                "department": "Design",
                "projects": [
                    {"name": "Project C", "status": "completed"},
                    {"name": "Project D", "status": "planning"}
                ]
            }
        ]
        
        # Paths to test data files
        self.test_json_file = self.test_data_dir / "test_data.json"
        self.test_csv_file = self.test_data_dir / "test_data.csv"
        
        # Output paths
        self.output_dir = self.temp_dir / "output"
        self.output_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """Clean up temporary directory after test."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    @classmethod
    def _create_test_data_files(cls):
        """Create standard test data files."""
        # Sample JSON data
        json_data = [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "profile": {
                    "age": 30,
                    "location": "New York"
                },
                "department": "Engineering",
                "projects": [
                    {"name": "Project A", "status": "completed"},
                    {"name": "Project B", "status": "in-progress"}
                ]
            },
            {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "profile": {
                    "age": 25,
                    "location": "San Francisco"
                },
                "department": "Design",
                "projects": [
                    {"name": "Project C", "status": "completed"},
                    {"name": "Project D", "status": "planning"}
                ]
            }
        ]
        
        # Write JSON test data
        json_file = cls.test_data_dir / "test_data.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)
        
        # Write CSV test data (flattened version)
        csv_file = cls.test_data_dir / "test_data.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # CSV headers
            writer.writerow([
                "name", "email", "profile.age", "profile.location", 
                "department", "projects"
            ])
            
            # CSV data
            writer.writerow([
                "John Doe", "john@example.com", "30", "New York", 
                "Engineering", '[{"name": "Project A", "status": "completed"}, {"name": "Project B", "status": "in-progress"}]'
            ])
            writer.writerow([
                "Jane Smith", "jane@example.com", "25", "San Francisco",
                "Design", '[{"name": "Project C", "status": "completed"}, {"name": "Project D", "status": "planning"}]'
            ])
    
    def assert_file_exists(self, file_path: Path, message: str = ""):
        """Assert that a file exists with helpful error message."""
        self.assertTrue(
            file_path.exists(),
            f"Expected file does not exist: {file_path}. {message}"
        )
    
    def assert_file_not_empty(self, file_path: Path, message: str = ""):
        """Assert that a file exists and is not empty."""
        self.assert_file_exists(file_path, message)
        self.assertGreater(
            file_path.stat().st_size, 0,
            f"File exists but is empty: {file_path}. {message}"
        )
    
    def assert_file_contains(self, file_path: Path, content: str, message: str = ""):
        """Assert that a file contains specific content."""
        self.assert_file_exists(file_path, message)
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        self.assertIn(
            content, file_content,
            f"Content not found in {file_path}: '{content}'. {message}"
        )
    
    def get_file_content(self, file_path: Path) -> str:
        """Get content of a file safely."""
        if not file_path.exists():
            return ""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def count_files_in_directory(self, directory: Path, pattern: str = "*") -> int:
        """Count files matching pattern in directory."""
        if not directory.exists():
            return 0
        return len(list(directory.glob(pattern)))


class UnifiedExportTestBase(DocumentCreatorTestBase):
    """
    Base class for testing any export format (Markdown, PDF, Word).
    
    This addresses your concern about having separate test classes for each format.
    Instead, we use one unified approach that can test any export format.
    """
    
    def verify_export_results(self, export_function, expected_extensions: List[str], 
                            data: List[Dict[Any, Any]] = None, **kwargs):
        """
        Universal method to test any export format.
        
        Args:
            export_function: The export function to test (export_to_markdown, export_to_pdf, etc.)
            expected_extensions: List of file extensions to expect (e.g., ['.md', '.pdf', '.docx'])
            data: Data to export (uses self.sample_data if not provided)
            **kwargs: Additional arguments to pass to export function
        """
        if data is None:
            data = self.sample_data
        
        # Call the export function
        try:
            result_files = export_function(data, self.output_dir, **kwargs)
            
            # Verify files were created
            self.assertIsInstance(result_files, list, "Export function should return a list of files")
            self.assertGreater(len(result_files), 0, "Export function should create at least one file")
            
            # Verify each file
            for file_path in result_files:
                self.assert_file_exists(file_path, f"Export function should create file: {file_path}")
                self.assert_file_not_empty(file_path, f"Created file should not be empty: {file_path}")
                
                # Check file extension
                file_extension = file_path.suffix.lower()
                self.assertIn(
                    file_extension, expected_extensions,
                    f"File has unexpected extension: {file_extension}, expected one of: {expected_extensions}"
                )
            
            # Verify correct number of files (should match number of data records)
            expected_file_count = len(data)
            actual_file_count = len(result_files)
            self.assertEqual(
                actual_file_count, expected_file_count,
                f"Expected {expected_file_count} files (one per data record), got {actual_file_count}"
            )
            
            return result_files
            
        except Exception as e:
            self.fail(f"Export function failed with error: {str(e)}")
    
    def verify_export_content_structure(self, file_path: Path, export_format: str):
        """
        Verify the internal structure of an exported file.
        
        Args:
            file_path: Path to the exported file
            export_format: Format type ('markdown', 'pdf', 'word')
        """
        if export_format == 'markdown':
            content = self.get_file_content(file_path)
            self._verify_markdown_structure(content, file_path)
        elif export_format == 'pdf':
            self._verify_pdf_structure(file_path)
        elif export_format == 'word':
            self._verify_word_structure(file_path)
    
    def _verify_markdown_structure(self, content: str, file_path: Path):
        """Verify Markdown file structure."""
        # Check for YAML front matter (if PyYAML is available)
        if content.startswith('---'):
            self.assertIn('---', content[3:], f"YAML front matter not properly closed in {file_path}")
        
        # Check for at least one heading
        self.assertTrue(
            '## ' in content or '# ' in content,
            f"Markdown file should contain at least one heading: {file_path}"
        )
    
    def _verify_pdf_structure(self, file_path: Path):
        """Verify PDF file structure."""
        # Basic PDF file validation
        with open(file_path, 'rb') as f:
            first_bytes = f.read(10)
        
        self.assertTrue(
            first_bytes.startswith(b'%PDF-'),
            f"File does not appear to be a valid PDF: {file_path}"
        )
    
    def _verify_word_structure(self, file_path: Path):
        """Verify Word file structure."""
        # Basic Word file validation (docx files are ZIP archives)
        import zipfile
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                # Check for required Word document structure
                required_files = ['word/document.xml', '[Content_Types].xml']
                zip_contents = zip_file.namelist()
                
                for required_file in required_files:
                    self.assertIn(
                        required_file, zip_contents,
                        f"Word document missing required file: {required_file}"
                    )
        except zipfile.BadZipFile:
            self.fail(f"File is not a valid Word document (ZIP archive): {file_path}")

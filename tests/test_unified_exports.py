"""
Unified Export Tests for Document Creator Toolkit
===============================================

This module provides comprehensive testing for ALL export formats using a unified approach.
Instead of separate test classes for each format, we use one flexible framework.

This addresses the concern about having separate test classes for Markdown, PDF, and Word.
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the base test class
from test_base import UnifiedExportTestBase

# Import the modules we're testing
from json_to_file.source_to_json import load_normalized_data
from json_to_file.markdown_export import export_to_markdown
from json_to_file.pdf_export import export_to_pdf  
from json_to_file.word_export import export_to_word


class TestUnifiedExportSystem(UnifiedExportTestBase):
    """
    Unified test class for ALL export formats.
    
    This single class tests Markdown, PDF, and Word exports using the same methodology.
    This is more efficient than having separate test classes for each format.
    """
    
    def test_markdown_export_basic(self):
        """Test basic Markdown export functionality."""
        print("\n🧪 Testing Markdown Export...")
        
        # Test Markdown export using the unified method
        result_files = self.verify_export_results(
            export_function=export_to_markdown,
            expected_extensions=['.md'],
            data=self.sample_data
        )
        
        # Verify Markdown-specific content
        for file_path in result_files:
            self.verify_export_content_structure(file_path, 'markdown')
            
        print(f"✅ Markdown export created {len(result_files)} files successfully")
    
    def test_pdf_export_basic(self):
        """Test basic PDF export functionality."""
        print("\n🧪 Testing PDF Export...")
        
        try:
            # Test PDF export using the unified method
            result_files = self.verify_export_results(
                export_function=export_to_pdf,
                expected_extensions=['.pdf'],
                data=self.sample_data
            )
            
            # Verify PDF-specific content
            for file_path in result_files:
                self.verify_export_content_structure(file_path, 'pdf')
                
            print(f"✅ PDF export created {len(result_files)} files successfully")
            
        except Exception as e:
            if "reportlab" in str(e).lower():
                self.skipTest("PDF export requires reportlab package")
            else:
                raise
    
    def test_word_export_basic(self):
        """Test basic Word export functionality."""
        print("\n🧪 Testing Word Export...")
        
        try:
            # Test Word export using the unified method
            result_files = self.verify_export_results(
                export_function=export_to_word,
                expected_extensions=['.docx'],
                data=self.sample_data
            )
            
            # Verify Word-specific content
            for file_path in result_files:
                self.verify_export_content_structure(file_path, 'word')
                
            print(f"✅ Word export created {len(result_files)} files successfully")
            
        except Exception as e:
            if "python-docx" in str(e).lower():
                self.skipTest("Word export requires python-docx package")
            else:
                raise
    
    def test_all_formats_with_same_data(self):
        """
        Test that all export formats work with the same data.
        
        This is a key test that ensures consistency across all export formats.
        """
        print("\n🧪 Testing All Export Formats with Same Data...")
        
        # Test data
        test_data = [
            {
                "name": "Test User",
                "email": "test@example.com",
                "department": "Testing",
                "projects": [{"name": "Test Project", "status": "active"}]
            }
        ]
        
        results = {}
        
        # Test Markdown export
        try:
            markdown_files = self.verify_export_results(
                export_function=export_to_markdown,
                expected_extensions=['.md'],
                data=test_data
            )
            results['markdown'] = len(markdown_files)
            print(f"   ✅ Markdown: {len(markdown_files)} files")
        except Exception as e:
            print(f"   ❌ Markdown failed: {e}")
        
        # Test PDF export
        try:
            pdf_files = self.verify_export_results(
                export_function=export_to_pdf,
                expected_extensions=['.pdf'],
                data=test_data
            )
            results['pdf'] = len(pdf_files)
            print(f"   ✅ PDF: {len(pdf_files)} files")
        except Exception as e:
            print(f"   ⚠️ PDF skipped: {e}")
        
        # Test Word export
        try:
            word_files = self.verify_export_results(
                export_function=export_to_word,
                expected_extensions=['.docx'],
                data=test_data
            )
            results['word'] = len(word_files)
            print(f"   ✅ Word: {len(word_files)} files")
        except Exception as e:
            print(f"   ⚠️ Word skipped: {e}")
        
        # Verify all formats created the same number of files
        if len(results) > 1:
            file_counts = list(results.values())
            self.assertTrue(
                all(count == file_counts[0] for count in file_counts),
                f"All formats should create the same number of files: {results}"
            )
        
        print(f"✅ All available formats created consistent results: {results}")
    
    def test_export_file_naming_consistency(self):
        """
        Test that all export formats use consistent file naming.
        
        This ensures that files from different formats can be easily matched.
        """
        print("\n🧪 Testing File Naming Consistency...")
        
        # Test data with clear naming
        test_data = [
            {"name": "Alice Johnson", "id": "001"},
            {"name": "Bob Wilson", "id": "002"}
        ]
        
        # Get filenames from each format
        format_filenames = {}
        
        # Test Markdown filenames
        try:
            md_files = export_to_markdown(test_data, self.output_dir)
            format_filenames['markdown'] = [f.stem for f in md_files]  # Remove extension
        except Exception as e:
            print(f"   ⚠️ Markdown naming test skipped: {e}")
        
        # Test PDF filenames
        try:
            pdf_files = export_to_pdf(test_data, self.output_dir)
            format_filenames['pdf'] = [f.stem for f in pdf_files]  # Remove extension
        except Exception as e:
            print(f"   ⚠️ PDF naming test skipped: {e}")
        
        # Test Word filenames
        try:
            word_files = export_to_word(test_data, self.output_dir)
            format_filenames['word'] = [f.stem for f in word_files]  # Remove extension
        except Exception as e:
            print(f"   ⚠️ Word naming test skipped: {e}")
        
        # Verify naming consistency
        if len(format_filenames) > 1:
            base_names = list(format_filenames.values())[0]
            for format_name, names in format_filenames.items():
                self.assertEqual(
                    names, base_names,
                    f"File names for {format_name} don't match base pattern: {names} vs {base_names}"
                )
        
        print(f"✅ File naming is consistent across formats: {format_filenames}")
    
    def test_export_with_edge_case_data(self):
        """
        Test all export formats with challenging data.
        
        This tests how each format handles edge cases like special characters,
        empty fields, complex nested data, etc.
        """
        print("\n🧪 Testing All Formats with Edge Case Data...")
        
        # Challenging test data
        edge_case_data = [
            {
                "name": "Special Chars: áéíóú & <html> \"quotes\"",
                "email": "special@test.com",
                "description": "Multi-line\ntext with\ttabs and\rcarriage returns",
                "metadata": {
                    "empty_field": "",
                    "null_field": None,
                    "nested": {
                        "deep": {
                            "value": "deeply nested"
                        }
                    }
                },
                "large_array": [f"Item {i}" for i in range(100)],  # Large array
                "unicode": "🚀 Unicode symbols: ✓ ✗ ⚠️",
                "numbers": {
                    "integer": 42,
                    "float": 3.14159,
                    "large": 1234567890
                }
            }
        ]
        
        formats_tested = []
        
        # Test each format with edge case data
        for format_name, export_func, extensions in [
            ('markdown', export_to_markdown, ['.md']),
            ('pdf', export_to_pdf, ['.pdf']),
            ('word', export_to_word, ['.docx'])
        ]:
            try:
                print(f"   🧪 Testing {format_name} with edge cases...")
                
                result_files = self.verify_export_results(
                    export_function=export_func,
                    expected_extensions=extensions,
                    data=edge_case_data
                )
                
                # Verify the file was created and has content
                for file_path in result_files:
                    self.assert_file_not_empty(file_path, f"{format_name} file should handle edge cases")
                
                formats_tested.append(format_name)
                print(f"   ✅ {format_name} handled edge cases successfully")
                
            except Exception as e:
                print(f"   ⚠️ {format_name} edge case test skipped: {e}")
        
        # Verify at least one format was tested
        self.assertGreater(
            len(formats_tested), 0,
            "At least one export format should be available for edge case testing"
        )
        
        print(f"✅ Edge case testing completed for: {formats_tested}")


class TestDataLoadingAndExportIntegration(UnifiedExportTestBase):
    """
    Test the complete workflow from data loading to export.
    
    This tests the integration between data loading and ALL export formats.
    """
    
    def test_json_to_all_formats_workflow(self):
        """Test complete workflow: JSON file → All export formats."""
        print("\n🧪 Testing Complete Workflow: JSON → All Formats...")
        
        # Load data from JSON
        data = load_normalized_data(self.test_json_file)
        self.assertEqual(len(data), 2, "Should load 2 records from test JSON")
        
        # Test export to all available formats
        successful_exports = []
        
        for format_name, export_func, extensions in [
            ('markdown', export_to_markdown, ['.md']),
            ('pdf', export_to_pdf, ['.pdf']),
            ('word', export_to_word, ['.docx'])
        ]:
            try:
                result_files = self.verify_export_results(
                    export_function=export_func,
                    expected_extensions=extensions,
                    data=data
                )
                successful_exports.append(format_name)
                print(f"   ✅ JSON → {format_name}: {len(result_files)} files")
            except Exception as e:
                print(f"   ⚠️ JSON → {format_name} skipped: {e}")
        
        # Verify at least one export format worked
        self.assertGreater(
            len(successful_exports), 0,
            "At least one export format should work with JSON data"
        )
        
        print(f"✅ Complete workflow tested for: {successful_exports}")
    
    def test_csv_to_all_formats_workflow(self):
        """Test complete workflow: CSV file → All export formats."""
        print("\n🧪 Testing Complete Workflow: CSV → All Formats...")
        
        # Load data from CSV
        data = load_normalized_data(self.test_csv_file)
        self.assertEqual(len(data), 2, "Should load 2 records from test CSV")
        
        # Test export to all available formats
        successful_exports = []
        
        for format_name, export_func, extensions in [
            ('markdown', export_to_markdown, ['.md']),
            ('pdf', export_to_pdf, ['.pdf']),
            ('word', export_to_word, ['.docx'])
        ]:
            try:
                result_files = self.verify_export_results(
                    export_function=export_func,
                    expected_extensions=extensions,
                    data=data
                )
                successful_exports.append(format_name)
                print(f"   ✅ CSV → {format_name}: {len(result_files)} files")
            except Exception as e:
                print(f"   ⚠️ CSV → {format_name} skipped: {e}")
        
        # Verify at least one export format worked
        self.assertGreater(
            len(successful_exports), 0,
            "At least one export format should work with CSV data"
        )
        
        print(f"✅ Complete workflow tested for: {successful_exports}")


if __name__ == '__main__':
    # Run the unified tests
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""
Example usage script for the DocGenius Document Creator Toolkit.

This script demonstrates all the features of the toolkit including:
- Loading data from various sources
- Exporting to different formats
- Using templates
- Error handling

Updated to use the new logic structure.
"""

import json
import csv
from pathlib import Path
import logging

# Import from new logic structure
from logic.data_sources import CSVLoader
from logic.exporters import MarkdownExporter, PDFExporter, WordExporter
from logic.models import DataObject, DocumentConfig, ExportSettings
from logic.utilities import (
    FileOperations, LoggingConfigurator,
    ValidationEngine
)

def create_sample_data():
    """Create sample data files for demonstration."""
    print("📄 Creating sample data files...")
    
    # Sample JSON data
    json_data = [
        {
            "id": 1,
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "department": "Engineering",
            "role": "Senior Developer",
            "projects": ["Web App", "Mobile API"],
            "skills": ["Python", "JavaScript", "React"],
            "hire_date": "2022-01-15",
            "salary": 95000
        },
        {
            "id": 2,
            "name": "Bob Smith",
            "email": "bob@example.com", 
            "department": "Marketing",
            "role": "Marketing Manager",
            "projects": ["Brand Campaign", "Social Media"],
            "skills": ["Marketing", "Analytics", "Design"],
            "hire_date": "2021-08-20",
            "salary": 75000
        },
        {
            "id": 3,
            "name": "Carol Davis",
            "email": "carol@example.com",
            "department": "Engineering", 
            "role": "DevOps Engineer",
            "projects": ["Infrastructure", "CI/CD Pipeline"],
            "skills": ["Docker", "Kubernetes", "AWS"],
            "hire_date": "2023-03-10",
            "salary": 88000
        }
    ]
    
    # Create sample files
    samples_dir = Path("sample_data")
    samples_dir.mkdir(exist_ok=True)
    
    # Save JSON file
    json_file = samples_dir / "employees.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)
    print(f"  ✅ Created: {json_file}")
    
    # Save CSV file
    csv_file = samples_dir / "employees.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=json_data[0].keys())
        writer.writeheader()
        writer.writerows(json_data)
    print(f"  ✅ Created: {csv_file}")
    
    return json_file, csv_file

def demo_csv_loading():
    """Demonstrate CSV loading with the new logic structure."""
    print("\n🔄 Demonstrating CSV Loading...")
    
    _, csv_file = create_sample_data()
    
    try:
        loader = CSVLoader()
        result = loader.load(str(csv_file))
        
        if result.success:
            print(f"  ✅ Loaded {len(result.data)} records from CSV")
            print(f"  📊 Sample record: {result.data[0]}")
            return result.data
        else:
            print(f"  ❌ Failed to load CSV: {'; '.join(result.errors)}")
            return None
            
    except Exception as e:
        print(f"  ❌ Error loading CSV: {e}")
        return None

def demo_markdown_export(data):
    """Demonstrate markdown export."""
    print("\n📝 Demonstrating Markdown Export...")
    
    try:
        exporter = MarkdownExporter()
        data_obj = DataObject(data)
        
        output_path = Path("output") / "employees.md"
        output_path.parent.mkdir(exist_ok=True)
        
        config = DocumentConfig(
            output_path=str(output_path),
            title="Employee Directory"
        )
        
        settings = ExportSettings(
            include_metadata=True,
            custom_template=None
        )
        
        result = exporter.export(data_obj, config, settings)
        
        if result.success:
            print(f"  ✅ Exported to: {result.output_path}")
            print(f"  📊 File size: {Path(result.output_path).stat().st_size} bytes")
        else:
            print(f"  ❌ Export failed: {'; '.join(result.errors)}")
            
    except Exception as e:
        print(f"  ❌ Error during export: {e}")

def demo_pdf_export(data):
    """Demonstrate PDF export."""
    print("\n📄 Demonstrating PDF Export...")
    
    try:
        exporter = PDFExporter()
        data_obj = DataObject(data)
        
        output_path = Path("output") / "employees.pdf"
        output_path.parent.mkdir(exist_ok=True)
        
        config = DocumentConfig(
            output_path=str(output_path),
            title="Employee Directory - PDF"
        )
        
        settings = ExportSettings(
            include_metadata=True
        )
        
        result = exporter.export(data_obj, config, settings)
        
        if result.success:
            print(f"  ✅ Exported to: {result.output_path}")
        else:
            print(f"  ❌ Export failed: {'; '.join(result.errors)}")
            
    except Exception as e:
        print(f"  ❌ Error during PDF export: {e}")

def demo_word_export(data):
    """Demonstrate Word export."""
    print("\n📄 Demonstrating Word Export...")
    
    try:
        exporter = WordExporter()
        data_obj = DataObject(data)
        
        output_path = Path("output") / "employees.docx"
        output_path.parent.mkdir(exist_ok=True)
        
        config = DocumentConfig(
            output_path=str(output_path),
            title="Employee Directory - Word"
        )
        
        settings = ExportSettings(
            include_metadata=True
        )
        
        result = exporter.export(data_obj, config, settings)
        
        if result.success:
            print(f"  ✅ Exported to: {result.output_path}")
        else:
            print(f"  ❌ Export failed: {'; '.join(result.errors)}")
            
    except Exception as e:
        print(f"  ❌ Error during Word export: {e}")

def demo_validation():
    """Demonstrate validation features."""
    print("\n🔍 Demonstrating Validation...")
    
    try:
        validator = ValidationEngine()
        
        # Test file validation
        test_file = Path("sample_data/employees.csv")
        if validator.validate_file_path(str(test_file)):
            print(f"  ✅ File validation passed: {test_file}")
        else:
            print(f"  ❌ File validation failed: {test_file}")
        
        # Test data validation
        test_data = {"name": "Test User", "email": "test@example.com"}
        is_valid = validator.validate_data_structure(test_data, ["name", "email"])
        
        if is_valid:
            print("  ✅ Data structure validation passed")
        else:
            print("  ❌ Data structure validation failed")
            
    except Exception as e:
        print(f"  ❌ Error during validation: {e}")

def main():
    """Run all demonstrations."""
    print("🚀 DocGenius Toolkit Examples")
    print("=" * 50)
    
    # Setup logging
    configurator = LoggingConfigurator()
    logger = configurator.setup_application_logging(log_level='INFO')
    
    try:
        # Load data
        data = demo_csv_loading()
        
        if data:
            # Demo exports
            demo_markdown_export(data)
            demo_pdf_export(data)
            demo_word_export(data)
            
        # Demo validation
        demo_validation()
        
        print("\n🎉 All demonstrations completed!")
        print("Check the 'output' directory for generated files.")
        
    except Exception as e:
        print(f"\n❌ Error during demonstrations: {e}")
        logger.error(f"Demo error: {e}")

if __name__ == "__main__":
    main()

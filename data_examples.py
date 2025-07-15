#!/usr/bin/env python3
"""
Example usage script for the Document Creator Toolkit.

This script demonstrates all the features of the toolkit including:
- Loading data from various sources
- Exporting to different formats
- Using templates
- YAML front matter selection
- Error handling
"""

import json
import csv
from pathlib import Path
import logging

# Import the toolkit
from json_to_file.source_to_json import load_normalized_data, DataSourceError
from json_to_file.markdown_export import export_to_markdown, interactive_yaml_key_selection
from json_to_file.pdf_export import export_to_pdf, check_pdf_requirements
from json_to_file.word_export import export_to_word, check_word_requirements
from json_to_file.utils import setup_logging, ensure_directory_exists

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
            "profile": {
                "age": 29,
                "location": "San Francisco",
                "skills": ["Python", "Machine Learning", "Data Analysis"],
                "experience_years": 5
            },
            "projects": [
                {"name": "ML Pipeline", "status": "completed", "priority": "high"},
                {"name": "Data Visualization", "status": "in-progress", "priority": "medium"}
            ],
            "performance": {
                "rating": 4.5,
                "goals_met": 8,
                "total_goals": 10
            }
        },
        {
            "id": 2,
            "name": "Bob Smith",
            "email": "bob@example.com",
            "department": "Marketing",
            "profile": {
                "age": 34,
                "location": "New York",
                "skills": ["SEO", "Content Marketing", "Analytics"],
                "experience_years": 8
            },
            "projects": [
                {"name": "Brand Campaign", "status": "completed", "priority": "high"},
                {"name": "Social Media Strategy", "status": "planning", "priority": "low"}
            ],
            "performance": {
                "rating": 4.2,
                "goals_met": 9,
                "total_goals": 10
            }
        },
        {
            "id": 3,
            "name": "Carol Davis",
            "email": "carol@example.com",
            "department": "Engineering",
            "profile": {
                "age": 26,
                "location": "Austin",
                "skills": ["React", "Node.js", "DevOps"],
                "experience_years": 3
            },
            "projects": [
                {"name": "Web App Redesign", "status": "in-progress", "priority": "high"},
                {"name": "API Documentation", "status": "completed", "priority": "medium"}
            ],
            "performance": {
                "rating": 4.8,
                "goals_met": 10,
                "total_goals": 10
            }
        }
    ]
    
    # Save JSON data
    with open("sample_employees.json", "w") as f:
        json.dump(json_data, f, indent=2)
    print("✅ Created sample_employees.json")
    
    # Create CSV data
    csv_data = [
        {
            "company_name": "Tech Innovations Inc",
            "company_industry": "Technology",
            "employee_count": 150,
            "contact_name": "Sarah Wilson",
            "contact_email": "sarah@techinnovations.com",
            "contact_phone": "555-0123",
            "address_street": "123 Tech Street",
            "address_city": "San Francisco",
            "address_state": "CA",
            "address_zip": "94105",
            "services": "Software Development, AI Solutions",
            "established_year": 2018
        },
        {
            "company_name": "Green Energy Solutions",
            "company_industry": "Energy",
            "employee_count": 75,
            "contact_name": "Mike Johnson",
            "contact_email": "mike@greenenergy.com",
            "contact_phone": "555-0456",
            "address_street": "456 Solar Avenue",
            "address_city": "Austin",
            "address_state": "TX",
            "address_zip": "78701",
            "services": "Solar Installation, Energy Consulting",
            "established_year": 2015
        }
    ]
    
    # Save CSV data
    with open("sample_companies.csv", "w", newline="") as f:
        if csv_data:
            writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
            writer.writeheader()
            writer.writerows(csv_data)
    print("✅ Created sample_companies.csv")
    
    return ["sample_employees.json", "sample_companies.csv"]

def demonstrate_data_loading():
    """Demonstrate data loading from various sources."""
    print("\n" + "="*50)
    print("DATA LOADING DEMONSTRATION")
    print("="*50)
    
    # Load JSON data
    print("\n📊 Loading JSON data...")
    try:
        json_data = load_normalized_data("sample_employees.json")
        print(f"✅ Loaded {len(json_data)} records from JSON")
        print(f"   Sample record keys: {list(json_data[0].keys())}")
    except DataSourceError as e:
        print(f"❌ JSON loading failed: {e}")
        return None
    
    # Load CSV data
    print("\n📊 Loading CSV data...")
    try:
        csv_data = load_normalized_data("sample_companies.csv")
        print(f"✅ Loaded {len(csv_data)} records from CSV")
        print(f"   Sample record keys: {list(csv_data[0].keys())}")
        print(f"   Nested structure example: {csv_data[0].get('company', {})}")
    except DataSourceError as e:
        print(f"❌ CSV loading failed: {e}")
        return None
    
    return json_data, csv_data

def demonstrate_markdown_export(data_list, output_dir):
    """Demonstrate Markdown export with different options."""
    print("\n" + "="*50)
    print("MARKDOWN EXPORT DEMONSTRATION")
    print("="*50)
    
    # Basic Markdown export
    print("\n📝 Basic Markdown export...")
    try:
        files = export_to_markdown(
            data_list,
            output_dir / "markdown_basic",
            filename_key="name",
            include_yaml_front_matter=False
        )
        print(f"✅ Basic Markdown export completed - {len(files)} files created")
    except Exception as e:
        print(f"❌ Basic Markdown export failed: {e}")
    
    # Markdown with YAML front matter (all keys)
    print("\n📝 Markdown with YAML front matter (all keys)...")
    try:
        files = export_to_markdown(
            data_list,
            output_dir / "markdown_yaml_all",
            filename_key="name",
            include_yaml_front_matter=True,
            selected_yaml_keys=None,  # All keys
            flatten_yaml_values=True
        )
        print(f"✅ YAML Markdown export completed - {len(files)} files created")
    except Exception as e:
        print(f"❌ YAML Markdown export failed: {e}")
    
    # Markdown with selected YAML keys
    print("\n📝 Markdown with selected YAML keys...")
    try:
        selected_keys = {"name", "email", "department", "profile.age", "profile.location"}
        files = export_to_markdown(
            data_list,
            output_dir / "markdown_yaml_selected",
            filename_key="name",
            include_yaml_front_matter=True,
            selected_yaml_keys=selected_keys,
            flatten_yaml_values=True
        )
        print(f"✅ Selected YAML Markdown export completed - {len(files)} files created")
        print(f"   Selected keys: {selected_keys}")
    except Exception as e:
        print(f"❌ Selected YAML Markdown export failed: {e}")

def demonstrate_pdf_export(data_list, output_dir):
    """Demonstrate PDF export."""
    print("\n" + "="*50)
    print("PDF EXPORT DEMONSTRATION")
    print("="*50)
    
    # Check requirements
    requirements = check_pdf_requirements()
    print(f"📋 PDF export capabilities: {requirements}")
    
    if requirements['direct_pdf']:
        print("\n📄 Direct PDF export...")
        try:
            files = export_to_pdf(
                data_list,
                output_dir / "pdf_direct",
                filename_key="name",
                use_template=False,
                pdf_title="Employee Report",
                pdf_author="Document Creator"
            )
            print(f"✅ Direct PDF export completed - {len(files)} files created")
        except Exception as e:
            print(f"❌ Direct PDF export failed: {e}")
    else:
        print("⚠️  Direct PDF export not available (reportlab not installed)")
    
    if requirements['template_pdf']:
        print("\n📄 Template-based PDF export...")
        print("   Note: Template-based PDF requires a Word template file")
        print("   Skipping template demo (no template provided)")
    else:
        print("⚠️  Template-based PDF export not available (docx packages not installed)")

def demonstrate_word_export(data_list, output_dir):
    """Demonstrate Word export."""
    print("\n" + "="*50)
    print("WORD EXPORT DEMONSTRATION")
    print("="*50)
    
    # Check requirements
    requirements = check_word_requirements()
    print(f"📋 Word export capabilities: {requirements}")
    
    if requirements['word_export']:
        print("\n📄 Direct Word export...")
        try:
            files = export_to_word(
                data_list,
                output_dir / "word_direct",
                filename_key="name",
                use_template=False,
                document_title="Employee Report",
                document_author="Document Creator"
            )
            print(f"✅ Direct Word export completed - {len(files)} files created")
        except Exception as e:
            print(f"❌ Direct Word export failed: {e}")
    else:
        print("⚠️  Word export not available (python-docx not installed)")

def demonstrate_error_handling():
    """Demonstrate error handling."""
    print("\n" + "="*50)
    print("ERROR HANDLING DEMONSTRATION")
    print("="*50)
    
    # Test invalid data source
    print("\n❌ Testing invalid data source...")
    try:
        load_normalized_data("nonexistent_file.json")
    except DataSourceError as e:
        print(f"✅ Correctly caught DataSourceError: {e}")
    
    # Test invalid data format
    print("\n❌ Testing invalid export data...")
    try:
        export_to_markdown(
            "invalid_data",  # Should be a list
            "./output"
        )
    except Exception as e:
        print(f"✅ Correctly caught export error: {e}")
    
    print("\n✅ Error handling works correctly!")

def main():
    """Main demonstration function."""
    print("🎯 Document Creator Toolkit - Feature Demonstration")
    print("="*60)
    
    # Setup logging
    setup_logging("INFO")
    
    # Create output directory
    output_dir = Path("./demo_output")
    ensure_directory_exists(str(output_dir))
    
    # Create sample data
    sample_files = create_sample_data()
    
    # Demonstrate data loading
    data_result = demonstrate_data_loading()
    if not data_result:
        print("❌ Data loading failed, cannot continue with export demonstrations")
        return
    
    json_data, csv_data = data_result
    
    # Demonstrate exports with JSON data
    demonstrate_markdown_export(json_data, output_dir)
    demonstrate_pdf_export(json_data, output_dir) 
    demonstrate_word_export(json_data, output_dir)
    
    # Demonstrate error handling
    demonstrate_error_handling()
    
    # Summary
    print("\n" + "="*60)
    print("DEMONSTRATION SUMMARY")
    print("="*60)
    print(f"✅ Created sample data files: {sample_files}")
    print(f"✅ Demonstrated data loading from JSON and CSV")
    print(f"✅ Demonstrated Markdown export with various YAML options")
    print(f"✅ Demonstrated PDF export (if available)")
    print(f"✅ Demonstrated Word export (if available)")
    print(f"✅ Demonstrated error handling")
    print(f"📁 Output files saved to: {output_dir.absolute()}")
    
    print("\n🎉 All demonstrations completed!")
    print("\nNext steps:")
    print("1. Explore the generated files in the demo_output directory")
    print("2. Try the interactive CLI: python main_cli.py")
    print("3. Check the README.md for more usage examples")
    
    # Cleanup option
    cleanup = input("\n🧹 Delete sample data files? (y/n): ").strip().lower()
    if cleanup == 'y':
        for file in sample_files:
            Path(file).unlink(missing_ok=True)
        print("✅ Sample data files deleted")

if __name__ == "__main__":
    main()

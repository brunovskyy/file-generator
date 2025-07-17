#!/usr/bin/env python3
"""
Setup script for the Document Creator Toolkit.

This script helps users install the necessary dependencies and set up the toolkit.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    
    # Core dependencies
    core_deps = ["requests"]
    optional_deps = {
        "YAML support": ["PyYAML"],
        "PDF export": ["reportlab"],
        "Word export": ["python-docx", "docxtpl"],
        "Word to PDF conversion": ["docx2pdf"]
    }
    
    # Install core dependencies
    for dep in core_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            return False
    
    # Install optional dependencies
    for feature, deps in optional_deps.items():
        print(f"\n📋 Installing {feature}...")
        for dep in deps:
            success = run_command(f"pip install {dep}", f"Installing {dep}")
            if not success:
                print(f"⚠️  {feature} may not work properly")
    
    return True

def create_output_directory():
    """Create the default output directory."""
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)
    print(f"✅ Created output directory: {output_dir.absolute()}")

def test_installation():
    """Test if the installation works."""
    print("\n🧪 Testing installation...")
    
    try:
        # Test imports
        # Import from new logic structure
        from logic.data_sources import CSVLoader
        from logic.exporters import MarkdownExporter
        from logic.models import DataObject, DocumentConfig, ExportSettings
        from logic.utilities import LoggingConfigurator
        
        # Backward compatibility functions
        def load_normalized_data(file_path: str):
            """Load data using new data sources structure."""
            if file_path.lower().endswith('.csv'):
                loader = CSVLoader()
                result = loader.load(file_path)
                return result.data if result.success else None
            else:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        def export_to_markdown(data, output_path: str, **kwargs):
            """Export to markdown using new exporter structure."""
            exporter = MarkdownExporter()
            data_obj = DataObject(data)
            config = DocumentConfig(output_path=output_path)
            settings = ExportSettings(**kwargs)
            return exporter.export(data_obj, config, settings)
        
        def setup_logging():
            """Setup logging using new utilities structure."""
            configurator = LoggingConfigurator()
            return configurator.setup_application_logging(log_level='INFO')
        
        print("✅ Core modules imported successfully")
        
        # Test CLI
        result = subprocess.run([sys.executable, "main_cli.py", "--help"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ CLI is working correctly")
        else:
            print("❌ CLI test failed")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Document Creator Toolkit Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Dependency installation failed")
        sys.exit(1)
    
    # Create output directory
    create_output_directory()
    
    # Test installation
    if not test_installation():
        print("\n❌ Installation test failed")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run 'python main_cli.py' for interactive mode")
    print("2. Run 'python main_cli.py --help' for command-line options")
    print("3. Check the README.md for usage examples")
    
    # Optional: Create a test data file
    create_test = input("\n📄 Create test data file? (y/n): ").strip().lower()
    if create_test == 'y':
        test_data = '''[
  {
    "name": "Sample Document",
    "description": "This is a test document",
    "category": "example",
    "tags": ["test", "sample", "demo"],
    "metadata": {
      "created": "2025-01-01",
      "author": "Document Creator"
    }
  }
]'''
        with open("sample_data.json", "w") as f:
            f.write(test_data)
        print("✅ Created sample_data.json")
        print("   Test with: python main_cli.py --source sample_data.json --export-types markdown")

if __name__ == "__main__":
    main()

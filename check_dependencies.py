#!/usr/bin/env python3
"""
Dependency Checker for Document Creator Toolkit
===============================================

This script checks which dependencies are installed and provides
installation instructions for missing ones.
"""

import sys
import importlib
import subprocess
from pathlib import Path

def check_dependency(module_name, package_name=None, purpose="", required=True):
    """Check if a dependency is available."""
    if package_name is None:
        package_name = module_name
    
    try:
        importlib.import_module(module_name)
        status = "✅ INSTALLED"
        color = "\033[92m"  # Green
    except ImportError:
        if required:
            status = "❌ MISSING (REQUIRED)"
            color = "\033[91m"  # Red
        else:
            status = "⚠️ MISSING (OPTIONAL)"
            color = "\033[93m"  # Yellow
    
    reset_color = "\033[0m"
    
    print(f"{color}{module_name:15} {status:20}{reset_color} {purpose}")
    
    if status.startswith("❌") or status.startswith("⚠️"):
        print(f"                    Install with: pip install {package_name}")
    
    return status.startswith("✅")

def main():
    """Main dependency checker."""
    print("🔍 Document Creator Toolkit - Dependency Check")
    print("=" * 60)
    print()
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} (Compatible)")
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} (Requires 3.8+)")
        return False
    
    print()
    print("Core Dependencies:")
    print("-" * 30)
    
    # Check core dependencies
    core_deps = [
        ("requests", "requests", "HTTP requests for API data loading", True),
        ("json", None, "JSON processing (built-in)", True),
        ("csv", None, "CSV processing (built-in)", True),
        ("pathlib", None, "File path handling (built-in)", True),
        ("argparse", None, "Command-line interface (built-in)", True),
        ("tkinter", None, "GUI dialogs (built-in)", True),
        ("unittest", None, "Testing framework (built-in)", True),
    ]
    
    core_available = True
    for dep in core_deps:
        if not check_dependency(*dep):
            core_available = False
    
    print()
    print("Optional Dependencies:")
    print("-" * 30)
    
    # Check optional dependencies
    optional_deps = [
        ("yaml", "PyYAML", "YAML front matter support", False),
        ("reportlab", "reportlab", "PDF generation", False),
        ("docx", "python-docx", "Word document creation", False),
        ("docxtpl", "docxtpl", "Word template processing", False),
        ("colorama", "colorama", "Colored CLI output", False),
    ]
    
    optional_available = []
    for dep in optional_deps:
        available = check_dependency(*dep)
        optional_available.append((dep[0], available))
    
    print()
    print("Development Dependencies:")
    print("-" * 30)
    
    # Check development dependencies
    dev_deps = [
        ("pytest", "pytest", "Advanced testing framework", False),
        ("black", "black", "Code formatting", False),
        ("flake8", "flake8", "Code linting", False),
        ("mypy", "mypy", "Type checking", False),
    ]
    
    for dep in dev_deps:
        check_dependency(*dep)
    
    print()
    print("=" * 60)
    print("Summary:")
    print("=" * 60)
    
    # Core functionality check
    if core_available:
        print("✅ Core functionality: AVAILABLE")
        print("   - You can load data from JSON, CSV, and APIs")
        print("   - You can export to Markdown format")
        print("   - CLI interface is fully functional")
    else:
        print("❌ Core functionality: MISSING DEPENDENCIES")
        print("   - Install missing core dependencies first")
        return False
    
    # Optional features check
    yaml_available = any(dep[0] == "yaml" and dep[1] for dep in optional_available)
    reportlab_available = any(dep[0] == "reportlab" and dep[1] for dep in optional_available)
    docx_available = any(dep[0] == "docx" and dep[1] for dep in optional_available)
    
    print()
    print("Available Export Formats:")
    print(f"  ✅ Markdown (always available)")
    print(f"  {'✅' if yaml_available else '⚠️'} Markdown with YAML front matter {'(available)' if yaml_available else '(falls back to JSON)'}")
    print(f"  {'✅' if reportlab_available else '❌'} PDF export {'(available)' if reportlab_available else '(disabled)'}")
    print(f"  {'✅' if docx_available else '❌'} Word export {'(available)' if docx_available else '(disabled)'}")
    
    print()
    print("Installation Recommendations:")
    print("-" * 40)
    
    missing_optional = []
    for dep_name, available in optional_available:
        if not available:
            missing_optional.append(dep_name)
    
    if not missing_optional:
        print("🎉 All recommended dependencies are installed!")
        print("   The toolkit has full functionality available.")
    else:
        print("💡 To enable all features, install missing dependencies:")
        print()
        
        if "yaml" in missing_optional:
            print("   # Enable YAML front matter in Markdown:")
            print("   pip install PyYAML")
        
        if "reportlab" in missing_optional:
            print("   # Enable PDF export:")
            print("   pip install reportlab")
        
        if "docx" in missing_optional:
            print("   # Enable Word document export:")
            print("   pip install python-docx docxtpl")
        
        if "colorama" in missing_optional:
            print("   # Enable colored CLI output:")
            print("   pip install colorama")
        
        print()
        print("   # Install all optional dependencies at once:")
        print("   pip install PyYAML reportlab python-docx docxtpl colorama")
        print()
        print("   # Or install from requirements file:")
        print("   pip install -r requirements.txt")
    
    print()
    print("📚 Next Steps:")
    print("   1. Install any missing dependencies you need")
    print("   2. Run the test suite: python run_tests.py")
    print("   3. Try the CLI: python main_cli.py")
    print("   4. Check the documentation in README.md")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

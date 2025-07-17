#!/usr/bin/env python3
"""
Quick dependency installer for Document Creator toolkit.
"""

import subprocess
import sys

CORE_DEPS = [
    "requests>=2.31.0",
    "PyYAML>=6.0.1",
    "colorama>=0.4.6"
]

OPTIONAL_DEPS = [
    "reportlab>=4.0.4",  # PDF export
    "python-docx>=0.8.11",  # Word export
    "docxtpl>=0.16.7",  # Word templates
]

def install_package(package):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🚀 Installing Document Creator dependencies...")
    
    # Install core dependencies
    print("\n📦 Installing core dependencies...")
    for package in CORE_DEPS:
        print(f"Installing {package}...")
        if install_package(package):
            print(f"✅ {package} installed successfully")
        else:
            print(f"❌ Failed to install {package}")
    
    # Install optional dependencies
    print("\n📦 Installing optional dependencies...")
    for package in OPTIONAL_DEPS:
        print(f"Installing {package}...")
        if install_package(package):
            print(f"✅ {package} installed successfully")
        else:
            print(f"⚠️ Failed to install {package} (optional)")
    
    print("\n🎉 Installation complete!")
    print("You can now run: python app_launcher_cli.py")

if __name__ == "__main__":
    main()

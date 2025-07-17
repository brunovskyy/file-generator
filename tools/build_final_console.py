"""
DocGenius Console EXE Builder
Comprehensive build system that includes ALL required dependencies.
"""
import subprocess
import sys
import os
import shutil
from pathlib import Path

def main():
    print("🏗️  DocGenius Console EXE Builder")
    print("=" * 50)
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    for path in ["build", "dist", "*.spec"]:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
                print(f"   Removed directory: {path}")
            else:
                os.remove(path)
                print(f"   Removed file: {path}")
    
    # Define ALL required dependencies for DocGenius
    core_dependencies = [
        # HTTP requests (data loading)
        'requests', 'urllib3', 'certifi', 'charset_normalizer', 'idna',
        
        # YAML support (document metadata)
        'yaml', 'PyYAML',
        
        # PDF export (CORE FEATURE)
        'reportlab', 'reportlab.pdfgen', 'reportlab.lib', 'reportlab.platypus',
        'reportlab.graphics', 'reportlab.pdfbase', 'pillow', 'PIL',
        
        # Word document support (CORE FEATURE)
        'docx', 'python-docx', 'lxml', 'lxml.etree', 'lxml.objectify',
        
        # Word templates (CORE FEATURE)
        'docxtpl', 'jinja2', 'docxcompose', 'babel',
        
        # CLI enhancements
        'colorama',
        
        # Windows COM support
        'win32com.client', 'pythoncom', 'pywintypes',
        
        # Standard library essentials
        'typing_extensions', 'setuptools', 'six', 'MarkupSafe'
    ]
    
    # Build command with ALL dependencies
    build_cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name=DocGenius-Console',
        '--onefile',
        '--console',  # Console window for CLI app
        '--clean',
        '--noconfirm',
        '--add-data=docgenius;docgenius',  # Include package
    ]
    
    # Add all hidden imports
    for dep in core_dependencies:
        build_cmd.extend(['--hidden-import', dep])
    
    # Add the main script
    build_cmd.append('app_launcher_cli.py')
    
    print("📦 Building EXE with ALL dependencies...")
    print(f"💡 Including {len(core_dependencies)} dependencies")
    print("⚠️  This may take several minutes...")
    
    try:
        # Run PyInstaller
        result = subprocess.run(build_cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print("✅ Build completed successfully!")
            
            # Check if EXE was created
            exe_path = Path("dist/DocGenius-Console.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📁 EXE created: {exe_path}")
                print(f"📏 Size: {size_mb:.1f} MB")
                return True
            else:
                print("❌ EXE file not found!")
                return False
                
        else:
            print("❌ Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Build timed out after 10 minutes!")
        return False
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Ready for testing!")
        print("💡 Test the EXE in an isolated environment to verify it works.")
    else:
        print("\n💥 Build failed!")
        sys.exit(1)

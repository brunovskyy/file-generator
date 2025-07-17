"""
Build script for generating DocGenius executable
Run this script to create a standalone EXE file.
"""

import sys
import subprocess
import os
from pathlib import Path

def main():
    """Build DocGenius EXE using PyInstaller."""
    project_root = Path(__file__).parent.parent
    
    print("🏗️ DocGenius EXE Builder")
    print("=" * 40)
    
    # Check if PyInstaller is available
    try:
        import PyInstaller
        print("✅ PyInstaller is available")
    except ImportError:
        print("❌ PyInstaller not installed")
        print("Installing PyInstaller...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("✅ PyInstaller installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            sys.exit(1)
    
    # Icon path (can be easily modified)
    icon_path = project_root / "assets" / "icon.ico"
    
    # Build command
    build_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "DocGenius",
        "--onefile",  # Single executable file
        "--clean",
        "--windowed",  # No console window
    ]
    
    # Add icon if available
    if icon_path.exists():
        build_cmd.extend(["--icon", str(icon_path)])
        print(f"🎨 Using icon: {icon_path}")
    else:
        print("⚠️ No icon file found. Create assets/icon.ico for custom icon.")
    
    # Add hidden imports for dependencies that might not be detected
    hidden_imports = [
        "json_to_file",
        "json_to_file.source_to_json",
        "json_to_file.markdown_export", 
        "json_to_file.pdf_export",
        "json_to_file.word_export",
        "json_to_file.utils",
        "tkinter",
        "tkinter.filedialog"
    ]
    
    for import_name in hidden_imports:
        build_cmd.extend(["--hidden-import", import_name])
    
    # Add entry point
    build_cmd.append("app_launcher_cli.py")
    
    print(f"\n🔨 Build command:")
    print(" ".join(build_cmd))
    
    # Run build
    try:
        print("\n⏳ Building EXE... This may take a few minutes...")
        
        result = subprocess.run(build_cmd, cwd=project_root)
        
        if result.returncode == 0:
            print("\n✅ EXE build completed successfully!")
            
            # Find the generated EXE
            dist_dir = project_root / "dist"
            exe_path = dist_dir / "DocGenius.exe"
            
            if exe_path.exists():
                print(f"📄 EXE location: {exe_path}")
                print(f"📊 EXE size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
                
                print("\n🎉 DocGenius.exe is ready for distribution!")
                print("💡 The EXE includes all dependencies and can run on systems without Python.")
            else:
                print("⚠️ EXE file not found in expected location")
        else:
            print("❌ EXE build failed")
            print("💡 Check the output above for error details")
            
    except Exception as e:
        print(f"❌ Error during build: {e}")

if __name__ == "__main__":
    main()

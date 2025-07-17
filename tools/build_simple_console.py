"""
Simple console EXE builder for DocGenius that avoids external dependencies
"""
import subprocess
import sys
import os

def build_console_exe():
    """Build console EXE using simple PyInstaller command"""
    try:
        # Clean previous builds
        if os.path.exists('build'):
            import shutil
            shutil.rmtree('build')
        if os.path.exists('dist/DocGenius-Console.exe'):
            os.remove('dist/DocGenius-Console.exe')
            
        # Simple build command - no spec file, with requests included
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--name=DocGenius-Console',
            '--onefile',
            '--console',  # Force console window
            '--clean',
            '--noconfirm',
            '--add-data=docgenius;docgenius',  # Include the package
            '--hidden-import=requests',  # Include requests
            '--hidden-import=urllib3',
            '--hidden-import=certifi',
            '--hidden-import=charset_normalizer',
            '--hidden-import=idna',
            'app_launcher_cli.py'
        ]
        
        print("Building console EXE...")
        print(f"Command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build successful!")
            print(f"EXE created: dist/DocGenius-Console.exe")
            return True
        else:
            print("❌ Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error during build: {e}")
        return False

if __name__ == "__main__":
    build_console_exe()

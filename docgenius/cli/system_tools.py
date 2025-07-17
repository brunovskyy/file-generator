"""
System Tools Interface for DocGenius
Provides system management, installation, and EXE generation utilities.
"""

import sys
import subprocess
import os
import platform
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    # Import from new package structure
    from ..logic.utilities import MessageDialogs
    
    # Backward compatibility functions
    def yes_no_prompt(message: str) -> bool:
        """Yes/no prompt using new dialog utilities."""
        return MessageDialogs.show_yes_no("Confirm", message)
    
    def prompt_user_choice(message: str, choices: list) -> str:
        """Prompt user for choice."""
        return MessageDialogs.show_choice("Select Option", message, choices)
except ImportError:
    # Fallback implementations if utils not available
    def yes_no_prompt(prompt: str, default: bool = True) -> bool:
        default_str = "Y/n" if default else "y/N"
        response = input(f"{prompt} ({default_str}): ").strip().lower()
        if not response:
            return default
        return response in ['y', 'yes', '1', 'true']
    
    def prompt_user_choice(prompt: str, options: List[str], default: str = None) -> str:
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        
        while True:
            choice = input(f"\nChoose option (1-{len(options)}): ").strip()
            try:
                index = int(choice) - 1
                if 0 <= index < len(options):
                    return options[index]
                else:
                    print(f"Please enter a number from 1 to {len(options)}")
            except ValueError:
                print("Please enter a valid number")


class SystemToolsInterface:
    """System tools interface for installation and management."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.app_name = "DocGenius"
        self.exe_name = "DocGenius.exe"
        # Icon path - can be easily changed here
        self.icon_path = self.project_root / "assets" / "icon.ico"
    
    def show_system_menu(self) -> str:
        """Show system tools menu and get user choice."""
        print("\n⚙️ System Tools Menu:")
        print("1. Check System Requirements")
        print("2. Install/Update Dependencies")
        print("3. Create Desktop Shortcut")
        print("4. Generate EXE File")
        print("5. Setup Virtual Environment")
        print("6. System Information")
        print("7. Clean Build Files")
        print("8. Back to Main Menu")
        
        while True:
            try:
                choice = input("\nChoose option (1-8): ").strip()
                if choice in ['1', '2', '3', '4', '5', '6', '7', '8']:
                    return choice
                else:
                    print("❌ Please choose a number from 1-8.")
            except KeyboardInterrupt:
                return '8'
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
    
    def check_system_requirements(self):
        """Check system requirements for DocGenius."""
        print("\n🔍 Checking System Requirements...")
        
        # Check Python version
        python_version = sys.version_info
        print(f"🐍 Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        if python_version >= (3, 8):
            print("✅ Python version is compatible (3.8+ required)")
        else:
            print("❌ Python version is too old (3.8+ required)")
        
        # Check platform
        system = platform.system()
        print(f"💻 Operating System: {system} {platform.release()}")
        
        # Check available disk space
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.project_root)
            free_gb = free // (1024**3)
            print(f"💾 Free Disk Space: {free_gb} GB")
            
            if free_gb < 1:
                print("⚠️ Low disk space (1GB+ recommended)")
            else:
                print("✅ Sufficient disk space available")
        except Exception as e:
            print(f"⚠️ Could not check disk space: {e}")
        
        # Check internet connectivity
        print("\n🌐 Checking Internet Connectivity...")
        try:
            import urllib.request
            urllib.request.urlopen('https://pypi.org', timeout=5)
            print("✅ Internet connection available")
        except Exception:
            print("❌ No internet connection (required for package installation)")
        
        # Check required system libraries
        print("\n📚 Checking System Libraries...")
        
        system_checks = {
            'tkinter': 'GUI dialogs',
            'subprocess': 'Process management',
            'pathlib': 'Path handling',
            'json': 'JSON processing'
        }
        
        for module, description in system_checks.items():
            try:
                __import__(module)
                print(f"✅ {module} - {description}")
            except ImportError:
                print(f"❌ {module} - {description} (MISSING)")
        
        input("\nPress Enter to continue...")
    
    def install_dependencies(self):
        """Install or update project dependencies."""
        print("\n📥 Installing/Updating Dependencies...")
        
        # Check if we're in a virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        
        if not in_venv:
            print("⚠️ Not in a virtual environment")
            if yes_no_prompt("Create virtual environment first?", default=True):
                self.setup_virtual_environment()
                return
        
        # Run dependency installer
        install_script = self.project_root / "install_deps.py"
        
        if install_script.exists():
            if yes_no_prompt("Run install_deps.py?", default=True):
                try:
                    print("▶️ Running dependency installer...")
                    result = subprocess.run([
                        sys.executable, str(install_script)
                    ], cwd=self.project_root)
                    
                    if result.returncode == 0:
                        print("✅ Dependencies installed successfully")
                    else:
                        print("⚠️ Installation completed with warnings")
                        
                except Exception as e:
                    print(f"❌ Error running installer: {e}")
        
        # Offer to install build tools for EXE generation
        if yes_no_prompt("Install EXE build tools (PyInstaller)?", default=False):
            try:
                print("📦 Installing PyInstaller...")
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "pyinstaller"
                ])
                print("✅ PyInstaller installed")
            except Exception as e:
                print(f"❌ Error installing PyInstaller: {e}")
        
        input("\nPress Enter to continue...")
    
    def create_desktop_shortcut(self):
        """Create desktop shortcut for DocGenius."""
        print("\n🔗 Creating Desktop Shortcut...")
        
        desktop_path = Path.home() / "Desktop"
        
        if not desktop_path.exists():
            print("❌ Desktop folder not found")
            input("Press Enter to continue...")
            return
        
        system = platform.system()
        
        if system == "Windows":
            self._create_windows_shortcut(desktop_path)
        elif system == "Darwin":  # macOS
            self._create_macos_shortcut(desktop_path)
        elif system == "Linux":
            self._create_linux_shortcut(desktop_path)
        else:
            print(f"❌ Unsupported operating system: {system}")
        
        input("\nPress Enter to continue...")
    
    def generate_exe(self):
        """Generate standalone EXE file using PyInstaller."""
        print(f"\n🏗️ Generating {self.exe_name}...")
        
        # Check if PyInstaller is available
        try:
            import PyInstaller
            print("✅ PyInstaller is available")
        except ImportError:
            print("❌ PyInstaller not installed")
            if yes_no_prompt("Install PyInstaller now?", default=True):
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
                    print("✅ PyInstaller installed")
                except Exception as e:
                    print(f"❌ Error installing PyInstaller: {e}")
                    input("Press Enter to continue...")
                    return
            else:
                input("Press Enter to continue...")
                return
        
        # Prepare build configuration
        print("\n⚙️ Configuring build settings...")
        
        build_options = [
            "Single file (slower startup, easier distribution)",
            "Directory bundle (faster startup, multiple files)",
            "Custom configuration"
        ]
        
        build_choice = prompt_user_choice("Choose build type:", build_options)
        
        # Build command
        build_cmd = [
            sys.executable, "-m", "PyInstaller",
            "--name", "DocGenius",
            "--clean"
        ]
        
        if build_choice.startswith("Single file"):
            build_cmd.append("--onefile")
            print("📦 Building as single executable file...")
        elif build_choice.startswith("Directory"):
            build_cmd.append("--onedir")
            print("📁 Building as directory bundle...")
        
        # Add icon if available
        if self.icon_path.exists():
            build_cmd.extend(["--icon", str(self.icon_path)])
            print(f"🎨 Using icon: {self.icon_path}")
        else:
            print("⚠️ No icon file found. Create assets/icon.ico for custom icon.")
        
        # Add windowed mode (no console)
        if yes_no_prompt("Hide console window? (recommended for end users)", default=True):
            build_cmd.append("--windowed")
        
        # Add entry point
        build_cmd.append("app_launcher_cli.py")
        
        print(f"\n🔨 Build command: {' '.join(build_cmd)}")
        
        if yes_no_prompt("Proceed with build?", default=True):
            try:
                print("\n⏳ Building EXE... This may take a few minutes...")
                
                result = subprocess.run(build_cmd, cwd=self.project_root)
                
                if result.returncode == 0:
                    print("✅ EXE build completed successfully!")
                    
                    # Find the generated EXE
                    dist_dir = self.project_root / "dist"
                    if dist_dir.exists():
                        exe_files = list(dist_dir.glob("*.exe"))
                        if exe_files:
                            exe_path = exe_files[0]
                            print(f"📄 EXE location: {exe_path}")
                            
                            if yes_no_prompt("Test the generated EXE?", default=True):
                                try:
                                    subprocess.Popen([str(exe_path)], cwd=exe_path.parent)
                                    print("🚀 EXE launched for testing")
                                except Exception as e:
                                    print(f"❌ Error testing EXE: {e}")
                        else:
                            print("⚠️ EXE file not found in dist/ directory")
                    else:
                        print("⚠️ dist/ directory not found")
                else:
                    print("❌ EXE build failed")
                    print("💡 Check the output above for error details")
                    
            except Exception as e:
                print(f"❌ Error during build: {e}")
        
        input("\nPress Enter to continue...")
    
    def setup_virtual_environment(self):
        """Setup virtual environment for the project."""
        print("\n🐍 Setting up Virtual Environment...")
        
        venv_path = self.project_root / ".venv"
        
        if venv_path.exists():
            print(f"⚠️ Virtual environment already exists at: {venv_path}")
            if not yes_no_prompt("Recreate virtual environment?", default=False):
                input("Press Enter to continue...")
                return
            
            # Remove existing venv
            import shutil
            try:
                shutil.rmtree(venv_path)
                print("🗑️ Removed existing virtual environment")
            except Exception as e:
                print(f"❌ Error removing existing venv: {e}")
                input("Press Enter to continue...")
                return
        
        try:
            print("📦 Creating virtual environment...")
            subprocess.run([
                sys.executable, "-m", "venv", str(venv_path)
            ], check=True)
            
            print("✅ Virtual environment created")
            
            # Determine activation script
            system = platform.system()
            if system == "Windows":
                activate_script = venv_path / "Scripts" / "activate.bat"
                pip_executable = venv_path / "Scripts" / "pip.exe"
            else:
                activate_script = venv_path / "bin" / "activate"
                pip_executable = venv_path / "bin" / "pip"
            
            print(f"\n📋 To activate the virtual environment:")
            if system == "Windows":
                print(f"   {activate_script}")
            else:
                print(f"   source {activate_script}")
            
            # Install dependencies in the new environment
            if yes_no_prompt("Install dependencies in virtual environment?", default=True):
                try:
                    print("📥 Installing dependencies...")
                    subprocess.run([
                        str(pip_executable), "install", "-r", "requirements.txt"
                    ], cwd=self.project_root, check=True)
                    
                    print("✅ Dependencies installed in virtual environment")
                except Exception as e:
                    print(f"❌ Error installing dependencies: {e}")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating virtual environment: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        input("\nPress Enter to continue...")
    
    def show_system_info(self):
        """Display detailed system information."""
        print("\n💻 System Information")
        print("=" * 50)
        
        # Python information
        print(f"🐍 Python Version: {sys.version}")
        print(f"📁 Python Executable: {sys.executable}")
        print(f"📚 Python Path: {sys.path[0]}")
        
        # System information
        print(f"\n💻 System: {platform.system()} {platform.release()}")
        print(f"🏗️ Architecture: {platform.architecture()[0]}")
        print(f"💾 Machine: {platform.machine()}")
        print(f"🖥️ Processor: {platform.processor()}")
        
        # Project information
        print(f"\n📁 Project Root: {self.project_root}")
        print(f"📂 Working Directory: {os.getcwd()}")
        
        # Environment information
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        print(f"🐍 Virtual Environment: {'Yes' if in_venv else 'No'}")
        
        if in_venv:
            print(f"📁 Virtual Env Path: {sys.prefix}")
        
        # Disk space
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.project_root)
            print(f"\n💾 Disk Usage:")
            print(f"   Total: {total // (1024**3)} GB")
            print(f"   Used: {used // (1024**3)} GB") 
            print(f"   Free: {free // (1024**3)} GB")
        except Exception:
            print("💾 Disk usage information unavailable")
        
        input("\nPress Enter to continue...")
    
    def clean_build_files(self):
        """Clean build files and temporary directories."""
        print("\n🧹 Cleaning Build Files...")
        
        # Directories to clean
        clean_dirs = [
            "build",
            "dist", 
            "__pycache__",
            "*.egg-info"
        ]
        
        # Files to clean
        clean_files = [
            "*.pyc",
            "*.pyo", 
            "*.pyd",
            ".DS_Store",
            "Thumbs.db"
        ]
        
        print("📋 Will clean the following:")
        for dir_name in clean_dirs:
            print(f"   📁 {dir_name}/")
        for file_pattern in clean_files:
            print(f"   📄 {file_pattern}")
        
        if yes_no_prompt("Proceed with cleanup?", default=True):
            cleaned_count = 0
            
            # Clean directories
            import shutil
            for dir_name in clean_dirs:
                if dir_name.endswith("*"):
                    # Handle wildcard patterns
                    pattern = dir_name.replace("*", "")
                    for item in self.project_root.rglob(f"*{pattern}"):
                        if item.is_dir():
                            try:
                                shutil.rmtree(item)
                                print(f"🗑️ Removed: {item}")
                                cleaned_count += 1
                            except Exception as e:
                                print(f"❌ Could not remove {item}: {e}")
                else:
                    dir_path = self.project_root / dir_name
                    if dir_path.exists():
                        try:
                            shutil.rmtree(dir_path)
                            print(f"🗑️ Removed: {dir_path}")
                            cleaned_count += 1
                        except Exception as e:
                            print(f"❌ Could not remove {dir_path}: {e}")
            
            # Clean files
            for file_pattern in clean_files:
                if "*" in file_pattern:
                    for file_path in self.project_root.rglob(file_pattern):
                        if file_path.is_file():
                            try:
                                file_path.unlink()
                                print(f"🗑️ Removed: {file_path}")
                                cleaned_count += 1
                            except Exception as e:
                                print(f"❌ Could not remove {file_path}: {e}")
            
            print(f"\n✅ Cleanup completed. Removed {cleaned_count} items.")
        
        input("\nPress Enter to continue...")
    
    def _create_windows_shortcut(self, desktop_path: Path):
        """Create Windows desktop shortcut."""
        try:
            import winshell
            from win32com.client import Dispatch
            
            shortcut_path = desktop_path / f"{self.app_name}.lnk"
            target = sys.executable
            arguments = str(self.project_root / "app_launcher_cli.py")
            working_dir = str(self.project_root)
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = target
            shortcut.Arguments = arguments
            shortcut.WorkingDirectory = working_dir
            shortcut.WindowStyle = 1  # Normal window
            
            if self.icon_path.exists():
                shortcut.IconLocation = str(self.icon_path)
            
            shortcut.save()
            
            print(f"✅ Desktop shortcut created: {shortcut_path}")
            
        except ImportError:
            print("❌ Required packages not available (winshell, pywin32)")
            print("💡 Install with: pip install winshell pywin32")
        except Exception as e:
            print(f"❌ Error creating shortcut: {e}")
    
    def _create_macos_shortcut(self, desktop_path: Path):
        """Create macOS desktop shortcut."""
        try:
            app_script = f"""#!/bin/bash
cd "{self.project_root}"
python app_launcher_cli.py
"""
            shortcut_path = desktop_path / f"{self.app_name}.command"
            shortcut_path.write_text(app_script)
            shortcut_path.chmod(0o755)
            
            print(f"✅ Desktop shortcut created: {shortcut_path}")
            
        except Exception as e:
            print(f"❌ Error creating shortcut: {e}")
    
    def _create_linux_shortcut(self, desktop_path: Path):
        """Create Linux desktop shortcut."""
        try:
            desktop_entry = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={self.app_name}
Comment=Document Creator Toolkit
Exec=python {self.project_root / 'app_launcher_cli.py'}
Path={self.project_root}
Terminal=true
StartupNotify=false
"""
            
            shortcut_path = desktop_path / f"{self.app_name}.desktop"
            shortcut_path.write_text(desktop_entry)
            shortcut_path.chmod(0o755)
            
            print(f"✅ Desktop shortcut created: {shortcut_path}")
            
        except Exception as e:
            print(f"❌ Error creating shortcut: {e}")
    
    def run(self):
        """Main system tools interface loop."""
        while True:
            try:
                choice = self.show_system_menu()
                
                if choice == '1':
                    self.check_system_requirements()
                elif choice == '2':
                    self.install_dependencies()
                elif choice == '3':
                    self.create_desktop_shortcut()
                elif choice == '4':
                    self.generate_exe()
                elif choice == '5':
                    self.setup_virtual_environment()
                elif choice == '6':
                    self.show_system_info()
                elif choice == '7':
                    self.clean_build_files()
                elif choice == '8':
                    print("🔙 Returning to main menu...")
                    break
                    
            except KeyboardInterrupt:
                if yes_no_prompt("\n⚠️ Return to main menu?", default=True):
                    break
                continue
            except Exception as e:
                print(f"❌ Error in system tools: {e}")
                if not yes_no_prompt("Continue in system tools?", default=True):
                    break

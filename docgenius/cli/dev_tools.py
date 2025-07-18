"""
Developer Tools Interface for DocGenius
Provides testing, debugging, and development utilities.
"""

import sys
import subprocess
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    # Import from new package structure
    from ..logic.utilities import (
        MessageDialogs, FileDialogs, DialogResult,
        LoggingConfigurator, SessionLogger,
        ValidationEngine
    )
    
    # Backward compatibility functions
    def yes_no_prompt(message: str, default: bool = True) -> bool:
        """Yes/no prompt using new dialog utilities."""
        dialogs = MessageDialogs()
        result = dialogs.confirm("Confirm", message)
        return result.value if result.success else default
    
    def prompt_user_choice(message: str, choices: list, default: str = None) -> str:
        """Prompt user for choice."""
        print(f"\n{message}")
        for i, choice in enumerate(choices, 1):
            marker = " (default)" if choice == default else ""
            print(f"{i}. {choice}{marker}")
        
        while True:
            try:
                user_input = input(f"\nChoose 1-{len(choices)} (or 'help'/'back'): ").strip()
                
                if user_input.lower() == 'help':
                    print("Valid commands:")
                    print(f"- Type a number (1-{len(choices)}) to select an option")
                    print("- Type 'help' to see this message")
                    print("- Type 'back' to return to previous step")
                    continue
                elif user_input.lower() == 'back':
                    return "back"
                
                choice_index = int(user_input) - 1
                if 0 <= choice_index < len(choices):
                    return choices[choice_index]
                else:
                    print(f"❌ Invalid option. Please choose 1-{len(choices)}.")
            except ValueError:
                print(f"❌ Please enter a number (1-{len(choices)}) or 'help'/'back'.")
            except KeyboardInterrupt:
                return "back"
    
    def select_folder_with_dialog() -> str:
        """Select folder with dialog."""
        file_dialogs = FileDialogs()
        result = file_dialogs.select_directory("Select Directory")
        return result.selected_path if result.success else ""
    
    def validate_data_source(file_path: str) -> bool:
        """Validate data source using new validation utilities."""
        validator = ValidationEngine()
        return validator.validate_file_path(file_path)
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


class DevToolsInterface:
    """Developer tools interface for testing and debugging."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
    
    def show_dev_menu(self) -> str:
        """Show developer tools menu and get user choice."""
        print("\n🔧 Developer Tools Menu:")
        print("1. Run All Tests")
        print("2. Run Specific Test Module") 
        print("3. Test Features (Interactive)")
        print("4. Check Dependencies")
        print("5. Install/Update Dependencies")
        print("6. View Development Logs")
        print("7. Generate Development Report")
        print("8. Check Code Quality")
        print("9. Back to Main Menu")
        
        while True:
            try:
                choice = input("\nChoose option (1-9): ").strip()
                if choice in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    return choice
                else:
                    print("❌ Please choose a number from 1-9.")
            except KeyboardInterrupt:
                return '9'
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
    
    def run_all_tests(self):
        """Run all test modules."""
        print("\n🧪 Running all tests...")
        
        test_files = [
            "run_tests.py",
            "tests/run_organized_tests.py"
        ]
        
        for test_file in test_files:
            test_path = self.project_root / test_file
            if test_path.exists():
                print(f"\n▶️ Running {test_file}...")
                try:
                    result = subprocess.run([
                        sys.executable, str(test_path)
                    ], capture_output=True, text=True, cwd=self.project_root)
                    
                    if result.returncode == 0:
                        print(f"✅ {test_file} passed")
                        if result.stdout:
                            print(result.stdout)
                    else:
                        print(f"❌ {test_file} failed")
                        if result.stderr:
                            print(result.stderr)
                        if result.stdout:
                            print(result.stdout)
                            
                except Exception as e:
                    print(f"❌ Error running {test_file}: {e}")
            else:
                print(f"⚠️ Test file {test_file} not found")
        
        input("\nPress Enter to continue...")
    
    def run_specific_test(self):
        """Run a specific test module."""
        print("\n🎯 Running specific test module...")
        
        test_modules = []
        tests_dir = self.project_root / "tests"
        
        if tests_dir.exists():
            for test_file in tests_dir.glob("test_*.py"):
                test_modules.append(test_file.name)
        
        if not test_modules:
            print("❌ No test modules found in tests/ directory")
            input("Press Enter to continue...")
            return
        
        print("\nAvailable test modules:")
        for i, module in enumerate(test_modules, 1):
            print(f"  {i}. {module}")
        
        try:
            choice = input(f"\nChoose module (1-{len(test_modules)}): ").strip()
            index = int(choice) - 1
            
            if 0 <= index < len(test_modules):
                selected_module = test_modules[index]
                test_path = tests_dir / selected_module
                
                print(f"\n▶️ Running {selected_module}...")
                
                result = subprocess.run([
                    sys.executable, "-m", "pytest", str(test_path), "-v"
                ], capture_output=True, text=True, cwd=self.project_root)
                
                if result.returncode == 0:
                    print(f"✅ {selected_module} passed")
                else:
                    print(f"❌ {selected_module} failed")
                
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(result.stderr)
            else:
                print("❌ Invalid selection")
                
        except ValueError:
            print("❌ Please enter a valid number")
        except Exception as e:
            print(f"❌ Error running test: {e}")
        
        input("\nPress Enter to continue...")
    
    def test_features_interactive(self):
        """Run interactive feature testing."""
        print("\n🎮 Interactive Feature Testing")
        
        # Check if test_features.py exists
        test_features_path = self.project_root / "test_features.py"
        
        if test_features_path.exists():
            print("🔍 Found test_features.py - running interactive tests...")
            try:
                result = subprocess.run([
                    sys.executable, str(test_features_path)
                ], cwd=self.project_root)
                
                if result.returncode != 0:
                    print("⚠️ Interactive tests completed with warnings/errors")
                    
            except Exception as e:
                print(f"❌ Error running interactive tests: {e}")
        else:
            # Provide manual testing options
            print("📋 Manual Feature Testing Options:")
            
            test_options = [
                "Test file dialog functionality",
                "Test data loading (CSV/JSON)",
                "Test export modules",
                "Test CLI navigation",
                "Back to dev menu"
            ]
            
            choice = prompt_user_choice("Choose test to run:", test_options)
            
            if choice == "Test file dialog functionality":
                self._test_file_dialogs()
            elif choice == "Test data loading (CSV/JSON)":
                self._test_data_loading()
            elif choice == "Test export modules":
                self._test_export_modules()
            elif choice == "Test CLI navigation":
                self._test_cli_navigation()
        
        input("\nPress Enter to continue...")
    
    def check_dependencies(self):
        """Check project dependencies."""
        print("\n📦 Checking Dependencies...")
        
        try:
            # Check requirements.txt
            req_file = self.project_root / "requirements.txt"
            if req_file.exists():
                print("✅ requirements.txt found")
                
                # Try to import each module
                dependencies = {
                    'requests': 'Network requests',
                    'PyYAML': 'YAML processing', 
                    'reportlab': 'PDF export',
                    'python-docx': 'Word export',
                    'docxtpl': 'Word templates',
                    'colorama': 'Colored output',
                    'tkinter': 'GUI dialogs'
                }
                
                print("\n📋 Dependency Status:")
                for package, description in dependencies.items():
                    try:
                        if package == 'python-docx':
                            import docx
                        elif package == 'PyYAML':
                            import yaml
                        else:
                            __import__(package)
                        print(f"✅ {package:<15} - {description}")
                    except ImportError:
                        print(f"❌ {package:<15} - {description} (MISSING)")
            else:
                print("⚠️ requirements.txt not found")
                
        except Exception as e:
            print(f"❌ Error checking dependencies: {e}")
        
        input("\nPress Enter to continue...")
    
    def install_dependencies(self):
        """Install or update dependencies."""
        print("\n📥 Installing/Updating Dependencies...")
        
        if yes_no_prompt("Run dependency installer?", default=True):
            install_script = self.project_root / "install_deps.py"
            
            if install_script.exists():
                try:
                    print("▶️ Running install_deps.py...")
                    result = subprocess.run([
                        sys.executable, str(install_script)
                    ], cwd=self.project_root)
                    
                    if result.returncode == 0:
                        print("✅ Dependencies installed successfully")
                    else:
                        print("⚠️ Installation completed with warnings")
                        
                except Exception as e:
                    print(f"❌ Error running installer: {e}")
            else:
                print("❌ install_deps.py not found")
                if yes_no_prompt("Install from requirements.txt instead?", default=True):
                    try:
                        result = subprocess.run([
                            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
                        ], cwd=self.project_root)
                        
                        if result.returncode == 0:
                            print("✅ Dependencies installed from requirements.txt")
                        else:
                            print("❌ Failed to install from requirements.txt")
                    except Exception as e:
                        print(f"❌ Error installing dependencies: {e}")
        
        input("\nPress Enter to continue...")
    
    def view_dev_logs(self):
        """View development logs."""
        print("\n📋 Development Logs")
        
        logs_dir = self.project_root / ".dev" / "logs"
        
        if not logs_dir.exists():
            print("❌ .dev/logs directory not found")
            input("Press Enter to continue...")
            return
        
        log_files = list(logs_dir.glob("*.md"))
        
        if not log_files:
            print("❌ No log files found in .dev/logs/")
            input("Press Enter to continue...")
            return
        
        # Sort by modification time (newest first)
        log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        print(f"\n📁 Found {len(log_files)} log files:")
        for i, log_file in enumerate(log_files, 1):
            print(f"  {i}. {log_file.name}")
        
        try:
            choice = input(f"\nChoose log to view (1-{len(log_files)}) or Enter for latest: ").strip()
            
            if not choice:
                selected_log = log_files[0]  # Latest
            else:
                index = int(choice) - 1
                if 0 <= index < len(log_files):
                    selected_log = log_files[index]
                else:
                    print("❌ Invalid selection")
                    input("Press Enter to continue...")
                    return
            
            print(f"\n📖 Viewing: {selected_log.name}")
            print("=" * 60)
            
            try:
                content = selected_log.read_text(encoding='utf-8')
                print(content)
            except Exception as e:
                print(f"❌ Error reading log file: {e}")
                
        except ValueError:
            print("❌ Please enter a valid number")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")
    
    def generate_dev_report(self):
        """Generate a development status report."""
        print("\n📊 Generating Development Report...")
        
        report = []
        report.append("# DocGenius Development Status Report")
        report.append(f"**Generated:** {self._get_current_timestamp()}\n")
        
        # Project structure
        report.append("## 📁 Project Structure")
        try:
            structure = self._get_project_structure()
            report.append("```")
            report.extend(structure)
            report.append("```\n")
        except Exception as e:
            report.append(f"❌ Error getting project structure: {e}\n")
        
        # Dependencies status
        report.append("## 📦 Dependencies Status")
        try:
            deps_status = self._get_dependencies_status()
            report.extend(deps_status)
            report.append("")
        except Exception as e:
            report.append(f"❌ Error checking dependencies: {e}\n")
        
        # Recent changes
        report.append("## 📝 Recent Development Logs")
        try:
            recent_logs = self._get_recent_logs()
            report.extend(recent_logs)
        except Exception as e:
            report.append(f"❌ Error getting recent logs: {e}\n")
        
        # Save report
        report_path = self.project_root / ".dev" / "logs" / f"dev_report_{self._get_timestamp_for_filename()}.md"
        
        try:
            report_path.parent.mkdir(exist_ok=True)
            report_path.write_text("\n".join(report), encoding='utf-8')
            print(f"✅ Report saved to: {report_path}")
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            print("\n📄 Report content:")
            print("\n".join(report))
        
        input("\nPress Enter to continue...")
    
    def check_code_quality(self):
        """Check code quality and formatting."""
        print("\n🔍 Checking Code Quality...")
        
        # Check if code quality tools are available
        tools_to_check = [
            ("black", "Code formatting"),
            ("flake8", "Code linting"),
            ("mypy", "Type checking")
        ]
        
        available_tools = []
        
        for tool, description in tools_to_check:
            try:
                result = subprocess.run([tool, "--version"], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    available_tools.append((tool, description))
                    print(f"✅ {tool} available - {description}")
                else:
                    print(f"❌ {tool} not available - {description}")
            except FileNotFoundError:
                print(f"❌ {tool} not installed - {description}")
        
        if not available_tools:
            print("\n⚠️ No code quality tools available")
            if yes_no_prompt("Install code quality tools?", default=False):
                try:
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", 
                        "black", "flake8", "mypy"
                    ])
                    print("✅ Code quality tools installed")
                except Exception as e:
                    print(f"❌ Error installing tools: {e}")
        else:
            if yes_no_prompt("Run code quality checks?", default=True):
                for tool, description in available_tools:
                    print(f"\n▶️ Running {tool}...")
                    try:
                        if tool == "black":
                            result = subprocess.run([tool, ".", "--check"], 
                                                  cwd=self.project_root)
                        elif tool == "flake8":
                            result = subprocess.run([tool, "."], 
                                                  cwd=self.project_root)
                        elif tool == "mypy":
                            result = subprocess.run([tool, "document_creator_core.py"], 
                                                  cwd=self.project_root)
                        
                        if result.returncode == 0:
                            print(f"✅ {tool} checks passed")
                        else:
                            print(f"⚠️ {tool} found issues")
                    except Exception as e:
                        print(f"❌ Error running {tool}: {e}")
        
        input("\nPress Enter to continue...")
    
    def _test_file_dialogs(self):
        """Test file dialog functionality."""
        print("\n🔍 Testing File Dialogs...")
        try:
            # Use the already imported select_folder_with_dialog
            print("Testing folder dialog...")
            folder = select_folder_with_dialog("Test Folder Selection")
            if folder:
                print(f"✅ Folder selected: {folder}")
            else:
                print("❌ No folder selected")
        except Exception as e:
            print(f"❌ Error testing dialogs: {e}")
    
    def _test_data_loading(self):
        """Test data loading functionality."""
        print("\n📊 Testing Data Loading...")
        try:
            # Use the already imported validate_data_source
            
            test_sources = [
                "tests/data/test_data.json",
                "tests/data/test_data.csv", 
                "https://jsonplaceholder.typicode.com/users"
            ]
            
            for source in test_sources:
                result = validate_data_source(source)
                status = "✅" if result else "❌"
                print(f"{status} {source}")
                
        except Exception as e:
            print(f"❌ Error testing data loading: {e}")
    
    def _test_export_modules(self):
        """Test export modules."""
        print("\n📄 Testing Export Modules...")
        try:
            modules_to_test = [
                ("json_to_file.markdown_export", "Markdown Export"),
                ("json_to_file.pdf_export", "PDF Export"),
                ("json_to_file.word_export", "Word Export")
            ]
            
            for module_name, description in modules_to_test:
                try:
                    __import__(module_name)
                    print(f"✅ {description} module loaded")
                except ImportError as e:
                    print(f"❌ {description} module failed: {e}")
                    
        except Exception as e:
            print(f"❌ Error testing export modules: {e}")
    
    def _test_cli_navigation(self):
        """Test CLI navigation functionality."""
        print("\n🧭 Testing CLI Navigation...")
        print("💡 This would launch the document creator in test mode")
        print("   For now, manually test using: python document_creator_core.py")
    
    def _get_current_timestamp(self):
        """Get current timestamp for reports."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_timestamp_for_filename(self):
        """Get timestamp suitable for filenames."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    def _get_project_structure(self):
        """Get project structure as list of strings."""
        structure = []
        
        def add_tree(path: Path, prefix: str = ""):
            try:
                items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
                for i, item in enumerate(items):
                    is_last = i == len(items) - 1
                    current_prefix = "└── " if is_last else "├── "
                    structure.append(f"{prefix}{current_prefix}{item.name}")
                    
                    if item.is_dir() and not item.name.startswith('.') and item.name != '__pycache__':
                        next_prefix = prefix + ("    " if is_last else "│   ")
                        if len(structure) < 50:  # Limit depth
                            add_tree(item, next_prefix)
            except PermissionError:
                pass
        
        structure.append("file-generator/")
        add_tree(self.project_root)
        return structure
    
    def _get_dependencies_status(self):
        """Get dependencies status as list of strings."""
        status = []
        
        dependencies = {
            'requests': 'Network requests',
            'PyYAML': 'YAML processing', 
            'reportlab': 'PDF export',
            'python-docx': 'Word export',
            'docxtpl': 'Word templates',
            'colorama': 'Colored output'
        }
        
        for package, description in dependencies.items():
            try:
                if package == 'python-docx':
                    import docx
                elif package == 'PyYAML':
                    import yaml
                else:
                    __import__(package)
                status.append(f"- ✅ **{package}** - {description}")
            except ImportError:
                status.append(f"- ❌ **{package}** - {description} (MISSING)")
        
        return status
    
    def _get_recent_logs(self):
        """Get recent development logs."""
        logs = []
        
        logs_dir = self.project_root / ".dev" / "logs"
        if logs_dir.exists():
            log_files = sorted(logs_dir.glob("*.md"), 
                             key=lambda x: x.stat().st_mtime, reverse=True)
            
            for log_file in log_files[:3]:  # Last 3 logs
                logs.append(f"- **{log_file.name}**")
        else:
            logs.append("- No development logs found")
        
        return logs
    
    def run(self):
        """Main developer tools interface loop."""
        while True:
            try:
                choice = self.show_dev_menu()
                
                if choice == '1':
                    self.run_all_tests()
                elif choice == '2':
                    self.run_specific_test()
                elif choice == '3':
                    self.test_features_interactive()
                elif choice == '4':
                    self.check_dependencies()
                elif choice == '5':
                    self.install_dependencies()
                elif choice == '6':
                    self.view_dev_logs()
                elif choice == '7':
                    self.generate_dev_report()
                elif choice == '8':
                    self.check_code_quality()
                elif choice == '9':
                    print("🔙 Returning to main menu...")
                    break
                    
            except KeyboardInterrupt:
                if yes_no_prompt("\n⚠️ Return to main menu?", default=True):
                    break
                continue
            except Exception as e:
                print(f"❌ Error in developer tools: {e}")
                if not yes_no_prompt("Continue in developer tools?", default=True):
                    break

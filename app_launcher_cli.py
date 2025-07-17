#!/usr/bin/env python3
"""
DocGenius - Document Creator Toolkit
Main application launcher with menu system for document creation and developer tools.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    # Import from new package structure
    from docgenius.logic.utilities import (
        DialogResult, FileDialogs, MessageDialogs, 
        LoggingConfigurator, SessionLogger
    )
    from docgenius.core.document_creator import main as document_creator_main
    from docgenius.cli.dev_tools import DevToolsInterface
    from docgenius.cli.system_tools import SystemToolsInterface
    
    # Backward compatibility utilities
    def setup_logging(log_level='INFO'):
        """Setup logging using new utilities structure."""
        configurator = LoggingConfigurator()
        logger = configurator.setup_application_logging(
            log_level=log_level,
            log_to_file=str(project_root / 'logs' / 'app_launcher_cli.log')
        )
        return logger
    
    def yes_no_prompt(message: str) -> bool:
        """Yes/no prompt using new dialog utilities."""
        return MessageDialogs.show_yes_no("Confirm", message)
except ImportError as e:
    print(f"❌ Import error: {e}")
    
    # Check if we're running as a bundled executable
    if getattr(sys, 'frozen', False):
        print("❌ Missing dependencies in bundled executable!")
        print("💡 This appears to be a packaging issue. Please report this bug.")
        print("🔧 Try downloading a fresh copy of the application.")
        input("Press Enter to exit...")
        sys.exit(1)
    else:
        print("💡 Running dependency check...")
        
        # Try to import and run dependency installer
        try:
            from tools import deps_installer_tool
            deps_installer_tool.main()
            print("✅ Dependencies installed. Please restart the application.")
            input("Press Enter to exit...")
            sys.exit(0)
        except ImportError:
            print("❌ Could not find dependency installer. Please run: python install_deps.py")
            input("Press Enter to exit...")
            sys.exit(1)


class DocGeniusApp:
    """Main application class for DocGenius toolkit."""
    
    def __init__(self):
        self.dev_tools = DevToolsInterface()
        self.system_tools = SystemToolsInterface()
        setup_logging("INFO")
    
    def show_banner(self):
        """Display application banner."""
        print("\n" + "="*60)
        print("🚀 DocGenius - Document Creator Toolkit")
        print("   Create documents from data sources with ease")
        print("="*60)
    
    def show_main_menu(self) -> str:
        """Display main menu and get user choice."""
        print("\n📋 Main Menu:")
        print("1. Create Documents")
        print("2. Developer Tools") 
        print("3. System Tools")
        print("4. Exit")
        
        while True:
            try:
                choice = input("\nChoose option (1-4): ").strip()
                if choice in ['1', '2', '3', '4']:
                    return choice
                else:
                    print("❌ Please choose a number from 1-4.")
            except KeyboardInterrupt:
                return '4'
            except Exception as e:
                print(f"❌ Error: {e}")
                continue
    
    def run_document_creator(self):
        """Run the document creation functionality."""
        try:
            print("\n🔄 Launching Document Creator...")
            document_creator_main()
        except KeyboardInterrupt:
            print("\n⚠️ Document creation cancelled.")
        except Exception as e:
            print(f"❌ Error in document creator: {e}")
            if yes_no_prompt("Return to main menu?", default=True):
                return
            else:
                sys.exit(1)
    
    def run_dev_tools(self):
        """Run developer tools interface."""
        try:
            print("\n🔧 Launching Developer Tools...")
            self.dev_tools_cli.run()
        except KeyboardInterrupt:
            print("\n⚠️ Developer tools cancelled.")
        except Exception as e:
            print(f"❌ Error in developer tools: {e}")
    
    def run_system_tools(self):
        """Run system tools interface."""
        try:
            print("\n⚙️ Launching System Tools...")
            self.system_tools_cli.run()
        except KeyboardInterrupt:
            print("\n⚠️ System tools cancelled.")
        except Exception as e:
            print(f"❌ Error in system tools: {e}")
    
    def run(self):
        """Main application loop."""
        self.show_banner()
        
        while True:
            try:
                choice = self.show_main_menu()
                
                if choice == '1':
                    self.run_document_creator()
                elif choice == '2':
                    self.run_dev_tools()
                elif choice == '3':
                    self.run_system_tools()
                elif choice == '4':
                    print("\n👋 Thank you for using DocGenius!")
                    break
                    
            except KeyboardInterrupt:
                if yes_no_prompt("\n⚠️ Do you want to exit DocGenius?", default=False):
                    break
                continue
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                if not yes_no_prompt("Continue running?", default=True):
                    break


def main():
    """Entry point for DocGenius application."""
    try:
        app = DocGeniusApp()
        app.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

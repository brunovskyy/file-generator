#!/usr/bin/env python3
"""
Simple runner for the file renaming script.
Run this to rename all files with the new naming convention.
"""

import subprocess
import sys
from pathlib import Path

def main():
    # Get the path to the renaming script
    script_dir = Path(__file__).parent
    rename_script = script_dir / "rename_files_with_imports.py"
    
    print("DocGenius File Renaming Tool")
    print("=" * 30)
    print()
    print("This will rename files according to the new naming convention:")
    print("- app_launcher_cli.py → app_launcher_cli.py")
    print("- document_creator_core.py → document_creator_core.py")
    print("- All logic layer files with consistent patterns")
    print("- And update ALL imports automatically!")
    print()
    
    # Ask user what they want to do
    print("Options:")
    print("1. Dry run (show what would happen)")
    print("2. Execute renaming")
    print("3. Cancel")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            print("\n--- Running DRY RUN ---")
            subprocess.run([sys.executable, str(rename_script), "--dry-run"])
            break
        elif choice == "2":
            print("\n--- Running LIVE EXECUTION ---")
            subprocess.run([sys.executable, str(rename_script)])
            break
        elif choice == "3":
            print("Cancelled.")
            break
        else:
            print("Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()

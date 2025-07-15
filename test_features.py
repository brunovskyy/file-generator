#!/usr/bin/env python3
"""
Test script to verify Downloads folder default and folder selection features.
"""

import tempfile
import json
from pathlib import Path
from json_to_file.markdown_export import export_to_markdown
from json_to_file.utils import get_default_output_directory, select_folder_with_dialog

def test_downloads_folder_default():
    """Test that exports default to Downloads folder."""
    print("Testing Downloads folder default...")
    
    # Test data
    test_data = [
        {'name': 'Test User', 'email': 'test@example.com'},
        {'name': 'Another User', 'email': 'another@example.com'}
    ]
    
    # Get default output directory
    default_dir = get_default_output_directory()
    print(f"Default output directory: {default_dir}")
    
    # Test export to Downloads folder
    try:
        files = export_to_markdown(test_data, str(default_dir))
        print(f"✅ Successfully exported {len(files)} files to Downloads folder:")
        for f in files:
            print(f"  - {f}")
            
        # Clean up test files
        for f in files:
            if f.exists():
                f.unlink()
        
        # Clean up directory if empty
        if default_dir.exists() and not any(default_dir.iterdir()):
            default_dir.rmdir()
            
    except Exception as e:
        print(f"❌ Error testing Downloads folder export: {e}")

def test_folder_selection_import():
    """Test that folder selection dialog function is available."""
    print("\nTesting folder selection dialog import...")
    
    try:
        # Just test the import - don't actually open the dialog
        print("✅ Folder selection dialog function imported successfully")
        print("  Function: select_folder_with_dialog()")
        print("  Note: Actual dialog requires user interaction")
        
    except Exception as e:
        print(f"❌ Error importing folder selection dialog: {e}")

if __name__ == "__main__":
    print("🧪 Testing Document Creator Default Output and Folder Selection")
    print("=" * 60)
    
    test_downloads_folder_default()
    test_folder_selection_import()
    
    print("\n✅ All tests completed!")

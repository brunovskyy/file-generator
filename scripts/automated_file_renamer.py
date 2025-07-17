#!/usr/bin/env python3
"""
Automated File Renaming Script for DocGenius Project
Renames files according to the new naming convention and updates all imports automatically.

Usage: python tools/rename_files_with_imports.py [--dry-run]
"""

import os
import re
import sys
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Set
import argparse

# Define the renaming mapping based on our analysis
RENAME_MAPPING = {
    # Root level core files
    'app_launcher_cli.py': 'app_launcher_cli.py',
    'document_creator_core.py': 'document_creator_core.py',
    'dev_tools_cli.py': 'dev_tools_cli.py',
    'system_tools_cli.py': 'system_tools_cli.py',
    'legacy_compat_layer.py': 'legacy_compat_layer.py',
    
    # Logic layer - data sources
    'logic/data_sources/base_loader.py': 'logic/data_sources/data_loader_base.py',
    'logic/data_sources/csv_loader.py': 'logic/data_sources/data_loader_csv.py',
    'logic/data_sources/json_loader.py': 'logic/data_sources/data_loader_json.py',
    'logic/data_sources/excel_loader.py': 'logic/data_sources/data_loader_excel.py',
    
    # Logic layer - exporters
    'logic/exporters/base_exporter.py': 'logic/exporters/export_handler_base.py',
    'logic/exporters/markdown_exporter.py': 'logic/exporters/export_handler_markdown.py',
    'logic/exporters/pdf_exporter.py': 'logic/exporters/export_handler_pdf.py',
    'logic/exporters/word_exporter.py': 'logic/exporters/export_handler_word.py',
    
    # Logic layer - models
    'logic/models/document.py': 'logic/models/document_model_core.py',
    'logic/models/table.py': 'logic/models/table_model_core.py',
    'logic/models/chart.py': 'logic/models/chart_model_core.py',
    
    # Logic layer - utilities
    'logic/utilities/file_utils.py': 'logic/utilities/file_utils_core.py',
    'logic/utilities/validation.py': 'logic/utilities/validation_utils_core.py',
    'logic/utilities/config.py': 'logic/utilities/config_manager_core.py',
    'logic/utilities/logging_config.py': 'logic/utilities/logging_config_manager.py',
    
    # Tools
    'tools/install_deps.py': 'tools/deps_installer_tool.py',
    'tools/setup.py': 'tools/setup_installer_tool.py',
    'tools/run_tests.py': 'tools/test_runner_tool.py',
    'tools/build_exe.py': 'tools/build_exe_tool.py',
    
    # Tests
    'tests/test_base.py': 'tests/test_base_framework.py',
    'tests/test_end_to_end.py': 'tests/test_integration_e2e.py',
    'tests/test_markdown_export.py': 'tests/test_export_markdown.py',
    'tests/test_source_to_json.py': 'tests/test_data_source_json.py',
    'tests/test_unified_exports.py': 'tests/test_export_unified.py',
    'tests/run_organized_tests.py': 'tests/test_runner_organized.py',
}

class FileRenamer:
    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root
        self.dry_run = dry_run
        self.changes_made = []
        self.errors = []
        
    def find_all_python_files(self) -> List[Path]:
        """Find all Python files in the project (excluding .venv)."""
        python_files = []
        for path in self.project_root.rglob("*.py"):
            if ".venv" not in str(path) and "__pycache__" not in str(path):
                python_files.append(path)
        return python_files
    
    def extract_imports_from_file(self, file_path: Path) -> List[Tuple[int, str, str]]:
        """Extract import statements from a Python file.
        Returns list of (line_number, original_line, import_module)
        """
        imports = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # Match different import patterns
                patterns = [
                    r'^from\s+([^\s]+)\s+import',  # from module import
                    r'^import\s+([^\s,]+)',        # import module
                ]
                
                for pattern in patterns:
                    match = re.match(pattern, stripped)
                    if match:
                        module = match.group(1)
                        imports.append((i, line, module))
                        break
                        
        except Exception as e:
            self.errors.append(f"Error reading {file_path}: {e}")
            
        return imports
    
    def convert_path_to_module(self, file_path: str) -> str:
        """Convert file path to Python module notation."""
        # Remove .py extension and convert path separators to dots
        module = file_path.replace('.py', '').replace('/', '.').replace('\\', '.')
        # Remove leading dots
        return module.lstrip('.')
    
    def update_imports_in_file(self, file_path: Path, old_to_new_modules: Dict[str, str]) -> bool:
        """Update import statements in a file based on the mapping."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Update each import mapping
            for old_module, new_module in old_to_new_modules.items():
                # Pattern for 'from old_module import ...'
                pattern1 = rf'\bfrom\s+{re.escape(old_module)}\b'
                replacement1 = f'from {new_module}'
                content = re.sub(pattern1, replacement1, content)
                
                # Pattern for 'import old_module'
                pattern2 = rf'\bimport\s+{re.escape(old_module)}\b'
                replacement2 = f'import {new_module}'
                content = re.sub(pattern2, replacement2, content)
                
                # Pattern for 'old_module.something' (direct usage)
                pattern3 = rf'\b{re.escape(old_module)}\.'
                replacement3 = f'{new_module}.'
                content = re.sub(pattern3, replacement3, content)
            
            # Only write if content changed
            if content != original_content:
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                self.changes_made.append(f"Updated imports in: {file_path}")
                return True
                
        except Exception as e:
            self.errors.append(f"Error updating imports in {file_path}: {e}")
            
        return False
    
    def rename_file(self, old_path: Path, new_path: Path) -> bool:
        """Rename a single file."""
        try:
            if not old_path.exists():
                self.errors.append(f"Source file not found: {old_path}")
                return False
                
            # Create parent directory if it doesn't exist
            new_path.parent.mkdir(parents=True, exist_ok=True)
            
            if not self.dry_run:
                shutil.move(str(old_path), str(new_path))
                
            self.changes_made.append(f"Renamed: {old_path} → {new_path}")
            return True
            
        except Exception as e:
            self.errors.append(f"Error renaming {old_path} to {new_path}: {e}")
            return False
    
    def create_module_mapping(self) -> Dict[str, str]:
        """Create mapping of old module names to new module names."""
        mapping = {}
        
        for old_file, new_file in RENAME_MAPPING.items():
            old_module = self.convert_path_to_module(old_file)
            new_module = self.convert_path_to_module(new_file)
            mapping[old_module] = new_module
            
        return mapping
    
    def run_rename_process(self) -> bool:
        """Execute the complete renaming process."""
        print(f"{'=== DRY RUN ===' if self.dry_run else '=== LIVE RUN ==='}")
        print(f"Project root: {self.project_root}")
        print()
        
        # Step 1: Filter mapping to only include files that exist
        print("Step 1: Creating module mapping for existing files...")
        existing_files = {}
        for old_file, new_file in RENAME_MAPPING.items():
            old_path = self.project_root / old_file
            if old_path.exists():
                existing_files[old_file] = new_file
        
        module_mapping = {}
        for old_file, new_file in existing_files.items():
            old_module = self.convert_path_to_module(old_file)
            new_module = self.convert_path_to_module(new_file)
            module_mapping[old_module] = new_module
            
        print(f"Found {len(module_mapping)} module mappings for existing files")
        
        # Step 2: Find all Python files
        print("\nStep 2: Finding all Python files...")
        all_files = self.find_all_python_files()
        print(f"Found {len(all_files)} Python files")
        
        # Step 3: Update imports in all files
        print("\nStep 3: Updating imports in all files...")
        for file_path in all_files:
            relative_path = file_path.relative_to(self.project_root)
            if str(relative_path) not in existing_files:
                # Only update imports in files that aren't being renamed
                self.update_imports_in_file(file_path, module_mapping)
        
        # Step 4: Rename files
        print("\nStep 4: Renaming files...")
        for old_file, new_file in existing_files.items():
            old_path = self.project_root / old_file
            new_path = self.project_root / new_file
            self.rename_file(old_path, new_path)
        
        # Step 5: Update imports in renamed files
        print("\nStep 5: Updating imports in renamed files...")
        for old_file, new_file in existing_files.items():
            if self.dry_run:
                # For dry run, use the original file
                target_path = self.project_root / old_file
            else:
                # For live run, use the new file
                target_path = self.project_root / new_file
            
            if target_path.exists():
                self.update_imports_in_file(target_path, module_mapping)
        
        # Print summary
        print(f"\n{'=== DRY RUN SUMMARY ===' if self.dry_run else '=== SUMMARY ==='}")
        print(f"Changes made: {len(self.changes_made)}")
        for change in self.changes_made:
            print(f"  ✓ {change}")
            
        if self.errors:
            print(f"\nErrors encountered: {len(self.errors)}")
            for error in self.errors:
                print(f"  ✗ {error}")
                
        return len(self.errors) == 0

def main():
    parser = argparse.ArgumentParser(description="Rename files and update imports automatically")
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be done without making changes')
    args = parser.parse_args()
    
    # Get project root (assuming script is in tools/ subdirectory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print("DocGenius File Renaming Script")
    print("=" * 40)
    print(f"Project root: {project_root}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE EXECUTION'}")
    
    if not args.dry_run:
        response = input("\nThis will rename files and update imports. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return
    
    renamer = FileRenamer(project_root, dry_run=args.dry_run)
    success = renamer.run_rename_process()
    
    if success:
        print(f"\n✓ Renaming process completed {'(simulated)' if args.dry_run else 'successfully'}!")
        if args.dry_run:
            print("Run without --dry-run to apply changes.")
    else:
        print("\n✗ Renaming process completed with errors!")
        sys.exit(1)

if __name__ == "__main__":
    main()

# File Renaming Summary

## What the Script Does

The automated renaming script (`tools/rename_files_with_imports.py`) will:

1. **Rename 22 existing files** according to the new naming convention
2. **Update all import statements** throughout the entire project
3. **Ensure nothing breaks** by maintaining proper module references

## Files That Will Be Renamed

### Root Level Files
- `app.py` → `app_launcher_cli.py`
- `document_creator.py` → `document_creator_core.py`
- `dev_tools.py` → `dev_tools_cli.py`
- `system_tools.py` → `system_tools_cli.py`
- `compat.py` → `legacy_compat_layer.py`

### Logic Layer - Data Sources
- `logic/data_sources/base_loader.py` → `logic/data_sources/data_loader_base.py`
- `logic/data_sources/csv_loader.py` → `logic/data_sources/data_loader_csv.py`

### Logic Layer - Exporters
- `logic/exporters/base_exporter.py` → `logic/exporters/export_handler_base.py`
- `logic/exporters/markdown_exporter.py` → `logic/exporters/export_handler_markdown.py`
- `logic/exporters/pdf_exporter.py` → `logic/exporters/export_handler_pdf.py`
- `logic/exporters/word_exporter.py` → `logic/exporters/export_handler_word.py`

### Logic Layer - Utilities
- `logic/utilities/file_utils.py` → `logic/utilities/file_utils_core.py`

### Tools
- `tools/install_deps.py` → `tools/deps_installer_tool.py`
- `tools/setup.py` → `tools/setup_installer_tool.py`
- `tools/run_tests.py` → `tools/test_runner_tool.py`
- `tools/build_exe.py` → `tools/build_exe_tool.py`

### Tests
- `tests/test_base.py` → `tests/test_base_framework.py`
- `tests/test_end_to_end.py` → `tests/test_integration_e2e.py`
- `tests/test_markdown_export.py` → `tests/test_export_markdown.py`
- `tests/test_source_to_json.py` → `tests/test_data_source_json.py`
- `tests/test_unified_exports.py` → `tests/test_export_unified.py`
- `tests/run_organized_tests.py` → `tests/test_runner_organized.py`

## Import Updates

The script will automatically update all import statements in **all 41 Python files** to use the new names, including:
- `from app import something` → `from app_launcher_cli import something`
- `import document_creator` → `import document_creator_core`
- All relative imports within the logic layer
- All test imports

## How to Use

### Option 1: Simple Runner
```bash
python tools/run_rename.py
```
This provides a menu with options for dry-run or live execution.

### Option 2: Direct Script
```bash
# Dry run (see what would happen)
python tools/rename_files_with_imports.py --dry-run

# Live execution
python tools/rename_files_with_imports.py
```

## Safety Features

✅ **Dry run mode** - See exactly what will happen before making changes
✅ **Automatic import updates** - No manual import fixing needed
✅ **Error handling** - Script stops if any errors occur
✅ **Backup recommended** - Though the script is safe, always good practice

## Expected Outcome

After running:
- All files will have clear, consistent names following the `{domain}_{purpose}_{type}.py` pattern
- All imports will work correctly
- No functionality will be broken
- Project will be much easier to navigate and understand

The naming convention will make it immediately clear what each file does:
- `app_launcher_cli.py` - Command line interface launcher
- `document_creator_core.py` - Core document creation functionality
- `data_loader_csv.py` - CSV data loading functionality
- `export_handler_markdown.py` - Markdown export handling
- etc.

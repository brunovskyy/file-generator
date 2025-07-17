# Scripts Directory

This directory contains reusable automation scripts for project maintenance.

## Automated File Renamer

**Files:**
- `automated_file_renamer.py` - Core renaming script with import updating
- `run_automated_renamer.py` - Simple menu-driven runner

**Purpose:**
Automatically renames files according to naming conventions and updates all import statements throughout the project to prevent breakage.

**Usage:**
```bash
# Menu-driven interface
python scripts/run_automated_renamer.py

# Direct usage
python scripts/automated_file_renamer.py --dry-run  # Preview changes
python scripts/automated_file_renamer.py           # Apply changes
```

**Features:**
- ✅ Dry-run mode for safe testing
- ✅ Automatic import statement updates
- ✅ Error handling and rollback safety
- ✅ Comprehensive change logging
- ✅ Only processes existing files

**Use Cases:**
- Project-wide file renaming
- Enforcing naming conventions
- Refactoring legacy codebases
- Standardizing file structures

## Future Scripts

This folder can be used for other automation scripts like:
- Dependency updaters
- Code formatters
- Documentation generators
- Test runners
- Build automation

---
*Generated on July 17, 2025 - Part of DocGenius project maintenance tools*

# DocGenius Tools

This directory contains utility scripts for developing and maintaining DocGenius.

## Scripts

### `install_deps.py`
Quick dependency installer for the toolkit.
```bash
python tools/install_deps.py
```

### `setup.py`
Comprehensive setup script with environment validation.
```bash
python tools/setup.py
```

### `run_tests.py`
Test runner for the complete test suite.
```bash
python tools/run_tests.py
```

### `build_exe.py`
Builds a standalone executable using PyInstaller.
```bash
python tools/build_exe.py
```

## Usage Notes

- Run these scripts from the project root directory
- Most scripts will automatically handle path resolution
- Check individual script help with `--help` flag where supported

# JSON Markdown Utilities

This folder contains utilities and configurations for processing JSON data and converting it into Markdown files. It is part of the Document Creator application.

## Folder Structure

- `cli_steps.py`: Contains step-by-step CLI logic for user interaction with improved API configuration flow and comprehensive input documentation.
- `config.py`: Defines application-wide settings and export configurations.
- `step_helpers.py`: Provides helper functions for JSON processing, Markdown conversion, and user input validation.
- `validators.py`: Includes validation utilities for file paths, URLs, and other inputs with enhanced error handling.

## Key Features

1. **Interactive CLI**: Guides users through the process of configuring JSON to Markdown conversion with an improved, user-friendly flow.
2. **Smart API Configuration**: Streamlined API setup that asks for details only when needed, supporting both simple GET requests and advanced configurations.
3. **Flexible Input Sources**: Supports local JSON files, remote URLs, and REST API endpoints with comprehensive authentication options.
4. **Comprehensive Documentation**: Each configuration step includes detailed descriptions of available inputs and their effects.
5. **Maintainable Architecture**: Modular design with separated concerns and reusable helper functions.
6. **Robust Validation**: Ensures input data and configurations are valid before processing, with graceful error handling.

## Recent Improvements

### Enhanced API Configuration Flow
- **Simplified User Experience**: The API setup now asks if you want to provide endpoint details first, reducing questions for simple use cases
- **Smart Defaults**: Basic GET requests can be configured with minimal input
- **Flexible Options**: Advanced users can still use cURL commands or detailed manual configuration
- **Better Error Handling**: Graceful fallbacks when parsing fails

### Improved Step Documentation
Each configuration step now provides:
- **Clear Input Descriptions**: Detailed explanation of what each field accepts
- **Real-World Examples**: Practical examples for complex configuration options
- **Behavior Explanations**: How auto-detection and fallback mechanisms work
- **Purpose Context**: When and why to use different configuration options

### Code Architecture Enhancements
- **Modular Design**: API logic separated into focused, reusable helper functions
- **Maintainable Structure**: Clear separation between UI prompts and business logic
- **No Code Duplication**: Common patterns extracted into shared utilities
- **Enhanced Testing**: Improved validation and error handling throughout

## Usage

These utilities are designed to be used as part of the main Document Creator application. The improved interactive CLI now provides:

### Configuration Steps
1. **JSON Input Source**: File path, URL, or API endpoint with automatic type detection
2. **API Details** (if applicable): Streamlined configuration with option for simple defaults or detailed setup
3. **Transaction Identifier**: Custom name or auto-generated timestamp for organizing exports
4. **Output Directory**: Custom path or default location with automatic creation
5. **Processing Options**: Content flattening and YAML front matter configuration
6. **File Naming**: Custom key selection or intelligent auto-detection

### API Configuration Options
- **Simple Mode**: Just provide the URL for basic GET requests
- **Advanced Mode**: Configure HTTP method, headers, query parameters, and request body
- **cURL Import**: Paste existing cURL commands for quick setup

Run the main script to start the interactive process with the enhanced user experience.

## Dependencies

- Python 3.8+
- Required libraries: `requests`, `pathlib`, `dataclasses`

## Contributing

Feel free to contribute to this project by adding new features or improving existing ones. When contributing:

- **Follow the modular architecture**: Keep functions focused and avoid duplicating logic
- **Include comprehensive documentation**: Document all inputs, behaviors, and examples
- **Add appropriate validation**: Ensure robust error handling and user feedback
- **Test the interactive flow**: Verify that changes work for both simple and advanced use cases
- **Update documentation**: Keep README and inline documentation current with changes

Make sure to follow the coding standards and include appropriate documentation for any new features.
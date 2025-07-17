"""
Utilities package for DocGenius logic components.

This package provides comprehensive utility modules for:
- File operations and path management
- Dialog interfaces and user interaction
- Data validation and verification
- Configuration management
- Logging and monitoring
- System utilities and environment management
- Data processing and transformation

All utilities are designed to be modular, reusable, and provide
consistent error handling and logging.
"""

# File operations and path management
from .file_utils_core import (
    FileOperationResult,
    PathManager,
    FileOperations,
    BackupManager,
    TemporaryFileManager,
    safe_create_directory,
    get_unique_filename,
    validate_file_path
)

# Dialog interfaces and user interaction
from .dialog_utils import (
    DialogResult,
    FileDialogs,
    MessageDialogs,
    InputDialogs,
    PreviewDialog,
    ProgressDialog,
    select_input_file,
    select_output_directory,
    select_template_file,
    confirm_operation,
    show_error_message,
    show_info_message
)

# Data validation and verification
from .validation_utils import (
    DataTypeValidator,
    FileValidator,
    BusinessLogicValidator,
    ValidationEngine,
    validate_email_field,
    validate_phone_field,
    validate_numeric_field,
    validate_required_field
)

# Configuration management
from .config_utils import (
    AppConfig,
    ExportConfig,
    ConfigManager,
    EnvironmentConfig,
    ConfigValidator,
    get_config_manager,
    get_app_config,
    get_export_config,
    update_app_setting,
    update_export_setting
)

# Logging and monitoring
from .logging_utils import (
    LogEntry,
    SessionStats,
    SessionLogger,
    PerformanceMonitor,
    SystemMonitor,
    LoggingConfigurator,
    OperationTimer,
    get_session_logger,
    setup_default_logging
)

# System utilities and environment management
from .system_utils import (
    SystemInfo,
    ProcessManager,
    DependencyChecker,
    EnvironmentManager,
    get_system_info,
    check_command_available,
    run_system_command,
    check_python_dependencies,
    get_app_directory
)

# Data processing and transformation
from .data_utils import (
    DataTransformer,
    DataValidator,
    DataAggregator,
    DataConverter,
    flatten_data,
    normalize_field_names,
    validate_data_quality,
    group_data_by_field,
    convert_to_csv
)

__all__ = [
    # File utilities
    "FileOperationResult",
    "PathManager", 
    "FileOperations",
    "BackupManager",
    "TemporaryFileManager",
    "safe_create_directory",
    "get_unique_filename",
    "validate_file_path",
    
    # Dialog utilities
    "DialogResult",
    "FileDialogs",
    "MessageDialogs", 
    "InputDialogs",
    "PreviewDialog",
    "ProgressDialog",
    "select_input_file",
    "select_output_directory",
    "select_template_file",
    "confirm_operation",
    "show_error_message",
    "show_info_message",
    
    # Validation utilities
    "DataTypeValidator",
    "FileValidator",
    "BusinessLogicValidator", 
    "ValidationEngine",
    "validate_email_field",
    "validate_phone_field",
    "validate_numeric_field",
    "validate_required_field",
    
    # Configuration utilities
    "AppConfig",
    "ExportConfig",
    "ConfigManager",
    "EnvironmentConfig",
    "ConfigValidator",
    "get_config_manager",
    "get_app_config",
    "get_export_config",
    "update_app_setting", 
    "update_export_setting",
    
    # Logging utilities
    "LogEntry",
    "SessionStats",
    "SessionLogger",
    "PerformanceMonitor",
    "SystemMonitor",
    "LoggingConfigurator",
    "OperationTimer",
    "get_session_logger",
    "setup_default_logging",
    
    # System utilities
    "SystemInfo",
    "ProcessManager",
    "DependencyChecker",
    "EnvironmentManager", 
    "get_system_info",
    "check_command_available",
    "run_system_command",
    "check_python_dependencies",
    "get_app_directory",
    
    # Data utilities
    "DataTransformer",
    "DataValidator",
    "DataAggregator",
    "DataConverter",
    "flatten_data",
    "normalize_field_names",
    "validate_data_quality",
    "group_data_by_field",
    "convert_to_csv"
]

# Version information
__version__ = "1.0.0"
__author__ = "DocGenius Development Team"


def get_utility_info():
    """Get information about available utilities."""
    return {
        "version": __version__,
        "author": __author__,
        "modules": {
            "file_utils": "File operations and path management",
            "dialog_utils": "GUI dialogs and user interaction",
            "validation_utils": "Data validation and verification", 
            "config_utils": "Configuration management",
            "logging_utils": "Logging and monitoring",
            "system_utils": "System utilities and environment management",
            "data_utils": "Data processing and transformation"
        },
        "total_functions": len(__all__)
    }

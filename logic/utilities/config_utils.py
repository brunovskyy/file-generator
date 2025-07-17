"""
Configuration management utilities for DocGenius.

This module provides configuration loading, validation, and management
capabilities for application settings and user preferences.
"""

import json
import yaml
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import os


@dataclass
class AppConfig:
    """Main application configuration."""
    
    # File handling
    default_input_directory: str = ""
    default_output_directory: str = ""
    default_template_directory: str = ""
    
    # Export settings
    default_export_format: str = "markdown"
    include_timestamps: bool = True
    create_backup_files: bool = True
    
    # UI preferences
    confirm_operations: bool = True
    show_progress_dialogs: bool = True
    remember_last_selections: bool = True
    
    # Processing options
    max_records_per_file: int = 1000
    validate_data_on_load: bool = True
    normalize_field_names: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_to_file: bool = True
    max_log_files: int = 10
    
    # Advanced
    custom_templates_enabled: bool = True
    developer_mode: bool = False
    auto_update_check: bool = True


@dataclass 
class ExportConfig:
    """Export-specific configuration."""
    
    # Common settings
    output_format: str = "markdown"
    template_file: Optional[str] = None
    include_metadata: bool = True
    
    # Markdown settings
    markdown_style: str = "github"  # github, commonmark, etc.
    include_toc: bool = False
    toc_depth: int = 3
    
    # PDF settings  
    pdf_page_size: str = "A4"
    pdf_margins: Dict[str, float] = None
    pdf_font_family: str = "Arial"
    pdf_font_size: int = 12
    
    # Word settings
    word_template: Optional[str] = None
    word_style_mapping: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.pdf_margins is None:
            self.pdf_margins = {"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0}


class ConfigManager:
    """Configuration file management and persistence."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        
        if config_dir is None:
            # Default to user's app data directory
            if os.name == 'nt':  # Windows
                config_dir = Path.home() / "AppData" / "Local" / "DocGenius"
            else:  # macOS/Linux
                config_dir = Path.home() / ".config" / "docgenius"
        
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        self.export_config_file = self.config_dir / "export_config.json"
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self._app_config: Optional[AppConfig] = None
        self._export_config: Optional[ExportConfig] = None
    
    def load_app_config(self) -> AppConfig:
        """
        Load application configuration from file.
        
        Returns:
            AppConfig instance with loaded or default settings
        """
        if self._app_config is not None:
            return self._app_config
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as file:
                    config_data = json.load(file)
                
                # Create AppConfig with loaded data
                self._app_config = AppConfig(**config_data)
                self.logger.info(f"Loaded app config from: {self.config_file}")
            else:
                # Create default configuration
                self._app_config = AppConfig()
                self.save_app_config(self._app_config)
                self.logger.info("Created default app configuration")
        
        except Exception as e:
            self.logger.error(f"Failed to load app config: {str(e)}")
            self._app_config = AppConfig()
        
        return self._app_config
    
    def save_app_config(self, config: AppConfig) -> bool:
        """
        Save application configuration to file.
        
        Args:
            config: AppConfig instance to save
            
        Returns:
            True if save was successful
        """
        try:
            config_data = asdict(config)
            
            with open(self.config_file, 'w', encoding='utf-8') as file:
                json.dump(config_data, file, indent=2)
            
            self._app_config = config
            self.logger.info(f"Saved app config to: {self.config_file}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to save app config: {str(e)}")
            return False
    
    def load_export_config(self) -> ExportConfig:
        """
        Load export configuration from file.
        
        Returns:
            ExportConfig instance with loaded or default settings
        """
        if self._export_config is not None:
            return self._export_config
        
        try:
            if self.export_config_file.exists():
                with open(self.export_config_file, 'r', encoding='utf-8') as file:
                    config_data = json.load(file)
                
                # Create ExportConfig with loaded data
                self._export_config = ExportConfig(**config_data)
                self.logger.info(f"Loaded export config from: {self.export_config_file}")
            else:
                # Create default configuration
                self._export_config = ExportConfig()
                self.save_export_config(self._export_config)
                self.logger.info("Created default export configuration")
        
        except Exception as e:
            self.logger.error(f"Failed to load export config: {str(e)}")
            self._export_config = ExportConfig()
        
        return self._export_config
    
    def save_export_config(self, config: ExportConfig) -> bool:
        """
        Save export configuration to file.
        
        Args:
            config: ExportConfig instance to save
            
        Returns:
            True if save was successful
        """
        try:
            config_data = asdict(config)
            
            with open(self.export_config_file, 'w', encoding='utf-8') as file:
                json.dump(config_data, file, indent=2)
            
            self._export_config = config
            self.logger.info(f"Saved export config to: {self.export_config_file}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to save export config: {str(e)}")
            return False
    
    def update_app_setting(self, key: str, value: Any) -> bool:
        """
        Update a single application setting.
        
        Args:
            key: Setting key to update
            value: New value for the setting
            
        Returns:
            True if update was successful
        """
        try:
            config = self.load_app_config()
            
            if hasattr(config, key):
                setattr(config, key, value)
                return self.save_app_config(config)
            else:
                self.logger.warning(f"Unknown config key: {key}")
                return False
        
        except Exception as e:
            self.logger.error(f"Failed to update setting {key}: {str(e)}")
            return False
    
    def update_export_setting(self, key: str, value: Any) -> bool:
        """
        Update a single export setting.
        
        Args:
            key: Setting key to update
            value: New value for the setting
            
        Returns:
            True if update was successful
        """
        try:
            config = self.load_export_config()
            
            if hasattr(config, key):
                setattr(config, key, value)
                return self.save_export_config(config)
            else:
                self.logger.warning(f"Unknown export config key: {key}")
                return False
        
        except Exception as e:
            self.logger.error(f"Failed to update export setting {key}: {str(e)}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Reset all configuration to default values.
        
        Returns:
            True if reset was successful
        """
        try:
            # Reset app config
            self._app_config = AppConfig()
            app_success = self.save_app_config(self._app_config)
            
            # Reset export config
            self._export_config = ExportConfig()
            export_success = self.save_export_config(self._export_config)
            
            success = app_success and export_success
            if success:
                self.logger.info("Reset all configuration to defaults")
            
            return success
        
        except Exception as e:
            self.logger.error(f"Failed to reset configuration: {str(e)}")
            return False
    
    def export_config(self, export_path: Path) -> bool:
        """
        Export current configuration to a file.
        
        Args:
            export_path: Path where to export configuration
            
        Returns:
            True if export was successful
        """
        try:
            app_config = self.load_app_config()
            export_config = self.load_export_config()
            
            combined_config = {
                'app_config': asdict(app_config),
                'export_config': asdict(export_config),
                'exported_at': str(datetime.now()),
                'version': '1.0'
            }
            
            with open(export_path, 'w', encoding='utf-8') as file:
                json.dump(combined_config, file, indent=2)
            
            self.logger.info(f"Exported configuration to: {export_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {str(e)}")
            return False
    
    def import_config(self, import_path: Path) -> bool:
        """
        Import configuration from a file.
        
        Args:
            import_path: Path to configuration file to import
            
        Returns:
            True if import was successful
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as file:
                combined_config = json.load(file)
            
            # Import app config
            if 'app_config' in combined_config:
                app_config = AppConfig(**combined_config['app_config'])
                self.save_app_config(app_config)
            
            # Import export config
            if 'export_config' in combined_config:
                export_config = ExportConfig(**combined_config['export_config'])
                self.save_export_config(export_config)
            
            self.logger.info(f"Imported configuration from: {import_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to import configuration: {str(e)}")
            return False


class EnvironmentConfig:
    """Environment-specific configuration management."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_environment_info(self) -> Dict[str, Any]:
        """
        Get information about the current environment.
        
        Returns:
            Dictionary with environment information
        """
        import platform
        import sys
        
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.architecture()[0],
            'python_version': sys.version,
            'executable_path': sys.executable,
            'working_directory': os.getcwd(),
            'user_home': str(Path.home()),
            'environment_variables': dict(os.environ)
        }
    
    def setup_logging(self, config: AppConfig) -> bool:
        """
        Setup logging configuration based on app config.
        
        Args:
            config: Application configuration
            
        Returns:
            True if logging setup was successful
        """
        try:
            import logging.handlers
            
            # Create logs directory
            logs_dir = Path.home() / ".docgenius" / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            
            # Configure root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(getattr(logging, config.log_level.upper()))
            
            # Clear existing handlers
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
            
            # File handler (if enabled)
            if config.log_to_file:
                log_file = logs_dir / "docgenius.log"
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=10 * 1024 * 1024,  # 10MB
                    backupCount=config.max_log_files
                )
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
                )
                file_handler.setFormatter(file_formatter)
                root_logger.addHandler(file_handler)
            
            self.logger.info("Logging configuration completed")
            return True
        
        except Exception as e:
            print(f"Failed to setup logging: {str(e)}")
            return False
    
    def check_dependencies(self) -> Dict[str, Any]:
        """
        Check availability of optional dependencies.
        
        Returns:
            Dictionary with dependency status
        """
        dependencies = {
            'required': {},
            'optional': {}
        }
        
        # Required dependencies
        required_modules = ['pathlib', 'json', 'csv', 'logging', 'tkinter']
        for module in required_modules:
            try:
                __import__(module)
                dependencies['required'][module] = {'available': True, 'version': None}
            except ImportError as e:
                dependencies['required'][module] = {'available': False, 'error': str(e)}
        
        # Optional dependencies
        optional_modules = {
            'yaml': 'PyYAML',
            'chardet': 'chardet',
            'openpyxl': 'openpyxl',
            'pandas': 'pandas',
            'jinja2': 'Jinja2'
        }
        
        for module, package_name in optional_modules.items():
            try:
                imported_module = __import__(module)
                version = getattr(imported_module, '__version__', 'unknown')
                dependencies['optional'][module] = {
                    'available': True, 
                    'version': version,
                    'package_name': package_name
                }
            except ImportError as e:
                dependencies['optional'][module] = {
                    'available': False, 
                    'error': str(e),
                    'package_name': package_name
                }
        
        return dependencies


class ConfigValidator:
    """Configuration validation utilities."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_app_config(self, config: AppConfig) -> List[str]:
        """
        Validate application configuration.
        
        Args:
            config: AppConfig to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if config.log_level.upper() not in valid_log_levels:
            errors.append(f"Invalid log level: {config.log_level}")
        
        # Validate numeric values
        if config.max_records_per_file <= 0:
            errors.append("max_records_per_file must be positive")
        
        if config.max_log_files <= 0:
            errors.append("max_log_files must be positive")
        
        # Validate directories (if specified)
        for dir_field in ['default_input_directory', 'default_output_directory', 'default_template_directory']:
            dir_path = getattr(config, dir_field)
            if dir_path and not Path(dir_path).exists():
                errors.append(f"{dir_field} does not exist: {dir_path}")
        
        return errors
    
    def validate_export_config(self, config: ExportConfig) -> List[str]:
        """
        Validate export configuration.
        
        Args:
            config: ExportConfig to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Validate output format
        valid_formats = ['markdown', 'pdf', 'word']
        if config.output_format not in valid_formats:
            errors.append(f"Invalid output format: {config.output_format}")
        
        # Validate template file (if specified)
        if config.template_file and not Path(config.template_file).exists():
            errors.append(f"Template file does not exist: {config.template_file}")
        
        # Validate numeric values
        if config.toc_depth <= 0:
            errors.append("toc_depth must be positive")
        
        if config.pdf_font_size <= 0:
            errors.append("pdf_font_size must be positive")
        
        # Validate PDF margins
        if config.pdf_margins:
            for margin_name, margin_value in config.pdf_margins.items():
                if not isinstance(margin_value, (int, float)) or margin_value < 0:
                    errors.append(f"Invalid PDF margin {margin_name}: {margin_value}")
        
        return errors


# Global config manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_app_config() -> AppConfig:
    """Convenience function to get application configuration."""
    return get_config_manager().load_app_config()


def get_export_config() -> ExportConfig:
    """Convenience function to get export configuration."""
    return get_config_manager().load_export_config()


def update_app_setting(key: str, value: Any) -> bool:
    """Convenience function to update an application setting."""
    return get_config_manager().update_app_setting(key, value)


def update_export_setting(key: str, value: Any) -> bool:
    """Convenience function to update an export setting."""
    return get_config_manager().update_export_setting(key, value)

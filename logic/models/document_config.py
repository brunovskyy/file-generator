"""
Configuration models for document generation settings.

This module defines configuration classes that control document
generation behavior, export settings, and processing options.
"""

from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

from .base_models import BaseModel, ValidationResult, FieldValidator, ModelValidator


class ExportFormat(Enum):
    """Supported export formats."""
    MARKDOWN = "markdown"
    PDF = "pdf"
    WORD = "word"
    HTML = "html"
    JSON = "json"


class YAMLKeySelection(Enum):
    """YAML key selection strategies for Markdown export."""
    ALL = "all"
    SELECT = "select"
    NONE = "none"
    COMMON = "common"


@dataclass
class DocumentConfig(BaseModel):
    """
    Central configuration object for document generation process.
    
    Contains all settings needed for loading data, processing it,
    and exporting to various formats.
    """
    
    # Source configuration
    source: str = ""
    source_format: Optional[str] = None
    source_encoding: str = "utf-8"
    
    # Export configuration
    export_formats: List[ExportFormat] = field(default_factory=list)
    output_directory: Optional[Path] = None
    filename_key: Optional[str] = None
    
    # Processing options
    flatten_nested_data: bool = True
    normalize_field_names: bool = True
    include_metadata: bool = True
    
    # API configuration (if source is API)
    api_method: str = "GET"
    api_headers: Dict[str, str] = field(default_factory=dict)
    api_query: Dict[str, Any] = field(default_factory=dict)
    api_body: Dict[str, Any] = field(default_factory=dict)
    
    # Format-specific settings
    markdown_settings: Optional['MarkdownSettings'] = None
    pdf_settings: Optional['PDFSettings'] = None
    word_settings: Optional['WordSettings'] = None
    
    def __post_init__(self):
        """Initialize default settings if not provided."""
        if self.output_directory is None:
            self.output_directory = Path.home() / "Downloads"
        
        # Convert string formats to enum
        if isinstance(self.export_formats, list):
            self.export_formats = [
                ExportFormat(fmt) if isinstance(fmt, str) else fmt
                for fmt in self.export_formats
            ]
    
    def add_export_format(self, format_type: Union[str, ExportFormat]) -> None:
        """Add an export format to the configuration."""
        if isinstance(format_type, str):
            format_type = ExportFormat(format_type)
        
        if format_type not in self.export_formats:
            self.export_formats.append(format_type)
    
    def remove_export_format(self, format_type: Union[str, ExportFormat]) -> None:
        """Remove an export format from the configuration."""
        if isinstance(format_type, str):
            format_type = ExportFormat(format_type)
        
        if format_type in self.export_formats:
            self.export_formats.remove(format_type)
    
    def get_format_settings(self, format_type: ExportFormat) -> Optional[BaseModel]:
        """Get settings for a specific export format."""
        if format_type == ExportFormat.MARKDOWN:
            return self.markdown_settings
        elif format_type == ExportFormat.PDF:
            return self.pdf_settings
        elif format_type == ExportFormat.WORD:
            return self.word_settings
        return None
    
    def validate(self) -> ValidationResult:
        """Validate the document configuration."""
        result = ValidationResult(is_valid=True)
        
        # Validate source
        if not self.source:
            result.add_error("Source is required")
        
        # Validate export formats
        if not self.export_formats:
            result.add_error("At least one export format is required")
        
        # Validate output directory
        if self.output_directory:
            output_path = Path(self.output_directory)
            if not output_path.parent.exists():
                result.add_error(f"Output directory parent does not exist: {output_path.parent}")
        
        # Validate format-specific settings
        for format_type in self.export_formats:
            settings = self.get_format_settings(format_type)
            if settings:
                settings_result = settings.validate()
                if not settings_result.is_valid:
                    for error in settings_result.errors:
                        result.add_error(f"{format_type.value}: {error}")
        
        return result


@dataclass
class ExportSettings(BaseModel):
    """
    Base export settings class for format-specific configurations.
    
    Provides common settings that apply to all export formats.
    """
    
    enabled: bool = True
    template_path: Optional[Path] = None
    template_url: Optional[str] = None
    use_template: bool = False
    custom_filename_pattern: Optional[str] = None
    
    def validate(self) -> ValidationResult:
        """Validate export settings."""
        result = ValidationResult(is_valid=True)
        
        # Validate template settings
        if self.use_template:
            if not self.template_path and not self.template_url:
                result.add_error("Template path or URL required when use_template is True")
            
            if self.template_path:
                if not Path(self.template_path).exists():
                    result.add_error(f"Template file does not exist: {self.template_path}")
        
        return result


@dataclass 
class MarkdownSettings(ExportSettings):
    """
    Markdown-specific export settings.
    
    Controls YAML front matter, content formatting, and
    Markdown-specific output options.
    """
    
    include_yaml_front_matter: bool = True
    yaml_key_selection: YAMLKeySelection = YAMLKeySelection.SELECT
    selected_yaml_keys: Set[str] = field(default_factory=set)
    flatten_yaml_values: bool = True
    
    # Content formatting
    include_table_of_contents: bool = False
    max_heading_level: int = 6
    code_block_language: str = "json"
    
    # File organization
    create_summary_file: bool = True
    group_by_field: Optional[str] = None
    
    def validate(self) -> ValidationResult:
        """Validate Markdown settings."""
        result = super().validate()
        
        # Validate YAML settings
        if self.yaml_key_selection == YAMLKeySelection.SELECT:
            if not self.selected_yaml_keys:
                result.add_warning("No YAML keys selected, will use all available keys")
        
        # Validate heading level
        if not 1 <= self.max_heading_level <= 6:
            result.add_error("Max heading level must be between 1 and 6")
        
        return result


@dataclass
class PDFSettings(ExportSettings):
    """
    PDF-specific export settings.
    
    Controls page layout, styling, fonts, and PDF-specific
    generation options.
    """
    
    # Page settings
    page_size: str = "A4"  # A4, Letter, Legal, etc.
    page_orientation: str = "portrait"  # portrait, landscape
    margin_top: float = 1.0  # inches
    margin_bottom: float = 1.0
    margin_left: float = 1.0
    margin_right: float = 1.0
    
    # Content settings
    font_family: str = "Helvetica"
    font_size: int = 12
    heading_font_family: str = "Helvetica-Bold"
    heading_font_size: int = 16
    
    # Document properties
    document_title: Optional[str] = None
    document_author: Optional[str] = None
    document_subject: Optional[str] = None
    document_keywords: List[str] = field(default_factory=list)
    
    # Layout options
    include_page_numbers: bool = True
    include_header: bool = False
    include_footer: bool = False
    header_text: Optional[str] = None
    footer_text: Optional[str] = None
    
    # Content formatting
    table_style: str = "grid"  # grid, simple, minimal
    image_max_width: float = 6.0  # inches
    line_spacing: float = 1.2
    
    def validate(self) -> ValidationResult:
        """Validate PDF settings."""
        result = super().validate()
        
        # Validate page size
        valid_page_sizes = ["A4", "Letter", "Legal", "A3", "A5"]
        if self.page_size not in valid_page_sizes:
            result.add_error(f"Page size must be one of: {valid_page_sizes}")
        
        # Validate orientation
        if self.page_orientation not in ["portrait", "landscape"]:
            result.add_error("Page orientation must be 'portrait' or 'landscape'")
        
        # Validate margins
        for margin_name, margin_value in [
            ("top", self.margin_top),
            ("bottom", self.margin_bottom),
            ("left", self.margin_left),
            ("right", self.margin_right)
        ]:
            if not 0 <= margin_value <= 4:
                result.add_error(f"Margin {margin_name} must be between 0 and 4 inches")
        
        # Validate font sizes
        if not 6 <= self.font_size <= 72:
            result.add_error("Font size must be between 6 and 72 points")
        
        if not 6 <= self.heading_font_size <= 72:
            result.add_error("Heading font size must be between 6 and 72 points")
        
        return result


@dataclass
class WordSettings(ExportSettings):
    """
    Word document-specific export settings.
    
    Controls Word document formatting, styles, and
    Microsoft Word-specific features.
    """
    
    # Document properties
    document_title: Optional[str] = None
    document_author: Optional[str] = None
    document_subject: Optional[str] = None
    document_keywords: List[str] = field(default_factory=list)
    
    # Style settings
    default_style: str = "Normal"
    heading_styles: Dict[int, str] = field(default_factory=lambda: {
        1: "Heading 1",
        2: "Heading 2", 
        3: "Heading 3"
    })
    
    # Formatting options
    font_name: str = "Calibri"
    font_size: int = 11
    line_spacing: float = 1.15
    
    # Layout options
    include_page_numbers: bool = True
    include_table_of_contents: bool = False
    page_break_before_sections: bool = False
    
    # Table formatting
    table_style: Optional[str] = "Table Grid"
    auto_fit_tables: bool = True
    
    # Content options
    embed_images: bool = True
    image_max_width: float = 6.0  # inches
    convert_urls_to_hyperlinks: bool = True
    
    def validate(self) -> ValidationResult:
        """Validate Word settings."""
        result = super().validate()
        
        # Validate font size
        if not 6 <= self.font_size <= 72:
            result.add_error("Font size must be between 6 and 72 points")
        
        # Validate line spacing
        if not 0.5 <= self.line_spacing <= 3.0:
            result.add_error("Line spacing must be between 0.5 and 3.0")
        
        # Validate image width
        if not 0.5 <= self.image_max_width <= 10:
            result.add_error("Image max width must be between 0.5 and 10 inches")
        
        return result


class ConfigValidator:
    """
    Configuration validation and consistency checking.
    
    Provides comprehensive validation across all configuration
    objects and ensures consistency between settings.
    """
    
    def __init__(self):
        self.validator = ModelValidator()
        self._setup_validation_rules()
    
    def _setup_validation_rules(self):
        """Set up standard validation rules."""
        # Document config rules
        self.validator.add_field_rule("source", "required")
        self.validator.add_field_rule("source", "min_length", min_len=1)
        self.validator.add_field_rule("export_formats", "required")
        
    def validate_config(self, config: DocumentConfig) -> ValidationResult:
        """
        Validate a complete document configuration.
        
        Args:
            config: Document configuration to validate
            
        Returns:
            Validation result with any errors or warnings
        """
        # Run basic model validation
        result = config.validate()
        
        # Cross-validation between settings
        self._validate_format_consistency(config, result)
        self._validate_template_settings(config, result)
        self._validate_source_settings(config, result)
        
        return result
    
    def _validate_format_consistency(self, config: DocumentConfig, result: ValidationResult):
        """Validate consistency between export formats and their settings."""
        for format_type in config.export_formats:
            settings = config.get_format_settings(format_type)
            
            if format_type in [ExportFormat.PDF, ExportFormat.WORD]:
                if settings and settings.use_template:
                    if not settings.template_path and not settings.template_url:
                        result.add_error(
                            f"{format_type.value} format requires template when use_template is True"
                        )
    
    def _validate_template_settings(self, config: DocumentConfig, result: ValidationResult):
        """Validate template-related settings."""
        template_formats = [ExportFormat.PDF, ExportFormat.WORD]
        
        for format_type in config.export_formats:
            if format_type in template_formats:
                settings = config.get_format_settings(format_type)
                if settings and settings.use_template:
                    # Check template accessibility
                    if settings.template_path:
                        if not Path(settings.template_path).exists():
                            result.add_error(
                                f"{format_type.value} template file not found: {settings.template_path}"
                            )
    
    def _validate_source_settings(self, config: DocumentConfig, result: ValidationResult):
        """Validate source-related settings."""
        # Check if source looks like a URL
        if config.source.startswith(('http://', 'https://')):
            if config.source_format not in ['api', 'json', 'csv', None]:
                result.add_warning(
                    f"URL source with format '{config.source_format}' may not be compatible"
                )
        
        # Check file extension consistency
        if not config.source.startswith(('http://', 'https://')):
            source_path = Path(config.source)
            if source_path.suffix:
                detected_format = self._detect_format_from_extension(source_path.suffix)
                if config.source_format and config.source_format != detected_format:
                    result.add_warning(
                        f"Source format '{config.source_format}' does not match "
                        f"file extension '{source_path.suffix}'"
                    )
    
    def _detect_format_from_extension(self, extension: str) -> Optional[str]:
        """Detect format from file extension."""
        extension_map = {
            '.json': 'json',
            '.csv': 'csv',
            '.txt': 'csv',
            '.tsv': 'csv'
        }
        return extension_map.get(extension.lower())

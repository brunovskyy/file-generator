"""
Abstract base exporter class and common interfaces.

This module defines the base exporter interface that all format-specific
exporters must implement, ensuring consistency across all export formats.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import logging

from ..models import DataObject, DataCollection, ValidationResult, BaseModel


@dataclass
class ExportResult:
    """
    Result container for export operations.
    
    Contains the result status, file paths, metadata, and any
    errors or warnings from the export process.
    """
    
    success: bool
    output_path: Optional[Path] = None
    file_size: Optional[int] = None
    export_duration: Optional[float] = None
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize metadata with defaults."""
        if 'export_timestamp' not in self.metadata:
            self.metadata['export_timestamp'] = datetime.now().isoformat()
    
    @classmethod
    def success_result(
        cls,
        output_path: Path,
        export_duration: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'ExportResult':
        """Create a successful export result."""
        file_size = output_path.stat().st_size if output_path.exists() else None
        
        return cls(
            success=True,
            output_path=output_path,
            file_size=file_size,
            export_duration=export_duration,
            metadata=metadata or {}
        )
    
    @classmethod
    def failure_result(
        cls,
        error_message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'ExportResult':
        """Create a failed export result."""
        return cls(
            success=False,
            error_message=error_message,
            metadata=metadata or {}
        )
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message to the result."""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary representation."""
        return {
            'success': self.success,
            'output_path': str(self.output_path) if self.output_path else None,
            'file_size': self.file_size,
            'export_duration': self.export_duration,
            'error_message': self.error_message,
            'warnings': self.warnings,
            'metadata': self.metadata
        }


@dataclass
class ExportContext:
    """
    Shared context and settings for export operations.
    
    Contains common settings that are shared across multiple
    export operations within a single session.
    """
    
    output_directory: Path
    transaction_id: str
    batch_mode: bool = False
    overwrite_existing: bool = False
    dry_run: bool = False
    progress_callback: Optional[callable] = None
    logger: Optional[logging.Logger] = None
    
    def __post_init__(self):
        """Initialize context with defaults."""
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
    
    def log_info(self, message: str) -> None:
        """Log an info message."""
        if self.logger:
            self.logger.info(f"[{self.transaction_id}] {message}")
    
    def log_warning(self, message: str) -> None:
        """Log a warning message.""" 
        if self.logger:
            self.logger.warning(f"[{self.transaction_id}] {message}")
    
    def log_error(self, message: str) -> None:
        """Log an error message."""
        if self.logger:
            self.logger.error(f"[{self.transaction_id}] {message}")
    
    def report_progress(self, current: int, total: int, message: str = "") -> None:
        """Report progress if callback is available."""
        if self.progress_callback:
            self.progress_callback(current, total, message)


class BaseExporter(ABC):
    """
    Abstract base class for all document exporters.
    
    Defines the standard interface that all format-specific exporters
    must implement, ensuring consistency and interoperability.
    """
    
    def __init__(self, settings: BaseModel, context: ExportContext):
        """
        Initialize the exporter with settings and context.
        
        Args:
            settings: Format-specific export settings
            context: Shared export context
        """
        self.settings = settings
        self.context = context
        self.format_name = self._get_format_name()
        self.file_extension = self._get_file_extension()
    
    @abstractmethod
    def _get_format_name(self) -> str:
        """Return the human-readable format name."""
        pass
    
    @abstractmethod
    def _get_file_extension(self) -> str:
        """Return the file extension for this format (without dot)."""
        pass
    
    @abstractmethod
    def validate_settings(self) -> ValidationResult:
        """
        Validate exporter configuration and dependencies.
        
        Returns:
            ValidationResult indicating if the exporter is ready to use
        """
        pass
    
    @abstractmethod
    def export_single(self, data_object: DataObject) -> ExportResult:
        """
        Export a single data object to a file.
        
        Args:
            data_object: Data object to export
            
        Returns:
            ExportResult containing operation status and metadata
        """
        pass
    
    def export_batch(self, data_collection: DataCollection) -> List[ExportResult]:
        """
        Export multiple data objects in batch.
        
        Args:
            data_collection: Collection of data objects to export
            
        Returns:
            List of ExportResult objects, one per exported file
        """
        results = []
        total_objects = len(data_collection)
        
        self.context.log_info(
            f"Starting batch export of {total_objects} objects to {self.format_name}"
        )
        
        for i, data_object in enumerate(data_collection):
            self.context.report_progress(
                i + 1, total_objects, 
                f"Exporting object {i + 1}/{total_objects}"
            )
            
            try:
                result = self.export_single(data_object)
                results.append(result)
                
                if result.success:
                    self.context.log_info(f"✅ Exported: {result.output_path.name}")
                else:
                    self.context.log_error(f"❌ Failed: {result.error_message}")
                    
            except Exception as e:
                error_result = ExportResult.failure_result(
                    f"Unexpected error exporting object {i}: {str(e)}"
                )
                results.append(error_result)
                self.context.log_error(f"❌ Exception: {str(e)}")
        
        # Log summary
        successful_exports = sum(1 for r in results if r.success)
        self.context.log_info(
            f"Batch export complete: {successful_exports}/{total_objects} successful"
        )
        
        return results
    
    def get_output_path(self, data_object: DataObject, index: Optional[int] = None) -> Path:
        """
        Generate output file path for a data object.
        
        Args:
            data_object: Data object being exported
            index: Optional index for objects without good filename keys
            
        Returns:
            Path where the exported file should be saved
        """
        filename = self._generate_filename(data_object, index)
        return self._get_available_filename(
            self.context.output_directory / f"{filename}.{self.file_extension}"
        )
    
    def preview_export(self, data_object: DataObject, max_length: int = 500) -> str:
        """
        Generate a preview of the export output without creating files.
        
        Args:
            data_object: Data object to preview
            max_length: Maximum length of preview text
            
        Returns:
            Preview string of the export output
        """
        try:
            # This is a default implementation that can be overridden
            preview_content = self._generate_preview_content(data_object)
            
            if len(preview_content) > max_length:
                preview_content = preview_content[:max_length] + "... [truncated]"
            
            return preview_content
            
        except Exception as e:
            return f"Preview generation failed: {str(e)}"
    
    def _generate_filename(self, data_object: DataObject, index: Optional[int] = None) -> str:
        """
        Generate a filename for the data object.
        
        Args:
            data_object: Data object being exported
            index: Optional index for fallback naming
            
        Returns:
            Base filename (without extension)
        """
        # Try to use custom filename pattern from settings
        if hasattr(self.settings, 'custom_filename_pattern') and self.settings.custom_filename_pattern:
            try:
                return self._apply_filename_pattern(data_object, self.settings.custom_filename_pattern)
            except Exception:
                pass  # Fall back to default naming
        
        # Try to use filename key
        filename_key = getattr(self.settings, 'filename_key', None)
        if filename_key:
            filename_value = data_object.get_field(filename_key)
            if filename_value:
                return self._sanitize_filename(str(filename_value))
        
        # Try common fields for filename
        for field in ['name', 'title', 'id', 'identifier']:
            value = data_object.get_field(field)
            if value:
                return self._sanitize_filename(str(value))
        
        # Fallback to index or object ID
        if index is not None:
            return f"document_{index + 1:03d}"
        else:
            return f"document_{data_object.metadata.get('object_id', 'unknown')}"
    
    def _apply_filename_pattern(self, data_object: DataObject, pattern: str) -> str:
        """Apply a filename pattern with variable substitution."""
        import re
        
        def replace_variable(match):
            var_name = match.group(1)
            value = data_object.get_field(var_name, f"unknown_{var_name}")
            return self._sanitize_filename(str(value))
        
        # Replace {field_name} patterns
        filename = re.sub(r'\{([^}]+)\}', replace_variable, pattern)
        return filename
    
    def _sanitize_filename(self, filename: str, max_length: int = 255) -> str:
        """
        Sanitize a filename for filesystem compatibility.
        
        Args:
            filename: Original filename
            max_length: Maximum filename length
            
        Returns:
            Sanitized filename
        """
        import re
        
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'\s+', '_', filename)  # Replace spaces with underscores
        filename = re.sub(r'_+', '_', filename)   # Collapse multiple underscores
        filename = filename.strip('_')            # Remove leading/trailing underscores
        
        # Truncate if too long
        if len(filename) > max_length:
            filename = filename[:max_length]
        
        # Ensure not empty
        if not filename:
            filename = "document"
        
        return filename
    
    def _get_available_filename(self, base_path: Path) -> Path:
        """
        Get an available filename, adding numbers if necessary.
        
        Args:
            base_path: Desired file path
            
        Returns:
            Available file path
        """
        if self.context.overwrite_existing or not base_path.exists():
            return base_path
        
        # Find available filename with suffix
        stem = base_path.stem
        suffix = base_path.suffix
        parent = base_path.parent
        
        counter = 1
        while True:
            new_path = parent / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1
    
    @abstractmethod
    def _generate_preview_content(self, data_object: DataObject) -> str:
        """
        Generate preview content for a data object.
        
        This method should be implemented by each format-specific exporter
        to provide appropriate preview functionality.
        
        Args:
            data_object: Data object to preview
            
        Returns:
            Preview content string
        """
        pass
    
    def _validate_dependencies(self) -> ValidationResult:
        """
        Validate that required dependencies are available.
        
        This base implementation checks for basic dependencies.
        Format-specific exporters should override this method.
        
        Returns:
            ValidationResult indicating dependency status
        """
        result = ValidationResult(is_valid=True)
        
        # Check that output directory is writable
        try:
            self.context.output_directory.mkdir(parents=True, exist_ok=True)
            
            # Test write access
            test_file = self.context.output_directory / ".write_test"
            test_file.touch()
            test_file.unlink()
            
        except Exception as e:
            result.add_error(f"Output directory is not writable: {str(e)}")
        
        return result

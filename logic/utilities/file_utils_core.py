"""
File system operations and path management utilities.

This module provides safe file operations, path validation,
and file management utilities for DocGenius.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List, Union, Dict, Any
from datetime import datetime
import tempfile
import logging


class FileOperationResult:
    """Result container for file operations."""
    
    def __init__(self, success: bool, path: Optional[Path] = None, error: Optional[str] = None):
        self.success = success
        self.path = path
        self.error = error
        self.timestamp = datetime.now()


class PathManager:
    """Path handling and validation utilities."""
    
    @staticmethod
    def validate_file_path(file_path: Union[str, Path]) -> bool:
        """
        Validate if a file path is accessible and valid.
        
        Args:
            file_path: Path to validate
            
        Returns:
            True if path is valid and accessible
        """
        try:
            path = Path(file_path)
            return path.exists() and path.is_file()
        except Exception:
            return False
    
    @staticmethod
    def validate_directory_path(dir_path: Union[str, Path]) -> bool:
        """
        Validate if a directory path is accessible and valid.
        
        Args:
            dir_path: Directory path to validate
            
        Returns:
            True if path is valid and accessible
        """
        try:
            path = Path(dir_path)
            return path.exists() and path.is_dir()
        except Exception:
            return False
    
    @staticmethod
    def normalize_path(path: Union[str, Path]) -> Path:
        """
        Normalize and resolve a path.
        
        Args:
            path: Path to normalize
            
        Returns:
            Normalized Path object
        """
        return Path(path).resolve()
    
    @staticmethod
    def get_safe_filename(filename: str, max_length: int = 255) -> str:
        """
        Create a filesystem-safe filename.
        
        Args:
            filename: Original filename
            max_length: Maximum filename length
            
        Returns:
            Safe filename
        """
        import re
        
        # Remove or replace invalid characters
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        safe_name = re.sub(r'\s+', '_', safe_name)  # Replace spaces with underscores
        safe_name = re.sub(r'_+', '_', safe_name)   # Collapse multiple underscores
        safe_name = safe_name.strip('_')            # Remove leading/trailing underscores
        
        # Truncate if too long
        if len(safe_name) > max_length:
            name_part, ext_part = os.path.splitext(safe_name)
            available_length = max_length - len(ext_part)
            safe_name = name_part[:available_length] + ext_part
        
        # Ensure not empty
        if not safe_name:
            safe_name = "file"
        
        return safe_name
    
    @staticmethod
    def get_unique_path(base_path: Path, max_attempts: int = 1000) -> Path:
        """
        Get a unique file path by adding numbers if necessary.
        
        Args:
            base_path: Desired file path
            max_attempts: Maximum attempts to find unique name
            
        Returns:
            Unique file path
        """
        if not base_path.exists():
            return base_path
        
        stem = base_path.stem
        suffix = base_path.suffix
        parent = base_path.parent
        
        for i in range(1, max_attempts + 1):
            new_path = parent / f"{stem}_{i}{suffix}"
            if not new_path.exists():
                return new_path
        
        # If we can't find a unique name, use timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return parent / f"{stem}_{timestamp}{suffix}"


class FileOperations:
    """Safe file system operations with error handling."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    def safe_create_directory(self, directory_path: Union[str, Path]) -> FileOperationResult:
        """
        Safely create a directory with error handling.
        
        Args:
            directory_path: Path to directory to create
            
        Returns:
            FileOperationResult with operation status
        """
        try:
            path = Path(directory_path)
            path.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Created directory: {path}")
            return FileOperationResult(success=True, path=path)
            
        except Exception as e:
            error_msg = f"Failed to create directory {directory_path}: {str(e)}"
            self.logger.error(error_msg)
            return FileOperationResult(success=False, error=error_msg)
    
    def safe_copy_file(self, source: Union[str, Path], destination: Union[str, Path]) -> FileOperationResult:
        """
        Safely copy a file with error handling.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            FileOperationResult with operation status
        """
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                return FileOperationResult(success=False, error=f"Source file not found: {source}")
            
            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(source_path, dest_path)
            
            self.logger.info(f"Copied file: {source_path} → {dest_path}")
            return FileOperationResult(success=True, path=dest_path)
            
        except Exception as e:
            error_msg = f"Failed to copy file {source} to {destination}: {str(e)}"
            self.logger.error(error_msg)
            return FileOperationResult(success=False, error=error_msg)
    
    def safe_move_file(self, source: Union[str, Path], destination: Union[str, Path]) -> FileOperationResult:
        """
        Safely move a file with error handling.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            FileOperationResult with operation status
        """
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                return FileOperationResult(success=False, error=f"Source file not found: {source}")
            
            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(source_path), str(dest_path))
            
            self.logger.info(f"Moved file: {source_path} → {dest_path}")
            return FileOperationResult(success=True, path=dest_path)
            
        except Exception as e:
            error_msg = f"Failed to move file {source} to {destination}: {str(e)}"
            self.logger.error(error_msg)
            return FileOperationResult(success=False, error=error_msg)
    
    def safe_delete_file(self, file_path: Union[str, Path]) -> FileOperationResult:
        """
        Safely delete a file with error handling.
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            FileOperationResult with operation status
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return FileOperationResult(success=True, path=path)  # Already deleted
            
            path.unlink()
            
            self.logger.info(f"Deleted file: {path}")
            return FileOperationResult(success=True, path=path)
            
        except Exception as e:
            error_msg = f"Failed to delete file {file_path}: {str(e)}"
            self.logger.error(error_msg)
            return FileOperationResult(success=False, error=error_msg)
    
    def get_file_info(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """
        Get information about a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information, or None if file doesn't exist
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return None
            
            stat = path.stat()
            
            return {
                'path': str(path),
                'name': path.name,
                'size': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'extension': path.suffix,
                'is_file': path.is_file(),
                'is_directory': path.is_dir()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get file info for {file_path}: {str(e)}")
            return None


class BackupManager:
    """File backup and recovery utilities."""
    
    def __init__(self, backup_directory: Optional[Path] = None):
        self.backup_directory = backup_directory or Path.home() / ".docgenius_backups"
        self.logger = logging.getLogger(__name__)
    
    def create_backup(self, file_path: Union[str, Path]) -> Optional[Path]:
        """
        Create a backup of a file.
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            Path to backup file, or None if backup failed
        """
        try:
            source_path = Path(file_path)
            
            if not source_path.exists():
                return None
            
            # Ensure backup directory exists
            self.backup_directory.mkdir(parents=True, exist_ok=True)
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source_path.stem}_{timestamp}{source_path.suffix}"
            backup_path = self.backup_directory / backup_name
            
            # Copy file to backup location
            shutil.copy2(source_path, backup_path)
            
            self.logger.info(f"Created backup: {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Failed to create backup for {file_path}: {str(e)}")
            return None
    
    def list_backups(self, pattern: str = "*") -> List[Path]:
        """
        List available backup files.
        
        Args:
            pattern: File pattern to match
            
        Returns:
            List of backup file paths
        """
        try:
            if not self.backup_directory.exists():
                return []
            
            return list(self.backup_directory.glob(pattern))
            
        except Exception as e:
            self.logger.error(f"Failed to list backups: {str(e)}")
            return []
    
    def restore_backup(self, backup_path: Union[str, Path], restore_path: Union[str, Path]) -> bool:
        """
        Restore a file from backup.
        
        Args:
            backup_path: Path to backup file
            restore_path: Path where to restore the file
            
        Returns:
            True if restore was successful
        """
        try:
            backup_file = Path(backup_path)
            restore_file = Path(restore_path)
            
            if not backup_file.exists():
                return False
            
            # Ensure restore directory exists
            restore_file.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(backup_file, restore_file)
            
            self.logger.info(f"Restored from backup: {backup_file} → {restore_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore backup {backup_path}: {str(e)}")
            return False
    
    def cleanup_old_backups(self, max_age_days: int = 30) -> int:
        """
        Clean up old backup files.
        
        Args:
            max_age_days: Maximum age of backups to keep
            
        Returns:
            Number of files deleted
        """
        try:
            if not self.backup_directory.exists():
                return 0
            
            cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
            deleted_count = 0
            
            for backup_file in self.backup_directory.glob("*"):
                if backup_file.stat().st_mtime < cutoff_time:
                    backup_file.unlink()
                    deleted_count += 1
            
            self.logger.info(f"Cleaned up {deleted_count} old backup files")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old backups: {str(e)}")
            return 0


class TemporaryFileManager:
    """Temporary file management utilities."""
    
    def __init__(self):
        self.temp_files = []
        self.temp_dirs = []
        self.logger = logging.getLogger(__name__)
    
    def create_temp_file(self, suffix: str = "", prefix: str = "docgenius_") -> Path:
        """
        Create a temporary file.
        
        Args:
            suffix: File suffix/extension
            prefix: File prefix
            
        Returns:
            Path to temporary file
        """
        temp_file = tempfile.NamedTemporaryFile(
            suffix=suffix,
            prefix=prefix,
            delete=False
        )
        temp_path = Path(temp_file.name)
        temp_file.close()
        
        self.temp_files.append(temp_path)
        return temp_path
    
    def create_temp_directory(self, prefix: str = "docgenius_") -> Path:
        """
        Create a temporary directory.
        
        Args:
            prefix: Directory prefix
            
        Returns:
            Path to temporary directory
        """
        temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def cleanup_temp_files(self) -> int:
        """
        Clean up all tracked temporary files and directories.
        
        Returns:
            Number of items cleaned up
        """
        cleaned_count = 0
        
        # Clean up temporary files
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
                    cleaned_count += 1
            except Exception as e:
                self.logger.warning(f"Failed to delete temp file {temp_file}: {str(e)}")
        
        # Clean up temporary directories
        for temp_dir in self.temp_dirs:
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                    cleaned_count += 1
            except Exception as e:
                self.logger.warning(f"Failed to delete temp directory {temp_dir}: {str(e)}")
        
        self.temp_files.clear()
        self.temp_dirs.clear()
        
        return cleaned_count
    
    def __del__(self):
        """Cleanup temporary files when object is destroyed."""
        self.cleanup_temp_files()


# Convenience functions
def safe_create_directory(directory_path: Union[str, Path]) -> bool:
    """Convenience function for safe directory creation."""
    ops = FileOperations()
    result = ops.safe_create_directory(directory_path)
    return result.success


def get_unique_filename(base_path: Union[str, Path]) -> Path:
    """Convenience function for getting unique filename."""
    return PathManager.get_unique_path(Path(base_path))


def validate_file_path(file_path: Union[str, Path]) -> bool:
    """Convenience function for file path validation."""
    return PathManager.validate_file_path(file_path)

"""
Logging and monitoring utilities for DocGenius.

This module provides centralized logging configuration, session tracking,
and system monitoring capabilities.
"""

import logging
import logging.handlers
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime, timedelta
import json
import sys
import time
import traceback
from dataclasses import dataclass, asdict


@dataclass
class LogEntry:
    """Structured log entry for session tracking."""
    
    timestamp: str
    level: str
    module: str
    message: str
    context: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    error_details: Optional[str] = None


@dataclass
class SessionStats:
    """Session statistics and metrics."""
    
    session_id: str
    start_time: str
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    warnings_count: int = 0
    errors_count: int = 0
    processed_records: int = 0
    generated_files: int = 0


class SessionLogger:
    """Session-based logging with automatic tracking."""
    
    def __init__(self, session_id: Optional[str] = None, log_dir: Optional[Path] = None):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = log_dir or Path.home() / ".docgenius" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_file = self.log_dir / f"session_{self.session_id}.json"
        self.start_time = datetime.now()
        self.entries: List[LogEntry] = []
        
        self.stats = SessionStats(
            session_id=self.session_id,
            start_time=self.start_time.isoformat()
        )
        
        self.logger = logging.getLogger(f"docgenius.session.{self.session_id}")
        self._setup_logger()
        
        self.logger.info(f"Session started: {self.session_id}")
    
    def _setup_logger(self):
        """Setup session-specific logger."""
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        self.logger.setLevel(logging.DEBUG)
        
        # Session file handler
        session_log_file = self.log_dir / f"session_{self.session_id}.log"
        file_handler = logging.FileHandler(session_log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def log(self, level: str, message: str, module: str = "main", 
           context: Optional[Dict[str, Any]] = None, 
           duration_ms: Optional[float] = None,
           error_details: Optional[str] = None):
        """
        Log a structured entry.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            module: Module or component name
            context: Additional context data
            duration_ms: Operation duration in milliseconds
            error_details: Error details if applicable
        """
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level.upper(),
            module=module,
            message=message,
            context=context,
            duration_ms=duration_ms,
            error_details=error_details
        )
        
        self.entries.append(entry)
        
        # Update statistics
        if level.upper() == "WARNING":
            self.stats.warnings_count += 1
        elif level.upper() in ["ERROR", "CRITICAL"]:
            self.stats.errors_count += 1
        
        # Log to standard logger
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_msg = f"[{module}] {message}"
        if context:
            log_msg += f" | Context: {json.dumps(context, default=str)}"
        if duration_ms:
            log_msg += f" | Duration: {duration_ms:.2f}ms"
        
        log_method(log_msg)
        
        # Save session data
        self._save_session_data()
    
    def operation_start(self, operation_name: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Start tracking an operation.
        
        Args:
            operation_name: Name of the operation
            context: Additional context
            
        Returns:
            Operation ID for tracking
        """
        operation_id = f"{operation_name}_{int(time.time() * 1000)}"
        
        self.log("INFO", f"Operation started: {operation_name}", 
                context={**(context or {}), "operation_id": operation_id})
        
        self.stats.total_operations += 1
        return operation_id
    
    def operation_success(self, operation_id: str, operation_name: str, 
                         duration_ms: float, context: Optional[Dict[str, Any]] = None):
        """Mark operation as successful."""
        self.log("INFO", f"Operation completed: {operation_name}", 
                duration_ms=duration_ms,
                context={**(context or {}), "operation_id": operation_id})
        
        self.stats.successful_operations += 1
    
    def operation_error(self, operation_id: str, operation_name: str, 
                       error: Exception, duration_ms: float, 
                       context: Optional[Dict[str, Any]] = None):
        """Mark operation as failed."""
        error_details = f"{type(error).__name__}: {str(error)}\n{traceback.format_exc()}"
        
        self.log("ERROR", f"Operation failed: {operation_name}", 
                duration_ms=duration_ms,
                context={**(context or {}), "operation_id": operation_id},
                error_details=error_details)
        
        self.stats.failed_operations += 1
    
    def record_processed(self, count: int = 1):
        """Record processed records count."""
        self.stats.processed_records += count
    
    def file_generated(self, count: int = 1):
        """Record generated files count."""
        self.stats.generated_files += count
    
    def end_session(self):
        """End the session and finalize statistics."""
        self.end_time = datetime.now()
        self.stats.end_time = self.end_time.isoformat()
        self.stats.duration_seconds = (self.end_time - self.start_time).total_seconds()
        
        self.log("INFO", f"Session ended: {self.session_id}", 
                context={"duration_seconds": self.stats.duration_seconds})
        
        self._save_session_data()
        
        # Close handlers
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)
    
    def _save_session_data(self):
        """Save session data to JSON file."""
        try:
            session_data = {
                "stats": asdict(self.stats),
                "entries": [asdict(entry) for entry in self.entries[-100:]]  # Keep last 100 entries
            }
            
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, default=str)
        
        except Exception as e:
            self.logger.error(f"Failed to save session data: {str(e)}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get session summary statistics."""
        return {
            "session_id": self.session_id,
            "duration": self.stats.duration_seconds or (datetime.now() - self.start_time).total_seconds(),
            "operations": {
                "total": self.stats.total_operations,
                "successful": self.stats.successful_operations,
                "failed": self.stats.failed_operations,
                "success_rate": (self.stats.successful_operations / max(1, self.stats.total_operations)) * 100
            },
            "issues": {
                "warnings": self.stats.warnings_count,
                "errors": self.stats.errors_count
            },
            "processing": {
                "records_processed": self.stats.processed_records,
                "files_generated": self.stats.generated_files
            }
        }


class PerformanceMonitor:
    """Performance monitoring utilities."""
    
    def __init__(self):
        self.timers: Dict[str, float] = {}
        self.counters: Dict[str, int] = {}
        self.measurements: List[Dict[str, Any]] = []
    
    def start_timer(self, name: str):
        """Start a performance timer."""
        self.timers[name] = time.time()
    
    def end_timer(self, name: str) -> float:
        """
        End a performance timer and return duration.
        
        Args:
            name: Timer name
            
        Returns:
            Duration in milliseconds
        """
        if name not in self.timers:
            return 0.0
        
        duration = (time.time() - self.timers[name]) * 1000
        del self.timers[name]
        
        self.measurements.append({
            "timestamp": datetime.now().isoformat(),
            "operation": name,
            "duration_ms": duration
        })
        
        return duration
    
    def increment_counter(self, name: str, amount: int = 1):
        """Increment a performance counter."""
        self.counters[name] = self.counters.get(name, 0) + amount
    
    def get_counter(self, name: str) -> int:
        """Get counter value."""
        return self.counters.get(name, 0)
    
    def get_average_duration(self, operation: str) -> Optional[float]:
        """Get average duration for an operation."""
        matching_measurements = [
            m for m in self.measurements 
            if m["operation"] == operation
        ]
        
        if not matching_measurements:
            return None
        
        total_duration = sum(m["duration_ms"] for m in matching_measurements)
        return total_duration / len(matching_measurements)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        return {
            "counters": dict(self.counters),
            "timers": {
                name: f"{(time.time() - start_time) * 1000:.2f}ms (running)"
                for name, start_time in self.timers.items()
            },
            "operations": {
                operation: {
                    "count": len([m for m in self.measurements if m["operation"] == operation]),
                    "average_duration_ms": self.get_average_duration(operation)
                }
                for operation in set(m["operation"] for m in self.measurements)
            },
            "total_measurements": len(self.measurements)
        }


class SystemMonitor:
    """System resource monitoring."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get current system information."""
        import platform
        import psutil
        
        try:
            return {
                "platform": platform.system(),
                "architecture": platform.architecture()[0],
                "python_version": sys.version,
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                }
            }
        except ImportError:
            # psutil not available, return basic info
            return {
                "platform": platform.system(),
                "architecture": platform.architecture()[0],
                "python_version": sys.version
            }
        except Exception as e:
            self.logger.warning(f"Failed to get system info: {str(e)}")
            return {"error": str(e)}
    
    def check_resource_availability(self) -> Dict[str, bool]:
        """Check if system resources are adequate."""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "memory_ok": memory.percent < 90,
                "disk_ok": disk.percent < 95,
                "cpu_ok": psutil.cpu_percent(interval=1) < 95
            }
        except ImportError:
            return {"psutil_available": False}
        except Exception as e:
            self.logger.warning(f"Resource check failed: {str(e)}")
            return {"error": str(e)}


class LoggingConfigurator:
    """Advanced logging configuration manager."""
    
    def __init__(self):
        self.configured_loggers: List[str] = []
    
    def setup_application_logging(self, 
                                 log_level: str = "INFO",
                                 log_to_file: bool = True,
                                 log_dir: Optional[Path] = None,
                                 max_log_files: int = 10,
                                 max_file_size_mb: int = 10) -> bool:
        """
        Setup comprehensive application logging.
        
        Args:
            log_level: Logging level
            log_to_file: Whether to log to file
            log_dir: Directory for log files
            max_log_files: Maximum number of log files to keep
            max_file_size_mb: Maximum log file size in MB
            
        Returns:
            True if setup was successful
        """
        try:
            # Configure root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(getattr(logging, log_level.upper()))
            
            # Clear existing handlers
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
            
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, log_level.upper()))
            
            console_formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
            
            # File handler (if enabled)
            if log_to_file:
                if log_dir is None:
                    log_dir = Path.home() / ".docgenius" / "logs"
                
                log_dir.mkdir(parents=True, exist_ok=True)
                log_file = log_dir / "docgenius.log"
                
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=max_file_size_mb * 1024 * 1024,
                    backupCount=max_log_files,
                    encoding='utf-8'
                )
                file_handler.setLevel(logging.DEBUG)
                
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
                )
                file_handler.setFormatter(file_formatter)
                root_logger.addHandler(file_handler)
            
            self.configured_loggers.append("root")
            return True
        
        except Exception as e:
            print(f"Failed to setup logging: {str(e)}")
            return False
    
    def setup_module_logger(self, module_name: str, 
                           level: Optional[str] = None) -> logging.Logger:
        """
        Setup a module-specific logger.
        
        Args:
            module_name: Name of the module
            level: Optional log level override
            
        Returns:
            Configured logger
        """
        logger = logging.getLogger(f"docgenius.{module_name}")
        
        if level:
            logger.setLevel(getattr(logging, level.upper()))
        
        self.configured_loggers.append(module_name)
        return logger
    
    def get_log_summary(self, log_file: Path, max_lines: int = 100) -> List[str]:
        """
        Get summary of recent log entries.
        
        Args:
            log_file: Path to log file
            max_lines: Maximum lines to return
            
        Returns:
            List of recent log lines
        """
        try:
            if not log_file.exists():
                return []
            
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            return lines[-max_lines:] if len(lines) > max_lines else lines
        
        except Exception as e:
            return [f"Error reading log file: {str(e)}"]


# Convenience functions and context managers
class OperationTimer:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str, logger: Optional[SessionLogger] = None):
        self.operation_name = operation_name
        self.logger = logger
        self.start_time = None
        self.operation_id = None
    
    def __enter__(self):
        self.start_time = time.time()
        if self.logger:
            self.operation_id = self.logger.operation_start(self.operation_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        
        if self.logger and self.operation_id:
            if exc_type is None:
                self.logger.operation_success(
                    self.operation_id, 
                    self.operation_name, 
                    duration_ms
                )
            else:
                self.logger.operation_error(
                    self.operation_id, 
                    self.operation_name, 
                    exc_val, 
                    duration_ms
                )


def get_session_logger(session_id: Optional[str] = None) -> SessionLogger:
    """Get or create a session logger."""
    return SessionLogger(session_id)


def setup_default_logging(level: str = "INFO") -> bool:
    """Setup default logging configuration."""
    configurator = LoggingConfigurator()
    return configurator.setup_application_logging(log_level=level)

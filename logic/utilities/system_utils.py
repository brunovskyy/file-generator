"""
System utilities for DocGenius.

This module provides system-level operations, environment checks,
and platform-specific utilities.
"""

import os
import sys
import subprocess
import platform
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
import shutil
import tempfile
import logging


class SystemInfo:
    """System information and capabilities detection."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get detailed platform information."""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'architecture': platform.architecture(),
            'python_version': sys.version,
            'python_executable': sys.executable,
            'platform_details': platform.platform()
        }
    
    def get_environment_variables(self, filter_prefix: Optional[str] = None) -> Dict[str, str]:
        """
        Get environment variables, optionally filtered by prefix.
        
        Args:
            filter_prefix: Optional prefix to filter variables
            
        Returns:
            Dictionary of environment variables
        """
        env_vars = dict(os.environ)
        
        if filter_prefix:
            env_vars = {
                key: value for key, value in env_vars.items()
                if key.startswith(filter_prefix)
            }
        
        return env_vars
    
    def check_disk_space(self, path: Union[str, Path]) -> Dict[str, Any]:
        """
        Check available disk space for a given path.
        
        Args:
            path: Path to check
            
        Returns:
            Dictionary with disk space information
        """
        try:
            path = Path(path)
            stat = shutil.disk_usage(path)
            
            return {
                'total_bytes': stat.total,
                'used_bytes': stat.total - stat.free,
                'free_bytes': stat.free,
                'total_gb': stat.total / (1024**3),
                'used_gb': (stat.total - stat.free) / (1024**3),
                'free_gb': stat.free / (1024**3),
                'percent_used': ((stat.total - stat.free) / stat.total) * 100
            }
        
        except Exception as e:
            self.logger.error(f"Failed to check disk space for {path}: {str(e)}")
            return {'error': str(e)}
    
    def check_memory_info(self) -> Dict[str, Any]:
        """
        Get memory information (basic implementation).
        
        Returns:
            Dictionary with available memory information
        """
        try:
            # Try to use psutil if available
            try:
                import psutil
                memory = psutil.virtual_memory()
                return {
                    'total_bytes': memory.total,
                    'available_bytes': memory.available,
                    'used_bytes': memory.used,
                    'percent_used': memory.percent,
                    'total_gb': memory.total / (1024**3),
                    'available_gb': memory.available / (1024**3),
                    'used_gb': memory.used / (1024**3)
                }
            except ImportError:
                # Fallback for systems without psutil
                if platform.system() == "Windows":
                    return self._get_windows_memory()
                elif platform.system() in ["Linux", "Darwin"]:
                    return self._get_unix_memory()
                else:
                    return {'error': 'Memory info not available on this platform'}
        
        except Exception as e:
            self.logger.error(f"Failed to get memory info: {str(e)}")
            return {'error': str(e)}
    
    def _get_windows_memory(self) -> Dict[str, Any]:
        """Get memory info on Windows using wmic."""
        try:
            result = subprocess.run(
                ['wmic', 'OS', 'get', 'TotalVisibleMemorySize,FreePhysicalMemory', '/value'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                memory_info = {}
                
                for line in lines:
                    if '=' in line:
                        key, value = line.split('=', 1)
                        if key.strip() and value.strip():
                            memory_info[key.strip()] = int(value.strip()) * 1024  # Convert KB to bytes
                
                if 'TotalVisibleMemorySize' in memory_info and 'FreePhysicalMemory' in memory_info:
                    total = memory_info['TotalVisibleMemorySize']
                    free = memory_info['FreePhysicalMemory']
                    used = total - free
                    
                    return {
                        'total_bytes': total,
                        'available_bytes': free,
                        'used_bytes': used,
                        'percent_used': (used / total) * 100,
                        'total_gb': total / (1024**3),
                        'available_gb': free / (1024**3),
                        'used_gb': used / (1024**3)
                    }
            
            return {'error': 'Could not parse Windows memory info'}
        
        except Exception as e:
            return {'error': f'Windows memory check failed: {str(e)}'}
    
    def _get_unix_memory(self) -> Dict[str, Any]:
        """Get memory info on Unix-like systems."""
        try:
            # Try reading /proc/meminfo on Linux
            if platform.system() == "Linux":
                with open('/proc/meminfo', 'r') as f:
                    lines = f.readlines()
                
                memory_info = {}
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        # Extract numeric value (assuming kB)
                        value_parts = value.strip().split()
                        if value_parts and value_parts[0].isdigit():
                            memory_info[key.strip()] = int(value_parts[0]) * 1024  # Convert kB to bytes
                
                if 'MemTotal' in memory_info and 'MemAvailable' in memory_info:
                    total = memory_info['MemTotal']
                    available = memory_info['MemAvailable']
                    used = total - available
                    
                    return {
                        'total_bytes': total,
                        'available_bytes': available,
                        'used_bytes': used,
                        'percent_used': (used / total) * 100,
                        'total_gb': total / (1024**3),
                        'available_gb': available / (1024**3),
                        'used_gb': used / (1024**3)
                    }
            
            return {'error': 'Unix memory info not implemented for this platform'}
        
        except Exception as e:
            return {'error': f'Unix memory check failed: {str(e)}'}


class ProcessManager:
    """Process execution and management utilities."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def run_command(self, 
                   command: Union[str, List[str]], 
                   cwd: Optional[Path] = None,
                   timeout: Optional[int] = None,
                   capture_output: bool = True,
                   shell: bool = False) -> Dict[str, Any]:
        """
        Run a system command with comprehensive error handling.
        
        Args:
            command: Command to run (string or list)
            cwd: Working directory
            timeout: Timeout in seconds
            capture_output: Whether to capture stdout/stderr
            shell: Whether to run in shell
            
        Returns:
            Dictionary with execution results
        """
        try:
            self.logger.debug(f"Running command: {command}")
            
            result = subprocess.run(
                command,
                cwd=cwd,
                timeout=timeout,
                capture_output=capture_output,
                text=True,
                shell=shell
            )
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout if capture_output else None,
                'stderr': result.stderr if capture_output else None,
                'command': str(command)
            }
        
        except subprocess.TimeoutExpired as e:
            error_msg = f"Command timed out after {timeout} seconds"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': 'timeout',
                'message': error_msg,
                'command': str(command)
            }
        
        except subprocess.CalledProcessError as e:
            error_msg = f"Command failed with return code {e.returncode}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': 'process_error',
                'message': error_msg,
                'returncode': e.returncode,
                'command': str(command)
            }
        
        except Exception as e:
            error_msg = f"Command execution failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': 'execution_error',
                'message': error_msg,
                'command': str(command)
            }
    
    def check_command_available(self, command: str) -> bool:
        """
        Check if a command is available in the system PATH.
        
        Args:
            command: Command name to check
            
        Returns:
            True if command is available
        """
        return shutil.which(command) is not None
    
    def get_command_path(self, command: str) -> Optional[str]:
        """
        Get the full path to a command.
        
        Args:
            command: Command name
            
        Returns:
            Full path to command, or None if not found
        """
        return shutil.which(command)
    
    def run_python_script(self, 
                         script_path: Path, 
                         args: Optional[List[str]] = None,
                         timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        Run a Python script with the current interpreter.
        
        Args:
            script_path: Path to Python script
            args: Arguments to pass to script
            timeout: Timeout in seconds
            
        Returns:
            Dictionary with execution results
        """
        command = [sys.executable, str(script_path)]
        if args:
            command.extend(args)
        
        return self.run_command(command, timeout=timeout)


class DependencyChecker:
    """Check and manage Python package dependencies."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def check_package_installed(self, package_name: str) -> bool:
        """
        Check if a Python package is installed.
        
        Args:
            package_name: Name of the package
            
        Returns:
            True if package is installed
        """
        try:
            __import__(package_name)
            return True
        except ImportError:
            return False
    
    def get_package_version(self, package_name: str) -> Optional[str]:
        """
        Get the version of an installed package.
        
        Args:
            package_name: Name of the package
            
        Returns:
            Package version string, or None if not installed
        """
        try:
            import importlib.metadata
            return importlib.metadata.version(package_name)
        except ImportError:
            # Fallback for older Python versions
            try:
                import pkg_resources
                return pkg_resources.get_distribution(package_name).version
            except:
                return None
        except Exception:
            return None
    
    def check_dependencies(self, requirements: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Check status of multiple dependencies.
        
        Args:
            requirements: List of package names or package==version specs
            
        Returns:
            Dictionary with dependency status
        """
        results = {}
        
        for requirement in requirements:
            # Parse requirement (handle package==version format)
            if '==' in requirement:
                package_name, required_version = requirement.split('==', 1)
            else:
                package_name = requirement
                required_version = None
            
            installed = self.check_package_installed(package_name)
            version = self.get_package_version(package_name) if installed else None
            
            results[package_name] = {
                'installed': installed,
                'version': version,
                'required_version': required_version,
                'version_match': (
                    version == required_version 
                    if required_version and version 
                    else True
                )
            }
        
        return results
    
    def install_package(self, package_name: str, upgrade: bool = False) -> bool:
        """
        Install a Python package using pip.
        
        Args:
            package_name: Name of package to install
            upgrade: Whether to upgrade if already installed
            
        Returns:
            True if installation was successful
        """
        try:
            command = [sys.executable, '-m', 'pip', 'install']
            
            if upgrade:
                command.append('--upgrade')
            
            command.append(package_name)
            
            process_manager = ProcessManager()
            result = process_manager.run_command(command, timeout=300)  # 5 minute timeout
            
            if result['success']:
                self.logger.info(f"Successfully installed {package_name}")
                return True
            else:
                self.logger.error(f"Failed to install {package_name}: {result.get('stderr', 'Unknown error')}")
                return False
        
        except Exception as e:
            self.logger.error(f"Package installation failed: {str(e)}")
            return False


class EnvironmentManager:
    """Environment and path management utilities."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_app_data_directory(self, app_name: str = "DocGenius") -> Path:
        """
        Get platform-appropriate application data directory.
        
        Args:
            app_name: Name of the application
            
        Returns:
            Path to application data directory
        """
        system = platform.system()
        
        if system == "Windows":
            app_data = os.environ.get('APPDATA')
            if app_data:
                return Path(app_data) / app_name
            else:
                return Path.home() / "AppData" / "Roaming" / app_name
        
        elif system == "Darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / app_name
        
        else:  # Linux and other Unix-like systems
            xdg_config = os.environ.get('XDG_CONFIG_HOME')
            if xdg_config:
                return Path(xdg_config) / app_name.lower()
            else:
                return Path.home() / ".config" / app_name.lower()
    
    def get_temp_directory(self, prefix: str = "docgenius_") -> Path:
        """
        Get a temporary directory for the application.
        
        Args:
            prefix: Prefix for temporary directory name
            
        Returns:
            Path to temporary directory
        """
        temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
        return temp_dir
    
    def cleanup_temp_directories(self, prefix: str = "docgenius_") -> int:
        """
        Clean up temporary directories created by the application.
        
        Args:
            prefix: Prefix to match for cleanup
            
        Returns:
            Number of directories cleaned up
        """
        temp_root = Path(tempfile.gettempdir())
        cleaned_count = 0
        
        try:
            for item in temp_root.iterdir():
                if item.is_dir() and item.name.startswith(prefix):
                    try:
                        shutil.rmtree(item)
                        cleaned_count += 1
                        self.logger.debug(f"Cleaned up temp directory: {item}")
                    except Exception as e:
                        self.logger.warning(f"Failed to clean up {item}: {str(e)}")
        
        except Exception as e:
            self.logger.error(f"Failed to cleanup temp directories: {str(e)}")
        
        return cleaned_count
    
    def set_environment_variable(self, name: str, value: str, persistent: bool = False) -> bool:
        """
        Set an environment variable.
        
        Args:
            name: Environment variable name
            value: Environment variable value
            persistent: Whether to make it persistent (Windows only)
            
        Returns:
            True if successful
        """
        try:
            os.environ[name] = value
            
            # On Windows, we can try to make it persistent
            if persistent and platform.system() == "Windows":
                try:
                    subprocess.run(
                        ['setx', name, value],
                        check=True,
                        capture_output=True
                    )
                except Exception as e:
                    self.logger.warning(f"Failed to set persistent environment variable: {str(e)}")
                    return False
            
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to set environment variable {name}: {str(e)}")
            return False


# Convenience functions
def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information."""
    system_info = SystemInfo()
    return {
        'platform': system_info.get_platform_info(),
        'disk_space': system_info.check_disk_space(Path.cwd()),
        'memory': system_info.check_memory_info()
    }


def check_command_available(command: str) -> bool:
    """Check if a system command is available."""
    return ProcessManager().check_command_available(command)


def run_system_command(command: Union[str, List[str]], **kwargs) -> Dict[str, Any]:
    """Run a system command with error handling."""
    return ProcessManager().run_command(command, **kwargs)


def check_python_dependencies(requirements: List[str]) -> Dict[str, Dict[str, Any]]:
    """Check status of Python package dependencies."""
    return DependencyChecker().check_dependencies(requirements)


def get_app_directory(app_name: str = "DocGenius") -> Path:
    """Get application data directory."""
    return EnvironmentManager().get_app_data_directory(app_name)

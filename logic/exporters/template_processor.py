"""
Template processing utilities for document generation.

This module provides template loading, validation, and processing
capabilities for template-based document generation.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path
import re
import requests
import tempfile
import json
from datetime import datetime

from ..models import DataObject, ValidationResult


class TemplateError(Exception):
    """Exception raised for template-related errors."""
    pass


class TemplateVariable:
    """
    Represents a template variable with metadata and validation.
    
    Template variables are placeholders in templates that get replaced
    with actual data values during rendering.
    """
    
    def __init__(
        self,
        name: str,
        required: bool = True,
        default_value: Any = None,
        validator: Optional[Callable] = None,
        transformer: Optional[Callable] = None
    ):
        self.name = name
        self.required = required
        self.default_value = default_value
        self.validator = validator
        self.transformer = transformer
    
    def validate_value(self, value: Any) -> ValidationResult:
        """Validate a value for this variable."""
        result = ValidationResult(is_valid=True)
        
        if value is None:
            if self.required:
                result.add_error(f"Required template variable '{self.name}' is missing")
            return result
        
        if self.validator:
            try:
                if not self.validator(value):
                    result.add_error(f"Template variable '{self.name}' failed validation")
            except Exception as e:
                result.add_error(f"Template variable '{self.name}' validation error: {str(e)}")
        
        return result
    
    def transform_value(self, value: Any) -> Any:
        """Transform a value using the configured transformer."""
        if value is None:
            return self.default_value
        
        if self.transformer:
            try:
                return self.transformer(value)
            except Exception:
                return value  # Return original if transformation fails
        
        return value


class BaseTemplate(ABC):
    """
    Abstract base class for all template types.
    
    Defines the common interface for template loading, validation,
    and variable processing.
    """
    
    def __init__(self, template_source: Union[str, Path], **kwargs):
        """
        Initialize template with source.
        
        Args:
            template_source: Template file path, URL, or content string
            **kwargs: Additional template-specific options
        """
        self.template_source = template_source
        self.template_content = None
        self.variables = {}
        self.metadata = kwargs
        self._loaded = False
    
    @abstractmethod
    def load_template(self) -> None:
        """Load template content from source."""
        pass
    
    @abstractmethod
    def extract_variables(self) -> List[TemplateVariable]:
        """Extract template variables from content."""
        pass
    
    @abstractmethod
    def render(self, data: Dict[str, Any]) -> Any:
        """Render template with provided data."""
        pass
    
    def validate(self) -> ValidationResult:
        """Validate template structure and variables."""
        result = ValidationResult(is_valid=True)
        
        if not self._loaded:
            try:
                self.load_template()
            except Exception as e:
                result.add_error(f"Failed to load template: {str(e)}")
                return result
        
        # Validate template content
        if not self.template_content:
            result.add_error("Template content is empty")
        
        # Extract and validate variables
        try:
            variables = self.extract_variables()
            self.variables = {var.name: var for var in variables}
        except Exception as e:
            result.add_error(f"Failed to extract template variables: {str(e)}")
        
        return result
    
    def validate_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate data against template requirements."""
        result = ValidationResult(is_valid=True)
        
        for var in self.variables.values():
            value = self._get_nested_value(data, var.name)
            var_result = var.validate_value(value)
            result = result.combine(var_result)
        
        return result
    
    def _get_nested_value(self, data: Dict[str, Any], key_path: str) -> Any:
        """Get nested value using dot notation."""
        current = data
        for part in key_path.split('.'):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current


class TextTemplate(BaseTemplate):
    """
    Simple text template with variable substitution.
    
    Supports basic variable replacement using configurable delimiters.
    """
    
    def __init__(
        self,
        template_source: Union[str, Path],
        opening_delimiter: str = "{{",
        closing_delimiter: str = "}}",
        **kwargs
    ):
        super().__init__(template_source, **kwargs)
        self.opening_delimiter = opening_delimiter
        self.closing_delimiter = closing_delimiter
        self.variable_pattern = None
    
    def load_template(self) -> None:
        """Load template content from source."""
        if isinstance(self.template_source, Path):
            # Load from file
            if not self.template_source.exists():
                raise TemplateError(f"Template file not found: {self.template_source}")
            
            with open(self.template_source, 'r', encoding='utf-8') as f:
                self.template_content = f.read()
                
        elif self.template_source.startswith(('http://', 'https://')):
            # Load from URL
            try:
                response = requests.get(self.template_source, timeout=30)
                response.raise_for_status()
                self.template_content = response.text
            except requests.RequestException as e:
                raise TemplateError(f"Failed to download template: {str(e)}")
                
        else:
            # Treat as template content string
            self.template_content = str(self.template_source)
        
        # Compile variable pattern
        escaped_open = re.escape(self.opening_delimiter)
        escaped_close = re.escape(self.closing_delimiter)
        self.variable_pattern = re.compile(
            f"{escaped_open}\\s*([^{escaped_close}]+)\\s*{escaped_close}"
        )
        
        self._loaded = True
    
    def extract_variables(self) -> List[TemplateVariable]:
        """Extract template variables from content."""
        if not self._loaded:
            self.load_template()
        
        variables = []
        matches = self.variable_pattern.findall(self.template_content)
        
        for match in set(matches):  # Remove duplicates
            var_name = match.strip()
            # Basic variable - can be enhanced with metadata
            variables.append(TemplateVariable(name=var_name))
        
        return variables
    
    def render(self, data: Dict[str, Any]) -> str:
        """Render template with provided data."""
        if not self._loaded:
            self.load_template()
        
        rendered_content = self.template_content
        
        # Apply variable transformations and substitutions
        for var in self.variables.values():
            value = self._get_nested_value(data, var.name)
            transformed_value = var.transform_value(value)
            
            # Replace all occurrences of this variable
            placeholder = f"{self.opening_delimiter}{var.name}{self.closing_delimiter}"
            rendered_content = rendered_content.replace(placeholder, str(transformed_value))
        
        return rendered_content


class TemplateLoader:
    """
    Template loading and caching utilities.
    
    Handles loading templates from various sources with caching
    for improved performance.
    """
    
    def __init__(self, cache_enabled: bool = True):
        self.cache_enabled = cache_enabled
        self._template_cache = {}
        self._content_cache = {}
    
    def load_template(
        self,
        template_source: Union[str, Path],
        template_type: str = "text",
        **kwargs
    ) -> BaseTemplate:
        """
        Load a template from source.
        
        Args:
            template_source: Template file path, URL, or content
            template_type: Type of template ('text', 'docx', etc.)
            **kwargs: Additional template options
            
        Returns:
            Loaded template instance
        """
        cache_key = str(template_source) + str(kwargs)
        
        if self.cache_enabled and cache_key in self._template_cache:
            return self._template_cache[cache_key]
        
        # Create template based on type
        if template_type == "text":
            template = TextTemplate(template_source, **kwargs)
        else:
            raise TemplateError(f"Unsupported template type: {template_type}")
        
        # Load and validate template
        template.load_template()
        validation_result = template.validate()
        
        if not validation_result.is_valid:
            raise TemplateError(f"Template validation failed: {validation_result.errors}")
        
        # Cache template if enabled
        if self.cache_enabled:
            self._template_cache[cache_key] = template
        
        return template
    
    def download_template(self, url: str, cache_duration: int = 3600) -> bytes:
        """
        Download template content from URL with caching.
        
        Args:
            url: Template URL
            cache_duration: Cache duration in seconds
            
        Returns:
            Template content as bytes
        """
        cache_key = url
        now = datetime.now().timestamp()
        
        # Check cache
        if self.cache_enabled and cache_key in self._content_cache:
            cached_data, cached_time = self._content_cache[cache_key]
            if now - cached_time < cache_duration:
                return cached_data
        
        # Download content
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            content = response.content
            
            # Cache content
            if self.cache_enabled:
                self._content_cache[cache_key] = (content, now)
            
            return content
            
        except requests.RequestException as e:
            raise TemplateError(f"Failed to download template from {url}: {str(e)}")
    
    def clear_cache(self) -> None:
        """Clear template cache."""
        self._template_cache.clear()
        self._content_cache.clear()


class TemplateValidator:
    """
    Template validation utilities.
    
    Provides comprehensive validation for templates including
    syntax checking, variable validation, and compatibility checks.
    """
    
    def __init__(self):
        self.validation_rules = []
    
    def add_validation_rule(self, rule: Callable[[BaseTemplate], ValidationResult]) -> None:
        """Add a custom validation rule."""
        self.validation_rules.append(rule)
    
    def validate_template(self, template: BaseTemplate) -> ValidationResult:
        """
        Comprehensive template validation.
        
        Args:
            template: Template to validate
            
        Returns:
            ValidationResult with any issues found
        """
        result = ValidationResult(is_valid=True)
        
        # Basic template validation
        basic_result = template.validate()
        result = result.combine(basic_result)
        
        # Apply custom validation rules
        for rule in self.validation_rules:
            try:
                rule_result = rule(template)
                result = result.combine(rule_result)
            except Exception as e:
                result.add_error(f"Validation rule failed: {str(e)}")
        
        return result
    
    def validate_template_compatibility(
        self,
        template: BaseTemplate,
        sample_data: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate template compatibility with sample data.
        
        Args:
            template: Template to validate
            sample_data: Sample data to test against
            
        Returns:
            ValidationResult indicating compatibility
        """
        result = ValidationResult(is_valid=True)
        
        # Check data compatibility
        data_result = template.validate_data(sample_data)
        result = result.combine(data_result)
        
        # Test rendering with sample data
        try:
            rendered = template.render(sample_data)
            if not rendered:
                result.add_warning("Template renders to empty content")
        except Exception as e:
            result.add_error(f"Template rendering failed: {str(e)}")
        
        return result


class VariableResolver:
    """
    Variable resolution and transformation utilities.
    
    Handles complex variable resolution including nested objects,
    default values, and data transformations.
    """
    
    def __init__(self):
        self.resolvers = {}
        self.transformers = {}
        self.default_values = {}
    
    def add_resolver(self, variable_name: str, resolver_func: Callable) -> None:
        """Add a custom variable resolver."""
        self.resolvers[variable_name] = resolver_func
    
    def add_transformer(self, variable_name: str, transformer_func: Callable) -> None:
        """Add a variable transformer."""
        self.transformers[variable_name] = transformer_func
    
    def set_default_value(self, variable_name: str, default_value: Any) -> None:
        """Set a default value for a variable."""
        self.default_values[variable_name] = default_value
    
    def resolve_variable(
        self,
        variable_name: str,
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Resolve a variable value from data.
        
        Args:
            variable_name: Name of variable to resolve
            data: Data dictionary
            context: Optional context for resolution
            
        Returns:
            Resolved variable value
        """
        # Check for custom resolver
        if variable_name in self.resolvers:
            try:
                return self.resolvers[variable_name](data, context or {})
            except Exception:
                pass  # Fall back to default resolution
        
        # Standard nested resolution
        value = self._get_nested_value(data, variable_name)
        
        # Apply transformer if available
        if variable_name in self.transformers:
            try:
                value = self.transformers[variable_name](value)
            except Exception:
                pass  # Keep original value
        
        # Use default if value is None
        if value is None and variable_name in self.default_values:
            value = self.default_values[variable_name]
        
        return value
    
    def _get_nested_value(self, data: Dict[str, Any], key_path: str) -> Any:
        """Get nested value using dot notation."""
        current = data
        for part in key_path.split('.'):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current


# Template processing convenience functions
def create_template_processor(
    template_source: Union[str, Path],
    template_type: str = "text",
    **kwargs
) -> BaseTemplate:
    """Create and load a template processor."""
    loader = TemplateLoader()
    return loader.load_template(template_source, template_type, **kwargs)


def render_template_with_data(
    template_source: Union[str, Path],
    data: Dict[str, Any],
    template_type: str = "text",
    **kwargs
) -> str:
    """Quick template rendering utility."""
    template = create_template_processor(template_source, template_type, **kwargs)
    return template.render(data)

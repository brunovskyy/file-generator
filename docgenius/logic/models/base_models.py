"""
Base model classes and validation framework for DocGenius.

This module provides the foundation for all data models used throughout
the application, including validation, serialization, and error handling.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass, field
from pathlib import Path
import json


@dataclass
class ValidationResult:
    """Container for validation results with errors and warnings."""
    
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def add_error(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Add an error message with optional context."""
        self.errors.append(message)
        self.is_valid = False
        if context:
            self.context.update(context)
    
    def add_warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Add a warning message with optional context."""
        self.warnings.append(message)
        if context:
            self.context.update(context)
    
    def combine(self, other: 'ValidationResult') -> 'ValidationResult':
        """Combine two validation results."""
        return ValidationResult(
            is_valid=self.is_valid and other.is_valid,
            errors=self.errors + other.errors,
            warnings=self.warnings + other.warnings,
            context={**self.context, **other.context}
        )


class BaseModel(ABC):
    """
    Abstract base class for all DocGenius models.
    
    Provides common functionality for validation, serialization,
    and error handling across all model classes.
    """
    
    @abstractmethod
    def validate(self) -> ValidationResult:
        """Validate the model and return validation result."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                if isinstance(value, BaseModel):
                    result[key] = value.to_dict()
                elif isinstance(value, (list, tuple)):
                    result[key] = [
                        item.to_dict() if isinstance(item, BaseModel) else item
                        for item in value
                    ]
                elif isinstance(value, Path):
                    result[key] = str(value)
                else:
                    result[key] = value
        return result
    
    def to_json(self, indent: Optional[int] = 2) -> str:
        """Convert model to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def __str__(self) -> str:
        """String representation of the model."""
        return f"{self.__class__.__name__}({self.to_dict()})"


class ValidationRule:
    """
    Individual validation rule with custom logic.
    
    Allows for flexible validation rules that can be applied
    to different model types and contexts.
    """
    
    def __init__(
        self,
        name: str,
        validation_func: callable,
        error_message: str,
        warning_message: Optional[str] = None
    ):
        self.name = name
        self.validation_func = validation_func
        self.error_message = error_message
        self.warning_message = warning_message
    
    def validate(self, value: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Apply the validation rule to a value."""
        result = ValidationResult(is_valid=True)
        
        try:
            is_valid = self.validation_func(value, context or {})
            
            if not is_valid:
                if self.warning_message and context and context.get('warnings_as_errors', False):
                    result.add_warning(self.warning_message)
                else:
                    result.add_error(self.error_message)
        
        except Exception as e:
            result.add_error(f"Validation rule '{self.name}' failed: {str(e)}")
        
        return result


class FieldValidator:
    """
    Field-level validator for model attributes.
    
    Provides common validation patterns like required fields,
    type checking, range validation, etc.
    """
    
    @staticmethod
    def required(field_name: str) -> ValidationRule:
        """Create a required field validation rule."""
        return ValidationRule(
            name=f"required_{field_name}",
            validation_func=lambda value, ctx: value is not None and str(value).strip() != "",
            error_message=f"Field '{field_name}' is required"
        )
    
    @staticmethod
    def type_check(field_name: str, expected_type: type) -> ValidationRule:
        """Create a type checking validation rule."""
        return ValidationRule(
            name=f"type_{field_name}",
            validation_func=lambda value, ctx: isinstance(value, expected_type),
            error_message=f"Field '{field_name}' must be of type {expected_type.__name__}"
        )
    
    @staticmethod
    def path_exists(field_name: str, must_exist: bool = True) -> ValidationRule:
        """Create a path existence validation rule."""
        def validate_path(value, ctx):
            if value is None:
                return not must_exist
            path = Path(value) if not isinstance(value, Path) else value
            return path.exists() if must_exist else True
        
        return ValidationRule(
            name=f"path_exists_{field_name}",
            validation_func=validate_path,
            error_message=f"Path in field '{field_name}' does not exist" if must_exist 
                         else f"Path in field '{field_name}' is invalid"
        )
    
    @staticmethod
    def choices(field_name: str, valid_choices: List[Any]) -> ValidationRule:
        """Create a choices validation rule."""
        return ValidationRule(
            name=f"choices_{field_name}",
            validation_func=lambda value, ctx: value in valid_choices,
            error_message=f"Field '{field_name}' must be one of: {valid_choices}"
        )
    
    @staticmethod
    def min_length(field_name: str, min_len: int) -> ValidationRule:
        """Create a minimum length validation rule."""
        return ValidationRule(
            name=f"min_length_{field_name}",
            validation_func=lambda value, ctx: len(str(value)) >= min_len,
            error_message=f"Field '{field_name}' must be at least {min_len} characters long"
        )
    
    @staticmethod
    def custom(field_name: str, validation_func: callable, error_message: str) -> ValidationRule:
        """Create a custom validation rule."""
        return ValidationRule(
            name=f"custom_{field_name}",
            validation_func=validation_func,
            error_message=error_message
        )


class ModelValidator:
    """
    Model-level validator that applies multiple validation rules.
    
    Coordinates validation across multiple fields and provides
    comprehensive validation results.
    """
    
    def __init__(self):
        self.rules: List[ValidationRule] = []
    
    def add_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule."""
        self.rules.append(rule)
    
    def add_field_rule(
        self,
        field_name: str,
        rule_type: str,
        **kwargs
    ) -> None:
        """Add a field validation rule using FieldValidator."""
        validator_method = getattr(FieldValidator, rule_type, None)
        if validator_method:
            rule = validator_method(field_name, **kwargs)
            self.add_rule(rule)
        else:
            raise ValueError(f"Unknown validation rule type: {rule_type}")
    
    def validate_model(
        self,
        model: BaseModel,
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate a model using all configured rules."""
        combined_result = ValidationResult(is_valid=True)
        
        for rule in self.rules:
            field_name = rule.name.split('_', 1)[-1]  # Extract field name from rule name
            field_value = getattr(model, field_name, None)
            
            rule_result = rule.validate(field_value, context)
            combined_result = combined_result.combine(rule_result)
        
        return combined_result

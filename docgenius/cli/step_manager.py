"""
Dynamic Step Management System
Handles conditional steps and progress tracking for DocGenius CLI.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class StepType(Enum):
    """Types of configuration steps."""
    ALWAYS = "always"          # Always appears
    CONDITIONAL = "conditional" # Appears based on conditions
    FORMAT_SPECIFIC = "format_specific"  # Specific to export formats


@dataclass
class StepDefinition:
    """Definition of a configuration step."""
    key: str
    title: str
    description: str
    step_type: StepType
    condition_func: Optional[callable] = None
    depends_on: List[str] = None
    order: int = 0


class StepManager:
    """Manages dynamic step calculation and navigation."""
    
    def __init__(self):
        self.steps = self._define_steps()
        self.current_config = {}
        
    def _define_steps(self) -> List[StepDefinition]:
        """Define all possible steps with their conditions."""
        return [
            StepDefinition(
                key="data_source",
                title="Data Source Selection",
                description="Choose your data source",
                step_type=StepType.ALWAYS,
                order=1
            ),
            StepDefinition(
                key="template_selection", 
                title="Template Selection",
                description="Choose document template",
                step_type=StepType.ALWAYS,
                order=2
            ),
            StepDefinition(
                key="export_formats",
                title="Export Format Selection", 
                description="Choose output formats",
                step_type=StepType.ALWAYS,
                order=3
            ),
            StepDefinition(
                key="output_directory",
                title="Output Directory",
                description="Choose where to save files", 
                step_type=StepType.ALWAYS,
                order=4
            ),
            StepDefinition(
                key="markdown_config",
                title="Markdown Configuration",
                description="Configure YAML and content options",
                step_type=StepType.FORMAT_SPECIFIC,
                condition_func=lambda config: 'markdown' in config.get('export_types', []),
                depends_on=["export_formats"],
                order=5
            ),
            StepDefinition(
                key="markdown_yaml_keys",
                title="YAML Key Selection", 
                description="Choose which keys for YAML front matter",
                step_type=StepType.CONDITIONAL,
                condition_func=lambda config: (
                    'markdown' in config.get('export_types', []) and 
                    config.get('yaml_front_matter', False) and
                    config.get('yaml_key_selection') == 'select'
                ),
                depends_on=["markdown_config"],
                order=6
            ),
            StepDefinition(
                key="pdf_config",
                title="PDF Configuration",
                description="Configure PDF layout and styling",
                step_type=StepType.FORMAT_SPECIFIC,
                condition_func=lambda config: 'pdf' in config.get('export_types', []),
                depends_on=["export_formats"],
                order=7
            ),
            StepDefinition(
                key="word_config", 
                title="Word Configuration",
                description="Configure Word document options",
                step_type=StepType.FORMAT_SPECIFIC,
                condition_func=lambda config: 'word' in config.get('export_types', []),
                depends_on=["export_formats"],
                order=8
            ),
            StepDefinition(
                key="template_variables",
                title="Template Variables",
                description="Map data fields to template variables",
                step_type=StepType.CONDITIONAL,
                condition_func=lambda config: config.get('template_path') is not None,
                depends_on=["template_selection"],
                order=9
            ),
            StepDefinition(
                key="final_review",
                title="Configuration Review",
                description="Review and confirm your settings",
                step_type=StepType.ALWAYS,
                order=100  # Always last
            )
        ]
    
    def get_active_steps(self, config: Dict[str, Any]) -> List[StepDefinition]:
        """Get list of steps that should be shown based on current config."""
        active_steps = []
        
        for step in sorted(self.steps, key=lambda s: s.order):
            if self._should_include_step(step, config):
                active_steps.append(step)
                
        return active_steps
    
    def _should_include_step(self, step: StepDefinition, config: Dict[str, Any]) -> bool:
        """Determine if a step should be included based on current config."""
        # Always include ALWAYS steps
        if step.step_type == StepType.ALWAYS:
            return True
            
        # Check conditions for conditional steps
        if step.condition_func:
            try:
                return step.condition_func(config)
            except Exception:
                return False
                
        return True
    
    def get_step_progress(self, current_step_key: str, config: Dict[str, Any]) -> Tuple[int, int, str]:
        """Get current step progress information."""
        active_steps = self.get_active_steps(config)
        
        # Find current step index
        current_index = None
        for i, step in enumerate(active_steps):
            if step.key == current_step_key:
                current_index = i + 1  # 1-based
                break
                
        if current_index is None:
            current_index = 1
            
        total_steps = len(active_steps)
        step_title = next((s.title for s in active_steps if s.key == current_step_key), "Unknown Step")
        
        return current_index, total_steps, step_title
    
    def get_next_step(self, current_step_key: str, config: Dict[str, Any]) -> Optional[str]:
        """Get the next step key based on current step and config."""
        active_steps = self.get_active_steps(config)
        
        # Find current step index
        current_index = None
        for i, step in enumerate(active_steps):
            if step.key == current_step_key:
                current_index = i
                break
                
        if current_index is None or current_index >= len(active_steps) - 1:
            return None
            
        return active_steps[current_index + 1].key
    
    def get_previous_step(self, current_step_key: str, config: Dict[str, Any]) -> Optional[str]:
        """Get the previous step key based on current step and config."""
        active_steps = self.get_active_steps(config)
        
        # Find current step index  
        current_index = None
        for i, step in enumerate(active_steps):
            if step.key == current_step_key:
                current_index = i
                break
                
        if current_index is None or current_index <= 0:
            return None
            
        return active_steps[current_index - 1].key
    
    def recalculate_steps(self, config: Dict[str, Any]) -> List[StepDefinition]:
        """Recalculate active steps when configuration changes."""
        self.current_config = config.copy()
        return self.get_active_steps(config)
    
    def get_step_summary(self, config: Dict[str, Any]) -> str:
        """Generate a summary of all active steps and their status."""
        active_steps = self.get_active_steps(config)
        
        summary_lines = ["📋 Configuration Steps:"]
        for i, step in enumerate(active_steps, 1):
            # Determine step status
            if self._is_step_completed(step.key, config):
                status = "✅"
            elif self._is_step_current(step.key, config):
                status = "🔄"
            else:
                status = "⬜"
                
            summary_lines.append(f"  {status} Step {i}: {step.title}")
            
        return "\n".join(summary_lines)
    
    def _is_step_completed(self, step_key: str, config: Dict[str, Any]) -> bool:
        """Check if a step has been completed."""
        completion_checks = {
            "data_source": lambda c: c.get('source') is not None,
            "template_selection": lambda c: True,  # Optional step
            "export_formats": lambda c: c.get('export_types') is not None,
            "output_directory": lambda c: c.get('output_dir') is not None,
            "markdown_config": lambda c: c.get('yaml_front_matter') is not None,
            "markdown_yaml_keys": lambda c: c.get('selected_keys') is not None,
            "pdf_config": lambda c: True,  # TODO: Implement PDF config checks
            "word_config": lambda c: True,  # TODO: Implement Word config checks
            "template_variables": lambda c: True,  # TODO: Implement template checks
            "final_review": lambda c: False  # Never completed until final
        }
        
        check_func = completion_checks.get(step_key)
        if check_func:
            try:
                return check_func(config)
            except Exception:
                return False
        return False
    
    def _is_step_current(self, step_key: str, config: Dict[str, Any]) -> bool:
        """Check if this is the current step being processed."""
        return config.get('current_step') == step_key

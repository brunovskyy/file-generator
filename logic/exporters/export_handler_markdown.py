"""
Markdown exporter with YAML front matter support.

This module provides comprehensive Markdown export functionality with
configurable YAML front matter, content formatting, and file organization.
"""

import json
from typing import Any, Dict, List, Optional, Set, Union
from pathlib import Path
from datetime import datetime
import logging

# Optional YAML support
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from .export_handler_base import BaseExporter, ExportResult, ExportContext
from .template_processor import TextTemplate, TemplateLoader
from ..models import DataObject, DataCollection, MarkdownSettings, ValidationResult


class MarkdownExportError(Exception):
    """Exception raised for Markdown export related errors."""
    pass


class YAMLFrontMatterGenerator:
    """
    YAML front matter generation utilities.
    
    Handles creation of YAML front matter blocks for Markdown documents
    with configurable key selection and value processing.
    """
    
    def __init__(self, settings: MarkdownSettings):
        self.settings = settings
    
    def generate_front_matter(self, data_object: DataObject) -> str:
        """
        Generate YAML front matter for a data object.
        
        Args:
            data_object: Data object to process
            
        Returns:
            YAML front matter string with delimiters
        """
        if not self.settings.include_yaml_front_matter:
            return ""
        
        yaml_data = self._extract_yaml_data(data_object)
        
        if not yaml_data:
            return "---\n---\n"
        
        # Generate YAML content
        if YAML_AVAILABLE:
            yaml_content = yaml.dump(
                yaml_data,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=True
            )
        else:
            # Fallback to JSON if PyYAML not available
            yaml_content = json.dumps(yaml_data, indent=2, ensure_ascii=False)
        
        return f"---\n{yaml_content}---\n"
    
    def _extract_yaml_data(self, data_object: DataObject) -> Dict[str, Any]:
        """Extract YAML data based on selection strategy."""
        if self.settings.yaml_key_selection.value == "none":
            return {}
        
        available_keys = data_object.get_all_keys()
        
        if self.settings.yaml_key_selection.value == "all":
            selected_keys = available_keys
        elif self.settings.yaml_key_selection.value == "select":
            selected_keys = self.settings.selected_yaml_keys
            if not selected_keys:
                selected_keys = available_keys  # Fallback to all if none selected
        elif self.settings.yaml_key_selection.value == "common":
            # This would need collection context - simplified for single object
            selected_keys = available_keys
        else:
            selected_keys = set()
        
        yaml_data = {}
        for key in selected_keys:
            value = data_object.get_field(key)
            if value is not None:
                if self.settings.flatten_yaml_values and self._is_complex_value(value):
                    # Skip complex values if flattening is enabled
                    continue
                yaml_data[key] = value
        
        return yaml_data
    
    def _is_complex_value(self, value: Any) -> bool:
        """Check if a value is complex (dict, list, etc.)."""
        return isinstance(value, (dict, list, tuple))


class MarkdownFormatter:
    """
    Markdown content formatting utilities.
    
    Handles conversion of data objects to properly formatted
    Markdown content with headers, tables, and code blocks.
    """
    
    def __init__(self, settings: MarkdownSettings):
        self.settings = settings
    
    def format_content(self, data_object: DataObject, excluded_keys: Optional[Set[str]] = None) -> str:
        """
        Format data object content as Markdown.
        
        Args:
            data_object: Data object to format
            excluded_keys: Keys to exclude from content
            
        Returns:
            Formatted Markdown content
        """
        sections = []
        excluded_keys = excluded_keys or set()
        
        # Get keys that were used in YAML front matter
        if self.settings.include_yaml_front_matter:
            yaml_generator = YAMLFrontMatterGenerator(self.settings)
            yaml_data = yaml_generator._extract_yaml_data(data_object)
            excluded_keys.update(yaml_data.keys())
        
        # Add table of contents if requested
        if self.settings.include_table_of_contents:
            toc = self._generate_table_of_contents(data_object, excluded_keys)
            if toc:
                sections.append("## Table of Contents\n\n" + toc + "\n")
        
        # Format data sections
        content_sections = self._create_content_sections(data_object, excluded_keys)
        sections.extend(content_sections)
        
        return "\n".join(sections)
    
    def _generate_table_of_contents(self, data_object: DataObject, excluded_keys: Set[str]) -> str:
        """Generate table of contents for the document."""
        toc_items = []
        
        for key in data_object.get_all_keys():
            if key not in excluded_keys:
                # Create TOC entry
                anchor = key.replace('.', '-').replace('_', '-').lower()
                title = key.replace('_', ' ').replace('.', ' → ').title()
                toc_items.append(f"- [{title}](#{anchor})")
        
        return "\n".join(toc_items)
    
    def _create_content_sections(self, data_object: DataObject, excluded_keys: Set[str]) -> List[str]:
        """Create content sections for data object fields."""
        sections = []
        
        for key in sorted(data_object.get_all_keys()):
            if key in excluded_keys:
                continue
            
            value = data_object.get_field(key)
            if value is None:
                continue
            
            section = self._format_field_section(key, value)
            if section:
                sections.append(section)
        
        return sections
    
    def _format_field_section(self, key: str, value: Any) -> str:
        """Format a single field as a Markdown section."""
        # Create section header
        header_level = min(self._calculate_header_level(key), self.settings.max_heading_level)
        header_prefix = "#" * header_level
        section_title = key.replace('_', ' ').replace('.', ' → ').title()
        
        header = f"{header_prefix} {section_title}\n\n"
        
        # Format content based on value type
        if isinstance(value, dict):
            content = self._format_dict_as_table(value)
        elif isinstance(value, list):
            content = self._format_list_as_markdown(value)
        elif isinstance(value, str) and self._looks_like_json(value):
            content = f"```{self.settings.code_block_language}\n{value}\n```"
        else:
            content = str(value)
        
        return header + content + "\n"
    
    def _calculate_header_level(self, key: str) -> int:
        """Calculate appropriate header level based on key depth."""
        depth = key.count('.')
        return min(depth + 2, self.settings.max_heading_level)  # Start at h2
    
    def _format_dict_as_table(self, data_dict: Dict[str, Any]) -> str:
        """Format dictionary as Markdown table."""
        if not data_dict:
            return "*No data*"
        
        # Create table headers
        table_lines = ["| Key | Value |", "|-----|-------|"]
        
        for key, value in data_dict.items():
            # Escape pipe characters in content
            key_escaped = str(key).replace('|', '\\|')
            value_escaped = str(value).replace('|', '\\|').replace('\n', ' ')
            
            table_lines.append(f"| {key_escaped} | {value_escaped} |")
        
        return "\n".join(table_lines)
    
    def _format_list_as_markdown(self, data_list: List[Any]) -> str:
        """Format list as Markdown bullet points."""
        if not data_list:
            return "*Empty list*"
        
        list_items = []
        for item in data_list:
            item_str = str(item).replace('\n', ' ')
            list_items.append(f"- {item_str}")
        
        return "\n".join(list_items)
    
    def _looks_like_json(self, value: str) -> bool:
        """Check if a string looks like JSON content."""
        stripped = value.strip()
        return (stripped.startswith('{') and stripped.endswith('}')) or \
               (stripped.startswith('[') and stripped.endswith(']'))


class MarkdownExporter(BaseExporter):
    """
    Main Markdown export engine.
    
    Converts data objects to Markdown files with configurable YAML front matter,
    content formatting, and file organization options.
    """
    
    def __init__(self, settings: MarkdownSettings, context: ExportContext):
        """Initialize Markdown exporter."""
        super().__init__(settings, context)
        self.yaml_generator = YAMLFrontMatterGenerator(settings)
        self.formatter = MarkdownFormatter(settings)
        self.template_loader = TemplateLoader() if settings.template_path or settings.template_url else None
    
    def _get_format_name(self) -> str:
        """Return the format name."""
        return "Markdown"
    
    def _get_file_extension(self) -> str:
        """Return the file extension."""
        return "md"
    
    def validate_settings(self) -> ValidationResult:
        """Validate Markdown export settings and dependencies."""
        result = ValidationResult(is_valid=True)
        
        # Validate base settings
        base_result = self.settings.validate()
        result = result.combine(base_result)
        
        # Check YAML dependency if needed
        if self.settings.include_yaml_front_matter and not YAML_AVAILABLE:
            result.add_warning(
                "PyYAML not available - will use JSON format for front matter"
            )
        
        # Validate template if specified
        if self.settings.use_template and self.template_loader:
            try:
                template = self._load_template()
                template_result = template.validate()
                result = result.combine(template_result)
            except Exception as e:
                result.add_error(f"Template validation failed: {str(e)}")
        
        # Validate dependencies
        deps_result = self._validate_dependencies()
        result = result.combine(deps_result)
        
        return result
    
    def export_single(self, data_object: DataObject) -> ExportResult:
        """Export a single data object to Markdown file."""
        try:
            start_time = datetime.now()
            
            # Generate output path
            output_path = self.get_output_path(data_object)
            
            # Check dry run mode
            if self.context.dry_run:
                return ExportResult.success_result(
                    output_path=output_path,
                    metadata={'dry_run': True, 'content_preview': self.preview_export(data_object)}
                )
            
            # Generate content
            if self.settings.use_template and self.template_loader:
                content = self._render_with_template(data_object)
            else:
                content = self._generate_markdown_content(data_object)
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            self.context.log_info(f"Created Markdown file: {output_path.name}")
            
            return ExportResult.success_result(
                output_path=output_path,
                export_duration=duration,
                metadata={
                    'format': 'markdown',
                    'yaml_front_matter': self.settings.include_yaml_front_matter,
                    'template_used': self.settings.use_template
                }
            )
            
        except Exception as e:
            self.context.log_error(f"Markdown export failed: {str(e)}")
            return ExportResult.failure_result(
                error_message=f"Markdown export failed: {str(e)}",
                metadata={'data_object_id': data_object.metadata.get('object_id')}
            )
    
    def _generate_markdown_content(self, data_object: DataObject) -> str:
        """Generate complete Markdown content for data object."""
        content_parts = []
        
        # Add YAML front matter
        if self.settings.include_yaml_front_matter:
            front_matter = self.yaml_generator.generate_front_matter(data_object)
            content_parts.append(front_matter)
        
        # Add main content
        main_content = self.formatter.format_content(data_object)
        content_parts.append(main_content)
        
        return "\n".join(content_parts)
    
    def _render_with_template(self, data_object: DataObject) -> str:
        """Render content using template."""
        template = self._load_template()
        
        # Prepare template data
        template_data = {
            **data_object.data,
            '_metadata': data_object.metadata,
            '_source_info': data_object.source_info
        }
        
        # Add generated front matter if needed
        if self.settings.include_yaml_front_matter:
            front_matter = self.yaml_generator.generate_front_matter(data_object)
            template_data['_yaml_front_matter'] = front_matter
        
        return template.render(template_data)
    
    def _load_template(self) -> TextTemplate:
        """Load and cache template."""
        if self.settings.template_path:
            template_source = Path(self.settings.template_path)
        elif self.settings.template_url:
            template_source = self.settings.template_url
        else:
            raise MarkdownExportError("No template source specified")
        
        return self.template_loader.load_template(template_source, "text")
    
    def _generate_preview_content(self, data_object: DataObject) -> str:
        """Generate preview content for data object."""
        try:
            content = self._generate_markdown_content(data_object)
            return content
        except Exception as e:
            return f"Preview generation failed: {str(e)}"
    
    def create_summary_file(
        self,
        data_collection: DataCollection,
        export_results: List[ExportResult]
    ) -> Optional[Path]:
        """
        Create a summary file for the export batch.
        
        Args:
            data_collection: Original data collection
            export_results: Results from batch export
            
        Returns:
            Path to created summary file, if created
        """
        if not self.settings.create_summary_file:
            return None
        
        try:
            summary_path = self.context.output_directory / "README.md"
            
            # Generate summary content
            summary_lines = [
                f"# Export Summary",
                f"",
                f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"**Transaction ID:** {self.context.transaction_id}",
                f"**Total Objects:** {len(data_collection)}",
                f"**Successful Exports:** {sum(1 for r in export_results if r.success)}",
                f"**Failed Exports:** {sum(1 for r in export_results if not r.success)}",
                f"",
                f"## Export Settings",
                f"",
                f"- **Format:** Markdown",
                f"- **YAML Front Matter:** {self.settings.include_yaml_front_matter}",
                f"- **Template Used:** {self.settings.use_template}",
                f"- **Output Directory:** {self.context.output_directory}",
                f"",
                f"## Generated Files",
                f""
            ]
            
            # Add file list
            for i, result in enumerate(export_results):
                if result.success:
                    summary_lines.append(f"- [{result.output_path.name}](./{result.output_path.name})")
                else:
                    summary_lines.append(f"- ❌ Object {i + 1}: {result.error_message}")
            
            # Add statistics if available
            stats = data_collection.get_statistics()
            if stats:
                summary_lines.extend([
                    f"",
                    f"## Data Statistics",
                    f"",
                    f"- **Unique Keys:** {stats.get('unique_keys', 'N/A')}",
                    f"- **Common Keys:** {stats.get('common_keys', 'N/A')}",
                    f"- **Memory Usage:** {stats.get('memory_usage_mb', 0):.2f} MB"
                ])
            
            # Write summary file
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(summary_lines))
            
            self.context.log_info(f"Created summary file: {summary_path.name}")
            return summary_path
            
        except Exception as e:
            self.context.log_warning(f"Failed to create summary file: {str(e)}")
            return None


# Convenience functions for backward compatibility
def export_to_markdown(
    data_list: List[Dict[str, Any]],
    output_directory: str,
    filename_key: Optional[str] = None,
    include_yaml_front_matter: bool = True,
    selected_yaml_keys: Optional[Set[str]] = None,
    flatten_yaml_values: bool = True,
    transaction_id: Optional[str] = None
) -> List[Path]:
    """
    Export data to Markdown format - compatibility function.
    
    This function provides backward compatibility with the existing API
    while using the new structured exporter architecture.
    """
    from ..models import DataCollection, DataObject
    from datetime import datetime
    import uuid
    
    # Convert legacy data format to new models
    data_objects = [
        DataObject(data=item, source_info={}, metadata={})
        for item in data_list
    ]
    data_collection = DataCollection(objects=data_objects)
    
    # Create settings
    settings = MarkdownSettings(
        include_yaml_front_matter=include_yaml_front_matter,
        selected_yaml_keys=selected_yaml_keys or set(),
        flatten_yaml_values=flatten_yaml_values,
        custom_filename_pattern=f"{{{filename_key}}}" if filename_key else None
    )
    
    # Create context
    context = ExportContext(
        output_directory=Path(output_directory),
        transaction_id=transaction_id or str(uuid.uuid4())[:8]
    )
    
    # Create and run exporter
    exporter = MarkdownExporter(settings, context)
    results = exporter.export_batch(data_collection)
    
    # Create summary file
    exporter.create_summary_file(data_collection, results)
    
    # Return file paths for compatibility
    return [result.output_path for result in results if result.success]

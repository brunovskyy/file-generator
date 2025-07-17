"""
PDF document exporter for DocGenius.

This module provides PDF export functionality using the BaseExporter
architecture with support for direct PDF generation and template-based
PDF creation.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime

from ..models.base_models import ValidationResult
from ..models.data_structures import DataObject, DataCollection
from ..models.document_config import DocumentConfig, PDFSettings
from .export_handler_base import BaseExporter, ExportResult, ExportContext
from .template_processor import TemplateProcessor


class PDFExporter(BaseExporter):
    """PDF document exporter with template support."""
    
    def __init__(self):
        super().__init__()
        self.format_name = "PDF"
        self.file_extension = ".pdf"
        self.template_processor = TemplateProcessor()
        
        # Check PDF dependencies
        self._check_dependencies()
    
    def _check_dependencies(self) -> None:
        """Check if PDF generation dependencies are available."""
        self.dependencies_available = True
        self.missing_dependencies = []
        
        try:
            import reportlab
            self.logger.debug("ReportLab available for PDF generation")
        except ImportError:
            self.dependencies_available = False
            self.missing_dependencies.append("reportlab")
            self.logger.warning("ReportLab not available - PDF generation disabled")
    
    def validate_config(self, config: DocumentConfig) -> ValidationResult:
        """
        Validate PDF-specific configuration.
        
        Args:
            config: Document configuration to validate
            
        Returns:
            ValidationResult with validation details
        """
        errors = []
        warnings = []
        
        # Check base configuration
        base_result = super().validate_config(config)
        if not base_result.is_valid:
            errors.extend(base_result.errors)
        if base_result.warnings:
            warnings.extend(base_result.warnings)
        
        # Check PDF-specific settings
        if hasattr(config, 'pdf_settings') and config.pdf_settings:
            pdf_settings = config.pdf_settings
            
            # Validate page size
            valid_page_sizes = ['A4', 'A3', 'A5', 'Letter', 'Legal', 'Tabloid']
            if pdf_settings.page_size not in valid_page_sizes:
                warnings.append(f"Unknown page size: {pdf_settings.page_size}")
            
            # Validate margins
            if pdf_settings.margins:
                for margin_name, margin_value in pdf_settings.margins.items():
                    if not isinstance(margin_value, (int, float)) or margin_value < 0:
                        errors.append(f"Invalid margin {margin_name}: {margin_value}")
            
            # Validate font settings
            if pdf_settings.font_size <= 0:
                errors.append("Font size must be positive")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def export_single(self, data_object: DataObject, context: ExportContext) -> ExportResult:
        """
        Export a single data object to PDF.
        
        Args:
            data_object: Data object to export
            context: Export context with configuration
            
        Returns:
            ExportResult with export details
        """
        try:
            if not self.dependencies_available:
                return ExportResult(
                    success=False,
                    error_message=f"PDF dependencies not available: {', '.join(self.missing_dependencies)}",
                    exported_files=[]
                )
            
            # Generate filename
            filename = self._generate_filename(data_object, context.config)
            output_path = context.output_directory / f"{filename}.pdf"
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Choose export method based on configuration
            if context.config.template_file:
                success = self._export_with_template(data_object, output_path, context)
            else:
                success = self._export_direct(data_object, output_path, context)
            
            if success:
                return ExportResult(
                    success=True,
                    exported_files=[output_path]
                )
            else:
                return ExportResult(
                    success=False,
                    error_message="PDF generation failed",
                    exported_files=[]
                )
        
        except Exception as e:
            self.logger.error(f"PDF export failed for {data_object.get_display_name()}: {str(e)}")
            return ExportResult(
                success=False,
                error_message=str(e),
                exported_files=[]
            )
    
    def _export_direct(self, data_object: DataObject, output_path: Path, 
                      context: ExportContext) -> bool:
        """
        Generate PDF directly using ReportLab.
        
        Args:
            data_object: Data object to export
            output_path: Output file path
            context: Export context
            
        Returns:
            True if successful
        """
        try:
            from reportlab.lib.pagesizes import letter, A4, A3, A5, legal, tabloid
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            
            # Get PDF settings
            pdf_settings = getattr(context.config, 'pdf_settings', PDFSettings())
            
            # Map page size names to ReportLab constants
            page_size_map = {
                'A4': A4,
                'A3': A3, 
                'A5': A5,
                'Letter': letter,
                'Legal': legal,
                'Tabloid': tabloid
            }
            page_size = page_size_map.get(pdf_settings.page_size, A4)
            
            # Create document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=page_size,
                topMargin=pdf_settings.margins.get('top', 1.0) * inch,
                bottomMargin=pdf_settings.margins.get('bottom', 1.0) * inch,
                leftMargin=pdf_settings.margins.get('left', 1.0) * inch,
                rightMargin=pdf_settings.margins.get('right', 1.0) * inch
            )
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Create custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=pdf_settings.font_size + 4,
                spaceAfter=12,
                fontName=pdf_settings.font_family if hasattr(pdf_settings, 'font_family') else 'Helvetica-Bold'
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=pdf_settings.font_size,
                fontName=pdf_settings.font_family if hasattr(pdf_settings, 'font_family') else 'Helvetica'
            )
            
            # Build content
            story = []
            
            # Title
            title = data_object.get_display_name()
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12))
            
            # Add metadata if enabled
            if context.config.include_metadata:
                metadata_data = [
                    ['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                    ['Format', 'PDF'],
                    ['Source', getattr(context.config, 'source_info', 'Unknown')]
                ]
                
                metadata_table = Table(metadata_data, colWidths=[1.5*inch, 3*inch])
                metadata_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(metadata_table)
                story.append(Spacer(1, 20))
            
            # Content table
            content_data = []
            
            # Add header
            content_data.append(['Field', 'Value'])
            
            # Add data fields
            flat_data = data_object.get_flattened_data()
            for key, value in flat_data.items():
                # Convert complex values to strings
                if isinstance(value, (dict, list)):
                    import json
                    value_str = json.dumps(value, indent=2, default=str)
                else:
                    value_str = str(value) if value is not None else ''
                
                content_data.append([key, value_str])
            
            # Create content table
            content_table = Table(content_data, colWidths=[2*inch, 4*inch])
            content_table.setStyle(TableStyle([
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Data rows
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('VALIGN', (0, 1), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                
                # Grid
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(content_table)
            
            # Build PDF
            doc.build(story)
            
            self.logger.info(f"Generated PDF: {output_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Direct PDF generation failed: {str(e)}")
            return False
    
    def _export_with_template(self, data_object: DataObject, output_path: Path,
                             context: ExportContext) -> bool:
        """
        Generate PDF using a template (Word template converted to PDF).
        
        Args:
            data_object: Data object to export
            output_path: Output file path
            context: Export context
            
        Returns:
            True if successful
        """
        try:
            # First, try to create a Word document from template
            word_template_path = Path(context.config.template_file)
            
            if not word_template_path.exists():
                self.logger.error(f"Template file not found: {word_template_path}")
                return False
            
            # Create temporary Word file
            from ..utilities.file_utils_core import TemporaryFileManager
            temp_manager = TemporaryFileManager()
            temp_word_file = temp_manager.create_temp_file(suffix=".docx")
            
            try:
                # Generate Word document from template
                success = self._generate_word_from_template(
                    data_object, word_template_path, temp_word_file, context
                )
                
                if not success:
                    return False
                
                # Convert Word to PDF
                return self._convert_word_to_pdf(temp_word_file, output_path)
            
            finally:
                # Cleanup temporary file
                temp_manager.cleanup_temp_files()
        
        except Exception as e:
            self.logger.error(f"Template-based PDF generation failed: {str(e)}")
            return False
    
    def _generate_word_from_template(self, data_object: DataObject, 
                                   template_path: Path, output_path: Path,
                                   context: ExportContext) -> bool:
        """Generate Word document from template."""
        try:
            from docxtpl import DocxTemplate
            
            # Load template
            doc = DocxTemplate(str(template_path))
            
            # Prepare context data
            template_context = data_object.get_flattened_data()
            
            # Add metadata
            if context.config.include_metadata:
                template_context.update({
                    'generated_date': datetime.now().strftime('%Y-%m-%d'),
                    'generated_time': datetime.now().strftime('%H:%M:%S'),
                    'source': getattr(context.config, 'source_info', 'Unknown')
                })
            
            # Render template
            doc.render(template_context)
            
            # Save document
            doc.save(str(output_path))
            
            return True
        
        except ImportError:
            self.logger.error("docxtpl not available for template processing")
            return False
        except Exception as e:
            self.logger.error(f"Word template generation failed: {str(e)}")
            return False
    
    def _convert_word_to_pdf(self, word_path: Path, pdf_path: Path) -> bool:
        """Convert Word document to PDF."""
        try:
            # Try different conversion methods
            
            # Method 1: Use docx2pdf if available
            try:
                import docx2pdf
                docx2pdf.convert(str(word_path), str(pdf_path))
                self.logger.info(f"Converted Word to PDF using docx2pdf: {pdf_path}")
                return True
            except ImportError:
                self.logger.debug("docx2pdf not available")
            except Exception as e:
                self.logger.warning(f"docx2pdf conversion failed: {str(e)}")
            
            # Method 2: Use pypandoc if available
            try:
                import pypandoc
                pypandoc.convert_file(str(word_path), 'pdf', outputfile=str(pdf_path))
                self.logger.info(f"Converted Word to PDF using pypandoc: {pdf_path}")
                return True
            except ImportError:
                self.logger.debug("pypandoc not available")
            except Exception as e:
                self.logger.warning(f"pypandoc conversion failed: {str(e)}")
            
            # Method 3: Use python-docx to extract text and create PDF
            return self._extract_word_to_pdf(word_path, pdf_path)
        
        except Exception as e:
            self.logger.error(f"Word to PDF conversion failed: {str(e)}")
            return False
    
    def _extract_word_to_pdf(self, word_path: Path, pdf_path: Path) -> bool:
        """Extract text from Word and create simple PDF."""
        try:
            from docx import Document
            from reportlab.platypus import SimpleDocTemplate, Paragraph
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.pagesizes import letter
            
            # Read Word document
            doc = Document(str(word_path))
            
            # Extract text
            text_content = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content.append(paragraph.text)
            
            # Create PDF
            pdf_doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            for text in text_content:
                story.append(Paragraph(text, styles['Normal']))
            
            pdf_doc.build(story)
            
            self.logger.info(f"Extracted Word content to PDF: {pdf_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Word text extraction failed: {str(e)}")
            return False
    
    def get_export_capabilities(self) -> Dict[str, Any]:
        """Get PDF export capabilities."""
        capabilities = super().get_export_capabilities()
        
        capabilities.update({
            "template_support": True,
            "direct_generation": True,
            "page_sizes": ["A4", "A3", "A5", "Letter", "Legal", "Tabloid"],
            "font_support": True,
            "table_support": True,
            "image_support": False,  # Basic implementation
            "dependencies": {
                "required": ["reportlab"],
                "optional": ["docxtpl", "docx2pdf", "pypandoc", "python-docx"],
                "available": self.dependencies_available
            }
        })
        
        return capabilities


# Backward compatibility functions
def export_to_pdf(data_list: List[Dict[str, Any]], 
                 output_directory: Union[str, Path],
                 filename_key: Optional[str] = None,
                 template_file: Optional[str] = None,
                 **kwargs) -> List[Path]:
    """
    Backward compatibility function for PDF export.
    
    Args:
        data_list: List of data dictionaries
        output_directory: Output directory path
        filename_key: Key to use for filename generation
        template_file: Optional template file path
        **kwargs: Additional configuration options
        
    Returns:
        List of generated file paths
    """
    try:
        # Convert to new data structures
        data_objects = [DataObject(data) for data in data_list]
        data_collection = DataCollection(data_objects)
        
        # Create configuration
        config = DocumentConfig(
            output_format="pdf",
            filename_key=filename_key,
            template_file=template_file,
            include_metadata=kwargs.get('include_metadata', True)
        )
        
        # Set PDF-specific settings if provided
        if 'pdf_settings' in kwargs:
            config.pdf_settings = kwargs['pdf_settings']
        elif any(k.startswith('pdf_') for k in kwargs):
            # Extract PDF settings from kwargs
            pdf_settings = PDFSettings()
            if 'pdf_page_size' in kwargs:
                pdf_settings.page_size = kwargs['pdf_page_size']
            if 'pdf_font_size' in kwargs:
                pdf_settings.font_size = kwargs['pdf_font_size']
            if 'pdf_margins' in kwargs:
                pdf_settings.margins = kwargs['pdf_margins']
            config.pdf_settings = pdf_settings
        
        # Create exporter and export
        exporter = PDFExporter()
        results = exporter.export_collection(data_collection, config, Path(output_directory))
        
        # Extract successful file paths
        exported_files = []
        for result in results:
            if result.success:
                exported_files.extend(result.exported_files)
        
        return exported_files
    
    except Exception as e:
        logging.getLogger(__name__).error(f"PDF export failed: {str(e)}")
        return []


def check_pdf_requirements() -> bool:
    """Check if PDF export requirements are met."""
    exporter = PDFExporter()
    return exporter.dependencies_available


def get_missing_requirements() -> List[str]:
    """Get list of missing PDF export requirements."""
    exporter = PDFExporter()
    return exporter.missing_dependencies

"""
PDF export functionality for the Document Creator toolkit.

This module provides functions to export normalized data to PDF format,
supporting both direct PDF generation and template-based document creation.
"""

import tempfile
import os
import requests
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging
from datetime import datetime

# Optional imports for PDF generation
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Optional imports for Word-to-PDF conversion
try:
    from docx import Document
    from docxtpl import DocxTemplate
    from docx2pdf import convert
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

from .utils import (
    sanitize_filename,
    ensure_directory_exists,
    DocumentCreatorError,
    get_available_filename
)


class PDFExportError(DocumentCreatorError):
    """Exception for PDF export related errors."""
    pass


def export_to_pdf(
    data_list: List[Dict[str, Any]],
    output_directory: str,
    filename_key: Optional[str] = None,
    template_url: Optional[str] = None,
    template_path: Optional[str] = None,
    use_template: bool = False,
    pdf_title: Optional[str] = None,
    pdf_author: Optional[str] = None
) -> List[Path]:
    """
    Export a list of dictionaries to PDF format.
    
    Args:
        data_list: List of dictionaries to export
        output_directory: Directory to save PDF files
        filename_key: Key to use for filename generation
        template_url: URL to Word template for template-based export
        template_path: Path to local Word template
        use_template: Whether to use template-based export
        pdf_title: Title for generated PDFs
        pdf_author: Author for generated PDFs
        
    Returns:
        List of Path objects for created files
        
    Raises:
        PDFExportError: If export fails
    """
    try:
        # Validate requirements
        if use_template and not DOCX_AVAILABLE:
            raise PDFExportError("Template-based PDF export requires python-docx, docxtpl, and docx2pdf packages")
        
        if not use_template and not REPORTLAB_AVAILABLE:
            raise PDFExportError("Direct PDF export requires reportlab package")
        
        # Ensure output directory exists
        output_path = ensure_directory_exists(output_directory)
        
        # Validate input data
        if not isinstance(data_list, list):
            raise PDFExportError("Data must be a list of dictionaries")
        
        if not data_list:
            raise PDFExportError("No data provided for export")
        
        created_files = []
        
        # Choose export method
        if use_template:
            created_files = export_pdf_with_template(
                data_list,
                output_path,
                filename_key,
                template_url,
                template_path
            )
        else:
            created_files = export_pdf_direct(
                data_list,
                output_path,
                filename_key,
                pdf_title,
                pdf_author
            )
        
        return created_files
        
    except Exception as e:
        raise PDFExportError(f"Failed to export to PDF: {str(e)}")


def export_pdf_direct(
    data_list: List[Dict[str, Any]],
    output_path: Path,
    filename_key: Optional[str],
    pdf_title: Optional[str],
    pdf_author: Optional[str]
) -> List[Path]:
    """
    Export data to PDF using direct generation (ReportLab).
    
    Args:
        data_list: List of dictionaries to export
        output_path: Directory to save PDFs
        filename_key: Key to use for filename generation
        pdf_title: Title for generated PDFs
        pdf_author: Author for generated PDFs
        
    Returns:
        List of Path objects for created files
    """
    created_files = []
    
    for index, data_object in enumerate(data_list):
        if not isinstance(data_object, dict):
            logging.warning(f"Skipping non-dictionary item at index {index}")
            continue
        
        # Generate filename
        filename = generate_pdf_filename(data_object, filename_key, index)
        file_path = get_available_filename(output_path / filename, "pdf")
        
        # Create PDF content
        create_pdf_with_reportlab(
            data_object,
            file_path,
            pdf_title,
            pdf_author
        )
        
        created_files.append(file_path)
        logging.info(f"✅ Created: {file_path.name}")
    
    return created_files


def export_pdf_with_template(
    data_list: List[Dict[str, Any]],
    output_path: Path,
    filename_key: Optional[str],
    template_url: Optional[str],
    template_path: Optional[str]
) -> List[Path]:
    """
    Export data to PDF using Word template conversion.
    
    Args:
        data_list: List of dictionaries to export
        output_path: Directory to save PDFs
        filename_key: Key to use for filename generation
        template_url: URL to Word template
        template_path: Path to local Word template
        
    Returns:
        List of Path objects for created files
    """
    created_files = []
    
    # Get template
    if template_url:
        template_data = download_template(template_url)
    elif template_path:
        with open(template_path, 'rb') as f:
            template_data = f.read()
    else:
        raise PDFExportError("Either template_url or template_path must be provided")
    
    for index, data_object in enumerate(data_list):
        if not isinstance(data_object, dict):
            logging.warning(f"Skipping non-dictionary item at index {index}")
            continue
        
        # Generate filename
        filename = generate_pdf_filename(data_object, filename_key, index)
        file_path = get_available_filename(output_path / filename, "pdf")
        
        # Create PDF from template
        pdf_data = render_template_to_pdf(template_data, data_object)
        
        # Write PDF file
        with open(file_path, 'wb') as f:
            f.write(pdf_data)
        
        created_files.append(file_path)
        logging.info(f"✅ Created: {file_path.name}")
    
    return created_files


def generate_pdf_filename(
    data_object: Dict[str, Any],
    filename_key: Optional[str],
    index: int
) -> str:
    """
    Generate a filename for a PDF file based on data object.
    
    Args:
        data_object: Dictionary containing data
        filename_key: Key to use for filename generation
        index: Index of the object in the list
        
    Returns:
        Sanitized filename without extension
    """
    base_filename = None
    
    # Try to get filename from specified key
    if filename_key:
        base_filename = data_object.get(filename_key)
    
    # Try common fallback keys
    if not base_filename:
        fallback_keys = ["name", "title", "filename", "id"]
        for key in fallback_keys:
            if key in data_object and data_object[key]:
                base_filename = data_object[key]
                break
    
    # Use timestamp + index as final fallback
    if not base_filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"document_{timestamp}_{index + 1}"
    
    return sanitize_filename(str(base_filename))


def create_pdf_with_reportlab(
    data_object: Dict[str, Any],
    file_path: Path,
    title: Optional[str] = None,
    author: Optional[str] = None
) -> None:
    """
    Create a PDF file using ReportLab from a data object.
    
    Args:
        data_object: Dictionary containing data to include in PDF
        file_path: Path where PDF should be saved
        title: Title for the PDF document
        author: Author for the PDF document
    """
    doc = SimpleDocTemplate(str(file_path), pagesize=letter)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Build story (content elements)
    story = []
    
    # Add title
    if title:
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 12))
    
    # Add content sections
    for key, value in data_object.items():
        # Add section heading
        section_title = key.replace('_', ' ').title()
        story.append(Paragraph(section_title, heading_style))
        story.append(Spacer(1, 6))
        
        # Add content based on value type
        if isinstance(value, (dict, list)):
            # Format complex data as table or text
            if isinstance(value, dict) and len(value) <= 10:
                # Create table for small dictionaries
                table_data = [[k, str(v)] for k, v in value.items()]
                table = Table(table_data, colWidths=[2*inch, 4*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(table)
            else:
                # Format as preformatted text
                import json
                formatted_text = json.dumps(value, indent=2, ensure_ascii=False)
                # Split into lines and create paragraphs
                lines = formatted_text.split('\n')
                for line in lines:
                    story.append(Paragraph(line, normal_style))
        else:
            # Simple values
            story.append(Paragraph(str(value), normal_style))
        
        story.append(Spacer(1, 12))
    
    # Build PDF
    doc.build(story)


def download_template(template_url: str) -> bytes:
    """
    Download a Word template from URL.
    
    Args:
        template_url: URL to the Word template
        
    Returns:
        Template data as bytes
        
    Raises:
        PDFExportError: If template cannot be downloaded
    """
    try:
        response = requests.get(template_url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        raise PDFExportError(f"Failed to download template: {str(e)}")


def render_template_to_pdf(
    template_data: bytes,
    data_object: Dict[str, Any],
    opening_delimiter: str = "{{",
    closing_delimiter: str = "}}",
    use_docxtpl: bool = True
) -> bytes:
    """
    Render a Word template with data and convert to PDF.
    
    Args:
        template_data: Word template data as bytes
        data_object: Dictionary containing data for template
        opening_delimiter: Opening delimiter for template variables
        closing_delimiter: Closing delimiter for template variables
        use_docxtpl: Whether to use docxtpl for advanced templating
        
    Returns:
        PDF data as bytes
        
    Raises:
        PDFExportError: If template rendering fails
    """
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save template
            template_path = temp_path / "template.docx"
            with open(template_path, 'wb') as f:
                f.write(template_data)
            
            # Render template
            if use_docxtpl:
                doc = DocxTemplate(str(template_path))
                doc.render(data_object)
                rendered_path = temp_path / "rendered.docx"
                doc.save(str(rendered_path))
            else:
                # Simple variable replacement
                doc = Document(str(template_path))
                for paragraph in doc.paragraphs:
                    for key, value in data_object.items():
                        placeholder = f"{opening_delimiter}{key}{closing_delimiter}"
                        if placeholder in paragraph.text:
                            paragraph.text = paragraph.text.replace(placeholder, str(value))
                
                rendered_path = temp_path / "rendered.docx"
                doc.save(str(rendered_path))
            
            # Convert to PDF
            pdf_path = temp_path / "output.pdf"
            convert(str(rendered_path), str(pdf_path))
            
            # Read PDF data
            with open(pdf_path, 'rb') as f:
                return f.read()
                
    except Exception as e:
        raise PDFExportError(f"Failed to render template to PDF: {str(e)}")


def check_pdf_requirements() -> Dict[str, bool]:
    """
    Check which PDF export features are available.
    
    Returns:
        Dictionary indicating which features are available
    """
    return {
        'direct_pdf': REPORTLAB_AVAILABLE,
        'template_pdf': DOCX_AVAILABLE,
        'reportlab': REPORTLAB_AVAILABLE,
        'docx': DOCX_AVAILABLE
    }


def get_missing_requirements() -> List[str]:
    """
    Get list of missing packages for PDF export.
    
    Returns:
        List of missing package names
    """
    missing = []
    
    if not REPORTLAB_AVAILABLE:
        missing.append('reportlab')
    
    if not DOCX_AVAILABLE:
        missing.extend(['python-docx', 'docxtpl', 'docx2pdf'])
    
    return missing

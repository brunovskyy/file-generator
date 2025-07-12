# === REQUIRED LIBRARIES ===
import requests
from docx import Document
import tempfile
import os
from docx2pdf import convert
from input_parser import parse_input_data

# Import docxtpl for advanced templating
from docxtpl import DocxTemplate

# === CONFIGURABLE INPUT PARAMETERS ===

# Public URL to the Word .docx template
TEMPLATE_URL = "https://zazsgfgfbnhymwnbuwvq.supabase.co/storage/v1/object/sign/document-templates/wowow.docx?token=eyJraWQiOiJzdG9yYWdlLXVybC1zaWduaW5nLWtleV8xMDJjODcxNy1mMGFiLTQzYmMtOTdiNy1kNzViYjZiODdkMjEiLCJhbGciOiJIUzI1NiJ9.eyJ1cmwiOiJkb2N1bWVudC10ZW1wbGF0ZXMvd293b3cuZG9jeCIsImlhdCI6MTc1MjIwMzQ5NSwiZXhwIjoxNzUyODA4Mjk1fQ.DAj1t6IrjhXVxXGpp_11ADb3QwDD24R0B7X2u4EWyPo"

# Dictionary of variable placeholders and their replacement values
DOCUMENT_VARIABLE_VALUES = [{
    "name": "Pineda Industries",
    "description": "Bruno Pineda",
    "products": [
        {"product_name": "Widget A", "price": 100},
        {"product_name": "Widget B", "price": 200}
    ]
},
{
    "name": "Tech Solutions",
    "description": "Alice Johnson",
    "products": [
        {"product_name": "Widget C", "price": 300}
    ]
}]
# Delimiters used in the Word template (e.g., {{company_name}})
OPENING_DELIMITER = "{{"
CLOSING_DELIMITER = "}}"
# Desired output file type: either 'pdf' or 'docx'
OUTPUT_EXTENSION = "pdf"

# === MAIN FUNCTION ===

def render_template_from_url(
    template_url: str,
    placeholders: dict,
    opening_delimiter: str = "{{",
    closing_delimiter: str = "}}",
    output_extension: str = "docx",  # Can be "docx" or "pdf"
    use_docxtpl: bool = True         # Switch between python-docx and docxtpl
) -> bytes:
    """
    Downloads a Word template from a URL, replaces all placeholders using the provided values,
    and returns the final document as bytes (in .pdf or .docx format).

    Parameters:
        template_url (str): Direct URL to the Word .docx template.
        placeholders (dict): Key-value pairs to replace in the document.
        opening_delimiter (str): Start tag for placeholders (e.g., '{{').
        closing_delimiter (str): End tag for placeholders (e.g., '}}').
        output_extension (str): Desired output format: 'pdf' or 'docx'.
        use_docxtpl (bool): If True, use docxtpl for advanced templating (supports loops).

    Returns:
        bytes: The rendered file in the chosen format (to be saved, returned via API, etc.)
    """
    # Step 1: Download the Word .docx file from the URL
    print("Starting template download...")
    template_response = requests.get(template_url)
    print(f"Download response status code: {template_response.status_code}")

    if template_response.status_code != 200:
        raise Exception(f"Error downloading template. Status code: {template_response.status_code}")

    print("Template downloaded successfully.")

    # Step 2: Create a temporary folder to work in
    with tempfile.TemporaryDirectory() as temporary_folder_path:
        print(f"Temporary folder created at: {temporary_folder_path}")

        downloaded_template_path = os.path.join(temporary_folder_path, "template.docx")
        with open(downloaded_template_path, "wb") as template_file:
            template_file.write(template_response.content)
        print(f"Template saved to: {downloaded_template_path}")

        # Step 3: Render the template using docxtpl or python-docx
        if use_docxtpl:
            # --- DOCXTPL LOGIC ---
            # Load the template with DocxTemplate
            doc = DocxTemplate(downloaded_template_path)
            print("Template loaded into DocxTemplate object.")

            # Render the template with the provided context (supports loops and conditionals)
            doc.render(placeholders)
            print("Template rendered with docxtpl.")

            # Save the rendered document
            updated_docx_path = os.path.join(temporary_folder_path, "updated_output.docx")
            doc.save(updated_docx_path)
            print(f"Rendered document saved at: {updated_docx_path}")

        else:
            # --- PYTHON-DOCX LOGIC (simple variable replacement only) ---
            document = Document(downloaded_template_path)
            print("Template loaded into Document object.")

            replaced_any = False
            for paragraph in document.paragraphs:
                for key, value in placeholders.items():
                    placeholder_pattern = f"{opening_delimiter}{key}{closing_delimiter}"
                    if placeholder_pattern in paragraph.text:
                        print(f"Replacing placeholder '{placeholder_pattern}' with '{value}' in paragraph: '{paragraph.text}'")
                        paragraph.text = paragraph.text.replace(placeholder_pattern, str(value))
                        replaced_any = True

            if not replaced_any:
                print("No placeholders were replaced in the document.")

            updated_docx_path = os.path.join(temporary_folder_path, "updated_output.docx")
            document.save(updated_docx_path)
            print(f"Updated document saved at: {updated_docx_path}")

        # Step 4: Return as PDF or DOCX
        if output_extension == "pdf":
            output_pdf_path = os.path.join(temporary_folder_path, "final_output.pdf")
            print("Starting conversion to PDF...")
            convert(updated_docx_path, output_pdf_path)
            print(f"PDF generated at: {output_pdf_path}")

            with open(output_pdf_path, "rb") as final_pdf_file:
                pdf_bytes = final_pdf_file.read()
            print("PDF read into memory.")
            return pdf_bytes

        elif output_extension == "docx":
            with open(updated_docx_path, "rb") as final_docx_file:
                docx_bytes = final_docx_file.read()
            print("DOCX read into memory.")
            return docx_bytes

        else:
            raise ValueError("Invalid output_extension. Must be 'pdf' or 'docx'.")

# === TESTING / EXAMPLE USAGE ===

if __name__ == "__main__":
    print("Running main example usage...")

    try:
        if OUTPUT_EXTENSION not in ("pdf", "docx"):
            raise ValueError("OUTPUT_EXTENSION must be 'pdf' or 'docx'.")

        data_list = parse_input_data(DOCUMENT_VARIABLE_VALUES)

        OUTPUT_DIR = "./output"
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        for idx, placeholders in enumerate(data_list):
            rendered_file_bytes = render_template_from_url(
                template_url=TEMPLATE_URL,
                placeholders=placeholders,
                opening_delimiter=OPENING_DELIMITER,
                closing_delimiter=CLOSING_DELIMITER,
                output_extension=OUTPUT_EXTENSION,
                use_docxtpl=True  # Set to False to use python-docx logic
            )

            base_filename = f"generated_output_{idx+1}.{OUTPUT_EXTENSION}" if len(data_list) > 1 else f"generated_output.{OUTPUT_EXTENSION}"
            output_filename = os.path.join(OUTPUT_DIR, base_filename)
            file_counter = 1
            while os.path.exists(output_filename):
                output_filename = os.path.join(
                    OUTPUT_DIR, f"generated_output_{idx+1}_{file_counter}.{OUTPUT_EXTENSION}"
                )
                file_counter += 1

            with open(output_filename, "wb") as output_file:
                output_file.write(rendered_file_bytes)

            print(f"✅ File generated: {output_filename}")

    except Exception as exception:
        print(f"❌ An error occurred: {exception}")
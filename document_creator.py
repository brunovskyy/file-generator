# === REQUIRED LIBRARIES ===
import requests
from docx import Document
import tempfile
import os
from docx2pdf import convert
from input_parser import parse_input_data

# === CONFIGURABLE INPUT PARAMETERS ===

# Public URL to the Word .docx template
TEMPLATE_URL = "https://zazsgfgfbnhymwnbuwvq.supabase.co/storage/v1/object/sign/document-templates/TEST%20Order%20Form%20-%20DASA%202025.docx?token=eyJraWQiOiJzdG9yYWdlLXVybC1zaWduaW5nLWtleV8xMDJjODcxNy1mMGFiLTQzYmMtOTdiNy1kNzViYjZiODdkMjEiLCJhbGciOiJIUzI1NiJ9.eyJ1cmwiOiJkb2N1bWVudC10ZW1wbGF0ZXMvVEVTVCBPcmRlciBGb3JtIC0gREFTQSAyMDI1LmRvY3giLCJpYXQiOjE3NTIwNzg1MzEsImV4cCI6MTc1MjY4MzMzMX0.dzYaZ6WPMvVxW3UC_khMhUlFr4Lq4pBhrFXXbRARR-c"
# Dictionary of variable placeholders and their replacement values
DOCUMENT_VARIABLE_VALUES = [{
    "name": "Pineda Industries",
    "description": "Bruno Pineda"
},
{
    "name": "Tech Solutions",
    "description": "Alice Johnson"
}]
# Delimiters used in the Word template (e.g., {{company_name}})
OPENING_DELIMITER = "{{"
CLOSING_DELIMITER = "}}"
# Desired output file type: either 'pdf' or 'docx'
OUTPUT_EXTENSION = "pdf"

# === MAIN FUNCTION ===

print("File is being executed")

def render_template_from_url(
    template_url: str,
    placeholders: dict,
    opening_delimiter: str = "{{",
    closing_delimiter: str = "}}",
    output_extension: str = "docx"  # Can be "docx" or "pdf"
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

    Returns:
        bytes: The rendered file in the chosen format (to be saved, returned via API, etc.)
    """
    # Step 1: Download the Word .docx file from the URL
    print("Starting template download...")
    template_response = requests.get(template_url)
    
    # Return Fetch Status Code for Debugging
    print(f"Download response status code: {template_response.status_code}")

    # Download Failure
    if template_response.status_code != 200:
        raise Exception(f"Error downloading template. Status code: {template_response.status_code}")

    # Download Success
    print("Template downloaded successfully.")

    # Step 2: Create a temporary folder to work in
    # This ensures that all intermediate files are cleaned up automatically.
    with tempfile.TemporaryDirectory() as temporary_folder_path:
        print(f"Temporary folder created at: {temporary_folder_path}")

        ## Save Downloaded File
        # Construct the full path for the downloaded template within the temporary folder.
        downloaded_template_path = os.path.join(temporary_folder_path, "template.docx")
        # Write the content of the downloaded template to the specified path in binary write mode.
        with open(downloaded_template_path, "wb") as template_file:
            template_file.write(template_response.content)
        print(f"Template saved to: {downloaded_template_path}")

        # Step 3: Load the .docx file into memory
        # Use the python-docx library to open and parse the Word document.
        document = Document(downloaded_template_path)
        print("Template loaded into Document object.")

        # Step 4: Replace placeholders in each paragraph
        replaced_any = False
        # Iterate through each paragraph in the document to find and replace placeholders.
        for paragraph in document.paragraphs:
            # Iterate through each key-value pair provided in the placeholders dictionary.
            for key, value in placeholders.items():
                # Construct the placeholder pattern using the specified delimiters.
                placeholder_pattern = f"{opening_delimiter}{key}{closing_delimiter}"
                # Check if the current paragraph's text contains the placeholder pattern.
                if placeholder_pattern in paragraph.text:
                    print(f"Replacing placeholder '{placeholder_pattern}' with '{value}' in paragraph: '{paragraph.text}'")
                    # Replace all occurrences of the placeholder with its corresponding value.
                    paragraph.text = paragraph.text.replace(placeholder_pattern, value)
                    replaced_any = True

        # Inform if no placeholders were found and replaced.
        if not replaced_any:
            print("No placeholders were replaced in the document.")

        # Step 5: Save the updated .docx file
        # Construct the path for the modified document within the temporary folder.
        updated_docx_path = os.path.join(temporary_folder_path, "updated_output.docx")
        # Save the modified Document object back to a .docx file.
        document.save(updated_docx_path)
        print(f"Updated document saved at: {updated_docx_path}")

        # Step 6: Return as PDF or DOCX
        # Check the desired output format specified by the user.
        if output_extension == "pdf":
            # Convert to PDF using docx2pdf
            # Construct the path for the output PDF file.
            output_pdf_path = os.path.join(temporary_folder_path, "final_output.pdf")
            print("Starting conversion to PDF...")
            # Use the docx2pdf library to convert the updated DOCX to PDF.
            convert(updated_docx_path, output_pdf_path)
            print(f"PDF generated at: {output_pdf_path}")

            # Read PDF file as bytes
            # Open the generated PDF file in binary read mode.
            with open(output_pdf_path, "rb") as final_pdf_file:
                # Read the entire content of the PDF file into a bytes object.
                pdf_bytes = final_pdf_file.read()
            print("PDF read into memory.")
            # Return the PDF content as bytes.
            return pdf_bytes

        elif output_extension == "docx":
            # Read updated DOCX file as bytes
            # Open the updated DOCX file in binary read mode.
            with open(updated_docx_path, "rb") as final_docx_file:
                # Read the entire content of the DOCX file into a bytes object.
                docx_bytes = final_docx_file.read()
            print("DOCX read into memory.")
            # Return the DOCX content as bytes.
            return docx_bytes

        else:
            # Raise an error if an unsupported output extension is provided.
            raise ValueError("Invalid output_extension. Must be 'pdf' or 'docx'.")


# === TESTING / EXAMPLE USAGE ===

# This block executes only when the script is run directly (not imported as a module).
if __name__ == "__main__":
    print("Running main example usage...")

    try:
        # Validate output extension
        if OUTPUT_EXTENSION not in ("pdf", "docx"):
            raise ValueError("OUTPUT_EXTENSION must be 'pdf' or 'docx'.")

        # Process input data (can be dict, list of dicts, or csv file)
        data_list = parse_input_data(DOCUMENT_VARIABLE_VALUES)  # Set DOCUMENT_VARIABLE_VALUES with your input data

        OUTPUT_DIR = "./output"
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        for idx, placeholders in enumerate(data_list):
            rendered_file_bytes = render_template_from_url(
                template_url=TEMPLATE_URL,
                placeholders=placeholders,
                opening_delimiter=OPENING_DELIMITER,
                closing_delimiter=CLOSING_DELIMITER,
                output_extension=OUTPUT_EXTENSION
            )

            # Generate a unique filename
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
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from scripts.document_creator import render_template_from_url  # Import your function

app = FastAPI()

class DocumentRequest(BaseModel):
    template_url: str
    placeholders: dict
    opening_delimiter: str = "{{"
    closing_delimiter: str = "}}"
    output_extension: str = "docx"

# Curl Example
# curl -X POST "http://localhost:8000/create-document" ^
#   -H "Content-Type: application/json" ^
#   -d "{\"template_url\": \"https://example.com/template.docx\", \"placeholders\": {\"name\": \"John Doe\", \"date\": \"2025-07-09\"}, \"opening_delimiter\": \"{{\", \"closing_delimiter\": \"}}\", \"output_extension\": \"docx\"}" ^
#   --output result.docx


# Example JSON Body
# {
#  "template_url": "https://example.com/template.docx",
#  "placeholders": {
#   "name": "John Doe",
#   "date": "2025-07-09"
#  },
#  "opening_delimiter": "{{",
#  "closing_delimiter": "}}",
#  "output_extension": "docx"
# }

@app.post("/create-document")
def create_document(req: DocumentRequest):
    try:
        result_bytes = render_template_from_url(
            template_url=req.template_url,
            placeholders=req.placeholders,
            opening_delimiter=req.opening_delimiter,
            closing_delimiter=req.closing_delimiter,
            output_extension=req.output_extension
        )
        # Return as a file response
        from fastapi.responses import Response
        media_type = "application/pdf" if req.output_extension == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        return Response(content=result_bytes, media_type=media_type)
    except Exception as exception:
        raise HTTPException(status_code=400, detail=str(exception))
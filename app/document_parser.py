# app/document_parser.py
import pypdf
import docx
import io
from .utils import chunk_text

def parse_document(file_content: bytes, filename: str) -> list[str]:
    """Parses a document (PDF or DOCX) from its byte content and returns text chunks."""
    text = ""
    file_extension = filename.split('.')[-1].lower()
    
    # Create an in-memory file-like object from the byte content
    file_stream = io.BytesIO(file_content)

    if file_extension == 'pdf':
        try:
            reader = pypdf.PdfReader(file_stream)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            raise ValueError(f"Error parsing PDF file: {e}")

    elif file_extension == 'docx':
        try:
            doc = docx.Document(file_stream)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            raise ValueError(f"Error parsing DOCX file: {e}")
            
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")

    if not text.strip():
        raise ValueError("Could not extract any text from the document.")

    return chunk_text(text)
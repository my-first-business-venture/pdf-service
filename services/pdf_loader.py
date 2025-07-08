from PyPDF2 import PdfReader
from config import FILE_PATH

def load_pdf_content() -> str:
    with open(FILE_PATH, "rb") as f:
        reader = PdfReader(f)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

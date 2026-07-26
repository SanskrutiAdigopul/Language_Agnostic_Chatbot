import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import os

# Point to your Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Path to Poppler binaries (used by pdf2image)
POPPLER_PATH = r"C:\Program Files\poppler-25.07.0\Library\bin"

# Supported languages for OCR (adjust as needed)
MULTILINGUAL_LANGS = "eng+hin+mar+guj+tam+tel+ben+kan+mal+pan+urd"

def extract_text_from_pdf(file_path: str, lang: str = MULTILINGUAL_LANGS) -> str:
    """Extract text from a PDF file using pdfplumber and fallback to OCR if needed."""
    text = ""

    # Try pdfplumber first (for softcopy PDFs)
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    # If no text found, fallback to OCR (for scanned PDFs)
    if not text.strip():
        images = convert_from_path(file_path, poppler_path=POPPLER_PATH)
        for img in images:
            text += pytesseract.image_to_string(img, lang=lang)

    return text.strip()

def chunk_text(text: str, max_tokens: int = 300, overlap: int = 50):
    """Split text into overlapping chunks for embeddings."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + max_tokens
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap
    return chunks
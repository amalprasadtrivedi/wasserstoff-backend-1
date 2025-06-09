import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import fitz  # PyMuPDF
import os
import tempfile

SUPPORTED_IMAGE_TYPES = ('.png', '.jpg', '.jpeg')


def extract_text(file_path: str) -> str:
    """
    Extracts text from a PDF or image file.
    Automatically applies OCR if necessary.
    """
    ext = os.path.splitext(file_path)[1].lower()
    text = ""

    try:
        if ext == ".pdf":
            text = extract_from_pdf(file_path)
        elif ext in SUPPORTED_IMAGE_TYPES:
            text = extract_from_image(file_path)
        else:
            print(f"[ERROR] Unsupported file type: {ext}")
    except Exception as e:
        print(f"[ERROR] Failed to extract text: {e}")

    return text


def extract_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.
    Tries normal text extraction first, falls back to OCR if needed.
    """
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()

        if not text.strip():  # If no text, fallback to OCR
            print("[INFO] Falling back to OCR for scanned PDF.")
            text = ocr_pdf(file_path)
    except Exception as e:
        print(f"[ERROR] PDF extraction failed: {e}")
    return text


def ocr_pdf(file_path: str) -> str:
    """
    Use OCR to extract text from scanned PDF pages (images).
    """
    text = ""
    try:
        images = convert_from_path(file_path)
        for img in images:
            text += pytesseract.image_to_string(img)
    except Exception as e:
        print(f"[ERROR] OCR for PDF failed: {e}")
    return text


def extract_from_image(file_path: str) -> str:
    """
    OCR text extraction from image files (PNG, JPG, JPEG).
    """
    text = ""
    try:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
    except Exception as e:
        print(f"[ERROR] Image OCR failed: {e}")
    return text

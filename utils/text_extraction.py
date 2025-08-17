import os
import re
import io
import zipfile
from typing import Optional
from collections import Counter

# PDF / image OCR libraries
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import docx2txt

# Configure these if your binaries are in nonstandard places
# (You can set environment variables TESSERACT_CMD and POPPLER_PATH)
utils_dir = os.path.dirname(__file__)
TESSERACT_CMD = os.environ.get("TESSERACT_CMD", os.path.abspath(os.path.join(utils_dir, "Tesseract-OCR", "tesseract.exe")))
POPPLER_PATH = os.environ.get("POPPLER_PATH", os.path.abspath(os.path.join(utils_dir, "poppler", "poppler-24.08.0", "Library", "bin")))

# Add Poppler to PATH for pdf2image
if os.path.exists(POPPLER_PATH) and POPPLER_PATH not in os.environ['PATH']:
    os.environ['PATH'] += os.pathsep + POPPLER_PATH

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

# Verify paths exist
if not os.path.exists(TESSERACT_CMD):
    print(f"Warning: Tesseract not found at {TESSERACT_CMD}")
if not os.path.exists(POPPLER_PATH):
    print(f"Warning: Poppler not found at {POPPLER_PATH}")


def _remove_headers_footers(text: str, min_occurrences: int = 2) -> str:
    lines = [l.rstrip() for l in text.splitlines() if l.strip()]
    counts = Counter(lines)
    repeated = {line for line, c in counts.items() if c >= min_occurrences}

    pages = text.split('\f') if '\f' in text else [text]
    out_lines = []
    for page in pages:
        page_lines = [ln for ln in page.splitlines()]
        # strip repeated headers from top
        while page_lines and page_lines[0].strip() in repeated:
            page_lines.pop(0)
        # strip repeated footers from bottom
        while page_lines and page_lines[-1].strip() in repeated:
            page_lines.pop()
        out_lines.extend(page_lines)
        out_lines.append("")  # page separator
    return "\n".join(out_lines).strip()


def _normalize_line_breaks(text: str) -> str:
    # join hyphenated words split across lines, collapse excess whitespace
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)
    # combine lines that are not headings (if next line starts lowercase)
    text = re.sub(r'\n(?=[a-z0-9\(\[] )', ' ', text)
    text = re.sub(r'\n{2,}', '\n\n', text)
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return text.strip()


def _remove_page_numbers(text: str) -> str:
    lines = text.splitlines()
    filtered = [l for l in lines if not re.match(r'^\s*(page\s*)?\d+(\s*of\s*\d+)?\s*$', l, re.I)]
    return "\n".join(filtered)


def _clean_artifacts(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\x00", " ")
    # remove many non-printable / weird unicode (keep typical punctuation)
    text = re.sub(r"[^\x09\x0A\x0D\x20-\x7E]+", " ", text)
    # collapse whitespace
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_text(text: str) -> str:
    """Run full cleaning pipeline."""
    if not text:
        return ""
    text = _remove_headers_footers(text)
    text = _remove_page_numbers(text)
    text = _normalize_line_breaks(text)
    text = _clean_artifacts(text)
    return text


def _ocr_pdf(file_path: str, dpi: int = 300) -> str:
    text = ""
    try:
        images = convert_from_path(file_path, poppler_path=POPPLER_PATH, dpi=dpi)
    except Exception as e:
        # Best-effort: if convert_from_path fails, return empty
        print(f"[text_extraction] OCR PDF failed: {e}")
        text = ""
    return text


def _extract_text_from_docx_images(file_path: str) -> str:
    text = ""
    with zipfile.ZipFile(file_path, 'r') as z:
        for name in z.namelist():
            if name.startswith('word/media/') and name.lower().endswith(('.png', '.jpg', '.jpeg')):
                data = z.read(name)
                try:
                    img = Image.open(io.BytesIO(data))
                    text += pytesseract.image_to_string(img) + "\n"
                except Exception:
                    continue
    return text


def extract_text(file_path: str) -> Optional[str]:
    """
    Universal text extractor:
      - PDF: use pdfplumber; if result empty fallback to OCR
      - DOCX: use docx2txt; if empty fallback to OCR of embedded images
    Returns cleaned text (never None — returns empty string when extraction fails).
    """
    if not file_path or not file_path.strip():
        raise ValueError("Empty file path provided")
        
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    raw = ""

    try:
        if ext == ".pdf":
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text() or ""
                        raw += page_text + "\n"
            except Exception as e:
                print(f"[text_extraction] pdfplumber failed: {e}; will try OCR fallback.")
                raw = ""

            if not raw.strip():
                raw = _ocr_pdf(file_path)

        elif ext == ".docx":
            try:
                raw = docx2txt.process(file_path) or ""
            except Exception as e:
                print(f"[text_extraction] docx2txt failed: {e}")
                raw = ""

            if not raw.strip():
                raw = _extract_text_from_docx_images(file_path)

        else:
            raise ValueError("Unsupported file type. Use .pdf or .docx")
    except Exception as e:
        print(f"[text_extraction] Unexpected extraction error: {e}")
        raw = ""

    cleaned = clean_text(raw)
    return cleaned
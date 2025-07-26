import pdfplumber
import docx2txt
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from pdf2image import convert_from_path
from PIL import Image
import os
import zipfile
import io
import re
from collections import Counter

def remove_headers_footers(text, min_occurrences=2):
    lines = text.splitlines()
    line_counts = Counter(line.strip() for line in lines if line.strip())
    repeated_lines = {line for line, count in line_counts.items() if count >= min_occurrences}

    cleaned_lines = []
    page_separator = '\f'

    pages = text.split(page_separator) if page_separator in text else [text]

    for page in pages:
        page_lines = page.splitlines()
        while page_lines and page_lines[0].strip() in repeated_lines:
            page_lines.pop(0)
        while page_lines and page_lines[-1].strip() in repeated_lines:
            page_lines.pop()
        cleaned_lines.extend(page_lines)
        cleaned_lines.append('')

    return '\n'.join(cleaned_lines).strip()

def normalize_line_breaks(text):
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    text = re.sub(r'\n(?=[a-z])', ' ', text)
    text = re.sub(r'\n{2,}', '\n\n', text)
    text = '\n'.join(line.rstrip() for line in text.splitlines())
    return text.strip()

def remove_page_numbers(text):
    lines = text.splitlines()
    filtered = [line for line in lines if not re.match(r'^\s*(Page\s*)?\d+(\s*of\s*\d+)?\s*$', line, re.IGNORECASE)]
    return '\n'.join(filtered)

def clean_text(text):
    text = remove_headers_footers(text)
    text = remove_page_numbers(text)
    text = normalize_line_breaks(text)
    return text

# --- Extraction functions ---

def extract_text_from_pdf(file_path):
    text = ''
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'

        if not text.strip():
            print("No text found in PDF. Trying OCR...")
            images = convert_from_path(file_path, poppler_path=r"C:\poppler\poppler-24.08.0\Library\bin")
            for image in images:
                ocr_text = pytesseract.image_to_string(image)
                text += ocr_text + '\n'

    except Exception as e:
        print(f"Error processing PDF: {e}")
    return text

def extract_text_from_docx(file_path):
    text = ''
    try:
        text = docx2txt.process(file_path).strip()

        if not text:
            # print("No text found in DOCX. Trying OCR on images...")
            with zipfile.ZipFile(file_path, 'r') as docx_zip:
                for file_name in docx_zip.namelist():
                    if file_name.startswith('word/media/') and file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                        image_data = docx_zip.read(file_name)
                        image = Image.open(io.BytesIO(image_data))
                        ocr_text = pytesseract.image_to_string(image)
                        text += ocr_text + '\n'

    except Exception as e:
        print(f"Error processing DOCX: {e}")
    return text
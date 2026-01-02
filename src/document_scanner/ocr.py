from pathlib import Path
from typing import Optional

import pdfplumber
import pytesseract
from PIL import Image


def extract_text_from_image(path: Path, language: str = "deu", tesseract_cmd: Optional[str] = None) -> str:
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    image = Image.open(path)
    return pytesseract.image_to_string(image, lang=language)


def pdf_to_images(path: Path, max_pages: int = 5) -> list[Image.Image]:
    images: list[Image.Image] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages[:max_pages]:
            images.append(page.to_image(resolution=300).original)
    return images


def extract_text_from_pdf(path: Path, language: str = "deu", tesseract_cmd: Optional[str] = None) -> str:
    text_parts: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    text = "\n".join(text_parts).strip()
    if text:
        return text
    images = pdf_to_images(path)
    ocr_results = [pytesseract.image_to_string(img, lang=language) for img in images]
    return "\n".join(ocr_results)

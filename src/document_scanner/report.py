from io import BytesIO
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter

from .models import ExtractedData


A4_SIZE = (2480, 3508)  # 300dpi


def _draw_text_block(draw: ImageDraw.ImageDraw, text: str, position: tuple[int, int], max_width: int, line_height: int = 40):
    x, y = position
    words = text.split()
    line = []
    for word in words:
        test_line = " ".join(line + [word])
        if draw.textlength(test_line) > max_width:
            draw.text((x, y), " ".join(line), fill="black")
            y += line_height
            line = [word]
        else:
            line.append(word)
    if line:
        draw.text((x, y), " ".join(line), fill="black")


def build_report_page(data: ExtractedData, source_name: str) -> BytesIO:
    image = Image.new("RGB", A4_SIZE, color="white")
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.load_default()
    draw.text((80, 60), "Scan Report", fill="black", font=title_font)
    draw.text((80, 120), f"Quelle: {source_name}", fill="black")
    draw.text((80, 180), "Summary:", fill="black")
    summary_text = "\n".join(f"- {item}" for item in data.summary)
    _draw_text_block(draw, summary_text, (120, 220), max_width=2200)

    y = 520
    fields = {
        "Dokumenttyp": data.document_type,
        "Absender": data.issuer,
        "Dokumentdatum": data.document_date.isoformat() if data.document_date else "unbekannt",
        "Betrag": f"{data.amount_total or 0:.2f} {data.currency}",
        "Faellig": data.due_date.isoformat() if data.due_date else "-",
        "IBAN": data.iban or "-",
        "Referenz": data.invoice_number or "-",
        "Steuerrelevant": "Ja" if data.is_tax_relevant else "Nein",
        "Kategorie": data.tax_category or "-",
    }
    for key, value in fields.items():
        draw.text((80, y), f"{key}: {value}", fill="black")
        y += 60
    draw.text((80, y + 40), "Original folgt auf den naechsten Seiten.", fill="black")

    buffer = BytesIO()
    image.save(buffer, format="PDF")
    buffer.seek(0)
    return buffer


def merge_report_with_original(report: BytesIO, original_path: Path) -> BytesIO:
    writer = PdfWriter()
    report_reader = PdfReader(report)
    for page in report_reader.pages:
        writer.add_page(page)

    original_reader = PdfReader(str(original_path))
    for page in original_reader.pages:
        writer.add_page(page)

    output = BytesIO()
    writer.write(output)
    output.seek(0)
    return output

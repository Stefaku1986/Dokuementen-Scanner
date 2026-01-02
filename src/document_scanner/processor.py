import json
import logging
import os
from datetime import datetime, time
from pathlib import Path
from typing import Optional

from jsonschema import validate

from .config import ScannerConfig
from .file_naming import build_filename, ensure_unique
from .graph import GraphClient
from .llm_client import LLMExtractor, parse_date
from .models import ExtractedData
from .ocr import extract_text_from_image, extract_text_from_pdf
from .report import build_report_page, merge_report_with_original

logger = logging.getLogger(__name__)


class DocumentProcessor:
    def __init__(self, cfg: ScannerConfig, schema_path: Path):
        self.cfg = cfg
        self.schema_path = schema_path
        self.schema = json.loads(schema_path.read_text(encoding="utf-8"))

    def _extract_text(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix in {".png", ".jpg", ".jpeg", ".tiff"}:
            return extract_text_from_image(
                path,
                language=self.cfg.ocr.language,
                tesseract_cmd=self.cfg.ocr.tesseract_cmd,
            )
        if suffix == ".pdf":
            return extract_text_from_pdf(
                path,
                language=self.cfg.ocr.language,
                tesseract_cmd=self.cfg.ocr.tesseract_cmd,
            )
        raise ValueError(f"Nicht unterstütztes Format: {suffix}")

    def _llm_extract(self, text: str) -> ExtractedData:
        if not self.cfg.llm.enabled:
            logger.warning("LLM deaktiviert, nutze Minimalwerte")
            return ExtractedData(
                document_type="Sonstiges",
                issuer="Unbekannt",
                document_date=None,
                amount_total=None,
                currency="EUR",
                due_date=None,
                iban=None,
                invoice_number=None,
                is_tax_relevant=False,
                tax_category=None,
                summary=[text[:200]],
            )
        api_key = os.environ.get(self.cfg.llm.api_key_env)
        if not api_key:
            raise RuntimeError("LLM aktiviert aber kein API-Key gefunden")
        extractor = LLMExtractor(
            api_key=api_key,
            model=self.cfg.llm.model,
            temperature=self.cfg.llm.temperature,
        )
        raw = extractor.extract(text, self.schema)
        validate(raw, self.schema)
        return ExtractedData(
            document_type=raw.get("document_type", "Sonstiges"),
            issuer=raw.get("issuer", "Unbekannt"),
            document_date=parse_date(raw.get("document_date")),
            amount_total=raw.get("amount_total"),
            currency=raw.get("currency", "EUR"),
            due_date=parse_date(raw.get("due_date")),
            iban=raw.get("iban"),
            invoice_number=raw.get("invoice_number"),
            is_tax_relevant=bool(raw.get("is_tax_relevant", False)),
            tax_category=raw.get("tax_category"),
            confidence=raw.get("confidence", {}),
            summary=raw.get("summary", []),
        )

    def process_file(self, path: Path) -> tuple[Path, ExtractedData]:
        logger.info("Verarbeite %s", path)
        text = self._extract_text(path)
        extracted = self._llm_extract(text)
        report_pdf = build_report_page(extracted, path.name)
        merged = merge_report_with_original(report_pdf, path)
        target_name = build_filename(
            extracted.document_date,
            extracted.document_type,
            extracted.issuer,
            extracted.amount_total,
            extracted.currency,
            extracted.due_date,
            extracted.is_tax_relevant,
        )
        target_path = ensure_unique(self.cfg.hotfolder.processed_dir / target_name)
        with target_path.open("wb") as f:
            f.write(merged.read())
        return target_path, extracted

    def upload(self, graph: GraphClient, local_path: Path, extracted: ExtractedData) -> str:
        folder = (
            f"{extracted.document_type}/"
            f"{extracted.document_date.year if extracted.document_date else datetime.now().year}/"
            f"{(extracted.document_date or datetime.now().date()).month:02d}"
        )
        return graph.upload_file(self.cfg.onedrive, f"{folder}/{local_path.name}", local_path)

    def create_calendar_event(
        self, graph: GraphClient, extracted: ExtractedData, onedrive_link: str
    ) -> Optional[str]:
        if not extracted.due_date or not extracted.amount_total:
            return None
        local_zone_date = datetime.combine(
            extracted.due_date, time.fromisoformat(self.cfg.calendar.default_time)
        ).astimezone()
        title = (
            f"Zahlung: {extracted.issuer} - {extracted.amount_total:.2f} "
            f"{extracted.currency} ({extracted.document_type})"
        )
        description = (
            f"IBAN: {extracted.iban}\nReferenz: {extracted.invoice_number}\n"
            f"OneDrive: {onedrive_link}\n" + "\n".join(extracted.summary)
        )
        return graph.create_calendar_event(
            self.cfg.calendar, title, local_zone_date, description, extracted.amount_total, extracted.currency
        )

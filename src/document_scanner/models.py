from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional


@dataclass
class ExtractedData:
    document_type: str
    issuer: str
    document_date: Optional[date]
    amount_total: Optional[float]
    currency: str
    due_date: Optional[date]
    iban: Optional[str]
    invoice_number: Optional[str]
    is_tax_relevant: bool
    tax_category: Optional[str]
    confidence: dict[str, float] = field(default_factory=dict)
    summary: list[str] = field(default_factory=list)


@dataclass
class ProcessingResult:
    source_path: Path
    report_path: Path
    new_filename: str
    one_drive_path: str
    calendar_event_id: Optional[str]

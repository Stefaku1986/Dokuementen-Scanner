import re
from datetime import date
from pathlib import Path
from typing import Optional

SAFE_CHAR_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


def sanitize_component(component: str, max_length: int = 60) -> str:
    component = component.strip().replace(" ", "")
    component = SAFE_CHAR_PATTERN.sub("-", component)
    component = re.sub(r"-+", "-", component).strip("-")
    return component[:max_length] if component else "unbekannt"


def build_filename(
    doc_date: Optional[date],
    doc_type: str,
    sender: str,
    amount: Optional[float],
    currency: str,
    due_date: Optional[date],
    tax_relevant: bool,
    version: int = 1,
) -> str:
    date_part = doc_date.isoformat() if doc_date else "0000-00-00"
    amount_part = f"{amount:.2f}" if amount is not None else "0.00"
    due_part = due_date.isoformat() if due_date else "none"
    base = "__".join(
        [
            date_part,
            sanitize_component(doc_type),
            sanitize_component(sender),
            amount_part,
            f"faellig_{due_part}",
            f"tax_{'Y' if tax_relevant else 'N'}",
        ]
    )
    if version > 1:
        base = f"{base}__v{version}"
    return f"{base}.pdf"


def ensure_unique(path: Path) -> Path:
    counter = 1
    candidate = path
    while candidate.exists():
        counter += 1
        candidate = path.with_name(path.stem + f"__v{counter}" + path.suffix)
    return candidate

import json
from datetime import date
from pathlib import Path

from jsonschema import validate

schema = json.loads(Path("config/llm_schema.json").read_text(encoding="utf-8"))


def test_schema_accepts_valid_payload():
    payload = {
        "document_type": "Rechnung",
        "issuer": "Beispiel GmbH",
        "document_date": "2024-01-02",
        "amount_total": 49.99,
        "currency": "EUR",
        "due_date": "2024-01-30",
        "iban": "DE02120300000000202051",
        "invoice_number": "INV-123",
        "is_tax_relevant": True,
        "tax_category": "Werbungskosten",
        "confidence": {"amount_total": 0.9},
        "summary": ["Dienstleistung", "Netto 42,00"]
    }
    validate(payload, schema)

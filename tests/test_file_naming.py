from datetime import date
from pathlib import Path

from document_scanner.file_naming import build_filename, ensure_unique, sanitize_component


def test_sanitize_component_strips_and_limits():
    assert sanitize_component(" Test /Name?", max_length=10) == "Test-Name"


def test_build_filename_schema():
    name = build_filename(date(2024, 1, 2), "Rechnung", "Müller & Co", 199.99, "EUR", date(2024, 1, 15), True)
    assert name.startswith("2024-01-02__Rechnung__M-ller-Co__199.99__faellig_2024-01-15__tax_Y")


def test_ensure_unique(tmp_path):
    target = tmp_path / "file.pdf"
    target.write_text("one")
    unique = ensure_unique(target)
    assert unique.name == "file__v2.pdf"

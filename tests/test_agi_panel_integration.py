"""Smoke checks for apps/aria/agi.html panel."""

from pathlib import Path


def test_agi_html_exists_and_references_persistence():
    path = Path(__file__).resolve().parents[1] / "apps" / "aria" / "agi.html"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "/api/agi/status" in text
    assert "/api/agi/stream" in text
    assert "/api/agi/persistence" in text
    assert "agi_stream_utils.js" in text

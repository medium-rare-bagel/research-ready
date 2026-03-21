import datetime
from rr_core.names import suggest_filename


def test_suggest_filename_adds_date_suffix():
    result = suggest_filename("report.pdf", datetime.date(2026, 3, 18))
    assert result == "report-2026-03-18.pdf"


def test_suggest_filename_handles_multiple_dots():
    result = suggest_filename("my.report.final.pdf", datetime.date(2026, 3, 18))
    assert result == "my.report.final-2026-03-18.pdf"


def test_suggest_filename_no_extension():
    result = suggest_filename("README", datetime.date(2026, 3, 18))
    assert result == "README-2026-03-18"

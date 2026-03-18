from pathlib import Path
import pytest
from rr.file import file_asset


def test_file_moves_to_destination(tmp_path):
    # Set up a project-like directory with a sources/ subdir and a file in inbox/
    (tmp_path / "inbox").mkdir()
    (tmp_path / "sources").mkdir()
    src = tmp_path / "inbox" / "raw_document.pdf"
    src.write_text("dummy content")

    file_asset(
        src=src,
        new_name="clean-report-2026-03-18.pdf",
        dest_dir=tmp_path / "sources",
    )

    assert (tmp_path / "sources" / "clean-report-2026-03-18.pdf").exists()
    assert not src.exists()

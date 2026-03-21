import json
import subprocess
from datetime import date
from pathlib import Path
import pytest
from rr_core.file import file_asset


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


def test_file_updates_index_json(tmp_path):
    (tmp_path / "inbox").mkdir()
    (tmp_path / "sources").mkdir()
    src = tmp_path / "inbox" / "raw_document.pdf"
    src.write_text("dummy content")
    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps({"last_rebuilt": "2026-03-18", "files": []}))

    file_asset(
        src=src,
        new_name="clean-report-2026-03-18.pdf",
        dest_dir=tmp_path / "sources",
        index_path=index_path,
        description="A clean report",
    )

    index = json.loads(index_path.read_text())
    assert len(index["files"]) == 1
    entry = index["files"][0]
    assert entry["filename"] == "clean-report-2026-03-18.pdf"
    assert entry["directory"] == "sources"
    assert entry["path"] == "sources/clean-report-2026-03-18.pdf"
    assert entry["description"] == "A clean report"
    assert entry["added"] == date.today().isoformat()


def test_file_regenerates_index_md(tmp_path):
    (tmp_path / "inbox").mkdir()
    (tmp_path / "sources").mkdir()
    src = tmp_path / "inbox" / "raw_document.pdf"
    src.write_text("dummy content")
    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps({"last_rebuilt": "2026-03-18", "files": []}))
    index_md_path = tmp_path / "index.md"

    file_asset(
        src=src,
        new_name="clean-report-2026-03-18.pdf",
        dest_dir=tmp_path / "sources",
        index_path=index_path,
        index_md_path=index_md_path,
        description="A clean report",
    )

    content = index_md_path.read_text()
    assert "[clean-report-2026-03-18.pdf](sources/clean-report-2026-03-18.pdf)" in content
    assert "sources" in content
    assert "A clean report" in content


def test_file_creates_git_commit(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "--allow-empty", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / "inbox").mkdir()
    (tmp_path / "sources").mkdir()
    src = tmp_path / "inbox" / "raw_document.pdf"
    src.write_text("dummy content")
    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps({"last_rebuilt": "2026-03-18", "files": []}))
    index_md_path = tmp_path / "index.md"

    file_asset(
        src=src,
        new_name="clean-report-2026-03-18.pdf",
        dest_dir=tmp_path / "sources",
        index_path=index_path,
        index_md_path=index_md_path,
        description="A clean report",
        project_root=tmp_path,
    )

    log = subprocess.check_output(["git", "log", "-1", "--format=%s"], cwd=tmp_path, text=True).strip()
    assert log == "File: clean-report-2026-03-18.pdf → sources/"


def test_file_nonexistent_source_raises(tmp_path):
    (tmp_path / "sources").mkdir()
    src = tmp_path / "inbox" / "ghost.pdf"  # does not exist

    with pytest.raises(FileNotFoundError):
        file_asset(
            src=src,
            new_name="ghost.pdf",
            dest_dir=tmp_path / "sources",
        )


def test_file_preserves_existing_index_entries(tmp_path):
    (tmp_path / "inbox").mkdir()
    (tmp_path / "sources").mkdir()
    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps({"last_rebuilt": "2026-03-18", "files": []}))

    for name, desc in [("first.pdf", "First file"), ("second.pdf", "Second file")]:
        src = tmp_path / "inbox" / name
        src.write_text("content")
        file_asset(
            src=src,
            new_name=name,
            dest_dir=tmp_path / "sources",
            index_path=index_path,
            description=desc,
        )

    index = json.loads(index_path.read_text())
    assert len(index["files"]) == 2
    filenames = [e["filename"] for e in index["files"]]
    assert "first.pdf" in filenames
    assert "second.pdf" in filenames


def test_file_destination_not_in_config_raises(tmp_path):
    (tmp_path / "inbox").mkdir()
    (tmp_path / "secret").mkdir()
    src = tmp_path / "inbox" / "raw_document.pdf"
    src.write_text("dummy content")
    allowed_dirs = ["sources", "analysis", "output", "shared", "scripts"]

    with pytest.raises(ValueError, match="secret"):
        file_asset(
            src=src,
            new_name="raw_document.pdf",
            dest_dir=tmp_path / "secret",
            allowed_dirs=allowed_dirs,
        )

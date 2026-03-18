import json
import subprocess
from pathlib import Path

import pytest

from rr.remove import remove_asset


def make_index(tmp_path: Path, files: list | None = None) -> None:
    index = {"last_rebuilt": "2026-03-18", "files": files or []}
    (tmp_path / "index.json").write_text(json.dumps(index))


def make_entry(filename: str, directory: str = "sources") -> dict:
    return {
        "filename": filename,
        "directory": directory,
        "path": f"{directory}/{filename}",
        "description": "A test file",
        "added": "2026-03-18",
        "tags": [],
    }


def test_remove_deletes_file_from_disk(tmp_path):
    (tmp_path / "sources").mkdir()
    f = tmp_path / "sources" / "report.pdf"
    f.write_bytes(b"%PDF")
    make_index(tmp_path, [make_entry("report.pdf")])

    remove_asset("sources/report.pdf", tmp_path)

    assert not f.exists()


def test_remove_removes_entry_from_index(tmp_path):
    (tmp_path / "sources").mkdir()
    f = tmp_path / "sources" / "report.pdf"
    f.write_bytes(b"%PDF")
    make_index(tmp_path, [make_entry("report.pdf")])

    remove_asset("sources/report.pdf", tmp_path)

    index = json.loads((tmp_path / "index.json").read_text())
    assert len(index["files"]) == 0


def test_remove_regenerates_index_md(tmp_path):
    (tmp_path / "sources").mkdir()
    f = tmp_path / "sources" / "report.pdf"
    f.write_bytes(b"%PDF")
    make_index(tmp_path, [make_entry("report.pdf")])
    index_md = tmp_path / "index.md"
    index_md.write_text("old content with report.pdf mention")

    remove_asset("sources/report.pdf", tmp_path, index_md_path=index_md)

    content = index_md.read_text()
    assert "report.pdf" not in content


def test_remove_git_commits(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    (tmp_path / "sources").mkdir()
    f = tmp_path / "sources" / "report.pdf"
    f.write_bytes(b"%PDF")
    make_index(tmp_path, [make_entry("report.pdf")])

    remove_asset("sources/report.pdf", tmp_path)

    log = subprocess.check_output(
        ["git", "log", "-1", "--format=%s"], cwd=tmp_path, text=True
    ).strip()
    assert log == "Remove: report.pdf"


def test_remove_file_not_on_disk_but_in_index(tmp_path):
    make_index(tmp_path, [make_entry("report.pdf")])

    result = remove_asset("sources/report.pdf", tmp_path)

    assert result["removed_from_index"] is True
    assert result["removed_from_disk"] is False
    assert result["warning"] is None
    index = json.loads((tmp_path / "index.json").read_text())
    assert len(index["files"]) == 0


def test_remove_file_on_disk_but_not_in_index(tmp_path):
    (tmp_path / "sources").mkdir()
    f = tmp_path / "sources" / "report.pdf"
    f.write_bytes(b"%PDF")
    make_index(tmp_path, [])

    result = remove_asset("sources/report.pdf", tmp_path)

    assert result["removed_from_disk"] is True
    assert result["removed_from_index"] is False
    assert result["warning"] == "sources/report.pdf was not in the index"
    assert not f.exists()


def test_remove_file_not_on_disk_not_in_index(tmp_path):
    make_index(tmp_path, [])

    with pytest.raises(FileNotFoundError):
        remove_asset("sources/ghost.pdf", tmp_path)


def test_remove_by_filename_falls_back_to_index_search(tmp_path):
    (tmp_path / "sources").mkdir()
    f = tmp_path / "sources" / "report.pdf"
    f.write_bytes(b"%PDF")
    make_index(tmp_path, [make_entry("report.pdf")])

    result = remove_asset("report.pdf", tmp_path)

    assert result["removed_from_index"] is True
    assert result["removed_from_disk"] is True
    assert not f.exists()


def test_remove_by_filename_ambiguous_raises(tmp_path):
    (tmp_path / "sources").mkdir()
    (tmp_path / "analysis").mkdir()
    (tmp_path / "sources" / "report.pdf").write_bytes(b"%PDF")
    (tmp_path / "analysis" / "report.pdf").write_bytes(b"%PDF")
    make_index(
        tmp_path,
        [make_entry("report.pdf", "sources"), make_entry("report.pdf", "analysis")],
    )

    with pytest.raises(ValueError, match="multiple files match"):
        remove_asset("report.pdf", tmp_path)


def test_remove_preserves_other_index_entries(tmp_path):
    (tmp_path / "sources").mkdir()
    f = tmp_path / "sources" / "report.pdf"
    f.write_bytes(b"%PDF")
    make_index(tmp_path, [make_entry("report.pdf"), make_entry("keepme.pdf")])

    remove_asset("sources/report.pdf", tmp_path)

    index = json.loads((tmp_path / "index.json").read_text())
    assert len(index["files"]) == 1
    assert index["files"][0]["filename"] == "keepme.pdf"

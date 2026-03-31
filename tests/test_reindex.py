import json
import subprocess
from datetime import date
from pathlib import Path

import pytest

from rr_core.config import load_config
from rr_core.index import load_index, save_index
from rr_core.init import init_project
from rr_core.reindex import reindex


@pytest.fixture()
def project(tmp_path):
    init_project("test-proj", tmp_path)
    root = tmp_path / "test-proj"
    config = load_config(root)
    return root, config


def _git_log_count(project_root: Path) -> int:
    result = subprocess.check_output(
        ["git", "log", "--oneline"], cwd=project_root, text=True
    )
    return len(result.strip().splitlines())


def _git_latest_message(project_root: Path) -> str:
    return subprocess.check_output(
        ["git", "log", "-1", "--format=%s"], cwd=project_root, text=True
    ).strip()


def test_reindex_empty_project_no_changes(project):
    root, config = project
    result = reindex(root, config)
    assert result["added"] == []
    assert result["removed"] == []
    assert result["unchanged"] == 0


def test_reindex_finds_new_file(project):
    root, config = project
    (root / "sources" / "paper.pdf").write_bytes(b"%PDF")
    result = reindex(root, config)
    assert "paper.pdf" in result["added"]
    index = load_index(root / "index.json")
    entry = index["files"][0]
    assert entry["filename"] == "paper.pdf"
    assert entry["directory"] == "sources"
    assert entry["description"] == "(no description)"
    assert entry["added"] == date.today().isoformat()


def test_reindex_preserves_existing_metadata(project):
    root, config = project
    index_path = root / "index.json"
    index = load_index(index_path)
    index["files"].append({
        "filename": "report.pdf",
        "directory": "sources",
        "path": "sources/report.pdf",
        "description": "My report",
        "added": "2025-01-01",
        "tags": ["important"],
    })
    save_index(index_path, index)
    (root / "sources" / "report.pdf").write_bytes(b"%PDF")
    result = reindex(root, config)
    assert result["added"] == []
    assert result["unchanged"] == 1
    new_index = load_index(index_path)
    entry = new_index["files"][0]
    assert entry["description"] == "My report"
    assert entry["added"] == "2025-01-01"
    assert entry["tags"] == ["important"]


def test_reindex_removes_missing_file(project):
    root, config = project
    index_path = root / "index.json"
    index = load_index(index_path)
    index["files"].append({
        "filename": "gone.pdf",
        "directory": "sources",
        "path": "sources/gone.pdf",
        "description": "deleted",
        "added": "2025-01-01",
        "tags": [],
    })
    save_index(index_path, index)
    result = reindex(root, config)
    assert "gone.pdf" in result["removed"]
    new_index = load_index(index_path)
    assert new_index["files"] == []


def test_reindex_mixed_changes(project):
    root, config = project
    index_path = root / "index.json"
    index = load_index(index_path)
    index["files"].append({
        "filename": "keep.pdf",
        "directory": "sources",
        "path": "sources/keep.pdf",
        "description": "keeper",
        "added": "2025-01-01",
        "tags": [],
    })
    index["files"].append({
        "filename": "gone.pdf",
        "directory": "sources",
        "path": "sources/gone.pdf",
        "description": "deleted",
        "added": "2025-01-01",
        "tags": [],
    })
    save_index(index_path, index)
    (root / "sources" / "keep.pdf").write_bytes(b"%PDF")
    (root / "sources" / "new.pdf").write_bytes(b"%PDF")
    # gone.pdf intentionally not on disk
    result = reindex(root, config)
    assert "new.pdf" in result["added"]
    assert "gone.pdf" in result["removed"]
    assert result["unchanged"] == 1


def test_reindex_skips_dotfiles(project):
    root, config = project
    (root / "sources" / ".DS_Store").write_bytes(b"")
    result = reindex(root, config)
    assert result["added"] == []
    index = load_index(root / "index.json")
    assert index["files"] == []


def test_reindex_creates_missing_directories(project):
    root, config = project
    config["structure"]["directories"].append("archive")
    reindex(root, config)
    assert (root / "archive").is_dir()


def test_reindex_skips_untracked_dirs(project):
    root, config = project
    # inbox is in structure.directories but NOT in tracked_dirs
    (root / "inbox" / "unfiled.pdf").write_bytes(b"%PDF")
    result = reindex(root, config)
    assert result["added"] == []
    index = load_index(root / "index.json")
    assert index["files"] == []


def test_reindex_updates_last_rebuilt_on_changes(project):
    root, config = project
    (root / "sources" / "paper.pdf").write_bytes(b"%PDF")
    reindex(root, config)
    index = load_index(root / "index.json")
    assert index["last_rebuilt"] == date.today().isoformat()


def test_reindex_no_commit_when_nothing_changed(project):
    root, config = project
    before = _git_log_count(root)
    reindex(root, config)
    assert _git_log_count(root) == before


def test_reindex_commits_when_changes_found(project):
    root, config = project
    (root / "sources" / "paper.pdf").write_bytes(b"%PDF")
    reindex(root, config)
    msg = _git_latest_message(root)
    assert "+1" in msg
    assert "added" in msg


def test_reindex_regenerates_index_md(project):
    root, config = project
    (root / "sources" / "report.pdf").write_bytes(b"%PDF")
    reindex(root, config)
    content = (root / "index.md").read_text()
    assert "report.pdf" in content


def test_reindex_new_entry_has_modified_field(project):
    root, config = project
    (root / "sources" / "paper.pdf").write_bytes(b"%PDF")
    reindex(root, config)
    index = load_index(root / "index.json")
    entry = index["files"][0]
    assert "modified" in entry
    assert entry["modified"] == entry["added"]


def test_reindex_preserves_existing_modified(project):
    root, config = project
    index_path = root / "index.json"
    index = load_index(index_path)
    index["files"].append({
        "filename": "report.pdf",
        "directory": "sources",
        "path": "sources/report.pdf",
        "description": "My report",
        "added": "2025-01-01",
        "modified": "2025-06-15",
        "tags": ["important"],
    })
    save_index(index_path, index)
    (root / "sources" / "report.pdf").write_bytes(b"%PDF")
    reindex(root, config)
    new_index = load_index(index_path)
    entry = new_index["files"][0]
    assert entry["modified"] == "2025-06-15"  # preserved from original

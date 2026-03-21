import json
from pathlib import Path
from rr_core.index import load_index


def test_load_index_returns_parsed_dict(tmp_path: Path) -> None:
    data = {"last_rebuilt": "2026-03-18", "files": []}
    (tmp_path / "index.json").write_text(json.dumps(data))
    result = load_index(tmp_path / "index.json")
    assert result == data


def test_add_entry_adds_file_entry_to_index(tmp_path: Path) -> None:
    from rr_core.index import add_entry
    index = {"last_rebuilt": "2026-03-18", "files": []}
    add_entry(index, filename="report.pdf", directory="sources", description="A report")
    assert len(index["files"]) == 1
    entry = index["files"][0]
    assert entry["filename"] == "report.pdf"
    assert entry["directory"] == "sources"
    assert entry["path"] == "sources/report.pdf"
    assert entry["description"] == "A report"
    assert "added" in entry
    assert entry["tags"] == []


def test_save_index_round_trips_through_load_index(tmp_path: Path) -> None:
    from rr_core.index import save_index
    data = {"last_rebuilt": "2026-03-18", "files": [{"filename": "report.pdf", "directory": "sources"}]}
    path = tmp_path / "index.json"
    save_index(path, data)
    assert path.exists()
    assert load_index(path) == data


def test_generate_index_md_produces_one_data_row(tmp_path: Path) -> None:
    from rr_core.index import add_entry, save_index, generate_index_md
    index = {"last_rebuilt": "2026-03-18", "files": []}
    add_entry(index, filename="report.pdf", directory="sources", description="A report")
    save_index(tmp_path / "index.json", index)
    generate_index_md(tmp_path / "index.md", index)
    content = (tmp_path / "index.md").read_text()
    assert "[report.pdf](sources/report.pdf)" in content
    assert "sources" in content
    assert "A report" in content
    # exactly one data row (not counting header rows)
    data_rows = [line for line in content.splitlines() if line.startswith("| [")]
    assert len(data_rows) == 1


def test_load_index_nonexistent_file_returns_empty_index(tmp_path: Path) -> None:
    result = load_index(tmp_path / "index.json")
    assert result["files"] == []
    assert "last_rebuilt" in result

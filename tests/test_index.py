import json
from pathlib import Path
from rr.index import load_index


def test_load_index_returns_parsed_dict(tmp_path: Path) -> None:
    data = {"last_rebuilt": "2026-03-18", "files": []}
    (tmp_path / "index.json").write_text(json.dumps(data))
    result = load_index(tmp_path / "index.json")
    assert result == data


def test_load_index_nonexistent_file_returns_empty_index(tmp_path: Path) -> None:
    result = load_index(tmp_path / "index.json")
    assert result["files"] == []
    assert "last_rebuilt" in result

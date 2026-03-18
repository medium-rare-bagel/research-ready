from pathlib import Path
from rr.init import init_project


def test_init_creates_project_directory(tmp_path: Path) -> None:
    init_project("my-project", tmp_path)
    assert (tmp_path / "my-project").is_dir()

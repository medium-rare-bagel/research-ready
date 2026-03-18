from pathlib import Path
import pytest
from rr.config import find_project_root


def test_find_project_root_from_project_dir(tmp_path):
    (tmp_path / "project.yaml").touch()
    assert find_project_root(tmp_path) == tmp_path


def test_find_project_root_from_subdirectory(tmp_path):
    (tmp_path / "project.yaml").touch()
    subdir = tmp_path / "sources"
    subdir.mkdir()
    assert find_project_root(subdir) == tmp_path


def test_find_project_root_raises_when_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        find_project_root(tmp_path)

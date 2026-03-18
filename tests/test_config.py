from pathlib import Path
import pytest
from rr.config import find_project_root


def test_find_project_root_from_project_dir(tmp_path):
    (tmp_path / "project.yaml").touch()
    assert find_project_root(tmp_path) == tmp_path

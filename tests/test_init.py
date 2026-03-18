from pathlib import Path
import yaml
from rr.init import init_project


def test_init_creates_project_directory(tmp_path: Path) -> None:
    init_project("my-project", tmp_path)
    assert (tmp_path / "my-project").is_dir()


def test_init_creates_subdirectories(tmp_path: Path) -> None:
    init_project("my-project", tmp_path)
    project_dir = tmp_path / "my-project"
    for name in ["inbox", "sources", "analysis", "output", "shared", "scripts"]:
        assert (project_dir / name).is_dir(), f"missing directory: {name}"


def test_init_creates_project_yaml(tmp_path: Path) -> None:
    init_project("my-project", tmp_path)
    config_path = tmp_path / "my-project" / "project.yaml"
    assert config_path.exists()
    config = yaml.safe_load(config_path.read_text())
    assert config["project"]["name"] == "my-project"
    assert config["structure"]["directories"] == [
        "inbox", "sources", "analysis", "output", "shared", "scripts"
    ]

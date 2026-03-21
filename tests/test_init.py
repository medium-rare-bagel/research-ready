from pathlib import Path
import json
import yaml
from rr_core.init import init_project


def test_init_creates_project_directory(tmp_path: Path) -> None:
    init_project("my-project", tmp_path)
    assert (tmp_path / "my-project").is_dir()


def test_init_creates_empty_index_json(tmp_path: Path) -> None:
    init_project("my-project", tmp_path)
    index_path = tmp_path / "my-project" / "index.json"
    assert index_path.exists()
    index = json.loads(index_path.read_text())
    assert "last_rebuilt" in index
    assert index["files"] == []


def test_init_creates_claude_md_with_project_name(tmp_path: Path) -> None:
    init_project("my-project", tmp_path)
    claude_md = tmp_path / "my-project" / "CLAUDE.md"
    assert claude_md.exists()
    assert "my-project" in claude_md.read_text()


def test_init_creates_git_repo_with_initial_commit(tmp_path: Path) -> None:
    import subprocess
    init_project("my-project", tmp_path)
    project_dir = tmp_path / "my-project"
    assert (project_dir / ".git").is_dir()
    log = subprocess.check_output(
        ["git", "log", "--oneline"], cwd=project_dir, text=True
    )
    assert "Initialize project: my-project" in log


def test_init_creates_gitignore(tmp_path: Path) -> None:
    init_project("my-project", tmp_path)
    assert (tmp_path / "my-project" / ".gitignore").exists()


def test_init_creates_subdirectories(tmp_path: Path) -> None:
    init_project("my-project", tmp_path)
    project_dir = tmp_path / "my-project"
    for name in ["inbox", "sources", "analysis", "output", "shared", "scripts"]:
        assert (project_dir / name).is_dir(), f"missing directory: {name}"


def test_init_creates_index_md_with_table_headers(tmp_path: Path) -> None:
    init_project("my-project", tmp_path)
    index_md = tmp_path / "my-project" / "index.md"
    assert index_md.exists()
    content = index_md.read_text()
    assert "| File | Directory | Added | Description |" in content
    assert "|------|-----------|-------|-------------|" in content


def test_init_creates_project_yaml(tmp_path: Path) -> None:
    init_project("my-project", tmp_path)
    config_path = tmp_path / "my-project" / "project.yaml"
    assert config_path.exists()
    config = yaml.safe_load(config_path.read_text())
    assert config["project"]["name"] == "my-project"
    assert config["structure"]["directories"] == [
        "inbox", "sources", "analysis", "output", "shared", "scripts"
    ]

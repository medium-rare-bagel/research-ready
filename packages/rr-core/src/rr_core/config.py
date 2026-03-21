from pathlib import Path
import yaml


def find_project_root(cwd: Path) -> Path:
    """Walk up from cwd looking for project.yaml. Returns the root path."""
    for directory in [cwd, *cwd.parents]:
        if (directory / "project.yaml").exists():
            return directory
    raise FileNotFoundError(f"No project.yaml found in {cwd} or any parent directory")


def load_config(project_root: Path) -> dict:
    """Parse project.yaml from the given project root."""
    return yaml.safe_load((project_root / "project.yaml").read_text())

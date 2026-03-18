from pathlib import Path


def find_project_root(cwd: Path) -> Path:
    """Walk up from cwd looking for project.yaml. Returns the root path."""
    for directory in [cwd, *cwd.parents]:
        if (directory / "project.yaml").exists():
            return directory
    raise FileNotFoundError(f"No project.yaml found in {cwd} or any parent directory")

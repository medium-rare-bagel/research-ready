from pathlib import Path
import yaml

DEFAULT_CONFIG = {
    "project": {
        "name": None,  # filled in at runtime
        "created": None,  # filled in at runtime
    },
    "structure": {
        "directories": ["inbox", "sources", "analysis", "output", "shared", "scripts"],
    },
    "index": {
        "file": "index.md",
        "tracked_dirs": ["sources", "analysis", "output", "shared", "scripts"],
    },
    "git": {
        "auto_commit": True,
    },
}


def init_project(name: str, parent: Path) -> None:
    project_dir = parent / name
    project_dir.mkdir()

    config = DEFAULT_CONFIG.copy()
    config["project"] = {"name": name, "created": None}
    (project_dir / "project.yaml").write_text(yaml.dump(config, sort_keys=False))

    for d in config["structure"]["directories"]:
        (project_dir / d).mkdir()

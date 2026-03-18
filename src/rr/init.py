from datetime import date
from pathlib import Path
import json
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


def _claude_md(name: str) -> str:
    return f"""\
# Project: {name}

## Structure
This project uses `rr` (Research Ready) for workspace management.
See `project.yaml` for the directory structure configuration.

## Key Files
- `index.json` — Asset index (source of truth). Updated by `rr file`, `rr remove`, `rr reindex`.
- `index.md` — Human-readable index (generated from index.json). Do not hand-edit.
- `project.yaml` — Project structure and configuration.

## Conventions
- All scripting in Python. Use `uv` for package management and tooling.
- The `inbox/` directory is a holding pen for unfiled materials.
- Filed assets go in `sources/`, `analysis/`, `output/`, `shared/`, or `scripts/`.
- `shared/` tracks materials sent to others — use the description to note the recipient.
- `scripts/` holds project-specific scripts — use the description to note what each does.
- Every file operation is auto-committed to git.

## Tools
This project was scaffolded with `rr`. Available commands:
- `rr file <path>` — Rename, move, and index a file
- `rr remove <path>` — Remove a file and update the index
- `rr reindex` — Rebuild the index from filesystem state
"""


def init_project(name: str, parent: Path) -> None:
    project_dir = parent / name
    project_dir.mkdir()

    config = DEFAULT_CONFIG.copy()
    config["project"] = {"name": name, "created": None}
    (project_dir / "project.yaml").write_text(yaml.dump(config, sort_keys=False))

    for d in config["structure"]["directories"]:
        (project_dir / d).mkdir()

    index = {"last_rebuilt": date.today().isoformat(), "files": []}
    (project_dir / "index.json").write_text(json.dumps(index, indent=2))

    (project_dir / "CLAUDE.md").write_text(_claude_md(name))

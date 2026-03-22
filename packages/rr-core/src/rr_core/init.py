import copy
from datetime import date
from pathlib import Path
import json
import yaml

from rr_core.git import git_commit_all, git_init

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


_GITIGNORE = """\
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/

# OS
.DS_Store
Thumbs.db

# Credentials
.env
*.key
*.pem
"""


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

## Filing Conventions
When filing assets with `rr file`, follow these conventions:
- **Naming:** Use a descriptive slug with date suffix: `descriptive-name-YYYY-MM-DD.ext` (e.g., `maxar-site-alpha-2024-03-15.png`)
- **Directory:** Choose based on content type:
  - `sources/` — Research materials, documents, images, data files
  - `analysis/` — Notes, working documents, findings
  - `output/` — Deliverables: reports, drafts, visualizations
  - `shared/` — Materials sent to others (note the recipient in the description)
  - `scripts/` — Project-specific scripts (note what each does in the description)
- **Description:** One-line concise summary of the file's content or purpose

## Tools
This project was scaffolded with `rr`. Available commands:
- `rr file <path>` — Rename, move, and index a file. Supports non-interactive mode:
  `rr file <path> --name <new-name> --dir <directory> --description <desc>`
- `rr remove <path>` — Remove a file and update the index
- `rr reindex` — Rebuild the index from filesystem state
"""


def init_project(name: str, parent: Path) -> None:
    project_dir = parent / name
    project_dir.mkdir()

    config = copy.deepcopy(DEFAULT_CONFIG)
    config["project"] = {"name": name, "created": None}
    (project_dir / "project.yaml").write_text(yaml.dump(config, sort_keys=False))

    for d in config["structure"]["directories"]:
        (project_dir / d).mkdir()

    index = {"last_rebuilt": date.today().isoformat(), "files": []}
    (project_dir / "index.json").write_text(json.dumps(index, indent=2))

    (project_dir / "index.md").write_text(
        f"# Project Index\n\nLast rebuilt: {index['last_rebuilt']}\n\n"
        "| File | Directory | Added | Description |\n"
        "|------|-----------|-------|-------------|\n"
    )

    (project_dir / "CLAUDE.md").write_text(_claude_md(name))

    (project_dir / ".gitignore").write_text(_GITIGNORE)

    git_init(project_dir)
    git_commit_all(project_dir, f"Initialize project: {name}")

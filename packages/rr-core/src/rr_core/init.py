import copy
from datetime import date
from pathlib import Path
import json
import yaml

from rr_core.git import git_commit_all, git_init
from rr_core.validate import validate_name

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
- The `inbox/` directory is a holding pen for unfiled materials.
- Filed assets go in `sources/`, `analysis/`, `output/`, `shared/`, or `scripts/`.
- `shared/` tracks materials sent to others — use the description to note the recipient.
- `scripts/` holds project-specific scripts — use the description to note what each does.
- Every file operation is auto-committed to git.

## Python & uv (IMPORTANT)

All scripting in this project uses Python with `uv` for package management, virtual environments, and task running.

**Do NOT:**
- Use `pip` or `pip install` — uv manages all dependencies
- Run `python` directly — use `uv run` instead
- Ignore `.venv/` — it's managed by uv automatically

**Common operations:**
- `uv init` — Initialize a new script or package
- `uv add <package>` — Add a dependency (NOT `pip install`)
- `uv run <command>` — Run a command in the project's virtual environment
- `uv run pytest` — Run tests (NOT `python -m pytest`)
- `uv sync` — Sync the virtual environment with `pyproject.toml`

**Example workflow:**
```
uv add requests numpy
uv run python script.py
```

If you see a `pyproject.toml` in the project, dependencies are already declared. Use `uv sync` then `uv run` — never pip.

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
- `rr file <path>` — Rename, move, and index a file
- `rr remove <path>` — Remove a file and update the index
- `rr reindex` — Rebuild the index from filesystem state

## Moving Files Between Directories
To move an already-filed asset to a different directory, just `rr file` it again with the new `--dir`. Do NOT use `rr remove` first — that deletes the file and risks data loss.

Example: move a file from sources/ to shared/:
```
rr file sources/report.pdf --dir shared --description "Shared with Emily"
```

## Non-Interactive Mode (IMPORTANT)
When using `rr` commands programmatically or from an AI assistant, ALWAYS use non-interactive flags to avoid interactive prompts:

```
rr file <path> --name <new-name> --dir <directory> --description "<desc>"
```

If any flag is provided, rr runs non-interactively — omitted flags get sensible defaults (name: auto-generated slug, dir: `sources`, description: empty). If NO flags are provided, rr prompts interactively for all values.

Example:
```
rr file inbox/report.pdf --name site-assessment-2026-03-22.pdf --dir sources --description "Site assessment report from March field visit"
```
"""


def init_project(name: str, parent: Path) -> None:
    validate_name(name)
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

# rr — Handoff

## Last Updated
2026-03-18 — `file_asset` core logic built and fully tested.

## What's Done
- **Project scaffolding** — `pyproject.toml` (src layout, `rr` entry point), Python 3.12 pinned, `pyyaml` runtime dep, `pytest` dev dep
- **`src/rr/git.py`** — `git_init`, `git_commit_all` via subprocess, separate from init logic
- **`rr init`** — `init_project(name, parent)` in `src/rr/init.py`: creates project dir, `project.yaml`, six subdirectories, `index.json`, `index.md` (table headers, no rows), `CLAUDE.md`, `.gitignore`, git repo + initial commit (8/8 tests passing)
- **`src/rr/index.py`** — `load_index`, `save_index`, `add_entry`, `generate_index_md` (5/5 tests passing)
- **`src/rr/file.py`** — `file_asset(src, new_name, dest_dir, ...)`: moves file, updates index.json, regenerates index.md, git commits. Optional params: `index_path`, `index_md_path`, `description`, `project_root`, `allowed_dirs`. (7/7 tests passing)
- **20 tests passing total**

## What's Next
- Wire up `src/rr/cli.py`: `rr file` Click command — interactive prompts for new name, destination, description — calls `file_asset` with all params resolved from project.yaml and project root
- After CLI: `rr reindex`

## Decisions Made (Not Yet in Spec)
- Git operations use `subprocess` (not GitPython or similar) — lightweight, no extra dep
- `rr init` creates `index.md` with table headers and no rows
- CLI framework: **Click**
- Logging: `logging.getLogger(__name__)` per module, INFO for user output, DEBUG for internals — not yet wired, add when building CLI
- `file_asset` takes `allowed_dirs: list[str]` (names only, not paths) for config validation — raises `ValueError` naming the bad directory before any move happens

## Open Issues
- None currently

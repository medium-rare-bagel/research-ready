# rr — Handoff

## Last Updated
2026-03-18 — `index.py` module built and tested. `rr init` now generates `index.md`.

## What's Done
- **Project scaffolding** — `pyproject.toml` (src layout, `rr` entry point), Python 3.12 pinned, `pyyaml` runtime dep, `pytest` dev dep
- **`src/rr/git.py`** — `git_init`, `git_commit_all` via subprocess, separate from init logic
- **`rr init`** — `init_project(name, parent)` in `src/rr/init.py`: creates project dir, `project.yaml`, six subdirectories, `index.json`, `index.md` (table headers, no rows), `CLAUDE.md`, `.gitignore`, git repo + initial commit (8/8 tests passing)
- **`src/rr/index.py`** — `load_index`, `save_index`, `add_entry`, `generate_index_md` (5/5 tests passing)
- **13 tests passing total**

## What's Next
- Build `rr file`: prompt user, move file, call `add_entry` + `save_index` + `generate_index_md`, git commit — start with `tests/test_file.py`
- Wire up `src/rr/cli.py` after `rr file` logic is solid — Click confirmed as CLI framework

## Decisions Made (Not Yet in Spec)
- Git operations use `subprocess` (not GitPython or similar) — lightweight, no extra dep
- `rr init` creates `index.md` with table headers and no rows (resolved open issue from prior session)
- CLI framework decided: **Click**
- Logging approach: `logging.getLogger(__name__)` per module, INFO for user output, DEBUG for internals — not yet wired, add when building CLI

## Open Issues
- None currently

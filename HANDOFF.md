# rr — Handoff

## Last Updated
2026-03-19 — Extracted wishlist into dedicated WISHLIST.md; cleaned up HANDOFF.

## What's Done
- **Project scaffolding** — `pyproject.toml` (src layout, `rr` entry point), Python 3.12 pinned, `pyyaml`+`click` runtime deps, `pytest` dev dep
- **`src/rr/git.py`** — `git_init`, `git_commit_all` via subprocess, `git_has_changes` helper
- **`rr init`** — `init_project(name, parent)` in `src/rr/init.py`: creates project dir, `project.yaml`, six subdirectories, `index.json`, `index.md` (table headers, no rows), `CLAUDE.md`, `.gitignore`, git repo + initial commit (8/8 tests passing)
- **`src/rr/index.py`** — `load_index`, `save_index`, `add_entry`, `generate_index_md` (5/5 tests passing)
- **`src/rr/file.py`** — `file_asset(src, new_name, dest_dir, ...)`: moves file, updates index.json, regenerates index.md, git commits. Optional params: `index_path`, `index_md_path`, `description`, `project_root`, `allowed_dirs`. (7/7 tests passing)
- **`src/rr/config.py`** — `find_project_root(cwd)` walks up from cwd looking for `project.yaml`; `load_config(project_root)` parses it (3/3 tests passing)
- **`src/rr/names.py`** — `suggest_filename(original, date)`: inserts `YYYY-MM-DD` before extension; handles multiple dots and no extension (3/3 tests passing)
- **`src/rr/reindex.py`** — `reindex(project_root, config, ...)`: scans tracked_dirs, diffs against index.json, adds/removes entries, preserves metadata, skips dotfiles, creates missing dirs, commits only when git has actual changes (12/12 tests passing)
- **`src/rr/remove.py`** — `remove_asset(file_path, project_root, ...)`: handles all four cases (in index + on disk, in index only, on disk only, neither), deletes file, removes entry, regenerates index.md, git commits "Remove: <filename>". Returns `{"removed_from_index": bool, "removed_from_disk": bool, "warning": str | None}`. Falls back to filename search if bare name given; raises `ValueError` if ambiguous. (10/10 tests passing)
- **`src/rr/cli.py`** — `ProjectContext` dataclass, `cli` Click group with `--verbose/-v` flag, `require_project` helper, `rr file`, `rr init`, `rr reindex`, `rr remove` subcommands (22/22 CLI tests passing)
- **Bug fix** — `rr file` now preserves the original file extension when the user omits it in the rename prompt (cli.py:83)
- **71 tests passing total**

## What's Next
- All four MVP subcommands are complete: `rr init`, `rr file`, `rr reindex`, `rr remove`
- See `WISHLIST.md` for feature ideas and backlog items

## Decisions Made (Not Yet in Spec)
- `file_asset` takes `allowed_dirs: list[str]` (names only, not paths) for config validation — raises `ValueError` naming the bad directory before any move happens
- Default filename suggestion format for `rr file`: `stem-YYYY-MM-DD.ext` (date suffix appended to stem, before extension)
- **Projects created by `rr init` are research workspaces, not Python packages.** No `pyproject.toml`, no `uv init`, no `.venv` inside scaffolded projects. `uv` is only for developing `rr` itself. (Now clarified in SPEC.md technical decisions table.)

## Known Spec Gaps (Low Priority)
- `index.json` entries missing `modified` field per spec schema
- `rr init` missing `--config` and `--no-git` flags per spec

## Open Issues

None.

# rr — Handoff

## Last Updated
2026-03-18 — `rr reindex` built and wired as CLI subcommand.

## What's Done
- **Project scaffolding** — `pyproject.toml` (src layout, `rr` entry point), Python 3.12 pinned, `pyyaml`+`click` runtime deps, `pytest` dev dep
- **`src/rr/git.py`** — `git_init`, `git_commit_all` via subprocess, separate from init logic
- **`rr init`** — `init_project(name, parent)` in `src/rr/init.py`: creates project dir, `project.yaml`, six subdirectories, `index.json`, `index.md` (table headers, no rows), `CLAUDE.md`, `.gitignore`, git repo + initial commit (8/8 tests passing)
- **`src/rr/index.py`** — `load_index`, `save_index`, `add_entry`, `generate_index_md` (5/5 tests passing)
- **`src/rr/file.py`** — `file_asset(src, new_name, dest_dir, ...)`: moves file, updates index.json, regenerates index.md, git commits. Optional params: `index_path`, `index_md_path`, `description`, `project_root`, `allowed_dirs`. (7/7 tests passing)
- **`src/rr/config.py`** — `find_project_root(cwd)` walks up from cwd looking for `project.yaml`; `load_config(project_root)` parses it (3/3 tests passing)
- **`src/rr/names.py`** — `suggest_filename(original, date)`: inserts `YYYY-MM-DD` before extension; handles multiple dots and no extension (3/3 tests passing)
- **`src/rr/reindex.py`** — `reindex(project_root, config, ...)`: scans tracked_dirs, diffs against index.json, adds/removes entries, preserves metadata, skips dotfiles, creates missing dirs, commits only when git has actual changes (12/12 tests passing)
- **`src/rr/git.py`** — added `git_has_changes(path)` helper
- **`src/rr/cli.py`** — `ProjectContext` dataclass, `cli` Click group with `--verbose/-v` flag, `require_project` helper, `rr file`, `rr init`, `rr reindex` subcommands (16/16 CLI tests passing)
- **55 tests passing total**

## What's Next
- Wire `rr remove` as a subcommand

## Decisions Made (Not Yet in Spec)
- Git operations use `subprocess` (not GitPython or similar) — lightweight, no extra dep
- `rr init` creates `index.md` with table headers and no rows
- CLI framework: **Click**
- Logging: `logging.getLogger(__name__)` per module, INFO for user output, DEBUG for internals — not yet wired, add when building CLI
- `file_asset` takes `allowed_dirs: list[str]` (names only, not paths) for config validation — raises `ValueError` naming the bad directory before any move happens
- Default filename suggestion format for `rr file`: `stem-YYYY-MM-DD.ext` (date suffix appended to stem, before extension)
- Project root discovery lives in `config.py` — `find_project_root` walks upward from cwd looking for `project.yaml`
- **Projects created by `rr init` are research workspaces, not Python packages.** No `pyproject.toml`, no `uv init`, no `.venv` inside scaffolded projects. `uv` is only for developing `rr` itself. (Now clarified in SPEC.md technical decisions table.)

### CLI Architecture (decided 2026-03-18)
- **Click group** with callback that resolves project context: calls `find_project_root(Path.cwd())`, on success stores `ProjectContext` on `ctx.obj`, on `FileNotFoundError` sets `ctx.obj = None`
- **`ProjectContext` dataclass** in `cli.py` — two fields: `root: Path`, `config: dict`
- **`require_project` helper** — called at top of subcommands that need a project. Checks `ctx.obj`, if `None` prints error ("not inside an rr project") and exits. Keeps group lenient for `rr init`, gives clear errors elsewhere.
- **`--verbose` / `-v` flag** on the group — sets logging level to `DEBUG` in group callback before subcommand runs

## Open Issues
- None currently

# rr — Development Guide

## What This Is
`rr` (Research Ready) is a Python CLI tool for scaffolding and managing research project workspaces. See `SPEC.md` for the full specification.

## Development Setup
- Python 3.12+
- `uv` for package management, virtual environments, and running
- `pytest` for testing

## uv Rules — READ THIS FIRST

**Always use uv. Never use pip, pip install, or python -m pip. Never fall back to pip.**

Common operations:
- `uv init` — initialize a new project
- `uv add <package>` — add a dependency (NOT pip install)
- `uv add --dev <package>` — add a dev dependency (e.g., pytest)
- `uv run <command>` — run a command in the project's virtual environment
- `uv run pytest` — run tests (NOT python -m pytest, NOT pytest directly)
- `uv sync` — sync the virtual environment with pyproject.toml
- `uv lock` — update the lockfile

If a package install fails with uv, troubleshoot uv — do not switch to pip.
The virtual environment lives in `.venv/` and is managed by uv automatically.
Dependencies are declared in `pyproject.toml`, not `requirements.txt`.

## Development Approach: Red/Green TDD

This is a personal tool, not enterprise software. The TDD discipline is about catching mistakes early and building confidence in the code — not about coverage metrics or test pyramids.

### The cycle

1. **Read SPEC.md** for what the feature should do
2. **Write one failing test** that asserts a specific behavior (red)
3. **Run it, confirm it fails** — if it passes, the test isn't testing anything new
4. **Write the minimum code** to make it pass (green)
5. **Run all tests** — make sure nothing else broke
6. **Refactor** if the code is messy, then run tests again
7. **Commit**
8. Repeat with the next behavior

### Practical guidelines

- One behavior per test. `test_init_creates_project_directory` not `test_init_works`.
- Test names should read like a sentence: `test_file_moves_to_destination_directory`.
- Don't test implementation details. Test what the user sees: files on disk, index content, git commits.
- Use `tmp_path` fixtures for filesystem tests — every test gets a clean directory.
- If you're unsure what to test next, re-read the relevant section of SPEC.md.
- Don't write tests for trivial getters/setters. Focus on behavior.
- Run tests with `uv run pytest`. Always.

Tests go in `tests/`. Source code goes in `src/rr/`.

## Code Standards
- Pythonic, idiomatic code. Type hints on all public functions.
- No unnecessary abstractions. Prefer simple functions over class hierarchies.
- Use `pathlib.Path` for all filesystem operations.
- YAML parsing via `pyyaml` or `ruamel.yaml`.
- CLI framework: decided during implementation (click or typer).

## Build Order
1. `rr init` — scaffold a project
2. `rr file` — file an asset into the project
3. `rr reindex` — rebuild the index
4. `rr remove` — remove a file

## Project Layout
```
rr/
├── CLAUDE.md              # This file
├── SPEC.md                # Project specification
├── pyproject.toml         # uv/Python project config
├── src/
│   └── rr/
│       ├── __init__.py
│       ├── cli.py         # CLI entry point and subcommands
│       ├── init.py        # rr init logic
│       ├── file.py        # rr file logic
│       ├── remove.py      # rr remove logic
│       ├── reindex.py     # rr reindex logic
│       ├── index.py       # Index read/write operations
│       ├── config.py      # project.yaml read/write
│       └── git.py         # Git operations (commit, init)
└── tests/
    ├── conftest.py        # Shared fixtures (tmp project dirs, etc.)
    ├── test_init.py
    ├── test_file.py
    ├── test_remove.py
    ├── test_reindex.py
    └── test_index.py
```

## Key Design Decisions
- **Configuration-driven:** Directory structure lives in `project.yaml`, not hardcoded.
- **Git auto-commit:** Every file operation commits automatically.
- **Dual index:** `index.json` is the source of truth (structured, extensible). `index.md` is generated from it (human-readable, Obsidian-compatible). Never parse `index.md` — always read/write `index.json`.
- **Relative paths:** All paths in the index are relative to the project root. This keeps projects portable across machines.
- **Flat structure:** One level of subdirectories. No nesting.
- **Obsidian-friendly:** Generated `index.md` uses standard markdown links. Projects can live inside or be symlinked into an Obsidian vault.
- **Separation of concerns:** Keep index operations (`index.py`) separate from filesystem operations (`file.py`). The index should not assume files are local — future versions may track remote files (e.g., Google Drive).

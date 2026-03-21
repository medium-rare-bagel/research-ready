# rr — Architecture

## Overview

rr is structured as a uv workspace with two packages. This separates the
business logic from the user interface, making the core callable by tools
other than the CLI.

## Packages

### rr-core
Contains all business logic — the actual work the tool does:
- Project scaffolding (init.py)
- Filing assets (file.py)
- Removing assets (remove.py)
- Rebuilding the index (reindex.py)
- Index read/write (index.py)
- Config read/write (config.py)
- Git operations (git.py)
- Filename utilities (names.py)

No Click dependency. Can be imported and called directly from any Python code.

### rr
Thin CLI wrapper only. Contains cli.py, which:
- Handles user prompts via Click
- Calls rr-core functions with the user's answers
- Formats output for display

Depends on rr-core.

## Why the Split?

The CLI (Click) blocks non-human callers. When Claude Code CLI tries to run
rr commands, it hits interactive prompts it can't answer. By keeping all
logic in rr-core with no CLI dependency, any caller — Claude Code, a future
GUI, scripts, tests — can use rr without going through Click.

## Future Packages

When a GUI is added, it becomes a third workspace member (e.g. rr-gui) that
imports rr-core directly. No refactor needed — the separation is already in
place.

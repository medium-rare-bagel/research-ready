# Stage 2 — Beta Blockers Implementation Plan

## Context
Beta target is Thursday 2026-04-03. Stage 1 (validation + non-interactive mode) is complete with 101 tests passing. Stage 2 implements 4 consensus-prioritized items that address spec defects, first-impression UX, and data safety for beta testers.

All 4 items are independent — no cross-dependencies. TDD cycle for each: write failing tests → minimum code to pass → run full suite → commit.

---

## Item 1: `modified` field in index entries

**Problem:** SPEC.md defines `modified` in the index schema but no code writes it. Also, `add_entry()` resets `added` on overwrite (pre-existing bug).

**Files:**
- `packages/rr-core/src/rr_core/index.py` — `add_entry()` (lines 6-20)
- `packages/rr-core/src/rr_core/reindex.py` — new entry construction (lines 69-76)
- `tests/test_index.py` — new tests
- `tests/test_reindex.py` — new tests

**Tests (red):**
1. `test_add_entry_includes_modified_field` — new entry has `modified` == `added`
2. `test_add_entry_overwrite_preserves_added_updates_modified` — on overwrite, `added` preserved from original, `modified` set to today, description updated
3. `test_reindex_new_entry_has_modified_field` — discovered file gets `modified` == `added`
4. `test_reindex_preserves_existing_modified` — existing entry's `modified` survives reindex

**Implementation (green):**
- `index.py:add_entry()`: Add `"modified": date.today().isoformat()` to entry dict. In overwrite branch (line 16-18), capture `existing["added"]` before replacing and set `entry["added"] = existing["added"]`
- `reindex.py`: Add `"modified": added_date` to the new entry dict at line 75
- `generate_index_md()`: No change (modified is JSON-only, not shown in markdown table)

---

## Item 2: Post-init welcome message + backup reminder

**Problem:** `rr init` prints one line. Beta testers arrive cold with no orientation.

**Files:**
- `packages/rr/src/rr/cli.py` — `init_cmd()` (line 44-56)
- `tests/test_cli.py` — new tests

**Tests (red):**
1. `test_init_shows_welcome_with_directories` — output contains directory names (sources, analysis, etc.)
2. `test_init_shows_key_files` — output mentions index.json, project.yaml, CLAUDE.md
3. `test_init_shows_command_summary` — output contains `rr file`, `rr remove`, `rr reindex`
4. `test_init_shows_backup_reminder` — output contains "backup" or "remote"
5. `test_init_shows_obsidian_tip` — output contains "Obsidian" and "Detect all file extensions"

**Implementation (green):**
- Read the created `project.yaml` to get actual directory list (correct even with future `--config` flag)
- Replace single `click.echo` with multi-line welcome block (~10 lines):
  ```
  Initialized project: {name}
    Directories: inbox, sources, analysis, output, shared, scripts
    Key files:   index.json, project.yaml, CLAUDE.md

  Quick start:
    rr file <path>   — rename, move, and index a file
    rr remove <path> — remove a file and update the index
    rr reindex       — rebuild the index from disk

  Tip: rr uses git for history, not backup. Consider setting up a remote.
  Tip: Using Obsidian? Enable Settings → Files and Links → Detect all file extensions
  ```
- Use `load_config(Path.cwd() / project_name)` to get the created project's config

---

## Item 3: Directory picker for `rr file`

**Problem:** Destination directory is free-text with no visibility into valid options.

**Files:**
- `packages/rr/src/rr/cli.py` — `file_cmd()` line 106
- `tests/test_cli.py` — new test

**Tests (red):**
1. `test_file_interactive_rejects_invalid_directory` — input "bogus" then "sources"; file ends up in sources (Click re-prompts on invalid Choice)

**Implementation (green):**
- Line 106, change:
  ```python
  dest_dir_name = click.prompt("Destination directory", default="sources")
  ```
  to:
  ```python
  dest_dir_name = click.prompt(
      "Destination directory",
      type=click.Choice(allowed_dirs, case_sensitive=True),
      default="sources",
  )
  ```
- All existing tests use valid directory names ("sources") so none break

---

## Item 4: Large file handling (size gate)

**Problem:** Bonny already filed a video. Large binaries bloat `.git/` permanently. Need a clean error before the move.

**Files:**
- `packages/rr-core/src/rr_core/init.py` — `DEFAULT_CONFIG` (add `max_file_size`)
- `packages/rr-core/src/rr_core/file.py` — `file_asset()` (add size check)
- `packages/rr/src/rr/cli.py` — `file_cmd()` (pass config value)
- `tests/test_file.py` — new tests

**Tests (red):**
1. `test_file_rejects_oversized_file` — file 1025 bytes, limit 1024 → ValueError matching "exceeds.*limit", file not moved
2. `test_file_allows_file_at_exact_limit` — file 1024 bytes, limit 1024 → succeeds
3. `test_file_no_size_limit_when_zero` — `max_file_size=0` → no check, large file succeeds
4. `test_file_no_size_limit_when_none` — `max_file_size=None` (default) → no check
5. `test_file_error_message_includes_sizes` — error message mentions file size and limit

**Implementation (green):**
- `init.py DEFAULT_CONFIG`: Add `"max_file_size": 52428800` (50MB) under `"git"` key
- `file.py file_asset()`: Add `max_file_size: int | None = None` param. Before `shutil.move` (line 34):
  ```python
  if max_file_size and src.stat().st_size > max_file_size:
      size_mb = src.stat().st_size / (1024 * 1024)
      limit_mb = max_file_size / (1024 * 1024)
      raise ValueError(
          f"File size ({size_mb:.1f} MB) exceeds limit ({limit_mb:.1f} MB). "
          f"Increase git.max_file_size in project.yaml or manage this file outside rr."
      )
  ```
- `cli.py file_cmd()`: Read `max_file_size = project.config.get("git", {}).get("max_file_size", 52428800)` and pass to `file_asset()`
- `max_file_size=0` disables the check (falsy). `None` (missing param) also disables.

---

## Verification

After all 4 items:
```bash
uv run pytest                    # all ~115 tests pass
uv run pytest -x --tb=short      # quick check, stop on first failure
```

Manual smoke test:
```bash
cd /tmp && rr init test-project  # verify welcome message
cd test-project
echo "hello" > inbox/doc.txt
rr file inbox/doc.txt            # verify directory picker shows choices
cat index.json | grep modified   # verify modified field exists
```

## Commit Strategy
One commit per item after all tests pass. Commit messages:
1. `Add modified field to index entries`
2. `Add post-init welcome message with tips`
3. `Add directory picker for rr file interactive mode`
4. `Add large file size gate`

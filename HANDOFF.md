# rr — Handoff

## Last Updated
2026-03-22 — Stage 1 complete (non-interactive mode + input validation)

## What's Done
- All four commands implemented: `rr init`, `rr file`, `rr reindex`, `rr remove`
- uv workspace structure: `packages/rr-core/` (business logic) + `packages/rr/` (CLI layer)
- 101/101 tests passing
- CLAUDE.md and ARCHITECTURE.md updated for workspace structure
- README added
- Pythonic code review (9/10) — four minor fixes: deepcopy for DEFAULT_CONFIG, unreachable return removed, hardcoded test path fixed, bare filename resolution extracted to `resolve_filename()` in index.py
- **Non-interactive mode** — `rr file` accepts `--name`, `--dir`, `--description` flags; skips prompts when any flag is provided; defaults applied for omitted flags; CLAUDE.md template updated with AI assistant instructions
- **Input validation** — `validate.py` module: `validate_name` (spaces, path separators), `validate_description` (280 chars), `validate_dest_dir` (path traversal guard), `check_overwrite` (overwrite detection). Wired into `file_asset()` and `init_project()`. CLI catches errors; interactive mode prompts for overwrite confirmation. `allow_overwrite` param on `file_asset()`.
- **Consensus-review fixes** (e0398fa) — 5 issues from three-model consensus evaluation: empty-string guard added to `validate_name`, duplicate index entry on overwrite fixed in `add_entry` (replaces in-place instead of appending), plus 3 other edge-case hardening items.
- **ROADMAP.md** created — beta target 2026-03-26, stage 1/2 priorities, beta tester profiles

## What's Next
- **Stage 2 evaluation** — pick beta blockers from candidate list (see ROADMAP.md Stage 2)
- Check SPEC.md for any unimplemented sections or spec drift

## Maintenance Notes
- **Generated CLAUDE.md template** lives in `packages/rr-core/src/rr_core/init.py` (`_claude_md()` function). This is the primary way AI assistants learn how to use rr inside a project. Review and update it whenever commands change or new usage patterns are discovered. Last reviewed: 2026-03-23 (added "Moving Files Between Directories" section after observing Claude attempt a dangerous remove-then-file workflow).

## Open Issues
- See `observed_errors.md` for real-world usage issues
- See `WISHLIST.md` for backlog items

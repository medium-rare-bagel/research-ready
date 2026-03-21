# rr — Handoff

## Last Updated
2026-03-21 — uv workspace refactor complete on branch refactor/uv-workspace

## Current Branch
refactor/uv-workspace — DO NOT merge to main until CLAUDE.md and ARCHITECTURE.md are updated

## What Was Done Today (2026-03-21)
- Restructured repo as a uv workspace with two packages:
  - `packages/rr-core/` — all business logic (init, file, remove, reindex, index, config, git, names)
  - `packages/rr/` — thin CLI layer only (cli.py), depends on rr-core
- Root pyproject.toml is now workspace coordinator only
- 73/73 tests passing (2 new tests added during refactor)
- Branch pushed to GitHub: refactor/uv-workspace

## Still To Do Before Merging Branch
- [ ] Update CLAUDE.md — project layout section is now wrong, add workspace commands
- [ ] Create ARCHITECTURE.md — document the rr-core/rr/rr-gui package boundary and rationale
- [ ] Merge refactor/uv-workspace → main when both docs are done

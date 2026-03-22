# rr — Roadmap

## Beta Target
**Thursday, 2026-03-26** — share with beta testers.

## Beta Testers

| Name | Background | CLI comfort | Has seen MVP | Role |
|------|-----------|-------------|--------------|------|
| Olivia | Data science | Learning | Yes (demo) | Primary user — onboarding stress test |
| Bonny | Former NYT reporter, OSINT lead | Comfortable | Yes (demo) | Primary user — power workflow |
| Auzden | Former AAA game dev | Strong | No | Code quality reviewer |
| Nyx | Geolocation expert | None, no interest | No | Future-state signal (needs non-CLI path) |

## Stage 1 — Must-haves (2026-03-22 morning)

1. ~~**Non-interactive / programmatic mode**~~ **DONE** — CLI flags (`--name`, `--dir`, `--description`) on `rr file`. Prompts skipped when any flag provided; sensible defaults for omitted flags. CLAUDE.md template includes AI assistant instructions. 3 tests passing.
2. ~~**Input validation**~~ **DONE** — `validate.py` module with four functions: `validate_name` (spaces, path separators), `validate_description` (280 chars), `validate_dest_dir` (path traversal), `check_overwrite` (FileExistsError). Wired into `file_asset()` and `init_project()`. CLI catches errors cleanly; interactive mode prompts for overwrite confirmation. 23 new tests, 101 total passing. Broader edge cases (null bytes, Windows reserved names) deferred.

## Stage 2 — Beta blockers (evaluate after Stage 1)

Candidates from wishlist review, to be scoped after Stage 1:
- `modified` field in index entries (spec compliance, low cost)
- Directory picker for `rr file` (one-line `click.Choice` win)
- Post-init welcome message + backup reminder (first impression)
- `rr status` (catch unfiled files)
- `rr tutorial` (onboarding for non-technical users)
- Large file handling (plan schema, even if full build is post-beta)
- Grouped index view (readability at scale)

## Feature Brainstorm — TBD

To be filled in after Stage 1 and Stage 2 evaluation. Goal: decide what fits in the 4-day window before Thursday.

## Post-Beta

- `--no-git` flag (requires end-to-end git-optional support)
- `rr destroy`
- `rr log`
- Git remote support
- Glob support for `rr file`
- `--config` flag for `rr init`

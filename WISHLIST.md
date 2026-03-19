# rr — Wishlist

Feature ideas and future possibilities. Not prioritized, not committed.

## Unindexed file awareness

Files saved directly into tracked directories (bypassing `rr file`) are invisible until `rr reindex`. Two options considered: (1) auto-triggered reindex, (2) status reporting (e.g., `rr status` or a note printed after other commands showing count of unindexed files). Leaning toward Option 2 — fits rr's explicit, user-driven design better. Not locked in yet.

## Obsidian-compatible link format (OBS-001)

Standard markdown links in `index.md` don't open non-markdown files in Obsidian; they create empty new notes instead. Need to decide: wikilinks (`[[path|name]]`), configurable format in `project.yaml`, or dual output. Evaluate during planning session 2026-03-22. See `observed_errors.md` OBS-001 for details.

## Git remote support

Option to configure and push to a git remote (GitHub, NAS, bare repo on external drive, etc.). Since rr already auto-commits every operation, adding remote sync would give users offsite backup and collaboration without needing a separate backup tool. Could be as simple as `rr remote set <url>` and an auto-push after each commit, or a manual `rr push`. Worth scoping during roadmap review.

## Large file handling

Git auto-commit means every filed asset gets stored in git history. For projects with video or other large binaries, this will bloat `.git/` fast (git's delta compression doesn't help with binaries). Leading option: a `git.max_file_size` setting in `project.yaml` that auto-adds files above the threshold to `.gitignore` while still tracking them in `index.json`. Keeps the index as the provenance record without bloating the repo. Other options considered: Git LFS (adds dependency), selective staging. Evaluate during roadmap planning.

## `rr init` customization

Currently `rr init` stamps out a fixed default structure. Ideas for making it more flexible:
- Interactive prompt to accept default directories or specify custom ones (comma-separated).
- LLM context file flexibility: `--no-llm` flag to skip `CLAUDE.md`, or a config key (`llm.context_file`) to generate for other tools (Cursor, Windsurf, etc.) or skip entirely. If going LLM-agnostic, the template content should be generic project context, not Claude-specific. A `--no-llm` flag is the 80/20 solution.
- The `--config` flag is already in the spec but unimplemented — could serve as the power-user path for full template control.
- Keep it simple: sensible defaults, minimal prompts, easy to just hit enter through.

## Backup reminder on init

Display a one-liner after project creation: "rr uses git for history tracking, not as a backup system. Consider setting up a remote or external backup for this project." Low-effort nudge that sets expectations at the right moment.

## Post-init welcome message

`rr init` currently prints a single line (`Initialized project: {name}`). For a user's first encounter with the tool — or after a break — that's not enough context. Add a brief post-init summary showing what was created (directories, key files) and the main commands (`rr file`, `rr remove`, `rr reindex`). Keep it to 6-8 lines of plain `click.echo` output — no new dependencies. Click's built-in `click.style()` is sufficient for any emphasis needed. Detail the exact output format during roadmap planning.

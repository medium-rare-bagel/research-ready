# rr — Wishlist

Feature ideas and future possibilities. Not prioritized, not committed.

## Directory picker for `rr file`

The destination directory prompt is free-text with a hardcoded default of `"sources"`. The user has to type the directory name with no visibility into what's available. Since `allowed_dirs` is already loaded from `project.yaml`, switching to `click.Choice(allowed_dirs)` would give tab-completion and input validation for free — one-line change. For a full interactive arrow-key menu, a dependency like `questionary` would be needed; `click.Choice` is the 80/20 solution.

## `rr edit`

Update metadata on an existing index entry without touching the file itself. Primary use case: changing a description after filing (`rr edit <filename> --description "better description"`). Could also support updating tags once those are actively used. Should match by filename (or path if ambiguous) and modify the entry in `index.json` in place, regenerate `index.md`, and git commit. Needs to handle the case where multiple entries share a filename (different directories) — either require `--dir` to disambiguate or prompt.

## `rr status`

Same mental model as `git status` — "what needs attention?" Scans tracked directories for files not present in `index.json` and lists them with actionable hints (e.g., `run 'rr file <path>' to index`). Strictly read-only — no automatic mutations. Useful for sanity-checking before switching projects or sharing with collaborators. Subsumes the earlier "unindexed file awareness" idea.

## `rr info`

Read-only project overview — "what is this project?" Displays project name, directory structure from `project.yaml`, count of indexed files, and last commit timestamp. Useful for orientation after a break or for onboarding a collaborator. Could also surface index health (entries pointing to missing files).

## Glob support for `rr file`

`rr file downloads/*.pdf` instead of filing one asset at a time. Low implementation cost with Click's existing argument handling; high daily-use payoff on projects with bulk ingest. Needs a decision on how to handle destination directory and description when multiple files are filed at once (prompt per file, single shared destination, or skip descriptions).

## `rr log`

Thin wrapper around `git log --oneline` scoped to the project root. Surfaces the provenance record rr is already building without requiring git literacy from collaborators. Good for sharing a project timeline or reviewing what was filed and when.

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

## `--no-git` and `--config` flags for `rr init`

Both are spec'd (SPEC.md lines 58-59) but not implemented. `--no-git` also requires end-to-end support: `file`, `remove`, and `reindex` currently call git unconditionally, so they'd need to check whether the project is a git repo before calling git operations. Without this, a no-git project would crash on the first file operation.

## `modified` field in index.json entries

The spec schema includes a `modified` field on index entries, but it's not populated by any current code path.

## Partial state on git failure

Git operations are the last step in `file_asset`, `remove_asset`, and `reindex`, but filesystem and index changes happen first with no rollback. If a git commit fails (lock contention, disk full, corrupted repo), the file is already moved/deleted and the index already updated — but nothing is committed. `git_commit_all` itself is two subprocess calls (`git add -A` then `git commit`), so a failure between them leaves staged-but-uncommitted changes. Options: try/except with rollback, journaling, or at minimum a clear warning that uncommitted changes remain.

## Input validation

No validation exists on user-supplied names or values. Project names (`rr init`), file names and descriptions (`rr file`), and destination directories all pass through unsanitized. Risks include path traversal (`../../etc`), empty strings, OS-reserved names (`CON`, `NUL`), null bytes, names exceeding filesystem limits (~255 bytes), and shell metacharacters. `project.yaml` is also loaded and trusted without validation. Additionally, `rr file` will silently overwrite an existing file at the destination (`shutil.move` behavior) and append a duplicate index entry — no existence check or confirmation. Specific concern: the destination directory in `rr file` should be explicitly verified to resolve inside the project root (`dest_dir.resolve().is_relative_to(project.root)`). The current `allowed_dirs` check catches traversal attempts by accident (it compares `dest_dir.name` against the list), but there's no intentional guard — a future refactor could easily break that incidental protection. The natural approach is a validation layer in `rr-core` that all entry points call before passing data to business logic. Scope the specific checks during brainstorming.

## Post-init welcome message

`rr init` currently prints a single line (`Initialized project: {name}`). For a user's first encounter with the tool — or after a break — that's not enough context. Add a brief post-init summary showing what was created (directories, key files) and the main commands (`rr file`, `rr remove`, `rr reindex`). Keep it to 6-8 lines of plain `click.echo` output — no new dependencies. Click's built-in `click.style()` is sufficient for any emphasis needed. Detail the exact output format during roadmap planning.

# rr — Wishlist

Feature ideas and future possibilities. Not prioritized, not committed.

---

## New Commands

### `rr edit`

Update metadata on an existing index entry without touching the file itself. Primary use case: changing a description after filing (`rr edit <filename> --description "better description"`). Could also support updating tags once those are actively used. Should match by filename (or path if ambiguous) and modify the entry in `index.json` in place, regenerate `index.md`, and git commit. Needs to handle the case where multiple entries share a filename (different directories) — either require `--dir` to disambiguate or prompt.

### `rr status`

Same mental model as `git status` — "what needs attention?" Scans tracked directories for files not present in `index.json` and lists them with actionable hints (e.g., `run 'rr file <path>' to index`). Strictly read-only — no automatic mutations. Useful for sanity-checking before switching projects or sharing with collaborators. Subsumes the earlier "unindexed file awareness" idea.

### `rr info`

Read-only project overview — "what is this project?" Displays project name, directory structure from `project.yaml`, count of indexed files, and last commit timestamp. Useful for orientation after a break or for onboarding a collaborator. Could also surface index health (entries pointing to missing files).

### `rr log`

Thin wrapper around `git log --oneline` scoped to the project root. Surfaces the provenance record rr is already building without requiring git literacy from collaborators. Good for sharing a project timeline or reviewing what was filed and when.

### `rr tutorial`

Interactive walkthrough that teaches rr's philosophy and discipline by doing. Creates a temporary practice project, walks the user through real operations (init, file, inspect, remove, reindex), and cleans up at the end. Built entirely with Click primitives: `click.echo()`/`click.style()` for explanatory text, `click.pause()` to pace sections, `click.confirm()` for gates. Key design decisions:
- **Show everything inline** — after each step, print the directory tree, cat the index, show the git log. The user never needs to inspect anything themselves.
- **Obsidian setup tip** — mention that users should enable **Settings → Files and Links → Detect all file extensions** in Obsidian so that links to non-`.md` files work. Natural place for this is right after the init step or in a dedicated "Obsidian integration" section.
- **Auto-cleanup** — end with `click.confirm("Delete the practice project?")` and `shutil.rmtree()`. No `rm -rf` knowledge required.
- Sits above the post-init welcome message in scope: the welcome message is "here's what was created," the tutorial is "here's why rr works this way, let's do it together."

### `rr destroy`

Tear down an entire rr project: remove the directory tree, index files, git repo — everything `rr init` created. Requires explicit confirmation (`click.confirm` with project name echo). Currently there's no way to remove a whole project without `rm -rf`, which is hostile to non-technical users. The `rr tutorial` cleanup need highlights this gap, but `rr destroy` is useful independently for any project the user wants to discard. **Beta note:** consider scoping `rr destroy` as tutorial-internal-only initially rather than a general user command, to reduce footgun risk.

### `rr search`

Search descriptions, filenames, and tags in `index.json`. Usage: `rr search <term>`. Case-insensitive substring match across entry fields. For a research tool, being able to find "that PDF about the Costa Rica incident" by searching descriptions is a core workflow. All the data is already in `index.json` — this is a read-only query with no filesystem side effects. Could later support `--tag`, `--dir`, or regex filters.

### Programmatic / non-interactive mode

The entire rr-core extraction exists so that programmatic callers (Claude Code CLI, scripts, future GUI) can use rr without hitting Click's interactive prompts. The missing piece: a way to pass all answers upfront via CLI flags. Example: `rr file document.pdf --name "2026-03-21-report.pdf" --dir sources --description "SOUTHCOM press release"`. When all required values are provided as flags, skip the interactive prompts entirely. When some are missing, prompt only for those. This is the concrete payoff of the rr-core / rr split and should be one of the first things built — without it, rr can't be used as a tool by any automated caller.

---

## Enhancements to Existing Commands

### Directory picker for `rr file`

The destination directory prompt is free-text with a hardcoded default of `"sources"`. The user has to type the directory name with no visibility into what's available. Since `allowed_dirs` is already loaded from `project.yaml`, switching to `click.Choice(allowed_dirs)` would give tab-completion and input validation for free — one-line change. For a full interactive arrow-key menu, a dependency like `questionary` would be needed; `click.Choice` is the 80/20 solution.

### Glob support for `rr file`

`rr file downloads/*.pdf` instead of filing one asset at a time. Low implementation cost with Click's existing argument handling; high daily-use payoff on projects with bulk ingest. Needs a decision on how to handle destination directory and description when multiple files are filed at once (prompt per file, single shared destination, or skip descriptions).

### `rr init` customization

Currently `rr init` stamps out a fixed default structure. Ideas for making it more flexible:
- Interactive prompt to accept default directories or specify custom ones (comma-separated).
- LLM context file flexibility: `--no-llm` flag to skip `CLAUDE.md`, or a config key (`llm.context_file`) to generate for other tools (Cursor, Windsurf, etc.) or skip entirely. If going LLM-agnostic, the template content should be generic project context, not Claude-specific. A `--no-llm` flag is the 80/20 solution.
- The `--config` flag is already in the spec but unimplemented — could serve as the power-user path for full template control.
- Keep it simple: sensible defaults, minimal prompts, easy to just hit enter through.

### `--no-git` and `--config` flags for `rr init`

Both are spec'd (SPEC.md lines 58-59) but not implemented. `--no-git` also requires end-to-end support: `file`, `remove`, and `reindex` currently call git unconditionally, so they'd need to check whether the project is a git repo before calling git operations. Without this, a no-git project would crash on the first file operation.

### Post-init welcome message

`rr init` currently prints a single line (`Initialized project: {name}`). For a user's first encounter with the tool — or after a break — that's not enough context. Add a brief post-init summary showing what was created (directories, key files) and the main commands (`rr file`, `rr remove`, `rr reindex`). Keep it to 6-8 lines of plain `click.echo` output — no new dependencies. Click's built-in `click.style()` is sufficient for any emphasis needed. Detail the exact output format during roadmap planning. Should also include an Obsidian tip: if the project will live in an Obsidian vault, enable **Settings → Files and Links → Detect all file extensions** so links to non-`.md` files (PDFs, .txt, etc.) resolve correctly.

### Tags end-to-end

Tags exist in the index schema but nothing writes to them and nothing uses them. Full support means: `rr file --tags "source,press-release"` to set tags on filing, `rr edit --tags` to update them later, `rr search --tag source` to filter by tag, and display tags in `index.md`. For OSINT work, tagging files by source type, date range, or topic is a natural workflow. The schema is ready — this is wiring up the read/write paths and surfacing tags in the UI.

### Grouped index view

`index.md` is currently a flat table. Once a project hits 30+ files across multiple directories, it gets unwieldy. Generate the markdown grouped by directory with section headers instead of (or in addition to) the flat table. Small change to `generate_index_md`, high daily-use value.

### Backup reminder on init

Display a one-liner after project creation: "rr uses git for history tracking, not as a backup system. Consider setting up a remote or external backup for this project." Low-effort nudge that sets expectations at the right moment.

---

## Data Integrity & Safety

### Input validation

No validation exists on user-supplied names or values. Project names (`rr init`), file names and descriptions (`rr file`), and destination directories all pass through unsanitized. Risks include path traversal (`../../etc`), empty strings, OS-reserved names (`CON`, `NUL`), null bytes, names exceeding filesystem limits (~255 bytes), and shell metacharacters. `project.yaml` is also loaded and trusted without validation. Additionally, `rr file` will silently overwrite an existing file at the destination (`shutil.move` behavior) and append a duplicate index entry — no existence check or confirmation. Specific concern: the destination directory in `rr file` should be explicitly verified to resolve inside the project root (`dest_dir.resolve().is_relative_to(project.root)`). The current `allowed_dirs` check catches traversal attempts by accident (it compares `dest_dir.name` against the list), but there's no intentional guard — a future refactor could easily break that incidental protection. The natural approach is a validation layer in `rr-core` that all entry points call before passing data to business logic. Scope the specific checks during brainstorming.

**Filename space enforcement:** `suggest_filename` in `names.py` should normalize spaces to underscores when generating the default (e.g., `VOI list.csv` → `VOI_list-2026-03-22.csv`). The "New name" prompt in `cli.py` should reject names containing spaces with a hint: "Spaces not allowed in filenames. Try underscores, hyphens, or camelCase." Keeps filenames clean for cross-platform compatibility and URL/path safety.

**Description length limit:** Hard cap at 280 characters on the description prompt in `cli.py`. If the user exceeds it, re-prompt: "Description too long (N/280 chars). Keep it to a single sentence." Keeps `index.md` table rows scannable. 280 chars (Twitter-length) is enough for a meaningful sentence without wrecking table layout.

### Partial state on git failure

Git operations are the last step in `file_asset`, `remove_asset`, and `reindex`, but filesystem and index changes happen first with no rollback. If a git commit fails (lock contention, disk full, corrupted repo), the file is already moved/deleted and the index already updated — but nothing is committed. `git_commit_all` itself is two subprocess calls (`git add -A` then `git commit`), so a failure between them leaves staged-but-uncommitted changes. Options: try/except with rollback, journaling, or at minimum a clear warning that uncommitted changes remain.

### Large file handling

Git auto-commit means every filed asset gets stored in git history. For projects with video or other large binaries, this will bloat `.git/` fast (git's delta compression doesn't help with binaries). Leading option: a `git.max_file_size` setting in `project.yaml` that auto-adds files above the threshold to `.gitignore` while still tracking them in `index.json`. Keeps the index as the provenance record without bloating the repo. Other options considered: Git LFS (adds dependency), selective staging. Evaluate during roadmap planning.

---

## Developer Experience

### `rr --version` flag

Print the installed version of rr. Useful for catching stale global installs — if the CLI source changes but the global `uv tool install` isn't re-run, the installed binary silently lags behind. A version flag makes mismatches obvious. Could also include a build hash or timestamp for finer-grained detection.

---

## Infrastructure

### Git remote support

Option to configure and push to a git remote (GitHub, NAS, bare repo on external drive, etc.). Since rr already auto-commits every operation, adding remote sync would give users offsite backup and collaboration without needing a separate backup tool. Could be as simple as `rr remote set <url>` and an auto-push after each commit, or a manual `rr push`. Worth scoping during roadmap review.

### `modified` field in index.json entries

The spec schema includes a `modified` field on index entries, but it's not populated by any current code path.

---

## Resolved

### ~~Obsidian-compatible link format (OBS-001)~~

Not an rr bug. Obsidian only detects `.md` files by default. Enabling **Settings → Files and Links → Detect all file extensions** makes standard markdown links work for all file types. No code changes needed. See `observed_errors.md` OBS-001. The `rr init` post-init message and `rr tutorial` should mention this setting (see those entries).

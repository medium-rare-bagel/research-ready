# rr — Research Ready

## Project Specification v0.1

### What is rr?

`rr` is a Python CLI tool that scaffolds and manages research project workspaces. It creates a structured directory with an asset index, git history, and a Claude Code configuration — so a new research project is immediately ready for work.

The target user is an OSINT/conflict monitoring researcher who works across investigative projects (Airwars, Bellingcat-style), personal research, and freelance work. The tool should be general enough to serve any research workflow but opinionated enough to be useful out of the box.

### Design Principles

1. **Shallow structure.** One level of subdirectories. Depth creates friction and reduces visibility.
2. **Index over taxonomy.** Don't organize files into deep folder trees — file them flat and track metadata in an index.
3. **Configuration-driven.** The project structure is defined in a YAML config file. Changing the structure means editing the config, not refactoring code.
4. **Git as audit trail.** Every file operation auto-commits. The git log is the project's provenance record.
5. **Pythonic.** Clean, idiomatic Python. Type hints. No unnecessary abstractions.

---

## CLI Interface

The tool is invoked as `rr` with subcommands:

### `rr init <project-name>`

Creates a new research project directory.

**What it does:**
1. Creates the project directory named `<project-name>`
2. Initializes a git repository
3. Creates the directory structure defined in `project.yaml`
4. Generates `project.yaml` with default configuration
5. Generates `CLAUDE.md` tailored to the project
6. Generates an empty `index.json` (empty files array)
7. Generates `index.md` from `index.json` (table headers, no rows)
8. Creates a `.gitignore` (Python defaults + OS files)
9. Makes an initial git commit ("Initialize project: <project-name>")

**Default directory structure:**

```
<project-name>/
├── project.yaml          # Project configuration
├── CLAUDE.md             # Claude Code context file
├── index.json            # Asset index (source of truth)
├── index.md              # Asset index (generated view)
├── .gitignore
├── inbox/                # Holding pen for unfiled materials
├── sources/              # Filed, named research materials
├── analysis/             # Notes, working documents, findings
├── output/               # Deliverables — reports, drafts, visualizations
├── shared/               # Materials sent to others (colleagues, editors, sources)
└── scripts/              # Project-specific scripts
```

**Options:**
- `--config <path>`: Use a custom project.yaml template instead of the default
- `--no-git`: Skip git initialization (for edge cases)

**Global option (available on all commands):**
- `--verbose` / `-v`: Show debug-level log output

### `rr file <path-to-file>`

Files a document from the inbox (or anywhere) into the project and updates the index.

**What it does:**
1. Prompts the user for:
   - **New filename** (suggests a default based on original name + date)
   - **Destination directory** (defaults to `sources/`, shows options from config)
   - **Description** (one-line, for the index)
2. Renames and moves the file to the chosen directory
3. Adds an entry to `index.md`
4. Git commits: "File: <filename> → <destination>"

**Example interaction:**
```
$ rr file inbox/IMG_20240315_satellite.png

  Current name: IMG_20240315_satellite.png
  New name [IMG_20240315_satellite.png]: maxar-site-alpha-2024-03-15.png
  Destination [sources/]: sources/
  Description: Maxar satellite imagery of Site Alpha, March 2024

  ✓ Moved to sources/maxar-site-alpha-2024-03-15.png
  ✓ Index updated
  ✓ Committed: "File: maxar-site-alpha-2024-03-15.png → sources/"
```

### `rr remove <path-to-file>`

Removes a file from the project and updates the index.

**What it does:**
1. Confirms removal with the user (shows filename + index description)
2. Deletes the file
3. Removes the entry from `index.json` and regenerates `index.md`
4. Git commits: "Remove: <filename>"

**Note:** The file is recoverable via `git checkout` since every prior state is committed.

### `rr reindex`

Rebuilds the index from the current state of the filesystem.

**What it does:**
1. Scans all directories listed in `project.yaml` under `index.tracked_dirs`
2. For files already in the index: preserves existing metadata (description, date)
3. For files found on disk but not in the index: adds them with date = file modification time, description = "(no description)"
4. For files in the index but not on disk: removes them from the index
5. Reports what changed (added, removed, unchanged)
6. Git commits: "Reindex: +N added, -N removed"

---

## Configuration: project.yaml

```yaml
project:
  name: "my-project"
  created: "2026-03-18"

structure:
  directories:
    - inbox
    - sources
    - analysis
    - output
    - shared
    - scripts

index:
  file: index.md
  tracked_dirs:
    - sources
    - analysis
    - output
    - shared
    - scripts

git:
  auto_commit: true
```

**Extending the structure:** Adding a new directory means adding it to `structure.directories` (and optionally `index.tracked_dirs`), then running `rr reindex`. The tool creates any missing directories on reindex.

---

## Index System

The project maintains a dual index: `index.json` is the source of truth, and `index.md` is a human-readable view generated from it.

### index.json (Source of Truth)

```json
{
  "last_rebuilt": "2026-03-18",
  "files": [
    {
      "filename": "maxar-site-alpha-2024-03-15.png",
      "directory": "sources",
      "path": "sources/maxar-site-alpha-2024-03-15.png",
      "description": "Maxar satellite imagery of Site Alpha, March 2024",
      "added": "2026-03-18",
      "modified": "2026-03-18",
      "tags": []
    },
    {
      "filename": "parse_casualty_data.py",
      "directory": "scripts",
      "path": "scripts/parse_casualty_data.py",
      "description": "Parses UN casualty CSV into timeline format",
      "added": "2026-03-18",
      "modified": "2026-03-18",
      "tags": []
    }
  ]
}
```

All paths are **relative to the project root**. This keeps projects portable across machines. Tooling resolves absolute paths at runtime.

**Why JSON as source of truth:**
- Unambiguous to parse (markdown tables have edge cases with pipes, alignment)
- Naturally extensible — add fields later without reformatting
- Claude Code works more reliably with structured data
- Tags field is included but empty for now — ready when needed

### index.md (Generated View)

Regenerated from `index.json` whenever the index changes. Never hand-edited.

```markdown
# Project Index

Last rebuilt: 2026-03-18

| File | Directory | Added | Description |
|------|-----------|-------|-------------|
| [maxar-site-alpha-2024-03-15.png](sources/maxar-site-alpha-2024-03-15.png) | sources | 2026-03-18 | Maxar satellite imagery of Site Alpha, March 2024 |
| [un-report-q4-2025.pdf](sources/un-report-q4-2025.pdf) | sources | 2026-03-18 | UN quarterly monitoring report |
| [timeline-draft.md](analysis/timeline-draft.md) | analysis | 2026-03-19 | Working timeline of events |
| [briefing-airwars-march.pdf](shared/briefing-airwars-march.pdf) | shared | 2026-03-20 | Monthly briefing sent to Airwars editorial |
| [parse_casualty_data.py](scripts/parse_casualty_data.py) | scripts | 2026-03-18 | Parses UN casualty CSV into timeline format |
```

**Why also markdown:**
- Human-readable in any text editor, GitHub, or Obsidian
- Relative markdown links are clickable in Obsidian and GitHub
- Git-diffable (changes show clearly in diffs)
- Useful as a quick reference without tooling

### Obsidian Compatibility

The generated `index.md` uses standard markdown links (`[name](path)`) which Obsidian renders as clickable links. If the project directory is inside or symlinked into an Obsidian vault, the index becomes a navigable hub for the project's assets. Any `.md` files in `analysis/` are also directly browseable as Obsidian notes.

Future consideration: if tags are added to the index, they could be generated in Obsidian-compatible `#tag` format.

---

## CLAUDE.md (Generated)

The generated CLAUDE.md should contain:

```markdown
# Project: <project-name>

## Structure
This project uses `rr` (Research Ready) for workspace management.
See `project.yaml` for the directory structure configuration.

## Key Files
- `index.json` — Asset index (source of truth). Updated by `rr file`, `rr remove`, `rr reindex`.
- `index.md` — Human-readable index (generated from index.json). Do not hand-edit.
- `project.yaml` — Project structure and configuration.

## Conventions
- All scripting in Python. Use `uv` for package management and tooling.
- The `inbox/` directory is a holding pen for unfiled materials.
- Filed assets go in `sources/`, `analysis/`, `output/`, `shared/`, or `scripts/`.
- `shared/` tracks materials sent to others — use the description to note the recipient.
- `scripts/` holds project-specific scripts — use the description to note what each does.
- Every file operation is auto-committed to git.

## Tools
This project was scaffolded with `rr`. Available commands:
- `rr file <path>` — Rename, move, and index a file
- `rr remove <path>` — Remove a file and update the index
- `rr reindex` — Rebuild the index from filesystem state
```

---

## Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | Python 3.12+ | User preference, ecosystem fit |
| Package manager | uv | User preference, modern Python tooling. `uv` is used to develop and run `rr` itself; projects created by `rr init` are research workspaces, not Python packages. |
| CLI framework | Click | Explicit control over prompts and options; well-documented; no magic. `rr file` needs interactive prompting that Click handles cleanly. |
| Config format | YAML | Human-editable, widely understood |
| Index format | JSON (source of truth) + Markdown (generated view) | JSON for reliable parsing and extensibility; Markdown for human/Obsidian readability |
| VCS | Git (auto-commit) | Audit trail, recovery, provenance |
| Testing | pytest + red/green TDD | Spec-driven, tests written first |
| Logging | Python `logging` module | Lightweight, debuggable, no external deps |

---

## Logging

The tool uses Python's built-in `logging` module. The goal is not comprehensive observability — it's "enough that Claude Code can help debug a problem from the log output."

**Two audiences, two levels:**

- **User-facing feedback** (`INFO`): What the tool did. Printed to stdout during normal operation. Examples: "✓ Created project directory", "✓ Index updated", "✓ Committed: File: report.pdf → sources/".
- **Debug detail** (`DEBUG`): What the tool is doing internally. Hidden by default, visible with `--verbose` flag. Examples: "Reading project.yaml from /path/to/project.yaml", "Parsing index.json: found 12 entries", "Git commit SHA: a3f2b1c".

**Implementation:**

- Each module gets its own logger: `logger = logging.getLogger(__name__)`
- Default level is `INFO` — user sees confirmations and errors
- `--verbose` flag on any command sets level to `DEBUG`
- Log format is simple: just the message for INFO, timestamp + module + message for DEBUG
- No log files. Everything goes to stderr (so stdout stays clean for any future piped output)

**What to log at DEBUG level:**
- Config file reads/writes (path, key values)
- Index operations (entries added, removed, preserved during reindex)
- Git operations (commands run, commit SHAs)
- File operations (source path, destination path, sizes)

**What NOT to log:**
- File contents
- Anything that would clutter the output during normal use

---

## Input Constraints & Validation

These rules apply to filenames in `rr file` and project names in `rr init`.

- **Filenames / project names:**
  - No spaces
  - No path separators (`/`, `\`)
  - No control characters (0x00–0x1F) or null bytes
  - No OS-reserved names (CON, PRN, AUX, NUL, COM1–9, LPT1–9 — case-insensitive, with or without extension)
  - Max 255 characters
- **Descriptions:** Max 280 characters
- **Destination directory:**
  - Must be a configured directory from `project.yaml` (`allowed_dirs` check)
  - Must resolve inside the project root (path traversal guard)
- **Overwrite:**
  - Interactive mode: detect and confirm before overwriting
  - Non-interactive mode: error if destination file already exists (no `--force` flag for beta)

---

## What This Tool Is NOT

- Not a database. The index is a JSON file and a generated markdown view.
- Not a media manager. It doesn't generate thumbnails, extract metadata from images, or transcode files.
- Not a collaboration tool. It's single-user, local-first.
- Not opinionated about research methodology. It organizes files; it doesn't tell you how to do research.

---

## Development Approach

**Spec-driven TDD:**
1. This spec defines acceptance criteria for each command
2. Each command gets tests written BEFORE implementation
3. Tests assert behavior described in this spec
4. Implementation is the minimum code to pass tests
5. Refactor after green

**Build order:**
1. `rr init` — foundational, everything else depends on a project existing
2. `rr file` — the most-used command, core workflow
3. `rr reindex` — safety net, needed before `remove` makes sense
4. `rr remove` — simplest command, but needs index operations from `file` and `reindex`

---

## Open Questions (To Resolve During Implementation)

1. **File naming conventions:** Should `rr file` enforce any naming pattern (e.g., date prefix)? Current spec: suggest but don't enforce.
2. **Inbox cleanup:** Should `rr file` warn if inbox is getting large? Nice-to-have, not MVP.

## Future: Google Drive Integration

Flagged for future development. The tool may eventually support syncing or tracking files that live in Google Drive alongside local files.

### Design implications for now (MVP)

- Keep index operations (`index.py`) cleanly separated from filesystem operations (`file.py`). The index should not assume files are always local.
- The index format may eventually need a column or field for location/URL. For now, the `Directory` column serves this role for local files. A future version could add a `Location` column that accepts either a local path or a Drive URL.
- No code changes needed for MVP. Just maintain the separation of concerns.

### Multi-account and credentials (future)

The user works across multiple contexts (Airwars, personal, freelance) which may involve different Google accounts. Future implementation must support:

- **Multiple Google account profiles** — a project should be able to specify which account it uses, not assume a single global credential.
- **Credential storage following best practices** — OAuth tokens should never be stored in the project directory or committed to git. Use OS-level secure storage (e.g., system keyring via `keyring` library) or a well-known config directory (`~/.config/rr/`).
- **Credentials out of project.yaml** — the project config may reference an account *name* or *profile*, but never contain tokens, secrets, or API keys directly. A separate, git-ignored, user-level config handles the mapping from profile name to credentials.
- **`.gitignore` awareness** — any future credential-adjacent files must be covered by `.gitignore` from day one. The current MVP `.gitignore` should already exclude common patterns (`.env`, `*.key`, etc.) as a safety net.

Practical design: something like `~/.config/rr/accounts.yaml` that maps profile names to OAuth credentials, and `project.yaml` just says `drive_account: airwars` or `drive_account: personal`.

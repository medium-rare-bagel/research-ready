# rr — Observed Errors

Errors and issues encountered during real-world usage of rr.
Collected for review during planning session (2026-03-22).

Resolved entries stay here until after planning, then get cleared.

---

## OBS-001 — Obsidian file links open empty notes instead of actual files

**Discovered:** 2026-03-18
**Status:** Resolved (2026-03-21)
**Severity:** Usability — core workflow broken in Obsidian

**What happened:**
Clicking a file link in `index.md` within Obsidian opens a blank new note instead of opening the actual file. Specifically affected `.txt` files — links wouldn't resolve.

**Root cause:**
Obsidian by default only detects `.md` files. Non-markdown files like `.txt` don't appear in the vault's file explorer or resolve as link targets unless you enable **Settings → Files and Links → Detect all file extensions**. This wasn't an rr bug — it was a vault configuration issue.

**Resolution:**
Toggle on **Detect all file extensions** in Obsidian settings (Settings → Files and Links). After enabling, `.txt` files appear in the vault file explorer and links resolve correctly. Note that non-markdown files won't get full markdown rendering/linking features, but they open and display as expected.

**No code changes needed.** The existing standard markdown link format `[name](relative/path.txt)` works correctly once the vault setting is enabled.

---

## OBS-002 — Generated CLAUDE.md uv guidance too weak; Claude uses system python

**Discovered:** 2026-03-22
**Status:** Open
**Severity:** Usability — Claude ignores project conventions

**What happened:**
User set up an rr project and asked Claude Code to write a script. Claude wrote the script directly (skipping `uv init`), then tried running it with system python instead of `uv run`. This caused dependency errors and wasted tokens. Claude only course-corrected after the user intervened, acknowledging the CLAUDE.md instruction it had ignored.

**Root cause:**
The `_claude_md` template in `init.py` (line 60) buries the uv instruction as a single bullet in the "Conventions" section: `"All scripting in Python. Use uv for package management and tooling."` This lacks:
- A prominent heading (compare "Non-Interactive Mode (IMPORTANT)" which works well)
- Negative instructions ("do NOT use pip", "do NOT use system python")
- Example commands (`uv init`, `uv add`, `uv run`)

**Proposed fix:**
Add a dedicated `## Python & uv (IMPORTANT)` section to the generated CLAUDE.md template, modeled on the non-interactive mode section. Include negative instructions and example commands. Pattern already proven effective in rr's own CLAUDE.md ("uv Rules — READ THIS FIRST").

---

## OBS-003 — Subdirectory nesting within allowed directories

**Discovered:** 2026-03-29
**Status:** Open
**Severity:** Design gap — spec vs. real user behavior

**What happened:**
Spec enforces "shallow structure — one level of subdirectories" as a design principle, but users naturally create nested directories for organization (e.g., `sources/videos`, `analysis/2024-reports`, `output/drafts`). Currently, `rr file` validates against the exact directories in `project.yaml` and rejects subdirectories.

**Root cause:**
Design principle prioritizes flat organization via metadata index over folder hierarchy, but users expect filesystem organization to work naturally. The strict validation prevents convenient workflows.

**Decision needed:**
Should `rr file` accept any subdirectory of an allowed directory, or enforce flat structure strictly?

**Option 1 (strict, current):** Keep rejecting subdirectories. Users organize via index metadata and tags, not folder nesting. Maintains design principle but conflicts with user expectations.

**Option 2 (permissive):** Allow `rr file inbox/doc.pdf --dir sources/videos`. Requires updating `validate_dest_dir()` to check path containment (dest is under an allowed directory) rather than exact match. Index tracks full path (`sources/videos/doc.pdf`). Users can organize via folders naturally.

**Impact:** No schema changes needed. The index.json already stores paths and would benefit from hierarchical grouping in generated index.md (group entries by directory with headers).

---

## OBS-004 — Index entries lack unique identifiers

**Discovered:** 2026-03-29
**Status:** Open
**Severity:** Spec gap — will break future features and programmatic access

**What happened:**
Index entries are identified by the combination of `filename` + `directory`, but this is insufficient as a unique key.

**Problems this causes:**

1. **Duplicate filenames across directories** — `sources/report.pdf` and `analysis/report.pdf` both have `filename: "report.pdf"`. Can distinguish by directory, but no reliable single identifier.

2. **`rr edit` ambiguity** — When implementing the wishlist feature to update descriptions/tags, which entry do you edit if names collide?

3. **Programmatic reference** — Claude Code and future GUIs need a stable way to reference "that specific entry" without relying on filename (which can change).

4. **File history/moves** — No way to track a single file's history if it's renamed or moved to a different directory.

5. **Conflict resolution** — If two operations try to modify the same entry simultaneously (edge case), there's no reliable way to detect it.

**Solution:**
Add a `"id"` field to each entry (UUID or similar). Generated on entry creation, persisted across renames/moves, never reused.

**Schema change:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "maxar-site-alpha-2024-03-15.png",
  "directory": "sources",
  "path": "sources/maxar-site-alpha-2024-03-15.png",
  "description": "...",
  "added": "2026-03-18",
  "modified": "2026-03-18",
  "tags": []
}
```

**Impact:**
- Breaking change to index.json schema — existing projects need migration.
- `rr reindex` should generate IDs for entries that lack them.
- All lookups (`remove`, `edit`, future features) should use `id` as the primary key, not filename.

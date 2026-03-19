# rr — Observed Errors

Errors and issues encountered during real-world usage of rr.
Collected for review during planning session (2026-03-22).

Resolved entries stay here until after planning, then get cleared.

---

## OBS-001 — Obsidian file links open empty notes instead of actual files

**Discovered:** 2026-03-18
**Status:** Open
**Severity:** Usability — core workflow broken in Obsidian

**What happened:**
Clicking a file link in `index.md` within Obsidian opens a blank new note instead of opening the actual file. Standard markdown links (`[name](relative/path.pdf)`) don't resolve to non-markdown files in Obsidian.

**Root cause:**
Obsidian treats standard markdown links as references to other notes, not as filesystem paths. For non-`.md` files, Obsidian doesn't resolve `[text](path)` links to actual files on disk — it interprets the path as a note name and creates a new empty note.

**Possible fixes (to evaluate 2026-03-22):**
1. **Wikilinks** — `[[path/to/file.pdf|display name]]` — native Obsidian format, works reliably for all file types
2. **Configurable link format** — let `project.yaml` choose between markdown links and wikilinks
3. **Dual output** — generate both `index.md` (wikilinks for Obsidian) and a second file with standard markdown links

**Workaround:** Open files directly from the file explorer sidebar instead of clicking links in `index.md`.

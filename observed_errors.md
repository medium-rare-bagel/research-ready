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

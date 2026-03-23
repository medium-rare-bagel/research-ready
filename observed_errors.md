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

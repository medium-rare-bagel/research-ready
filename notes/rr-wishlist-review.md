---
tags: [rr, planning, brainstorm]
date: 2026-03-21
status: pre-brainstorm review
---

# rr Wishlist Review — Pre-Brainstorm
> Prepared 2026-03-21 for Sunday 2026-03-22 brainstorming session.
> Three-pass review against repo WISHLIST.md.

> [!note] How to read this table
> **Plain Language** = what the feature is and why you'd want it
> **Critical Take** = honest cost-benefit / YAGNI — is it worth building, and when?

---

## New Commands

| Feature | 💋 Plain Language | ⚖️ Critical Take |
|---------|-------------------|------------------|
| `rr edit` | Filed a document with a bad description? This lets you fix it without deleting and re-filing. Update descriptions and tags directly. | Low implementation cost. Useful but not beta-blocking — you can remove and re-file as a workaround. Include in beta if tags become a real workflow. |
| `rr status` | A "did I miss anything?" command. Scans your project folders and tells you which files haven't been formally indexed yet. Read-only, no changes. | High value for non-technical users who drop files in folders without using `rr file`. Prevents index rot. Worth including for beta. |
| `rr info` | A quick dashboard: project name, directory structure, file count, last commit timestamp. Good for orienting yourself after a break. | Overlaps with what `index.md` already shows. Useful but not urgent. Moderate priority — post-beta is fine. |
| `rr log` | See the history of what was filed and when, without needing to know any git commands. | YAGNI if users have any git literacy. High value if target beta users are truly non-technical. Implementation is trivial (thin git wrapper). Decide based on who your first beta users actually are. |
| `rr tutorial` | A guided first-run experience. Creates a safe practice project, walks you through all commands by actually doing them, then cleans up. Includes an Obsidian setup tip (enable "Detect all file extensions") at the right moment. Users learn by doing, not by reading docs. | High priority for beta. If you're sharing with non-technical OSINT researchers, onboarding is everything. This is how they get started without you holding their hand. |
| `rr destroy` | Safely delete an entire rr project — all files, git history, everything — with confirmation prompts. | YAGNI for beta as a user-facing command. Users can drag to trash. Real footgun risk behind a thin confirmation dialog. Only genuine need is `rr tutorial` cleanup — scope that internally instead. Revisit post-beta if users ask for it. |
| `rr search` | Search your index by description, filename, or tags to find files without scrolling a big table. Case-insensitive, works across all entry fields. | Natural for a research tool. All data already in index.json — read-only query, no side effects. Low implementation cost. Worth doing for beta. |
| Programmatic / non-interactive mode | Right now Claude Code CLI can't use rr because rr asks questions and waits for answers. This adds flags so all answers can be provided upfront: `rr file doc.pdf --name report.pdf --dir sources --description "SOUTHCOM release"`. When all flags are provided, skip prompts entirely. | *High priority.* This is the entire reason for the rr-core refactor done today. Without it, Claude Code can't use rr as a tool. The architecture is ready — this is the next concrete build. |

---

## Enhancements to Existing Commands

| Feature | 💋 Plain Language | ⚖️ Critical Take |
|---------|-------------------|------------------|
| Directory picker for `rr file` | Instead of typing the directory name from memory, you see a list and pick from it. No typos, no guessing what's valid. | One-line change using `click.Choice`. Low cost, high daily-use improvement. Do this for beta. |
| Glob support for `rr file` | File multiple documents at once — `rr file downloads/*.pdf` instead of one at a time. | Power user feature. Adds real complexity around batch prompting (one description per file? shared destination?). Post-beta unless early users specifically ask for it. |
| `rr init` customization | Choose your own directory structure when creating a project. Also: a `--no-llm` flag to skip the CLAUDE.md file if you're not using AI coding tools. | `--no-llm` flag is reasonable for beta (not everyone uses Claude Code). Full custom directories is more complex. Prioritize `--no-llm`, defer full customization. |
| `--no-git` and `--config` flags for `rr init` | `--no-git` creates a project without version history. `--config` lets you load a custom template instead of the defaults — for power users who have a standard project structure they always use. | Both are spec'd but unimplemented. `--no-git` requires updating `file`, `remove`, and `reindex` to handle missing git gracefully — not trivial. `--config` is a power-user feature. Medium priority overall; prioritize `--no-git` if beta users need it. |
| Post-init welcome message | Right now `rr init` prints one line and goes silent. This adds a 6-8 line summary showing what directories were created, what key files exist, and the main commands to run next. Includes the Obsidian tip about enabling file extension detection. | Low cost, high first-impression value. A new user's first interaction with the tool is `rr init` — if they don't know what to do next, they're stuck. Do this for beta. |
| Backup reminder on init | A one-liner displayed after project creation: "rr uses git for history tracking, not as a backup system. Consider setting up a remote or external backup." Sets correct expectations at exactly the right moment. | Trivial to implement (one `click.echo`). High value for non-technical users who might assume git = backup. Do this alongside the post-init welcome message. |
| Tags end-to-end | Tags exist in the index schema but nothing writes them and nothing searches by them. Full wiring: set tags on `rr file`, update with `rr edit`, filter with `rr search --tag`. | Builds on `rr edit` and `rr search`. Plan the end-to-end flow now so `rr edit` is designed with tags in mind. Medium priority. |
| Grouped index view | index.md is one flat table. Once a project hits 30+ files, grouping by directory with section headers makes it much easier to navigate in Obsidian. | Small change to `generate_index_md`, high daily-use payoff on larger projects. Low cost. |

---

## Data Integrity & Safety

| Feature | 💋 Plain Language | ⚖️ Critical Take |
|---------|-------------------|------------------|
| Input validation | Prevents bad inputs from causing problems: empty names, accidentally overwriting existing files, path tricks, names that break on Windows. | Beta-blocking. This isn't a feature, it's a correctness issue. A non-technical user sharing a project name with a slash in it shouldn't be able to corrupt their project. High priority. |
| Partial state on git failure | If git fails mid-operation (disk full, lock conflict), your file might move but never commit. This would add rollback so either everything works or nothing changes. | Important for data integrity but rare in practice for a personal tool. Solid medium priority — not beta-blocking but worth planning. At minimum, a clear warning message when this happens. |
| Large file handling | Video files and large images will bloat git history permanently. This would auto-skip large files from git while still tracking them in the index. | Directly relevant to your OSINT workflow (you filed a SOUTHCOM video today). Plan the schema now even if full implementation is post-beta. A simple `git.max_file_size` config key in `project.yaml` is the 80/20 solution. |

---

## Infrastructure

| Feature | 💋 Plain Language | ⚖️ Critical Take |
|---------|-------------------|------------------|
| Git remote support | Automatically push to GitHub or a NAS after each operation. Offsite backup built in, no extra steps. | Complex, requires user to configure remotes. Post-beta. rr already creates local git — users can push themselves. Don't build this until users actually ask for it. |
| `modified` field in index entries | index.json has a field for when files were last modified, but nothing actually writes to it. | Not a feature — it's a spec compliance gap. Low-cost fix. Just implement it. |

---

> [!tip] Suggested Beta Priority Order
>
> **Must-have before any beta user touches it:**
> 1. Input validation — correctness issue, not a feature
> 2. Non-interactive / programmatic mode — unlocks Claude Code integration
> 3. `modified` field fix — spec compliance, low cost
>
> **High value for beta:**
> 4. Directory picker for `rr file` — one-line win, daily-use improvement
> 5. Post-init welcome message + backup reminder — first impression, trivial cost
> 6. `rr status` — discoverability, helps users catch unfiled files
> 7. `rr tutorial` — onboarding for non-technical users
> 8. Large file handling — plan the schema now, even if full build is post-beta
> 9. Grouped index view — low cost, high readability payoff for larger projects
>
> **Reasonable for beta, not blocking:**
> 10. `--no-llm` flag for `rr init`
> 11. `rr edit` (if tags are part of beta workflow)
> 12. `rr search` + tags end-to-end
>
> **Post-beta:**
> - `--no-git` flag for `rr init` (requires end-to-end git-optional support)
> - `rr destroy` (users can drag to trash)
> - `rr log` (git literate users don't need it; non-technical users need tutorial first)
> - Git remote support
> - Glob support for `rr file`
> - `--config` flag for `rr init`

# rr — Communicating Git Value to New Users

## The Problem

Many OSINT/conflict monitoring researchers are not developers. They understand file management, spreadsheets, and shared drives — but not version control. The instinct is: "Why do I need git? I have folders."

The goal is not to teach git. It's to make git's value *obvious from the tool's behavior* for users who've never heard of it, and to give you material for a presentation to those who are skeptical.

---

## In-Tool Integration Points

### 1. `rr init` success message

After initializing a project, print a brief, plain-language note about what git is doing:

```
✓ Created project: operation-sandstorm
✓ Directory structure created
✓ Git repository initialized
✓ Initial commit made

  Git is tracking this project. Every time you file, move, or remove
  a document, rr commits the change automatically. You can always
  recover any version of any file — nothing is ever permanently lost.

  Run `rr log` to see the project history.  (future command)
  Run `git log --oneline` to see raw commit history.
```

Keep it short. One paragraph. Don't over-explain.

---

### 2. `--help` descriptions

Write commit-awareness into every command description. Users who read `--help` should immediately understand that operations are recorded:

```
rr file <path>    File a document into the project.
                  Prompts for filename, destination, and description.
                  Moves the file, updates the index, and commits the change.
                  The file is recoverable via git if removed later.

rr remove <path>  Remove a file from the project and update the index.
                  Commits the removal — the file is recoverable via:
                    git checkout <commit-hash> -- <path>

rr reindex        Rebuild the index from the current filesystem state.
                  Commits the updated index.
```

The phrase *"recoverable via git"* is the hook. Users who don't know what that means will ask. Users who do know will appreciate it.

---

### 3. Confirmation messages after commit

When `rr` commits, print the short SHA:

```
✓ Committed: "File: maxar-site-alpha.png → sources/"  [a3f2b1c]
```

The SHA is a subtle signal: this is permanent, referenced, retrievable. It makes the audit trail visible without explaining it.

---

### 4. First-file hint (one-time only)

On the *first* `rr file` operation in a project (detectable from `index.json` being empty), print a one-time note:

```
  Tip: Every file operation is committed to git automatically.
  To see the project history at any time: git log --oneline
  To recover a deleted file:             git checkout <sha> -- <path>
```

Don't repeat this on subsequent operations.

---

## Presentation: How to Frame Git for Researchers

### Core message (one sentence)

*"Git is a time machine for your project — every change is recorded, nothing is ever permanently lost, and you can always prove what you knew and when you knew it."*

### Three angles that land with OSINT researchers

**1. Provenance and credibility**
> "When did you download this image? Was the website showing this content on March 3rd or March 15th? Can you prove it?"
> Git answers these questions automatically. Every file operation is timestamped and attributed. If you're ever challenged on your methods, the git log is your contemporaneous record.

**2. Nothing is permanent (in a good way)**
> "What happens when you accidentally delete the wrong file? When you overwrite a document you needed? When a hard drive fails?"
> With git, every prior state of the project is recoverable. `rr` commits before every destructive operation. Deletion is reversible.

**3. Parallel investigation threads (future)**
> "What if you need to explore a hypothesis that turns out to be wrong, without contaminating your main project?"
> Git branches let you work on a theory without touching the main project. If the theory is wrong, discard the branch. If it's right, merge it. (This is a future `rr` feature — worth mentioning as a direction.)

---

## Diagram and Illustration Suggestions

### Diagram 1 — The Timeline / Audit Trail

A horizontal timeline showing git commits as labeled events:

```
──●──────────────●──────────────●──────────────●──▶ time
  │              │              │              │
  Init project   File:          File:          Remove:
  [a1b2c3]       maxar-img.png  un-report.pdf  draft-v1.md
                 [d4e5f6]       [g7h8i9]       [j0k1l2]
```

*Use case:* Show this when explaining provenance. "This is your project's history. Every event is here. Immutable. Timestamped."

---

### Diagram 2 — Recovery Flow

A simple before/after showing file deletion and recovery:

```
[sources/video.mp4]  →  rr remove  →  [file gone from disk]
                                             │
                                    git checkout g7h8i9 -- sources/video.mp4
                                             │
                                    [file restored exactly as it was]
```

*Use case:* Show this when addressing the "what if I make a mistake" concern.

---

### Diagram 3 — What git stores vs. what you see

Two-column view:

```
What you see (project directory)    What git stores (invisible, in .git/)
────────────────────────────────    ──────────────────────────────────────
sources/                            Every version of every committed file
  maxar-img.png       ←─────────── maxar-img.png @ commit a1b2c3
  un-report.pdf       ←─────────── un-report.pdf @ commit d4e5f6
index.json            ←─────────── index.json @ commits a1, d4, g7, j0...
index.md              ←─────────── index.md @ commits a1, d4, g7, j0...
```

*Use case:* Demystify what git is actually doing. It's not magic — it's a structured archive living inside `.git/`.

---

### Diagram 4 — rr workflow with git overlay

Show the standard `rr file` workflow with git layer visible:

```
User drops file       rr file prompts      File moved        Index updated     git commit
into inbox/     →     for name/dest/   →   to sources/   →  (index.json,  →   "File: X → sources/"
                      description                            index.md)         [SHA: a3f2b1c]
```

*Use case:* The "here's what rr does, step by step" slide. Makes git visible as a layer, not an afterthought.

---

## Notes on Delivery

- *Keep git invisible for most users.* The best-case scenario is a user who uses `rr` for six months and never thinks about git — but has a complete audit trail they can produce on request.
- *Surface git when things go wrong.* The error case (accidental deletion, corruption) is when git's value becomes undeniable.
- *Avoid git jargon in the tool itself.* Say "recoverable" not "revert." Say "project history" not "commit log." Say "recorded" not "committed" in user-facing text (even if the underlying concept is commits).

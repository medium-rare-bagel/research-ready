# Learnings

Personal engineering journal. Patterns, principles, and decisions worth remembering — for building tools generally and for working with an LLM as a collaborator.

Move this file out of the project repo once you've found a permanent home for it.

## 2026-03-19 — Dependency discipline

Considered `rich` for post-init output (twice). Decided against it — Click's built-in `click.style()` covers the need. Principle: don't add a dependency for something the existing stack already handles. The heavier the dependency, the stronger the justification needs to be.

## 2026-03-19 — Where decisions get recorded

Not every decision needs its own doc. If a decision is project-shaping, it goes in SPEC.md. If it's "we're not doing X," it usually belongs inline where the alternative is discussed (e.g., the wishlist item). A "decisions we didn't make" doc tends to grow without bound.

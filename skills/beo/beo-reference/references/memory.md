# Semantic Memory

> [!NOTE]
> This reference is subordinate to [references/kernel.md](file:///Users/beowulf/Work/personal/beo-skills/skills/beo/beo-reference/references/kernel.md). `references/kernel.md` is the canonical owner of BEO rules and invariants.

Memory authority boundary is canonical in `references/kernel.md` §7 Memory & Learning Boundary: qmd and Obsidian are advisory only and never grant approval, execution permission, verdicts, closure, or Human Gate resolution.

## Learning location

Default Obsidian learning directory:

`<vault>/beo-learnings/`

Do not write reusable learning outputs under:

`skills/beo/beo-reference/learnings/`

If a lesson becomes repeated workflow behavior, promote it into one of:

- BEO skill card,
- BEO reference,
- BEO registry,
- helper script,
- `AGENTS.template.md` managed block.

## Recall

Recall is opt-in. Use it only when a prior lesson is explicitly useful, such as a similar previous failure, a user request for recall, or review/debug needing prior context.

`beo_recall.py` searches, in order:

1. qmd when configured.
2. Hydrated matching markdown under the resolved Obsidian learning directory.
3. Local fallback markdown under `.beads/learnings/`.

Snippets are leads only; hydrate matching notes before relying on them.

## Learning writes

`beo-learn` runs only when an explicit `learning_candidate` exists or the user asks to save a BEO lesson. Write the smallest safe markdown note through `beo_memory_write.py`.

Notes must store structural handles only, never secrets, raw credentials, or customer-sensitive data. `beo-learn` writes the note only. It may emit `qmd_refresh_recommended`; qmd refresh/indexing belongs only to explicit `beo-setup` or authorized BEO maintenance. If Obsidian is unavailable, write to `.beads/learnings/`.

## Note shape

Use plain markdown with YAML frontmatter containing source bead, source phase, condition, safe evidence refs, `secret_policy: handles_only`, and tags. The body should be short: Trigger, Lesson, Reuse/Prevention Rule, Evidence refs, and Non-authority disclaimer.

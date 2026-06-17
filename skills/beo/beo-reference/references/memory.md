# Semantic Memory

> [!NOTE]
> This reference is subordinate to `references/kernel.md`. `references/kernel.md` is the canonical owner of BEO rules and invariants.

Memory authority boundary is canonical in `references/kernel.md` (Memory & Learning Boundary section): qmd and Obsidian are advisory only and never grant approval, execution permission, verdicts, closure, or Human Gate resolution.

## Learning location

Default Obsidian learning directory:

`<vault>/beo-learnings/`

Do not write reusable learning outputs under the skills/beo/beo-reference/learnings/ directory.

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

Notes must store structural handles only, never secrets, raw credentials, or customer-sensitive data. `beo-learn` writes the note only. It may emit `qmd_refresh_recommended`; qmd refresh/indexing belongs only to explicit `beo-setup` or authorized BEO maintenance. `beo_memory_write.py` writes to the configured Obsidian `<vault>/beo-learnings/` directory when `BEO_OBSIDIAN_VAULT` resolves to a writable vault path; otherwise it falls back to `.beads/learnings/`.

## Note shape

Notes follow the [Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf) v0.1 conventions for interoperability.

### YAML frontmatter

Required:
- `type` — one of `learning`, `decision`, `reference`
- `basis_ref` — the durable reference this note is based on
- `evidence_refs` — non-empty YAML list of repo-relative or durable refs
- `secret_policy: handles_only`

Contextual (required per mode):
- `source_bead_id`, `source_phase`, `condition_id` — for `learning_candidate` mode
- `source_type: user_request` — for `user_request` mode

Optional (OKF conventions):
- `tags` — YAML list of topic keywords for filtering
- `timestamp` — ISO 8601 datetime of when the knowledge was captured
- `title` — human-readable concept name
- `description` — one-line summary for OKF consumers
- `resource` — URL or path to original source
- `case_type` — BEO-specific: `success_pattern`, `failure_pattern`, `near_miss`, `recurring_mistake`, `cannot_deliver_pattern`, `debug_pattern`, `authoring_candidate`

### Body

Use short markdown sections: Trigger, Lesson, Reuse/Prevention Rule, Evidence refs, and Non-authority disclaimer. The body is free-form for OKF consumers; BEO agents parse sections by convention, not by schema.

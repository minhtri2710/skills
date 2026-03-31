# CHANGELOG

## 2026-03-31

### Refactored beo skill architecture

Restructured the `skills/beo` skill set toward a thinner-`SKILL.md`, stronger-`references/` model.

#### Main goals
- Reduce duplicated operational guidance across skills
- Move exact procedures and command sequences into reference files
- Keep `SKILL.md` focused on triggers, invariants, hard gates, and core workflow
- Improve maintainability and consistency across the beo pipeline

### Added shared canonical protocols

Created new shared references under `skills/beo/reference/references/`:

- `slug-protocol.md`
  - canonical creation, preservation, and recovery of `feature_slug`
- `state-and-handoff-protocol.md`
  - canonical `STATE.md` and `HANDOFF.json` semantics and shapes
- `learnings-read-protocol.md`
  - canonical read-side workflow for `critical-patterns.md`, `.beads/learnings/`, and optional QMD search
- `approval-gates.md`
  - canonical user-approval requirements for validation, review, compounding, and dream flows
- `bead-description-templates.md`
  - shared Markdown templates for planned, reactive-fix, and follow-up beads

### Added skill-specific operations references

Added new per-skill operational references:

- `skills/beo/router/references/router-operations.md`
- `skills/beo/planning/references/planning-operations.md`
- `skills/beo/validating/references/validation-operations.md`
- `skills/beo/executing/references/execution-operations.md`
- `skills/beo/compounding/references/compounding-operations.md`
- `skills/beo/swarming/references/swarming-operations.md`
- `skills/beo/reviewing/references/reviewing-operations.md`
- `skills/beo/debugging/references/debugging-operations.md`
- `skills/beo/dream/references/dream-operations.md`
- `skills/beo/writing-skills/references/writing-skills-operations.md`

These files now hold operational details that were previously embedded directly in `SKILL.md` files.

### Reduced `SKILL.md` size across the repo

Refactored the main beo skills to be shorter and more focused:

| Skill | Approx. final lines |
|------|----------------------|
| `router` | 203 |
| `exploring` | 250 |
| `planning` | 249 |
| `validating` | 129 |
| `executing` | 133 |
| `swarming` | 70 |
| `reviewing` | 133 |
| `debugging` | 84 |
| `compounding` | 115 |
| `dream` | 58 |
| `writing-skills` | 154 |
| `reference` | 30 |

### Standardized bead descriptions as Markdown

Updated bead/task guidance so descriptions consistently use Markdown format.

Applied across planning, debugging, reviewing, router instant path, validation checks, and artifact protocol.

Established shared templates for:
- planned execution beads
- reactive fix beads
- follow-up beads

### Rewired skills to shared protocols

Updated beo skills and references to point to the shared canonical sources for:
- slug handling
- state/handoff handling
- prior learnings retrieval
- approval-gated actions
- bead description formats

This reduced duplicated instructions and made protocol changes easier to centralize in the future.

### Changed knowledge-store preference order

Updated the beo knowledge-store model to prefer richer tools first:

1. Obsidian CLI for writes and vault-backed knowledge continuity
2. QMD for indexed retrieval and semantic search
3. Flat files under `.beads/learnings/` as fallback

Applied this change in:
- `reference/references/knowledge-store.md`
- `reference/references/learnings-read-protocol.md`
- `reference/references/file-conventions.md`
- `dream/references/dream-operations.md`
- `compounding/SKILL.md`
- `compounding/references/compounding-operations.md`

This means the repo now treats Obsidian/QMD as the preferred knowledge-store path, with flat files used when the richer toolchain is unavailable or cannot be used safely.

### Final consistency pass

Completed a repo-wide final pass to:
- fix broken or stale reference paths
- align wording with shared protocols
- improve trigger descriptions in frontmatter
- strengthen hard gates where needed
- ensure markdown reference paths resolve correctly

Notable improvements included:
- stronger trigger wording for `beo-router`, `beo-executing`, `beo-swarming`, `beo-debugging`, `beo-compounding`, `beo-dream`, and `beo-writing-skills`
- explicit hard gate for `beo-swarming` when Agent Mail is unavailable
- explicit hard gate for `beo-debugging` before proceeding without a one-sentence root cause

### Reference navigation improvements

Updated `skills/beo/reference/SKILL.md` so it now serves as a stronger entry point for:
- CLI references
- artifact protocol
- bead description templates
- slug protocol
- state/handoff protocol
- learnings read protocol
- approval gates

### Result

The `skills/beo` system now follows a clearer architecture:

- `SKILL.md` = trigger + policy + gates + core workflow
- skill-local `references/` = detailed operational playbooks
- shared `reference/references/` = canonical cross-skill protocols

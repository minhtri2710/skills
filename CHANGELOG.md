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

### Added planning foundation for single-phase and multi-phase work

Expanded the beo planning model to distinguish whole-feature strategy from current-phase execution preparation.

#### New planning artifacts
- Added `approach.md` as the canonical strategy artifact for:
  - gap analysis
  - recommended approach
  - alternatives considered
  - risk map
- Added optional `phase-plan.md` for multi-phase features to describe:
  - whole-feature sequencing
  - current-phase selection
  - intentionally deferred later phases

#### New current-phase semantics
- `phase-contract.md` now explicitly means **current phase only**
- `story-map.md` now explicitly means **current phase only**
- Multi-phase work keeps whole-feature sequencing in `phase-plan.md` instead of overloading current-phase artifacts

#### Shared protocol updates
- Extended `state-and-handoff-protocol.md` with planning-aware fields:
  - `planning_mode`
  - `has_phase_plan`
  - `current_phase`
  - `total_phases`
  - `phase_name`
- Extended `approval-gates.md` with multi-phase planning approval semantics
- Updated `file-conventions.md` and `pipeline-contracts.md` to reflect the new artifact hierarchy

#### Router and downstream skill updates
- Updated `beo-router` to distinguish:
  - approach-level planning state
  - current-phase planning state
  - current-phase completion vs whole-feature completion
- Updated `beo-validating`, `beo-executing`, `beo-swarming`, and `beo-reviewing` to respect planning-aware routing and current-phase scope
- Added current-phase-aware handoff rules so multi-phase work routes back to planning instead of jumping directly to final review

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
- planning-aware routing consistency across router, validation, execution, swarming, and review

### Reference navigation improvements

Updated `skills/beo/reference/SKILL.md` so it now serves as a stronger entry point for:
- CLI references
- artifact protocol
- bead description templates
- slug protocol
- state/handoff protocol
- learnings read protocol
- approval gates
- planning-aware artifact semantics

### Result

The `skills/beo` system now follows a clearer architecture:

- `SKILL.md` = trigger + policy + gates + core workflow
- skill-local `references/` = detailed operational playbooks
- shared `reference/references/` = canonical cross-skill protocols

And the planning pipeline now distinguishes:
- whole-feature strategy (`approach.md`)
- optional whole-feature sequencing (`phase-plan.md`)
- current-phase execution preparation (`phase-contract.md`, `story-map.md`, current-phase beads)

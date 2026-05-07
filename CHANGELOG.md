# CHANGELOG

## 2026-05-05

### Doctrine hardening: operational usability, drift reduction, bypass prevention

Hardened existing beo doctrine for operational safety without adding owners, gates, scripts, or topology changes.

#### Changed
- `PASS_EXECUTE` now requires explicit `approval_ref` for all approval actions, including `approval_action=unchanged`.
- Multi-bead partial progress requires matching canonical values in both `STATE.json` and `readiness-record.json`; missing, stale, null, or mismatched values are treated as `false`.
- Execution Set Cards remain display-only; all display card fields use a `display_` prefix.
- Bounded reactive fixes still route through `beo-validate`; no direct `beo-review -> beo-execute` path.
- `beo-route` remains exception-resolution, not a normal pipeline hop.
- Added runtime preflight checklist to `operator-card.md` (display guidance only).
- Added structured readiness-record layout to `artifacts.md` (evidence grouping only, not a second authority).
- Added review severity taxonomy (P0/P1/P2/P3) to `artifacts.md`.
- Deduplicated multi-step doctrine restatements from skill files into canonical reference pointers.

#### Files changed
- `beo-reference -> references/operator-card.md` — runtime preflight checklist; reactive-fix loop pointer to pipeline
- `skills/beo/execute/SKILL.md` — preflight pointer; partial-progress conditions pointer
- `skills/beo/validate/SKILL.md` — readiness-record grouping note; partial-progress conditions pointer
- `skills/beo/review/SKILL.md` — severity taxonomy reference
- `beo-reference -> references/artifacts.md` — structured readiness-record layout; review severity taxonomy
- `beo-reference -> references/pipeline.md` — canonical reactive-fix loop section
- `beo-reference -> references/state.md` — explicit `approval_ref` and `partial_progress_allowed` hardening
- `beo-reference -> references/manual-consistency-checklist.md` — severity and readiness-record layout checks
- `skills/beo/author/references/manual-pressure-scenarios.md` — scenarios 51-54

## 2026-04-25

### Minimal beo ownership architecture

Refactored the beo corpus around the fixed 12-skill topology and final canonical shared reference set.

#### Main improvements
- Standardized every `SKILL.md` around one primary owned decision, one ownership predicate, exact writable surfaces, strict boundaries, and enumerated allowed successors.
- Consolidated shared schemas, mappings, protocols, command forms, and registries into the final 13 canonical shared references.
- Reduced skill-local references to asset or appendix roles only.
- Refocused `beo-author` on skill contract authorship only, with manual pressure scenarios as prose rather than checker or fixture ownership.
- Normalized `AGENTS.md` to pointer-only runtime doctrine while preserving the managed beo block.

#### Current canonical shared references
- `approval.md`
- `artifacts.md`
- `authoring.md`
- `cli.md`
- `complexity.md`
- `doctrine-map.md`
- `go-mode.md`
- `learning.md`
- `operator-card.md`
- `pipeline.md`
- `skill-contract-common.md`
- `state.md`
- `status-mapping.md`

#### Manual validation
- `beo-author/SKILL.md` owns skill authoring only.
- No author-owned checker scripts remain.
- No author-owned route fixtures remain.
- Author no longer owns release surfaces.
- Author references contain only skill-writing guidance.

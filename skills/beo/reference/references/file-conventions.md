# File Conventions

Canonical locations for all pipeline artifacts and state files.

Every skill in the beo pipeline reads from or writes to these paths.

## State Files

| File | Written By | Read By | Purpose |
|------|-----------|---------|---------|
| `.beads/STATE.md` | beo-exploring, beo-planning, beo-validating, beo-swarming, beo-executing, beo-reviewing, beo-compounding | Next skill in pipeline | Intra-session skill-to-skill handoff state (see `state-and-handoff-protocol.md` for canonical schema) |
| `.beads/HANDOFF.json` | Any skill (at 65% context budget) | beo-router (Phase 3) | Cross-session resume; survives context resets (see `state-and-handoff-protocol.md` for canonical schema) |

**Rule**: Use `state-and-handoff-protocol.md` as the canonical source for `STATE.md` and `HANDOFF.json` semantics and schemas.

## Feature Artifact Root

All feature artifacts live under:

```text
.beads/artifacts/<feature_slug>/
```

`<feature_slug>` is the immutable slug created by the router.

See `pipeline-contracts.md` → Feature Slug for derivation rules.

## Feature Artifacts

| File | Written By | Read By | Purpose |
|------|-----------|---------|---------|
| `CONTEXT.md` | beo-exploring | beo-planning, beo-validating, beo-executing, beo-reviewing, beo-compounding | Locked decisions: the source of truth |
| `discovery.md` | beo-planning | beo-validating, beo-compounding | Research findings from discovery work |
| `approach.md` | beo-planning | beo-validating, beo-executing, beo-reviewing, beo-compounding, future planning cycles | Chosen implementation strategy, alternatives, and risk map |
| `plan.md` | beo-planning | beo-validating, beo-executing, beo-compounding | Human-readable planning summary |
| `phase-plan.md` | beo-planning | beo-router, beo-validating, future planning cycles | Optional whole-feature sequencing artifact for multi-phase work |
| `phase-contract.md` | beo-planning | beo-router, beo-validating, beo-executing, beo-reviewing, beo-compounding | Current phase as a closed loop: entry/exit state, demo story, scope, pivot signals |
| `story-map.md` | beo-planning | beo-router, beo-validating, beo-executing, beo-reviewing, beo-compounding | Current phase story sequence, closure check, story-to-bead mapping |
| `debug-notes.md` | beo-debugging | beo-compounding, beo-debugging | Failure patterns discovered during debugging |
| `compounding-patterns.md` | beo-compounding (Agent 1) | beo-compounding orchestrator | Staging: reusable patterns extracted |
| `compounding-decisions.md` | beo-compounding (Agent 2) | beo-compounding orchestrator | Staging: decision analysis |
| `compounding-failures.md` | beo-compounding (Agent 3) | beo-compounding orchestrator | Staging: failure analysis |

## Artifact Semantics

### `CONTEXT.md`
`CONTEXT.md` is the feature-definition artifact.

It holds:

- locked product / behavior decisions
- scope boundaries
- out-of-scope decisions
- planning-relevant open questions

All downstream planning and execution must honor it.

### `discovery.md`
`discovery.md` captures findings from research:

- architecture topology
- existing patterns
- constraints
- external dependency notes

It is evidence, not the final plan.

### `approach.md`
`approach.md` is the strategy artifact.

It should explain:

- what the feature needs to make true
- what the codebase already provides
- what is missing or risky
- the chosen implementation direction
- alternatives considered
- the risk map
- whether the work stays single-phase or becomes multi-phase

### `plan.md`
`plan.md` is the human-readable plan summary.

It should remain readable by a teammate or reviewer who wants the shape of the plan quickly without reading all structured artifacts in depth.

`plan.md` is not a replacement for `approach.md`, `phase-plan.md`, `phase-contract.md`, or `story-map.md`.

### `phase-plan.md`
`phase-plan.md` is optional.

It exists only when the feature should be understood as **multi-phase**.

It defines:

- the whole-feature goal
- why one phase is not enough
- the 2-4 meaningful phases
- why the order makes sense
- which phase is the current phase to prepare now
- what later phases remain intentionally deferred

If the feature fits one clean closed loop, `phase-plan.md` should be absent.

### `phase-contract.md`
`phase-contract.md` always describes the **current phase only**.

This is the canonical rule.

It must never be interpreted as a whole-feature contract when the feature is multi-phase.

If the feature is single-phase, the current phase may also cover the full execution scope.  
If the feature is multi-phase, `phase-contract.md` still describes only the selected current phase.

### `story-map.md`
`story-map.md` always maps the **current phase only**.

This is the canonical rule.

It must never be interpreted as a whole-feature story map when the feature is multi-phase.

If future phases exist, they remain deferred in `phase-plan.md`.

## Planning Mode Interpretation

The artifact model supports two planning modes:

### Single-phase
Expected artifact shape:

- `CONTEXT.md`
- `discovery.md`
- `approach.md`
- `plan.md`
- `phase-contract.md`
- `story-map.md`

`phase-plan.md` is normally absent.

### Multi-phase
Expected artifact shape:

- `CONTEXT.md`
- `discovery.md`
- `approach.md`
- `plan.md`
- `phase-plan.md`
- `phase-contract.md` *(current phase only)*
- `story-map.md` *(current phase only)*

The presence of `phase-plan.md` indicates that the feature has later phases beyond the currently prepared one.

## Router / Validation Reading Rules

When `phase-plan.md` exists:

- router should treat the feature as potentially multi-phase
- validating should treat `phase-contract.md` and `story-map.md` as current-phase artifacts
- current-phase completion must not automatically imply whole-feature completion

When `phase-plan.md` is absent:

- router and validating may treat the work as single-phase unless other evidence contradicts that assumption

## Pipeline-Level Files

| File | Written By | Read By | Purpose |
|------|-----------|---------|---------|
| `.beads/review-findings.md` | beo-reviewing | beo-compounding | P1/P2/P3 severity findings from specialist reviewers |
| `.beads/learnings/YYYYMMDD-<slug>.md` | beo-compounding | all skills (Phase 0) | Finalized learnings from completed features |
| `.beads/critical-patterns.md` | beo-compounding | beo-exploring, beo-planning, beo-validating, beo-debugging, beo-dream | Promoted high-value patterns (multi-feature, generalizable) |
| `.beads/learnings/dream-run-provenance.md` | beo-dream | beo-dream | Dream run markers: tracks when last consolidation ran |

## Knowledge Store

Preferred knowledge-store order:

1. Obsidian CLI writes/reads in the vault
2. QMD retrieval over indexed learnings
3. Flat files under `.beads/learnings/` as fallback

| Operation | Preferred | Fallback |
|-----------|-----------|----------|
| Write learnings | Obsidian vault via `obsidian create/append` | Flat file to `.beads/learnings/` |
| Search learnings | QMD query/search plus vault context | `grep` over `.beads/learnings/` and `.beads/critical-patterns.md` |

See `knowledge-store.md` for full integration details.

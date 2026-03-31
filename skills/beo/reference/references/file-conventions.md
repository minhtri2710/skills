# File Conventions

Canonical locations for all pipeline artifacts and state files. Every skill in the beo pipeline reads from or writes to these paths.

## State Files

| File | Written By | Read By | Purpose |
|------|-----------|---------|---------|
| `.beads/STATE.md` | beo-exploring, beo-planning, beo-validating, beo-swarming, beo-executing, beo-reviewing, beo-compounding | Next skill in pipeline | Intra-session skill-to-skill handoff state (see `state-and-handoff-protocol.md` for canonical schema) |
| `.beads/HANDOFF.json` | Any skill (at 65% context budget) | beo-router (Phase 3) | Cross-session resume; survives context resets (see `state-and-handoff-protocol.md` for canonical schema) |

**Rule**: Use `state-and-handoff-protocol.md` as the canonical source for `STATE.md` and `HANDOFF.json` semantics and schemas.

## Feature Artifacts

All feature artifacts live under `.beads/artifacts/<feature-name>/`:

`<feature-name>` is the immutable `feature_slug` created by the router. See `pipeline-contracts.md` → Feature Slug for derivation rules.

| File | Written By | Read By | Purpose |
|------|-----------|---------|---------|
| `CONTEXT.md` | beo-exploring | beo-planning, beo-validating, beo-executing, beo-reviewing, beo-compounding | Locked decisions: the source of truth |
| `discovery.md` | beo-planning | beo-validating, beo-compounding | Research findings from discovery subagents |
| `plan.md` | beo-planning | beo-validating, beo-executing, beo-compounding | High-level approach summary (compatibility artifact, not the validation gate) |
| `phase-contract.md` | beo-planning | beo-router, beo-validating, beo-executing, beo-reviewing, beo-compounding | Phase as closed loop: entry/exit state, demo story, scope, pivot signals |
| `story-map.md` | beo-planning | beo-router, beo-validating, beo-executing, beo-reviewing, beo-compounding | Story sequence, closure check, story-to-bead mapping |
| `debug-notes.md` | beo-debugging | beo-compounding, beo-debugging | Failure patterns discovered during debugging |
| `compounding-patterns.md` | beo-compounding (Agent 1) | beo-compounding orchestrator | Staging: reusable patterns extracted |
| `compounding-decisions.md` | beo-compounding (Agent 2) | beo-compounding orchestrator | Staging: decision analysis |
| `compounding-failures.md` | beo-compounding (Agent 3) | beo-compounding orchestrator | Staging: failure analysis |

## Pipeline-Level Files

| File | Written By | Read By | Purpose |
|------|-----------|---------|---------|
| `.beads/review-findings.md` | beo-reviewing | beo-compounding | P1/P2/P3 severity findings from 5 specialist reviewers |
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

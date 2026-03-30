# File Conventions

Canonical locations for all pipeline artifacts and state files. Every skill in the beo pipeline reads from or writes to these paths.

## State Files

| File | Written By | Read By | Purpose |
|------|-----------|---------|---------|
| `.beads/STATE.md` | beo-exploring, beo-planning, beo-validating, beo-swarming, beo-executing, beo-reviewing, beo-compounding | Next skill in pipeline | Intra-session skill-to-skill handoff state (see `pipeline-contracts.md` for canonical schema) |
| `.beads/HANDOFF.json` | Any skill (at 65% context budget) | beo-router (Phase 3) | Cross-session resume — survives context resets (see `pipeline-contracts.md` for canonical schema) |

**Rule**: STATE.md is for the happy-path handoff between adjacent skills. HANDOFF.json is the emergency checkpoint written when context is running out. Router reads HANDOFF.json on resume; all other skills read STATE.md from the predecessor.

### HANDOFF.json Schema

```json
{
  "schema_version": 1,
  "phase": "<skill phase name>",
  "skill": "beo-<skill-name>",
  "feature": "<epic-id>",
  "feature_name": "<feature-name>",
  "next_action": "<what to do next>",
  "in_flight_beads": ["<bead-ids>"],
  "timestamp": "<iso8601>"
}
```

`schema_version` is always an integer (currently `1`).

## Feature Artifacts

All feature artifacts live under `.beads/artifacts/<feature-name>/`:

`<feature-name>` is the immutable `feature_slug` created by the router. See `pipeline-contracts.md` → Feature Slug for derivation rules.

| File | Written By | Read By | Purpose |
|------|-----------|---------|---------|
| `CONTEXT.md` | beo-exploring | beo-planning, beo-validating, beo-executing, beo-reviewing, beo-compounding | Locked decisions — the source of truth |
| `discovery.md` | beo-planning | beo-validating, beo-compounding | Research findings from discovery subagents |
| `plan.md` | beo-planning | beo-validating, beo-executing, beo-compounding | Task decomposition, risk map, approach |
| `debug-notes.md` | beo-debugging | beo-compounding, beo-debugging | Failure patterns discovered during debugging |
| `compounding-patterns.md` | beo-compounding (Agent 1) | beo-compounding orchestrator | Staging: reusable patterns extracted |
| `compounding-decisions.md` | beo-compounding (Agent 2) | beo-compounding orchestrator | Staging: decision analysis |
| `compounding-failures.md` | beo-compounding (Agent 3) | beo-compounding orchestrator | Staging: failure analysis |

## Pipeline-Level Files

| File | Written By | Read By | Purpose |
|------|-----------|---------|---------|
| `.beads/review-findings.md` | beo-reviewing | beo-compounding | P1/P2/P3 severity findings from 5 specialist reviewers |
| `.beads/learnings/YYYYMMDD-<slug>.md` | beo-compounding | all skills (Phase 0) | Finalized learnings from completed features |
| `.beads/critical-patterns.md` | beo-compounding | beo-exploring, beo-planning, beo-debugging, beo-dream | Promoted high-value patterns (multi-feature, generalizable) |
| `.beads/learnings/dream-run-provenance.md` | beo-dream | beo-dream | Dream run markers — tracks when last consolidation ran |

## Knowledge Store (Optional)

When Obsidian CLI and QMD are available:

| Operation | Tool | Fallback |
|-----------|------|----------|
| Write learnings | `obsidian create` | Flat file to `.beads/learnings/` |
| Search learnings | `qmd query` | `grep` over `.beads/learnings/` and `.beads/critical-patterns.md` |

See `knowledge-store.md` for full integration details.

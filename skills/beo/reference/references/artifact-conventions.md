# Artifact Conventions

Combined reference for artifact storage protocols, slug lifecycle, and file layout conventions.

## Table of Contents

- [Artifact Protocol](#artifact-protocol)
  - [Locations](#locations)
  - [Spec (Bead Description)](#spec-bead-description)
  - [Report (Comment-Backed)](#report-comment-backed)
  - [Task State (Comment-Backed)](#task-state-comment-backed)
  - [Version Semantics](#version-semantics)
  - [Batch Sync Rule](#batch-sync-rule)
- [Slug Lifecycle](#slug-lifecycle)
  - [Why This Exists](#why-this-exists)
  - [Source of Truth](#source-of-truth)
  - [Creation Procedure](#creation-procedure)
  - [Read Procedure](#read-procedure)
  - [Safe Update Procedure](#safe-update-procedure)
  - [Hard Rules](#hard-rules)
  - [Recovery Procedure](#recovery-procedure)
- [File Layout](#file-layout)
  - [State Files](#state-files)
  - [Feature Artifact Root](#feature-artifact-root)
  - [Feature Artifacts](#feature-artifacts)
  - [Artifact Semantics](#artifact-semantics)
  - [Planning Mode Interpretation](#planning-mode-interpretation)
  - [Artifact Cleanup on Replanning](#artifact-cleanup-on-replanning)
  - [Pipeline-Level Files](#pipeline-level-files)
  - [Knowledge Store](#knowledge-store)

---

## Artifact Protocol

Tasks use three artifact types: **spec** (what to do), **report** (what was done), and **task_state** (machine-readable status snapshot). Each has a specific location within the bead system.

### Locations

| Artifact | Storage | Read Command | Write Command |
|----------|---------|-------------|---------------|
| `spec` | Bead description | `br show <id> --json` → `.description` | `br update <id> --description "<content>"` |
| `report` | Bead comment (latest) | `br comments list <id> --json` → scan for header | `br comments add <id> --no-daemon --message "<formatted>"` |
| `task_state` | Bead comment (latest) | `br comments list <id> --json` → scan for header | `br comments add <id> --no-daemon --message "<formatted>"` |

### Spec (Bead Description)

The task specification is the bead's description field. Write it once during task creation or planning, always in Markdown format.

#### Required Spec Structure

Use `bead-description-templates.md` as the single source of truth for all bead description formats.

- Planned execution beads → **Planned Task Bead Template**
- Reactive fix beads → **Reactive Fix Bead Template**
- Review/debug follow-up beads → **Follow-Up Bead Template**

Every bead description must be Markdown-formatted.

Reactive fix beads (created by `beo-reviewing` or `beo-debugging`) are exempt from the Story Context requirement, but they must still follow the shared reactive template.

Instant-path beads created by `beo-router` still use the Planned Task Bead Template, but may use abbreviated Story Context.

```bash
# Write spec
br update <id> --description "<Markdown content using the appropriate shared bead template>"
```

### Report (Comment-Backed)

The report captures what the worker accomplished. It is appended as a bead comment with a specific header format.

#### Format

```
---ARTIFACT:report:v<version>---
<markdown content>
---END_ARTIFACT---
```

#### Writing a Report

```bash
# For short reports (< 32KB)
br comments add <id> --no-daemon --message "---ARTIFACT:report:v1---
## Summary
Implemented auth middleware with JWT validation.

## Changes
- Created src/middleware/auth.ts (new file, 45 lines)
- Added tests in src/middleware/auth.test.ts (3 test cases)

## Verification
- All 156 tests pass
- Manual test: unauthenticated request returns 401
---END_ARTIFACT---" --no-daemon

# For large reports, write to a temp file first using your file writing tool,
# then attach it:
br comments add <id> --file /tmp/report.md --no-daemon
```

#### Reading the Latest Report

```bash
# List all comments, find the latest report artifact
br comments list <id> --json --no-daemon
# Inspect the returned comments and scan backwards for the last report artifact header
# The latest version wins (v2 supersedes v1)
```

#### Completion Report Minimum Fields

When execution policy requires close-time validation, every completion report must include:
- bead ID
- files changed
- tests added or modified
- verification result

### Task State (Comment-Backed)

The task_state artifact is a machine-readable status snapshot used by the orchestrator and monitoring tools. It follows the same comment-backed format as reports.

#### Format

```
---ARTIFACT:task_state:v<version>---
beo_status: <pending | dispatch_prepared | in_progress | done | blocked | failed | partial | cancelled>
worker: <agent-name or empty>
claimed_at: <ISO-8601 or empty>
blocked_by: <bead-id list or empty>
blocker_type: <MISSING_CONTEXT | DEPENDENCY_NOT_MET | TECHNICAL_FAILURE | AMBIGUITY or empty>
context_pct: <estimated context usage percentage>
---END_ARTIFACT---
```

#### Writing a Task State

```bash
br comments add <id> --no-daemon --message "---ARTIFACT:task_state:v1---
beo_status: in_progress
worker: BlueLake
claimed_at: 2026-03-15T10:30:00Z
blocked_by:
blocker_type:
context_pct: 35
---END_ARTIFACT---" --no-daemon
```

Task state is optional and **informational only**. The authoritative bead status is always the `br` status (see `status-mapping.md` → Reading Beo State from br). Workers update `task_state` when claiming, blocking, or completing beads. The orchestrator reads the latest version to build the swarm status view.

**Important:** A `task_state` comment with `beo_status: done` does **not** close the bead. The actual closure requires `br close <id>` per `status-mapping.md`. Always write `task_state: done` only **after** `br close` succeeds.

Reservation release and swarm coordination stay in execution flow and Agent Mail protocols, not in new artifact kinds. If workers record `beo_status: done`, they do so only after `br close` succeeds and after the completion report is written.

### Version Semantics

- Versions are monotonically increasing integers: v1, v2, v3...
- When reading, always take the **latest** (highest version number) artifact of each kind
- When writing, increment the version if updating an existing artifact
- Multiple versions of the same artifact kind can coexist in comments. Only the latest matters.

### Batch Sync Rule

After writing multiple artifacts or making multiple br mutations:

```bash
br sync --flush-only   # Export DB to JSONL for git
```

---

## Slug Lifecycle

Canonical protocol for creating, reading, preserving, and recovering the immutable `feature_slug` used across the beo pipeline.

### Why This Exists

The `feature_slug` is the stable identifier that ties together:
- the epic bead description
- `.beads/artifacts/<feature-slug>/`
- `STATE.json`
- `HANDOFF.json`
- learnings file naming

Once created, it must not drift.

### Source of Truth

The canonical storage location is the **first line of the epic description**:

```text
slug: <feature_slug>
```

See `pipeline-contracts.md` → **Feature Slug** for derivation rules and invariants.

### When To Create

Only the router creates the slug, at epic creation time.

### Creation Procedure

1. Derive the slug from the epic title using the pipeline-contract rules.
2. Write it as the first line of the epic description.

```bash
br update <EPIC_ID> --description "slug: <feature_slug>"
```

### Read Procedure

Whenever a skill needs artifact paths, read the current epic description first and extract the first line.

Expected first line:

```text
slug: <feature_slug>
```

Use that slug for:
- `.beads/artifacts/<feature_slug>/...`
- `feature_name` in `HANDOFF.json` (historical field name; value is still the slug)
- the `feature_slug` field in `STATE.json`
- learnings file slug components where applicable

### Safe Update Procedure

When updating the epic description for summaries or planning content:

1. Read the current description first.
2. Extract and preserve the first line.
3. Replace only the body below the slug line.
4. Rewrite the full description with the slug first.

Canonical shape:

```bash
br update <EPIC_ID> --description "slug: <feature_slug>\n<rest of description>"
```

### Hard Rules

- Never overwrite an epic description without preserving the first-line slug.
- Never derive artifact paths from the mutable epic title after creation.
- Never rename the slug because the feature title changed.
- Never move the slug line below any other content.

### Recovery Procedure

If the slug line is missing:

#### Case 1: No tasks yet
- recover the slug from the epic title
- rewrite the epic description with the slug first line

#### Case 2: Tasks or artifacts already exist
- STOP
- inspect `.beads/artifacts/` to identify the existing feature directory
- restore that slug to the epic description
- do not guess between multiple plausible directories without user confirmation

### Example Summary Update

```bash
br update <EPIC_ID> --description "slug: <feature_slug>\nFeature: <name>\n\nScope: <summary>\nDecisions: <count> locked\nDomains: <list>"
```

---

## File Layout

Canonical locations for all pipeline artifacts and state files.

Every skill in the beo pipeline reads from or writes to these paths.

### State Files

| File | Written By | Read By | Purpose |
|------|-----------|---------|---------|
| `.beads/STATE.json` | beo-router, beo-exploring, beo-planning, beo-validating, beo-swarming, beo-executing, beo-reviewing, beo-compounding | Next skill in pipeline | Intra-session skill-to-skill handoff state (see `state-and-handoff-protocol.md` for canonical schema) |
| `.beads/HANDOFF.json` | Any skill (at 65% context budget) | beo-router (Phase 3) | Cross-session resume; survives context resets (see `state-and-handoff-protocol.md` for canonical schema) |
| `.beads/beo_status.mjs` | beo-using-beo | Humans and agents | Read-only scout command summarizing onboarding, state, and optional handoff status |

**Rule**: Use `state-and-handoff-protocol.md` as the canonical source for `STATE.json` and `HANDOFF.json` semantics and schemas.

### Feature Artifact Root

All feature artifacts live under:

```text
.beads/artifacts/<feature_slug>/
```

`<feature_slug>` is the immutable slug created by the router.

See `pipeline-contracts.md` → Feature Slug for derivation rules.

### Feature Artifacts

| File | Written By | Read By | Purpose |
|------|-----------|---------|---------|
| `CONTEXT.md` | beo-exploring | beo-planning, beo-validating, beo-executing, beo-reviewing, beo-compounding | Locked decisions: the source of truth |
| `discovery.md` | beo-planning | beo-validating, beo-compounding | Research findings from discovery work |
| `approach.md` | beo-planning | beo-validating, beo-executing, beo-reviewing, beo-compounding, future planning cycles | Chosen implementation strategy, alternatives, and risk map |
| `plan.md` | beo-planning | beo-validating, beo-executing, beo-reviewing, beo-compounding | Human-readable planning summary |
| `phase-plan.md` | beo-planning | beo-router, beo-validating, future planning cycles | Optional whole-feature sequencing artifact for multi-phase work |
| `phase-contract.md` | beo-planning | beo-router, beo-validating, beo-executing, beo-reviewing, beo-compounding | Current phase as a closed loop: entry/exit state, demo story, scope, pivot signals |
| `story-map.md` | beo-planning | beo-router, beo-validating, beo-executing, beo-reviewing, beo-compounding | Current phase story sequence, closure check, story-to-bead mapping |
| `debug-notes.md` | beo-debugging | beo-compounding, beo-debugging | Failure patterns discovered during debugging |
| `compounding-patterns.md` | beo-compounding (Agent 1) | beo-compounding orchestrator | Staging: reusable patterns extracted |
| `compounding-decisions.md` | beo-compounding (Agent 2) | beo-compounding orchestrator | Staging: decision analysis |
| `compounding-failures.md` | beo-compounding (Agent 3) | beo-compounding orchestrator | Staging: failure analysis |

### Artifact Semantics

#### `CONTEXT.md`
`CONTEXT.md` is the feature-definition artifact.

It holds:

- locked product / behavior decisions
- scope boundaries
- out-of-scope decisions
- planning-relevant open questions

All downstream planning and execution must honor it.

#### `discovery.md`
`discovery.md` captures findings from research:

- architecture topology
- existing patterns
- constraints
- external dependency notes

It is evidence, not the final plan.

#### `approach.md`
`approach.md` is the strategy artifact.

It should explain:

- what the feature needs to make true
- what the codebase already provides
- what is missing or risky
- the chosen implementation direction
- alternatives considered
- the risk map
- whether the work stays single-phase or becomes multi-phase

#### `plan.md`
`plan.md` is the human-readable plan summary.

It should remain readable by a teammate or reviewer who wants the shape of the plan quickly without reading all structured artifacts in depth.

`plan.md` is not a replacement for `approach.md`, `phase-plan.md`, `phase-contract.md`, or `story-map.md`.

#### `phase-plan.md`
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

#### `phase-contract.md`
`phase-contract.md` always describes the **current phase only**.

This is the canonical rule.

It must never be interpreted as a whole-feature contract when the feature is multi-phase.

If the feature is single-phase, the current phase may also cover the full execution scope.  
If the feature is multi-phase, `phase-contract.md` still describes only the selected current phase.

#### `story-map.md`
`story-map.md` always maps the **current phase only**.

This is the canonical rule.

It must never be interpreted as a whole-feature story map when the feature is multi-phase.

If future phases exist, they remain deferred in `phase-plan.md`.

### Planning Mode Interpretation

See `pipeline-contracts.md` → Planning Artifact Hierarchy for the canonical artifact table, gate-controlling designations, and planning mode rules (single-phase vs. multi-phase artifact shapes).

Key reading rules are summarized here for convenience:

- When `phase-plan.md` exists, the feature is multi-phase; `phase-contract.md` and `story-map.md` describe only the current phase
- When `phase-plan.md` is absent, the work is single-phase unless other evidence contradicts that assumption
- Current-phase completion must not automatically imply whole-feature completion when `phase-plan.md` exists

### Artifact Cleanup on Replanning

See `state-and-handoff-protocol.md` → Planning-Aware Field Transition Cleanup for the canonical replanning cleanup rules, including single-phase conversion, multi-phase re-sequencing, and phase advancement procedures.

**Hard rule:** Stale `phase-plan.md` must be deleted, not marked invalid. Current-phase artifacts (`phase-contract.md`, `story-map.md`) must always reflect the actual current phase.

### Pipeline-Level Files

| File | Written By | Read By | Purpose |
|------|-----------|---------|---------|
| `.beads/review-findings.md` | beo-reviewing | beo-compounding | P1/P2/P3 severity findings from specialist reviewers |
| `.beads/learnings/YYYYMMDD-<slug>.md` | beo-compounding | all skills (Phase 0) | Finalized learnings from completed features |
| `.beads/critical-patterns.md` | beo-compounding | beo-exploring, beo-planning, beo-validating, beo-debugging, beo-dream | Promoted high-value patterns (multi-feature, generalizable) |
| `.beads/learnings/dream-run-provenance.md` | beo-dream | beo-dream | Dream run markers: tracks when last consolidation ran |

### Knowledge Store

Canonical knowledge-store order:

1. Flat files under `.beads/learnings/` and `.beads/critical-patterns.md` (authoritative)
2. QMD retrieval over indexed learnings (optional enhancement)
3. Obsidian CLI reads/writes in the vault (optional mirror)

| Operation | Canonical | Optional enhancement |
|-----------|-----------|----------------------|
| Write learnings | Flat file to `.beads/learnings/` | Mirror to Obsidian vault via `obsidian create/append` |
| Search learnings | `grep` over `.beads/learnings/` and `.beads/critical-patterns.md` | QMD query/search plus vault context |

See `knowledge-store.md` for full integration details.

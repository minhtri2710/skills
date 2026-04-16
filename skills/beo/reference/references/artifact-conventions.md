# Artifact Conventions

Reference for artifact storage protocols, slug lifecycle, and file layout conventions.
Follow these rules for all beo pipeline artifacts.

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
  - [Artifact Cleanup on Replanning](#artifact-cleanup-on-replanning)
  - [Pipeline-Level Files](#pipeline-level-files)
  - [Knowledge Store](#knowledge-store)

---

## Artifact Protocol

Use three artifact types for tasks: **spec** (what to do), **report** (what was done), and **task_state** (machine-readable status snapshot).

### Locations

| Artifact | Storage | Read Command | Write Command |
|----------|---------|-------------|---------------|
| `spec` | Bead description | `br show <id> --json` → `.description` | `br update <id> --description "<content>"` |
| `report` | Bead comment (latest) | `br comments list <id> --json` → scan for header | `br comments add <id> --no-daemon --message "<formatted>"` |
| `task_state` | Bead comment (latest) | `br comments list <id> --json` → scan for header | `br comments add <id> --no-daemon --message "<formatted>"` |

### Spec (Bead Description)

Store the task specification in the bead description. Write it during task creation or planning. Format it as Markdown.

#### Required Spec Structure

Use `bead-description-templates.md` as the single source of truth.

| Bead type | Required template |
|-----------|-------------------|
| Planned execution beads | **Planned Task Bead Template** |
| Reactive fix beads | **Reactive Fix Bead Template** |
| Review/debug follow-up beads | **Follow-Up Bead Template** |

Checklist:
- Format every bead description as Markdown.
- Exempt reactive fix beads created by `beo-review` or `beo-debug` from Story Context.
- Keep reactive fix beads on the shared reactive template.
- Use the Planned Task Bead Template for instant-path beads created by `beo-route`.
- Allow abbreviated Story Context for instant-path beads.

```bash
# Write spec
br update <id> --description "<Markdown content using the appropriate shared bead template>"
```

### Report (Comment-Backed)

Append the worker report as a bead comment with the required header format.

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

When execution policy requires close-time validation, include:
- bead ID
- files changed
- tests added or modified
- verification result

### Task State (Comment-Backed)

Use `task_state` for a machine-readable status snapshot. Store it as a comment-backed artifact with the same format pattern as reports.

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

Checklist:
- Treat task state as optional and informational only.
- Treat `br` status as authoritative. See `status-mapping.md` → Reading Beo State from br.
- Update `task_state` when claiming, blocking, or completing beads.
- Read the latest version to build the swarm status view.
- Do not treat `beo_status: done` as bead closure.
- Run `br close <id>` to close the bead, per `status-mapping.md`.
- Write `task_state: done` only after `br close` succeeds.
- Keep reservation release and swarm coordination in execution flow and Agent Mail protocols, not new artifact kinds.
- If workers record `beo_status: done`, do it only after `br close` succeeds and after writing the completion report.

### Version Semantics

- Use monotonically increasing integer versions: v1, v2, v3...
- Read the latest (highest version number) artifact of each kind.
- Increment the version when updating an existing artifact.
- Allow multiple versions of the same artifact kind in comments. Only the latest matters.

### Batch Sync Rule

After writing multiple artifacts or making multiple br mutations:

```bash
br sync --flush-only   # Export DB to JSONL for git
```

---

## Slug Lifecycle

Use this protocol to create, read, preserve, and recover the immutable `feature_slug` across the beo pipeline.

### Why This Exists

The `feature_slug` ties together:
- the epic bead description
- `.beads/artifacts/<feature-slug>/`
- `STATE.json`
- `HANDOFF.json`
- learnings file naming

Do not let it drift after creation.

### Source of Truth

Store the canonical slug in the first line of the epic description:

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

Read the epic description. Extract the first-line slug. Use it for:
- `.beads/artifacts/<feature_slug>/...`
- `feature_name` in `HANDOFF.json` (historical field name; value is still the slug)
- `feature_slug` in `STATE.json`
- learnings file slug components

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

Use these canonical locations for pipeline artifacts and state files.

### State Files

| File | Written By | Read By | Purpose |
|------|-----------|---------|---------|
| `.beads/STATE.json` | beo-route, beo-explore, beo-plan, beo-validate, beo-swarm, beo-execute, beo-review, beo-compound | Next skill in pipeline | Intra-session skill-to-skill handoff state (see `state-and-handoff-protocol.md` for canonical schema) |
| `.beads/HANDOFF.json` | Any skill (at 65% context budget) | beo-route (Phase 3) | Cross-session resume; survives context resets (see `state-and-handoff-protocol.md` for canonical schema) |
| `.beads/beo_status.mjs` | beo-onboard | Humans and agents | Read-only scout command summarizing onboarding, state, and optional handoff status |

**Rule**: Use `state-and-handoff-protocol.md` as the canonical source for `STATE.json` and `HANDOFF.json` semantics and schemas.

### Feature Artifact Root

Store all feature artifacts under:

```text
.beads/artifacts/<feature_slug>/
```

`<feature_slug>` is the immutable slug created by the router.

See `pipeline-contracts.md` → Feature Slug for derivation rules.

### Feature Artifacts

| File | Written By | Read By | Purpose |
|------|-----------|---------|---------|
| `CONTEXT.md` | beo-explore | beo-plan, beo-validate, beo-execute, beo-review, beo-compound | Locked decisions: the source of truth |
| `discovery.md` | beo-plan | beo-validate, beo-compound | Research findings from discovery work |
| `approach.md` | beo-plan | beo-validate, beo-execute, beo-review, beo-compound, future planning cycles | Chosen implementation strategy, alternatives, and risk map |
| `plan.md` | beo-plan | beo-validate, beo-execute, beo-review, beo-compound | Human-readable planning summary |
| `phase-plan.md` | beo-plan | beo-route, beo-validate, future planning cycles | Optional whole-feature sequencing artifact for multi-phase work |
| `phase-contract.md` | beo-plan | beo-route, beo-validate, beo-execute, beo-review, beo-compound | Current phase as a closed loop: entry/exit state, demo story, scope, pivot signals |
| `story-map.md` | beo-plan | beo-route, beo-validate, beo-execute, beo-review, beo-compound | Current phase story sequence, closure check, story-to-bead mapping |

### Artifact Semantics

| Artifact | Role | Key Rule |
|----------|------|----------|
| `CONTEXT.md` | Feature definition: locked decisions, scope boundaries, out-of-scope, open questions | All downstream must honor it |
| `discovery.md` | Research findings: architecture topology, existing patterns, constraints, external deps | Evidence, not the final plan |
| `approach.md` | Strategy: goal, existing state, gaps/risks, chosen direction, alternatives, risk map, single/multi-phase decision | Canonical strategy artifact |
| `plan.md` | Human-readable plan summary for quick consumption | Not a replacement for structured artifacts |
| `phase-plan.md` | Optional multi-phase sequencing: whole-feature goal, 2-4 phases, ordering rationale, current phase selection | Absent for single-phase work |
| `phase-contract.md` | **Current phase only**: entry/exit state, demo story, scope, pivot signals | Never whole-feature in multi-phase |
| `story-map.md` | **Current phase only**: story sequence, closure check, story-to-bead mapping | Future phases deferred in `phase-plan.md` |

**Planning mode rules** — see `pipeline-contracts.md` → Planning Artifact Hierarchy for full details:
- `phase-plan.md` present → multi-phase; `phase-contract.md` and `story-map.md` describe only the current phase
- `phase-plan.md` absent → single-phase
- Current-phase completion ≠ whole-feature completion when multi-phase

### Artifact Cleanup on Replanning

See `state-and-handoff-protocol.md` → Planning-Aware Field Transition Cleanup for canonical replanning cleanup rules, including single-phase conversion, multi-phase re-sequencing, and phase advancement procedures.

**Hard rule:** Delete stale `phase-plan.md`; do not mark it invalid. Keep current-phase artifacts (`phase-contract.md`, `story-map.md`) aligned to the actual current phase.

### Pipeline-Level Files

| File | Written By | Read By | Purpose |
|------|-----------|---------|---------|
| `.beads/artifacts/<feature_slug>/review-findings.md` | beo-review | beo-compound | P1/P2/P3 severity findings from specialist reviewers for one feature |
| `.beads/learnings/YYYYMMDD-<feature_slug>.md` | beo-compound | all skills when relevant | Finalized learnings from one completed feature |
| `.beads/critical-patterns.md` | beo-dream | beo-explore, beo-plan, beo-validate, beo-debug, beo-dream | Promoted high-value patterns consolidated from multiple features with explicit approval |

### Knowledge Store

Use this canonical knowledge-store order:

1. Flat files under `.beads/learnings/` and `.beads/critical-patterns.md` (authoritative)
2. QMD retrieval over indexed learnings (optional enhancement)
3. Obsidian CLI reads/writes in the vault (optional mirror)

| Operation | Canonical | Optional enhancement |
|-----------|-----------|----------------------|
| Write learnings | Flat file to `.beads/learnings/` | Mirror to Obsidian vault via `obsidian create/append` |
| Search learnings | `grep` over `.beads/learnings/` and `.beads/critical-patterns.md` | QMD query/search plus vault context |

See `knowledge-store.md` for full integration details.

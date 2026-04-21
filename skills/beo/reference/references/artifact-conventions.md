# Artifact Conventions

Use these rules for all beo pipeline artifacts.

## Artifact Protocol

Task artifacts come in three kinds:
- `spec` — what to do
- `report` — what was done
- `task_state` — machine-readable status snapshot

### Locations

| Artifact | Storage | Read Command | Write Command |
|----------|---------|-------------|---------------|
| `spec` | Bead description | `br show <id> --json` → `.description` | `br update <id> --description "<content>"` |
| `report` | Latest bead comment artifact | `br comments list <id> --json --no-daemon` → scan for header | `br comments add <id> --no-daemon --message "<formatted>"` |
| `task_state` | Latest bead comment artifact | `br comments list <id> --json --no-daemon` → scan for header | `br comments add <id> --no-daemon --message "<formatted>"` |

### Spec

Store task specifications in the bead description as Markdown. Write them during task creation or planning. Use `bead-description-templates.md` as the source of truth.

| Bead type | Required template |
|-----------|-------------------|
| Planned execution beads | Planned Task Bead Template |
| Reactive fix beads | Reactive Fix Bead Template |
| Review/debug follow-up beads | Follow-Up Bead Template |

Rules:
- Format every bead description as Markdown.
- Exempt reactive fix beads created by `beo-review` or `beo-debug` from Story Context.
- Keep reactive fix beads on the shared reactive template.
- Use abbreviated Story Context only where the chosen template explicitly allows it.

```bash
br update <id> --description "<Markdown content using the shared bead template>"
```

### Report

Store worker reports as comment-backed artifacts:

```text
---ARTIFACT:report:v<version>---
<markdown content>
---END_ARTIFACT---
```

Short report example:

```bash
br comments add <id> --no-daemon --message "---ARTIFACT:report:v1---
## Summary
Implemented auth middleware with JWT validation.

## Changes
- Created src/middleware/auth.ts
- Added tests in src/middleware/auth.test.ts

## Verification
- All 156 tests pass
---END_ARTIFACT---"
```

Large reports may be attached from a temp file:

```bash
br comments add <id> --file /tmp/report.md --no-daemon
```

Read the latest report by scanning `br comments list <id> --json --no-daemon` backward for the newest report artifact header.

Close-time report minimum fields:
- bead ID
- files changed
- tests added or modified
- verification result

### Task State

Store `task_state` as a comment-backed artifact with this shape:

```text
---ARTIFACT:task_state:v<version>---
beo_status: <pending | dispatch_prepared | in_progress | done | blocked | failed | partial | cancelled>
worker: <agent-name or empty>
claimed_at: <ISO-8601 or empty>
blocked_by: <bead-id list or empty>
blocker_type: <MISSING_CONTEXT | DEPENDENCY_NOT_MET | TECHNICAL_FAILURE | AMBIGUITY or empty>
context_pct: <estimated context usage percentage>
---END_ARTIFACT---
```

Example:

```bash
br comments add <id> --no-daemon --message "---ARTIFACT:task_state:v1---
beo_status: in_progress
worker: BlueLake
claimed_at: 2026-03-15T10:30:00Z
blocked_by:
blocker_type:
context_pct: 35
---END_ARTIFACT---"
```

Rules:
- Treat task state as optional and informational only.
- Treat `br` status as authoritative. See `status-mapping.md`.
- Update `task_state` when claiming, blocking, or completing beads.
- Read the latest version when building swarm status.
- Do not treat `beo_status: done` as bead closure.
- Run `br close <id>` before writing `task_state: done`.
- If a worker records `task_state: done`, write the completion report first.
- Keep reservation release and swarm coordination in execution flow and Agent Mail protocols, not new artifact kinds.

### Version Semantics

- Use monotonically increasing integer versions: `v1`, `v2`, `v3`, ...
- Read the highest version of each artifact kind.
- Increment the version when updating an artifact.
- Multiple versions may coexist in comments; only the latest matters.

### Batch Sync Rule

After multiple artifact writes or multiple `br` mutations:

```bash
br sync --flush-only
```

## Slug Lifecycle

Use this protocol to create, read, preserve, and recover the immutable `feature_slug`.

### Source of Truth

Store the canonical slug in the first line of the epic description:

```text
slug: <feature_slug>
```

The slug ties together:
- the epic description
- `.beads/artifacts/<feature_slug>/`
- `STATE.json`
- `HANDOFF.json`
- learnings file naming

### When To Create

Create the slug during new-feature intake, before any artifact or learning depends on it.

### Creation Procedure

1. Create the feature epic if it does not already exist.
2. Derive the slug from the epic title using pipeline rules.
3. Write it as the first line of the epic description.

```bash
br update <EPIC_ID> --description "slug: <feature_slug>"
```

### Read Procedure

Extract the first-line slug from the epic description and use it for:
- `.beads/artifacts/<feature_slug>/...`
- `feature_name` in `HANDOFF.json`
- `feature_slug` in `STATE.json`
- learnings file slug components

### Safe Update Procedure

When updating the epic description:

1. Read the current description first.
2. Preserve the first line.
3. Replace only the body below the slug line.
4. Rewrite the full description with the slug first.

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

Case 1: no tasks yet
- recover the slug from the epic title
- rewrite the epic description with the slug first line

Case 2: tasks or artifacts already exist
- stop
- inspect `.beads/artifacts/` to identify the existing feature directory
- restore that slug to the epic description
- do not guess between multiple plausible directories without user confirmation

Example summary update:

```bash
br update <EPIC_ID> --description "slug: <feature_slug>\nFeature: <name>\n\nScope: <summary>\nDecisions: <count> locked\nDomains: <list>"
```

## File Layout

### State Files

| File | Written By | Read By | Purpose |
|------|-----------|---------|---------|
| `.beads/STATE.json` | `beo-route`, `beo-explore`, `beo-plan`, `beo-validate`, `beo-swarm`, `beo-execute`, `beo-review`, `beo-compound` | Next skill in pipeline | Intra-session handoff state |
| `.beads/HANDOFF.json` | Any skill at context checkpoint | `beo-route` on resume | Cross-session resume |
| `.beads/onboarding.json` | `beo-onboard` | All beo skills during onboarding checks | Bootstrap readiness and startup-contract freshness |
| `.beads/beo_status.mjs` | `beo-onboard` | Humans and agents | Read-only scout summary |

Use `state-and-handoff-protocol.md` as the canonical source for `STATE.json` and `HANDOFF.json` schema and semantics.

### Feature Artifact Root

Store all feature artifacts under:

```text
.beads/artifacts/<feature_slug>/
```

### Feature Artifacts

| File | Written By | Read By | Purpose |
|------|-----------|---------|---------|
| `CONTEXT.md` | `beo-explore` | downstream skills | Locked decisions; source of truth |
| `discovery.md` | `beo-plan` | validation and later planning | Research findings |
| `approach.md` | `beo-plan` | validation, execution, review, later planning | Chosen strategy and risk map |
| `plan.md` | `beo-plan` | validation, execution, review, compounding | Human-readable plan summary |
| `phase-plan.md` | `beo-plan` | routing, validation, later planning | Optional whole-feature sequencing for multi-phase work |
| `phase-contract.md` | `beo-plan` | routing, validation, execution, review, compounding | Current-phase entry/exit state, demo story, scope, pivot signals |
| `story-map.md` | `beo-plan` | routing, validation, execution, review, compounding | Current-phase story order and story-to-bead mapping |

### Artifact Semantics

| Artifact | Role | Key Rule |
|----------|------|----------|
| `CONTEXT.md` | Feature definition | All downstream work must honor it |
| `discovery.md` | Research findings | Evidence, not the final plan |
| `approach.md` | Strategy and risk map | Canonical strategy artifact |
| `plan.md` | Plan summary | Not a replacement for structured artifacts |
| `phase-plan.md` | Whole-feature sequencing | Absent for single-phase work |
| `phase-contract.md` | Current phase only | Never whole-feature in multi-phase work |
| `story-map.md` | Current phase only | Future phases stay deferred in `phase-plan.md` |

Planning mode rules:
- `phase-plan.md` present → multi-phase
- `phase-plan.md` absent → single-phase
- current-phase completion is not whole-feature completion in multi-phase work

### Artifact Cleanup On Replanning

Use `state-and-handoff-protocol.md` for canonical replanning cleanup. Hard rule: delete stale `phase-plan.md`; do not mark it invalid. Keep `phase-contract.md` and `story-map.md` aligned to the real current phase.

### Pipeline-Level Files

| File | Written By | Read By | Purpose |
|------|-----------|---------|---------|
| `.beads/artifacts/<feature_slug>/review-findings.md` | `beo-review` | `beo-compound` | Review findings for one feature |
| `.beads/learnings/YYYYMMDD-<feature_slug>.md` | `beo-compound` | all skills when relevant | Finalized learnings for one feature |
| `.beads/critical-patterns.md` | `beo-compound`, `beo-dream` | relevant skills | Promoted reusable patterns and long-horizon consolidated guidance |

### Knowledge Store

Precedence:
1. `.beads/learnings/` and `.beads/critical-patterns.md` as authoritative flat files
2. QMD retrieval over indexed learnings when available
3. Obsidian CLI reads or writes as optional mirror or read enhancement

| Operation | Canonical | Optional enhancement |
|-----------|-----------|----------------------|
| Write learnings | Flat file to `.beads/learnings/` | Mirror to Obsidian vault via `obsidian create/append` |
| Search learnings | QMD query/search plus direct read of `.beads/critical-patterns.md` | Flat-file content search |

See `knowledge-store.md` for full integration details.

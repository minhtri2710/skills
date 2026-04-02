# Pipeline Contracts

Canonical definitions for cross-cutting pipeline protocols. All skills reference this file for pipeline-level rules (back-edge responsibilities, artifact write rules, slug protocol). For task-state transitions and label semantics, see `status-mapping.md` as the canonical source. For approval grant rules, see `approval-gates.md`.

## Table of Contents

1. [State Routing Table](#state-routing-table)
2. [HANDOFF.json Schema](#handoffjson-schema)
3. [STATE.md Schema](#statemd-schema)
4. [Label Lifecycle](#label-lifecycle)
5. [Task Enumeration](#task-enumeration)
6. [Epic Lifecycle](#epic-lifecycle)
7. [Shared Artifact Write Rules](#shared-artifact-write-rules)
8. [Feature Slug](#feature-slug)

---

## State Routing Table

Evaluate **top-to-bottom, first match wins**. Earlier rows take priority.

| # | Condition | State | Route To |
|---|-----------|-------|----------|
| 1 | Skill creation or editing requested | **meta-skill** | `beo-writing-skills` |
| 2 | Any tasks have `blocked` or `failed` labels, `debug_attempted` label absent | **needs-debugging** | `beo-debugging` |
| 3 | Any tasks have `blocked` or `failed` labels, `debug_attempted` label present | **blocked** | Report blockers, ask user for decision |
| 4 | All tasks closed, epic closed, no learnings file | **learnings-pending** | `beo-compounding` |
| 5 | Epic is closed | **completed** | Report status, ask for next work |
| 6 | Any tasks have `partial` or `cancelled` labels, epic still open | **partial-completion** | Report status, ask user for decision |
| 7 | Epic exists, all tasks for the final execution scope are closed, epic still open, and no later phases remain | **ready-to-review** | `beo-reviewing` |
| 8 | Epic exists, current-phase tasks exist, some in_progress/closed (and no blocked/failed) | **executing** | `beo-executing` |
| 9 | Epic exists, current-phase tasks exist, `approved` label on epic, all tasks open, 3+ independent tasks | **ready-to-swarm** | `beo-swarming` |
| 10 | Epic exists, current-phase tasks exist, `approved` label on epic, all tasks open, ≤2 independent tasks | **ready-to-execute** | `beo-executing` |
| 11 | Epic exists, current-phase tasks exist, no `approved` label, `phase-contract.md` AND `story-map.md` exist | **ready-to-validate** | `beo-validating` |
| 12 | Epic exists, `approach.md` exists, no `approved` label, current-phase artifacts missing or incomplete | **planning-current-phase** | `beo-planning` |
| 13 | Epic exists, `CONTEXT.md` exists, no `approach.md` | **planning-needs-approach** | `beo-planning` |
| 14 | Epic exists, no tasks, no `approved` label | **exploring** | `beo-exploring` |
| 15 | Learnings stale (last dream run >30 days or 3+ new learnings since last dream), user requests consolidation | **consolidation-due** | `beo-dream` |

Key changes from prior versions:
- explicit distinction between approach-level planning and current-phase planning
- routing now recognizes that `phase-contract.md` and `story-map.md` are current-phase artifacts
- final review is only valid when later phases do not remain
- current-phase completion is not whole-feature completion for multi-phase work

Ordering notes:
1. Row 4 (`learnings-pending`) must stay above Row 5 (`completed`) so closed epics route to compounding before they are treated as fully complete.
2. Row 14 (`exploring`) is the fallback after the context and planning-artifact rows fail. Read it as "epic exists, but planning has not actually started yet."

### Planning Artifact Hierarchy

The planning phase now produces up to seven artifacts in this order:

| Artifact | Role | Gate-Controlling |
|----------|------|-----------------|
| `CONTEXT.md` | Locked decisions: source of truth | Yes (exploring → planning gate) |
| `discovery.md` | Research findings from discovery work | No |
| `approach.md` | Chosen implementation strategy, alternatives, and risk map | Yes for strategy quality; informs validation and downstream routing |
| `plan.md` | Human-readable planning summary | No |
| `phase-plan.md` | Optional whole-feature sequencing for multi-phase work | Yes when present (planning approval for multi-phase sequencing) |
| `phase-contract.md` | Current phase as closed loop: entry/exit state, demo, scope | Yes (planning → validating gate) |
| `story-map.md` | Current-phase story sequence, closure check, story-to-bead mapping | Yes (planning → validating gate) |

The validation gate requires `phase-contract.md` AND `story-map.md` for the **current phase**.

`phase-plan.md` is optional and only exists when the feature is multi-phase.

---

## HANDOFF.json Schema

Use `state-and-handoff-protocol.md` as the canonical source for the base `HANDOFF.json` schema, resume semantics, cleanup rule, and `STATE.md` header requirements.

---

## Label Lifecycle

### `approved` Label

| Event | Action | Skill |
|-------|--------|-------|
| User approves current phase for execution | `br label add <EPIC_ID> -l approved` | validating |
| Back-edge to planning | `br label remove <EPIC_ID> -l approved` | executing, swarming, reviewing |
| Back-edge to exploring | `br label remove <EPIC_ID> -l approved` | validating, reviewing |

**Invariant:** The `approved` label must be removed whenever routing back to planning or exploring. This forces re-validation before execution resumes.

### Status Labels

| Label | Set By | Removed By |
|-------|--------|------------|
| `dispatch_prepared` | executing (Phase 2) | executing (Phase 2, after claim) |
| `blocked` | executing (blocker handling) | executing (stale label cleanup) |
| `failed` | executing (blocker handling) | executing (stale label cleanup) |
| `partial` | executing (partial completion) | executing (stale label cleanup) |
| `cancelled` | user decision | - |
| `debug_attempted` | beo-debugging (Step 5) | beo-executing (on unblock) |

---

## Task Enumeration

**Canonical command** to list tasks under an epic:

```bash
br dep list <EPIC_ID> --direction up --type parent-child --json
```

Do NOT use `jq 'select(.id | startswith(...))'`. The `startswith` pattern assumes dotted IDs and misses fix beads created with dependency edges instead of dotted child IDs.

Interpret task enumeration against the active planning mode:
- for single-phase work, the epic task set is the current execution scope
- for multi-phase work, only the current-phase subset is executable now; later phases remain deferred in `phase-plan.md`

---

## Epic Lifecycle

The canonical Feature States table (planning → approved → executing → completed) lives in `status-mapping.md` → Feature States.

**Summary:** Epics start as `open` with no labels (planning), gain `approved` via validation, transition to `in_progress` when execution claims them, and close when the feature completes. See `status-mapping.md` for the full state table and exact commands.

**Who transitions to executing:** The first skill that starts execution (executing or swarming) must run `br update <EPIC_ID> --claim` before dispatching any workers.

**Router epic query:** Use `br list --type epic -a --json` to find all epics including `in_progress` and `closed` ones. Filter in application logic.

---

## Shared Artifact Write Rules

### critical-patterns.md

- **Who writes:** Only `beo-compounding` proposes entries.
- **Approval required:** Compounding must present proposed promotions to the user and receive explicit approval before appending. Never auto-append.
- **Format:** See compounding's Phase 4 for entry format.
- **Aligned with:** dream (hard rule: do not edit `critical-patterns.md` without explicit approval) and reviewing (red flag: "Promoting learnings without approval").

### Fix Beads (from debugging)

Fix beads must use BOTH `--parent` and an explicit blocking dependency:

```bash
br create "Fix: <root cause summary>" -t task --parent <EPIC_ID> --deps blocks:<original-bead-id>
```

This ensures fix beads are:
1. Visible in epic task enumeration (via `--parent`)
2. Properly blocking the original bead (via `--deps blocks:<original-bead-id>`)

### Task Creation During Validation

Validation may only create **spike beads** (time-boxed experiments, priority 0). Spikes are not implementation tasks; they are experiments to reduce uncertainty. For actual missing tasks, route back to `beo-planning`.

---

## Feature Slug

Every feature gets an immutable `feature_slug` created once by the router and used for all artifact paths.

**Rules:**
- Derived from the epic title at creation time
- Lowercase, hyphens only, max 40 chars: `auth-token-refresh`, `bead-scope-isolation`
- Stored in: epic bead description (first line: `slug: <feature_slug>`), HANDOFF.json (`feature_name` field, which carries the slug/path identifier), STATE.md (`Feature` field)
- Used for: `.beads/artifacts/<feature_slug>/` path, HANDOFF resume context, and learnings file slug component

**Canonical derivation:**
1. Take the epic title
2. Lowercase
3. Replace spaces and underscores with hyphens
4. Remove all non-alphanumeric-hyphen characters
5. Collapse consecutive hyphens
6. Truncate to 40 characters
7. Remove trailing hyphens

Once set, the slug never changes, even if the epic title is updated later.

# Pipeline Contracts

Canonical definitions for cross-cutting pipeline protocols. All skills reference this file for pipeline-level rules (back-edge responsibilities, artifact write rules, slug protocol). For task-state transitions and label semantics, see `status-mapping.md` as the canonical source. For approval grant rules, see `approval-gates.md`.

## Table of Contents

1. [State Routing Table](#state-routing-table)
2. [HANDOFF.json Schema](#handoffjson-schema)
3. [STATE.json Schema](#statejson-schema)
4. [Label Lifecycle](#label-lifecycle)
5. [Task Enumeration](#task-enumeration)
6. [Epic Lifecycle](#epic-lifecycle)
7. [Shared Artifact Write Rules](#shared-artifact-write-rules)
8. [Feature Slug](#feature-slug)

---

## State Routing Table

Evaluate **top-to-bottom, first match wins**. Earlier rows take priority.

### NextAction Types

Every router cycle ends with exactly one `NextAction`:

| Type | Meaning |
|------|---------|
| `LoadSkill(name)` | Continue the pipeline by loading the named skill |
| `ReturnToUser(reason)` | Pause the pipeline; a human decision or clarification is needed |
| `Stop(done)` | The session is complete; no further routing needed |

### Quick-Scope Definition

Quick applies only when ALL of these are true:
- the work touches `<=2` files
- there is no new public API
- there are no schema changes
- there is no user-facing behavior change
- there is no auth/security impact

This includes very small, well-scoped requests that previously fell under instant intake, such as single-file work that is plausibly `<30 minutes`.

| # | Condition | State | Route To |
|---|-----------|-------|----------|
| 1 | `.beads/onboarding.json` is missing, unreadable, or stale | **needs-onboarding** | `LoadSkill(beo-using-beo)` |
| 2 | Skill creation or editing requested | **meta-skill** | `LoadSkill(beo-writing-skills)` |
| 3 | User explicitly requests learnings consolidation / dream work and the request is not impossible or stale | **consolidation-requested** | `LoadSkill(beo-dream)` |
| 4 | No active epic exists and the new request is clearly debug work | **new-debug-intake** | `LoadSkill(beo-debugging)` |
| 5 | No active epic exists and the new request is clearly quick-scoped work | **new-quick-intake** | create epic + Quick Path Scaffold, then `LoadSkill(beo-validating)` |
| 6 | No active epic exists and the request is normal feature intake | **new-feature-intake** | create epic, then `LoadSkill(beo-exploring)` |
| 7 | Any tasks in the active execution scope have `blocked` or `failed` labels, `debug_attempted` label absent | **needs-debugging** | `LoadSkill(beo-debugging)` |
| 8 | Any tasks in the active execution scope have `blocked` or `failed` labels, `debug_attempted` label present | **blocked** | `ReturnToUser(blockers need a decision)` |
| 9 | Epic is closed, any child task NOT closed | **invalid-epic-closure** | `ReturnToUser(epic closure is inconsistent and open tasks must be resolved)` |
| 10 | All tasks in the final execution scope are in canonical terminal states (`done`, `cancelled`, or `failed`), epic closed, no learnings file | **learnings-pending** | `LoadSkill(beo-compounding)` |
| 11 | Epic is closed | **completed** | `Stop(done)` |
| 12 | Any tasks in the active execution scope have `partial` or `cancelled` labels, epic still open | **partial-completion** | `ReturnToUser(partial completion requires a decision)` |
| 13 | Epic exists, all tasks for the current phase are in canonical terminal states (`done`, `cancelled`, or `failed`), epic still open, and later phases remain | **phase-complete-needs-replan** | `LoadSkill(beo-planning)` |
| 14 | Epic exists, all tasks for the final execution scope are in canonical terminal states (`done`, `cancelled`, or `failed`), epic still open, and no later phases remain | **ready-to-review** | `LoadSkill(beo-reviewing)` |
| 15 | Epic exists, current-phase tasks exist, no `approved` label, and some current-phase tasks are already `in_progress` or `closed` | **approval-invalidated** | `LoadSkill(beo-planning)` |
| 16 | Epic exists, current-phase tasks exist, `approved` label on epic, and some current-phase tasks are `in_progress` or `closed` (and no blocked/failed) | **executing** | `LoadSkill(beo-executing)` |
| 17 | Epic exists, current-phase tasks exist, `approved` label on epic, all tasks open, 3+ independent tasks | **ready-to-swarm** | `LoadSkill(beo-swarming)` |
| 18 | Epic exists, current-phase tasks exist, `approved` label on epic, all tasks open, ≤2 independent tasks | **ready-to-execute** | `LoadSkill(beo-executing)` |
| 19 | Epic exists, current-phase tasks exist, no `approved` label, `phase-contract.md` AND `story-map.md` exist, and execution approval has not yet been granted or was removed on a back-edge | **ready-to-validate** | `LoadSkill(beo-validating)` |
| 20 | Epic exists, planning mode is `multi-phase`, `phase-plan.md` exists, phase sequence/current phase approval is still pending, and execution has not been approved | **awaiting-planning-approval** | `ReturnToUser(planning approval is required before continuing)` |
| 21 | Epic exists, `approach.md` exists, no `approved` label, current-phase artifacts missing or incomplete | **planning-current-phase** | `LoadSkill(beo-planning)` |
| 22 | Epic exists, `CONTEXT.md` exists, no `approach.md` | **planning-needs-approach** | `LoadSkill(beo-planning)` |
| 23 | Epic exists, no tasks, no `approved` label | **exploring** | `LoadSkill(beo-exploring)` |

Key changes from prior versions:
- explicit distinction between approach-level planning and current-phase planning
- routing now recognizes that `phase-contract.md` and `story-map.md` are current-phase artifacts
- explicit phase-advancement routing sends completed current phases with later phases remaining back to planning
- execution routing now requires a valid `approved` label lifecycle before re-entering `beo-executing`
- final review is only valid when later phases do not remain

Ordering notes:
1. The onboarding row must stay first so stale or missing onboarding blocks all deeper routing.
2. Explicit user-intent rows stay near the top so meta-skill work and explicit dream requests short-circuit feature-state routing when they are actually actionable.
3. New-feature intake rows stay above active-feature rows so clearly quick/debug/normal feature requests can bootstrap correctly before normal state routing applies.
4. `invalid-epic-closure` (row 9) must stay above `learnings-pending` and `completed` so a prematurely closed epic with open child tasks is caught before being treated as finished.
5. `learnings-pending` must stay above `completed` so closed epics route to compounding before they are treated as fully complete.
6. `phase-complete-needs-replan` must stay above review and execution rows so multi-phase advancement does not get misclassified as generic execution.
7. `awaiting-planning-approval` must stay above `planning-current-phase` and `ready-to-validate` semantics in any implementation logic so explicit planning-approval pauses are not skipped on resume.
8. `exploring` is the fallback after the context and planning-artifact rows fail. Read it as "epic exists, but planning has not actually started yet."

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

Use `state-and-handoff-protocol.md` as the canonical source for the base `HANDOFF.json` schema, resume semantics, cleanup rule, and `STATE.json` header requirements.

---

## STATE.json Schema

Use `state-and-handoff-protocol.md` as the canonical source for the `STATE.json` schema, field definitions, and write semantics.

---

## Label Lifecycle

See `status-mapping.md` as the canonical source for all label semantics, status-to-label mappings, and stale label cleanup rules.

The `approved` label back-edge removal invariant: `approved` must be removed whenever routing back to planning or exploring; on normal completion it remains on the closed epic as historical state.

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

**Summary:** Epics start as `open` with no labels (planning), gain `approved` via validation, transition to `in_progress` when execution claims them, and close when the feature completes. Closed epics normally retain `approved` as the historical marker that validated execution completed without a planning/exploring back-edge. See `status-mapping.md` for the full state table and exact commands.

**Who transitions to executing:** The first skill that starts execution (executing or swarming) must run `br update <EPIC_ID> --claim` before dispatching any workers.

**Router epic query:** Use `br list --type epic -a --json` to find all epics including `in_progress` and `closed` ones. Filter in application logic.

---

## Shared Artifact Write Rules

### critical-patterns.md

- **Who writes:** `beo-compounding` and `beo-dream` propose entries.
- **Approval required:** Both skills must present proposed promotions to the user and receive explicit approval before appending. Never auto-append.
- **Format:** See compounding's Phase 4 for entry format.
- **Aligned with:** dream (hard rule: do not edit `critical-patterns.md` without explicit approval) and reviewing (red flag: "Promoting learnings without approval").

### Fix Beads (from debugging)

Fix beads use `--parent` for graph visibility and reference the affected bead ID in the description for traceability:

```bash
br create "Fix: <root cause summary>" -t task --parent <EPIC_ID> -p 1 --json
```

Do not use `--deps blocks:<closed-bead>` — the original bead is typically already closed, making the blocking dependency a no-op.
Reference the affected bead ID in the fix bead description (using the Reactive Fix Bead Template from `bead-description-templates.md`) instead.

### Task Creation During Validation

Validation may only create **spike beads** (time-boxed experiments, priority 0). Spikes are not implementation tasks; they are experiments to reduce uncertainty. For actual missing tasks, route back to `beo-planning`.

---

## Feature Slug

Feature slugs are canonicalized and managed by `slug-protocol.md`.

- Use `feature_slug` for artifact paths and learnings file naming.
- Store the same immutable slug in the epic description, `STATE.json`, and `HANDOFF.json`.
- Do not restate slug derivation or mutation rules here; `slug-protocol.md` is the single source of truth for creation, reading, safe update, and recovery.

---

See also: `approval-gates.md` for gate definitions that reference this contract.

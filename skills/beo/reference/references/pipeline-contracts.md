# Pipeline Contracts

Canonical pipeline-level rules for all skills: back-edge responsibilities, artifact write rules, and slug protocol. Use `status-mapping.md` for task-state transitions and label semantics, and `approval-gates.md` for approval grant rules.

## Table of Contents

1. [State Routing Table](#state-routing-table)
2. [Cross-Skill Invariants](#cross-skill-invariants)
3. [HANDOFF.json Schema](#handoffjson-schema)
4. [STATE.json Schema](#statejson-schema)
5. [Label Lifecycle](#label-lifecycle)
6. [Task Enumeration](#task-enumeration)
7. [Epic Lifecycle](#epic-lifecycle)
8. [Shared Artifact Write Rules](#shared-artifact-write-rules)
9. [Feature Slug](#feature-slug)

---

## State Routing Table

Evaluate **top-to-bottom; first match wins**.

### NextAction Types

Every router cycle ends with exactly one `NextAction`:

| Type | Meaning |
|------|---------|
| `LoadSkill(name)` | Continue the pipeline by loading the named skill |
| `ReturnToUser(reason)` | Pause the pipeline; a human decision or clarification is needed |
| `Stop(done)` | The session is complete; no further routing needed |

### Quick-Scope Definition

Apply quick scope only when ALL are true:
- the work touches `<=2` files
- there is no new public API
- there are no schema changes
- there is no user-facing behavior change
- there is no auth/security impact

Include very small, well-scoped requests that previously fell under instant intake, such as single-file work plausibly `<30 minutes`.

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

Ordering notes:
1. Keep the onboarding row first; stale or missing onboarding blocks deeper routing.
2. Keep explicit user-intent rows near the top; let meta-skill work and explicit dream requests short-circuit feature-state routing when actionable.
3. Keep new-feature intake rows above active-feature rows; bootstrap quick/debug/normal feature requests before normal state routing applies.
4. Keep `invalid-epic-closure` (row 9) above `learnings-pending` and `completed`; catch prematurely closed epics with open child tasks before treating them as finished.
5. Keep `learnings-pending` above `completed`; route closed epics to compounding before treating them as fully complete.
6. Keep `phase-complete-needs-replan` above review and execution rows; do not misclassify multi-phase advancement as generic execution.
7. Keep `awaiting-planning-approval` above `planning-current-phase` and `ready-to-validate`; do not skip explicit planning-approval pauses on resume.
8. Treat `exploring` as the fallback after the context and planning-artifact rows fail: epic exists, but planning has not started.

### Planning Artifact Hierarchy

Planning produces up to seven artifacts in this order:

| Artifact | Role | Gate-Controlling |
|----------|------|-----------------|
| `CONTEXT.md` | Locked decisions: source of truth | Yes (exploring → planning gate) |
| `discovery.md` | Research findings from discovery work | No |
| `approach.md` | Chosen implementation strategy, alternatives, and risk map | Yes for strategy quality; informs validation and downstream routing |
| `plan.md` | Human-readable planning summary | No |
| `phase-plan.md` | Optional whole-feature sequencing for multi-phase work | Yes when present (planning approval for multi-phase sequencing) |
| `phase-contract.md` | Current phase as closed loop: entry/exit state, demo, scope | Yes (planning → validating gate) |
| `story-map.md` | Current-phase story sequence, closure check, story-to-bead mapping | Yes (planning → validating gate) |

Validation requires `phase-contract.md` AND `story-map.md` for the **current phase**.

Create `phase-plan.md` only for multi-phase work.

---

## Cross-Skill Invariants

Use these rules for all cross-skill handoffs. If a local skill summary disagrees, this section wins.

### Single-Feature Workspace Thread

Beo uses singleton `.beads/STATE.json` and `.beads/HANDOFF.json` files, so one workspace supports one active feature thread at a time.

Checklist:
- Do not silently choose among multiple active epics.
- Route back to the user to select the intended epic before deeper routing continues.
- Treat multiple active epics as ambiguity, not as a recoverable default, in onboarding, router, and resume flows.

### Planning -> Validating Boundary

Planning owns artifact creation and current-phase decomposition. Validating owns execution-readiness proof.

Checklist:
- Hand off from planning only after current-phase artifacts and bead graph exist.
- Treat planning approval for `multi-phase` work as approval for sequence and current-phase selection only; never treat it as execution approval.
- Do not invent missing planning artifacts in validating; if they are absent or structurally wrong, route back to planning.

### Validation Approval Ownership

Execution approval belongs to `beo-validating`.

Checklist:
- Add `approved` in `beo-validating` only after explicit user approval.
- Do not let any other skill add `approved`.
- Remove `approved` on any back-edge to planning or exploring before replanning continues.

See `approval-gates.md` for the per-skill ownership matrix.

### Validating -> Executing / Swarming Mode Selection

Do not treat validation as complete until the next execution mode is chosen.

Checklist:
- Route to `beo-swarming` if 3+ independent ready tasks exist with isolated file scope and no serial bottleneck.
- Otherwise route to `beo-executing`.
- Treat "swarming not justified" as a mode-selection outcome, not a planning defect.

### Execution and Review Back-Edges

Preserve planning integrity when scope changes.

Checklist:
- If implementation or UAT reveals a planning-level intent change, update `CONTEXT.md`, remove `approved`, and route back to `beo-planning`.
- If execution discovers a local fixable defect without changing locked decisions, keep work in execution/review flow instead of reopening planning.
- Re-enter review-created P1 fixes through `beo-executing`; do not patch code directly in review.

### Phase Advancement and Closure

Treat current-phase completion and feature completion as different states.

Checklist:
- If later phases remain, route current-phase completion back to `beo-planning` and keep the feature open.
- If no later phases remain and the final execution scope is terminal, route to `beo-reviewing`.
- Close the epic in `beo-reviewing` only after P1 fixes are resolved and UAT passes.
- Move state to `learnings-pending` after closure and before compounding begins.

### Resume and HANDOFF Precedence

Use both checkpoint files and live graph state when resuming.

Checklist:
- Let a valid, current `HANDOFF.json` drive resume.
- Ignore malformed handoff data; reconstruct from live graph state and artifacts.
- Let live state win when live graph/artifact state contradicts a stale handoff.
- Treat `HANDOFF.json` as cleanup state, not durable truth; remove it only after the receiving skill writes fresh `STATE.json`.

---

## HANDOFF.json Schema

Use `state-and-handoff-protocol.md` as the canonical source for the base `HANDOFF.json` schema, resume semantics, cleanup rule, and `STATE.json` header requirements.

---

## STATE.json Schema

Use `state-and-handoff-protocol.md` as the canonical source for the `STATE.json` schema, field definitions, and write semantics.

---

## Label Lifecycle

See `status-mapping.md` as the canonical source for all label semantics, status-to-label mappings, and stale label cleanup rules.

Back-edge removal invariant for `approved`:
- Remove it via `br label remove <EPIC_ID> -l approved` whenever routing back to planning or exploring.
- Leave it on the closed epic on normal completion as historical state.
- See `approval-gates.md` → Approved Label Ownership for the per-skill responsibility matrix.

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

| Topic | Contract |
|------|----------|
| Summary | Start epics as `open` with no labels (planning), add `approved` via validation, transition to `in_progress` when execution claims them, and close when the feature completes. Closed epics normally retain `approved` as the historical marker that validated execution completed without a planning/exploring back-edge. See `status-mapping.md` for the full state table and exact commands. |
| Who transitions to executing | Run `br update <EPIC_ID> --claim` in the first skill that starts execution (executing or swarming) before dispatching any workers. |
| Router epic query | Use `br list --type epic -a --json` to find all epics, including `in_progress` and `closed`. Filter in application logic. |
| Who closes the epic | Let `beo-reviewing` close the epic via `br close <EPIC_ID>` as part of the completion handoff, after all P1 fixes are resolved and UAT passes. Do this before writing `learnings-pending` state. Do not let any other skill close the epic during normal pipeline flow. |

---

## Shared Artifact Write Rules

### critical-patterns.md

| Field | Rule |
|------|------|
| Who writes | `beo-compounding` and `beo-dream` propose entries. |
| Approval required | Present proposed promotions to the user and receive explicit approval before appending. Never auto-append. |
| Format | See compounding's Phase 4 for entry format. |
| Aligned with | Follow dream (hard rule: do not edit `critical-patterns.md` without explicit approval) and reviewing (red flag: "Promoting learnings without approval"). |

### Fix Beads (from debugging)

Use `--parent` for graph visibility and reference the affected bead ID in the description for traceability:

```bash
br create "Fix: <root cause summary>" -t task --parent <EPIC_ID> -p 1 --json
```

Do not use `--deps blocks:<closed-bead>`; the original bead is typically already closed, so the blocking dependency is a no-op.
Reference the affected bead ID in the fix bead description instead, using the Reactive Fix Bead Template from `bead-description-templates.md`.

### Task Creation During Validation

Create only **spike beads** during validation (time-boxed experiments, priority 0). Do not treat spikes as implementation tasks; use them to reduce uncertainty. For actual missing tasks, route back to `beo-planning`.

---

## Feature Slug

Feature slugs are canonicalized and managed by `artifact-conventions.md#slug-lifecycle`.

- Use `feature_slug` for artifact paths and learnings file naming.
- Store the same immutable slug in the epic description, `STATE.json`, and `HANDOFF.json`.
- Do not restate slug derivation or mutation rules here; `artifact-conventions.md#slug-lifecycle` is the single source of truth for creation, reading, safe update, and recovery.

---

See also: `approval-gates.md` for gate definitions that reference this contract.

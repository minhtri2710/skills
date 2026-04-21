# Router Operations

Detailed operational playbook for `beo-route`.

Load this file when you need exact bootstrap checks, intake classification rules, resume validation, planning-aware routing, or doctor-mode commands.

## Intent Short-Circuit Rule

Before doing full feature-state routing, check whether the user's explicit request already selects a meta-path.
Examples:
- creating or editing a beo skill -> `beo-author`
- root-cause analysis of blocked/failing work -> `beo-debug`
- explicit learnings consolidation request -> `beo-dream`

If explicit user intent clearly selects one of these paths, honor it unless live state proves the request is impossible, stale, or aimed at the wrong feature.

Conversational phrasing is **not** a valid short-circuit. Requests like "research X with me", "let's explore X", or "help me think through X" imply non-trivial work and must route through the state table normally. Route emits a next target only; if the session should pause for a human answer or a simple lookup, route must still emit `next: "user"` or `next: "done"` rather than answering directly.

## Table of Contents

- [1. Workspace Bootstrap](#1-workspace-bootstrap)
- [2. New Feature Intake Classification](#2-new-feature-intake-classification)
- [3. Quick Scope Handling](#3-quick-scope-handling)
- [4. Artifact Inspection Order](#4-artifact-inspection-order)
- [5. Planning-Aware Routing Rules](#5-planning-aware-routing-rules)
- [6. Resume From Handoff](#6-resume-from-handoff)
- [7. Doctor Mode](#7-doctor-mode)
- [8. STATE.json on Handoff](#8-statejson-on-handoff)

## 1. Workspace Bootstrap

Run once per session when onboarding is missing or stale, or when `.beads/` is missing or unhealthy.

Before normal bootstrap, run the live `beo-onboard` repo check against the current skill install.
If the live check reports onboarding missing, unreadable, stale, or otherwise unhealthy, stop and route to `beo-onboard`.

If the live check reports onboarding current and `.beads/beo_status.mjs` exists, run `node .beads/beo_status.mjs --json` as a read-only quick scout for repo-local state, handoff, and recorded onboarding metadata.
Do not use `.beads/onboarding.json` or repo-local `beo_status` output as the source of truth for startup freshness, managed startup contract mismatch, or managed `AGENTS.md` block drift.

Only continue deeper workspace interpretation after onboarding is current.

Optional knowledge-search availability check:

```bash
qmd status 2>/dev/null
```

If workspace repair is needed, use the doctor-mode commands in section 7 rather than treating bootstrap repair as normal routing work.

## 1b. Multi-Epic and Label-Aware Detection

Before classifying new requests or resuming active features, check for these conditions:

### Multi-Epic Ambiguity

Query all epics and filter for active ones:

```bash
br list --type epic -a --json
```

Filter the results for epics that are `open` or `in_progress`. If more than one active epic exists, route to `user` with state `multi-epic-ambiguity` and ask which epic to continue. Do not silently pick one.

### Swarming Label Detection

When resuming an active epic, check whether it carries the `swarming` label (via `br show <EPIC_ID> --json` and inspecting labels). If `swarming` and `approved` are both present, route to `beo-swarm` for coordinator resume (matching state routing table row 18). This includes the window after the coordinator adds the `swarming` label but before any worker has claimed a bead — requiring `in_progress` tasks would cause the router to fall through to ready-to-swarm and initialise a duplicate swarm. If `swarming` is present without `approved`, treat it as a stale label — it will be cleaned up on the next validation pass.

### Cancelled-Needs-Decision

When current-scope tasks include `cancelled` outcomes, check whether each cancelled task carries the `cancelled_accepted` label (`br show <TASK_ID> --json`, inspect labels array). If any cancelled task lacks `cancelled_accepted`, route to `user` with state `cancelled-needs-decision`. Do not silently advance past unaccepted cancelled outcomes.

When the user accepts a cancelled task's outcome, persist the decision: `br label add <TASK_ID> -l cancelled_accepted`. See `status-mapping.md` → Cancelled-Outcome Acceptance for full label semantics.

## 2. New Feature Intake Classification

Use this section to classify brand-new requests before deeper routing.

### New Debug Intake

If the request is clearly for root-cause analysis of a concrete failure, classify it as `new-debug-intake` and route to `beo-debug`.

Do not create epics, tasks, or artifacts in route. Any intake bootstrap required by the chosen downstream flow is owned downstream or must be surfaced as a user-facing prerequisite.

### New Feature Intake

If the request is feature delivery work, classify it as either:
- `new-quick-intake` when it satisfies the quick-scope definition in `beo-reference` → `references/pipeline-contracts.md`
- `new-feature-intake` otherwise

Both classifications route to `beo-explore`. Route records the correct next target and stops; it does not create epics, tasks, slugs, or artifact directories. Feature-intake bootstrap belongs to the downstream intake skill.

## 3. Quick Scope Handling

Quick scope is a routing signal, not a route-owned execution shortcut.

When a request is quick-scoped:
- preserve the `new-quick-intake` classification in `STATE.json`
- route to `beo-explore`
- let downstream skills decide how lightweight the requirement and planning artifacts can be while preserving canonical ownership

If quick-scoped work later expands:
- keep the normal pipeline ownership (`beo-explore` for unlocked requirements, `beo-plan` for solution redesign)
- do not treat earlier quick classification as permission to skip planning or validation

## 4. Artifact Inspection Order

When assessing an active feature, inspect artifacts in this order:

1. `CONTEXT.md`
2. `discovery.md`
3. `approach.md`
4. `plan.md`
5. `phase-plan.md` *(if present)*
6. `phase-contract.md`
7. `story-map.md`

Interpretation rules:

- if `phase-plan.md` exists, the feature is potentially multi-phase
- if `phase-plan.md` does not exist, the feature is usually single-phase unless other evidence contradicts that assumption
- `phase-contract.md` and `story-map.md` always describe the **current phase** only

## 5. Planning-Aware Routing Rules

| Rule | Condition | Route / Action |
|------|-----------|----------------|
| A | CONTEXT.md exists, no approach.md | → beo-plan |
| B | approach.md exists, missing phase-contract.md or story-map.md | → beo-plan |
| C | phase-plan.md exists | Treat as multi-phase unless clearly obsolete; current-phase completion ≠ whole-feature completion |
| D | All current-phase beads closed + phase-plan.md + later phases remain | → beo-plan (prepare next phase) |
| E | Execution complete, no later phases | → beo-review |

```text
if phase_plan exists and current phase complete and later phases remain:
  route = beo-plan
else if no later phases remain and implementation complete:
  route = beo-review
```

## 6. Resume From Handoff

### Read the Handoff

Read `.beads/HANDOFF.json` with your file reading tool.

Use the canonical schema from `beo-reference` → `references/state-and-handoff-protocol.md`.

Before trusting the handoff, run the live `beo-onboard` repo check again against the current skill install.
If the live check reports onboarding missing, unreadable, stale, or otherwise unhealthy, route to `beo-onboard` before resuming the saved skill.

### Read planning-aware fields when present

If present, read and trust these fields unless live artifacts clearly contradict them:

- `planning_mode`
- `has_phase_plan`
- `current_phase`
- `total_phases`
- `phase_name`
- `artifacts`
- `mode`

### Verify It Is Still Valid

```bash
# Check that the epic still exists and is open
br show <feature_epic_id> --json

# Check task states haven't changed externally
br dep list <feature_epic_id> --direction up --type parent-child --json
```

Also re-check the artifact set in the canonical inspection order.

If `has_phase_plan = true`, verify that `phase-plan.md` still exists.

If `mode = "go"`, resume within go-mode rather than normal routing. Preserve the saved `skill`, `next`, and any supporting `reason` / `content`, and continue using go-mode semantics at the next human gate unless live state clearly invalidates the checkpoint.

### Clean Up Only After Fresh Checkpoint

After the resumed skill writes a fresh `STATE.json`, clean up `HANDOFF.json` according to `beo-reference` → `references/state-and-handoff-protocol.md`.

## 7. Doctor Mode

Use when asked to inspect project health or diagnose workflow issues.

```bash
# Full graph analysis
bv --robot-insights --format json

# Check for stale work
br stale --days 7 --json

# Check for cycles
br dep cycles --json

# Check for blocked items
br blocked --json
```

In addition to graph health, report planning shape when relevant:

- whether `approach.md` exists
- whether `phase-plan.md` exists
- whether current-phase artifacts exist
- whether the feature appears single-phase or multi-phase

### Diagnostic Table

| Finding | Severity | Action |
|---------|----------|--------|
| Dependency cycles | **HIGH** | Report exact cycle, ask user to break it |
| Tasks blocked >24h | **MEDIUM** | Report blockers, suggest resolution |
| Tasks in_progress >4h with no commits | **MEDIUM** | May be abandoned; check with user |
| Epic with no tasks and no plan | **LOW** | Stale feature; suggest cleanup or activation |
| Closed tasks with open dependencies | **HIGH** | Inconsistent state; investigate |
| `phase-plan.md` exists but no current-phase artifacts | **MEDIUM** | Route back to planning |
| Current phase complete but later phases remain | **MEDIUM** | Route back to planning for next phase prep |

## 8. STATE.json on Handoff

After classifying the state and before loading the next skill, write `.beads/STATE.json` using the complete canonical schema from `beo-reference` → `references/state-and-handoff-protocol.md` § Canonical STATE.json Schema.

All 12 required fields must be present: the 7 base fields (`schema_version`, `phase`, `status`, `feature`, `feature_slug`, `tasks`, `next`) plus the 5 planning-aware fields (`planning_mode`, `has_phase_plan`, `current_phase`, `total_phases`, `phase_name`).

This ensures every skill transition has a readable state record, not just handoff-from-checkpoint scenarios.

# Router Operations

Operational playbook for `beo-route`.

## Intent Short-Circuit Rule

Before full feature-state routing, check whether explicit user intent already selects a meta path:
- creating or editing a beo skill → `beo-author`
- root-cause analysis of blocked or failing work → `beo-debug`
- explicit learnings consolidation → `beo-dream`

Honor explicit intent unless live state proves the request impossible, stale, or aimed at the wrong feature.

Conversational phrasing is not a short-circuit. Requests like "explore this with me" still route through the state table. Route emits a next target only; if the correct outcome is pause or completion, emit `next: "user"` or `next: "done"`.

## 1. Workspace Bootstrap

Run the live `beo-onboard` repo check before deeper routing. If onboarding is missing, unreadable, stale, or otherwise unhealthy, route to `beo-onboard`.

If onboarding is current and `.beads/beo_status.mjs` exists, run:

```bash
node .beads/beo_status.mjs --json
```

Use it only as a read-only scout. Do not treat `.beads/onboarding.json` or repo-local scout output as the source of truth for startup freshness or managed `AGENTS.md` drift.

Optional knowledge-search availability check:

```bash
qmd status 2>/dev/null
```

## 1b. Multi-Epic and Label-Aware Detection

### Multi-Epic Ambiguity

Query all epics:

```bash
br list --type epic -a --json
```

If more than one epic is active (`open` or `in_progress`), route to `user` with `multi-epic-ambiguity`. Do not silently pick one.

### Swarming Label Detection

When resuming an active epic, inspect labels via `br show <EPIC_ID> --json`:
- `swarming` + `approved` → route to `beo-swarm`
- `swarming` without `approved` → treat as stale; validation will clean it up

### Cancelled-Needs-Decision

When current-scope tasks include `cancelled` outcomes, inspect each cancelled task for `cancelled_accepted`:
- if any cancelled task lacks `cancelled_accepted`, route to `user` with `cancelled-needs-decision`
- if the user accepts a cancelled outcome, persist it with `br label add <TASK_ID> -l cancelled_accepted`

See `status-mapping.md` for full label semantics.

## 2. New Feature Intake Classification

### New Debug Intake

If the request is clearly for root-cause analysis of a concrete failure, classify it as `new-debug-intake` and route to `beo-debug`.

Route does not create epics, tasks, slugs, or artifacts.

### New Feature Intake

If the request is feature work:
- `new-quick-intake` when it matches the quick-scope definition in `pipeline-contracts.md`
- `new-feature-intake` otherwise

Both route to `beo-explore`. Intake bootstrap belongs downstream.

## 3. Quick Scope Handling

Quick scope is a routing signal, not a route-owned shortcut.

When work is quick-scoped:
- preserve `new-quick-intake` in `STATE.json`
- route to `beo-explore`
- let downstream skills decide how lightweight the artifacts can be

If quick work expands later, keep normal ownership: unlocked requirements go to `beo-explore`; redesign goes to `beo-plan`.

## 4. Artifact Inspection Order

For an active feature, inspect artifacts in this order:

1. `CONTEXT.md`
2. `discovery.md`
3. `approach.md`
4. `plan.md`
5. `phase-plan.md` if present
6. `phase-contract.md`
7. `story-map.md`

Interpretation:
- `phase-plan.md` present → potentially multi-phase
- `phase-plan.md` absent → usually single-phase unless other evidence contradicts it
- `phase-contract.md` and `story-map.md` always describe the current phase only

## 5. Planning-Aware Routing Rules

| Rule | Condition | Route |
|---|---|---|
| A | `CONTEXT.md` exists, no `approach.md` | `beo-plan` |
| B | `approach.md` exists, missing `phase-contract.md` or `story-map.md` | `beo-plan` |
| C | `phase-plan.md` exists | treat as multi-phase unless clearly stale |
| D | Current phase complete and later phases remain | `beo-plan` |
| E | Execution complete and no later phases remain | `beo-review` |

## 6. Resume From Handoff

Read `.beads/HANDOFF.json` with the canonical schema from `state-and-handoff-protocol.md`.

Before trusting it, run the live onboarding check again. If onboarding is stale, route to `beo-onboard`.

When present, trust these fields unless live artifacts clearly contradict them:
- `planning_mode`
- `has_phase_plan`
- `current_phase`
- `total_phases`
- `phase_name`
- `artifacts`
- `mode`

Verify saved state with:

```bash
br show <feature_epic_id> --json
br dep list <feature_epic_id> --direction up --type parent-child --json
```

Also re-check artifacts in canonical order. If `has_phase_plan = true`, verify `phase-plan.md` still exists.

If `mode = "go"`, resume within go mode rather than normal routing.

Clean up `HANDOFF.json` only after the resumed skill writes fresh canonical state.

## 7. Doctor Mode

Use doctor mode only when asked to inspect project health or workflow issues.

```bash
bv --robot-insights --format json
br stale --days 7 --json
br dep cycles --json
br blocked --json
```

Also report:
- whether `approach.md` exists
- whether `phase-plan.md` exists
- whether current-phase artifacts exist
- whether the feature appears single-phase or multi-phase

| Finding | Severity | Action |
|---------|----------|--------|
| Dependency cycles | HIGH | report exact cycle and ask user to break it |
| Tasks blocked >24h | MEDIUM | report blockers and likely resolution |
| Tasks in progress >4h with no commits | MEDIUM | may be abandoned; check with user |
| Epic with no tasks and no plan | LOW | stale feature; suggest cleanup or activation |
| Closed tasks with open dependencies | HIGH | investigate inconsistent state |
| `phase-plan.md` exists but current-phase artifacts do not | MEDIUM | route back to planning |
| Current phase complete but later phases remain | MEDIUM | route back to planning |

## 8. STATE.json on Handoff

After classifying state and before yielding, write `.beads/STATE.json` using the complete canonical schema from `state-and-handoff-protocol.md`.

All 12 required fields must be present:
- base: `schema_version`, `phase`, `status`, `feature`, `feature_slug`, `tasks`, `next`
- planning-aware: `planning_mode`, `has_phase_plan`, `current_phase`, `total_phases`, `phase_name`

# Task Status Mapping

Beo uses richer task states than br's native model. This table maps each Beo state to the exact br CLI commands required.

## Beo States → br Commands

| Beo State | br Status | br Labels | Commands (in order) |
|---------------|-----------|-----------|-------------------|
| `pending` | `open` | (none) | `br update <id> -s open` then remove stale labels: `br label remove <id> -l blocked`, `br label remove <id> -l failed`, `br label remove <id> -l partial`, `br label remove <id> -l cancelled`, `br label remove <id> -l cancelled_accepted`, `br label remove <id> -l dispatch_prepared`, `br label remove <id> -l in_progress` |
| `dispatch_prepared` | `open` | `dispatch_prepared` | `br label add <id> -l dispatch_prepared` |
| `in_progress` | `in_progress` | `in_progress` | `br update <id> --claim` then `br label remove <id> -l dispatch_prepared` then `br label add <id> -l in_progress` |
| `done` | `closed` | (none) | `br label remove <id> -l in_progress` then `br close <id>` |
| `blocked` | `deferred` | `blocked` | `br label remove <id> -l in_progress` then `br update <id> -s deferred` then `br label add <id> -l blocked` |
| `failed` | `deferred` | `failed` | `br label remove <id> -l in_progress` then `br update <id> -s deferred` then `br label add <id> -l failed` |
| `partial` | `deferred` | `partial` | `br label remove <id> -l in_progress` then `br update <id> -s deferred` then `br label add <id> -l partial` |
| `cancelled` | `deferred` | `cancelled` | `br label remove <id> -l in_progress` then `br update <id> -s deferred` then `br label add <id> -l cancelled` |

## Allowed State Transitions

```
pending → dispatch_prepared → in_progress → done
                                          → blocked → pending (after unblock)
                                          → failed → pending (re-queue)
                                          → partial → cancelled → pending
```

**Forbidden transitions**:
- `done → in_progress` (NEVER reopen a completed task; create a new one)
- `done → pending` (same reason)
- Any skip of `dispatch_prepared` (always goes pending → dispatch_prepared → in_progress)

## Reading Beo State from br

To determine the Beo state from br output:

```
if status == "closed" → done
if status == "deferred":
  if has label "blocked" → blocked
  if has label "failed" → failed
  if has label "partial" → partial
  if has label "cancelled" → cancelled
if status == "in_progress" → in_progress
if status == "open":
  if has label "dispatch_prepared" → dispatch_prepared
  else → pending
```

## Canonical Terminal-State Semantics

For routing and completion decisions, treat these Beo task states as terminal outcomes:

- `done`
- `cancelled`
- `failed`

Notes:
- `done` is the only successful terminal state and maps to `br status = "closed"`
- `cancelled` and `failed` are terminal but non-success states and map to `br status = "deferred"` plus their label
- `blocked` and `partial` are **not** terminal for routing/completion purposes

When shared routing docs say "all tasks are in canonical terminal states," they mean every task resolves to one of the three states above after applying this mapping.

### Advancement Semantics

Only `done`/`closed` tasks advance cleanly through the pipeline. Non-success terminal outcomes are handled differently:

- **`failed` tasks** are caught by the routing table's debugging pathway (`needs-debugging` → `beo-debug`) before reaching review. They do not appear at the review gate under normal routing.
- **`cancelled` tasks** require explicit user acceptance before phase advancement or review. The routing table's `cancelled-needs-decision` state pauses for user direction. The user may choose to:
  - re-queue the task (reset to `pending`)
  - accept the outcome and proceed with review
  - re-plan the affected scope

Do not silently advance a feature through review when non-success terminal states are present.

## Feature States

| Feature State | br Epic Status | br Labels | How to Set |
|--------------|---------------|-----------|-----------|
| `planning` | `open` | (none) | Default immediately after epic creation |
| `approved` | `open` | `approved` | `br label add <epic> -l approved` |
| `executing` | `in_progress` | `approved` | `br update <epic> --claim` |
| `swarming` | `in_progress` | `approved`, `swarming` | `br label add <epic> -l swarming` (added when swarm coordination starts; removed on completion, degradation, or handoff; assumes epic is already claimed via `br update <epic> --claim`) |
| `completed` | `closed` | `approved` | `br close <epic>` |

## Cancelled-Outcome Acceptance

The `cancelled_accepted` label is the canonical persistence mechanism for tracking user acceptance of cancelled task outcomes:

- **Set:** `br label add <TASK_ID> -l cancelled_accepted` — when the user explicitly accepts a cancelled task's outcome for phase advancement or review.
- **Scope:** Per-task, not per-epic. Each cancelled task requires individual acceptance.
- **Durability:** The label persists across context resets and session resumes, making acceptance state queryable by any skill.
- **Query:** After listing cancelled tasks, check each for `cancelled_accepted` in `br show <TASK_ID> --json` labels array.
- **Removal:** Remove only when the task is re-queued to `pending` (the stale label cleanup sequence below already covers this).

A phase or feature is ready to advance past cancelled tasks only when every `cancelled` task in the active scope also carries the `cancelled_accepted` label.

## Stale Label Cleanup

Before setting a new state, always remove conflicting labels. The safe cleanup sequence:

```bash
# Before marking pending (removes all status labels)
br label remove <id> -l blocked
br label remove <id> -l failed
br label remove <id> -l partial
br label remove <id> -l cancelled
br label remove <id> -l cancelled_accepted
br label remove <id> -l dispatch_prepared
br label remove <id> -l in_progress

# Before marking in_progress (remove dispatch_prepared)
br label remove <id> -l dispatch_prepared

# Before marking done (remove in_progress)
br label remove <id> -l in_progress
```

Note: `br label remove` on a non-existent label is a no-op (safe to run unconditionally).

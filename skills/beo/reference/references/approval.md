# Approval

Only `beo-validate` can write `PASS_EXECUTE`.

## Stale Approval

`beo-validate` must differentiate between critical changes that require re-planning and minor drift that requires only a review note.

### Hard Invalidators (Must Re-Plan)
Changes to any of the following invalidate `PASS_EXECUTE` immediately:
- **Scope**: Any change to `scope.files.allow` or `scope.files.forbid`.
- **Criteria**: Any change to `acceptance_criteria`.
- **Safety**: Changes to `human_gates`, `external_side_effects`, `stateful_external_systems`, `risk_scope`, or `rollback_boundary`.
- **Execution**: Changes to `scope.verify.commands`, `selected_execution_set`, or `execution_mode`.
- **Strict**: Any change to `STRICT.md` or `ROLLBACK.md` artifact hashes.

### Soft Drift (Review & Confirm)
Changes to non-approval-bearing metadata do not invalidate `PASS_EXECUTE` but must be acknowledged:
- **Identity**: Issue `title` or `labels` (e.g., adding `beo:quick`).
- **Context**: `assumptions`, `non_goals`, or ordinary Beads comments.
- **Protocol**: If soft drift is detected, `beo-validate` may preserve `PASS_EXECUTE` but must append a `runtime_event` or Beads comment noting the drift. `beo_check.py` records a `drift_observation_hash` to track this advisory state. `assumptions` and `non_goals` are explicitly excluded from approval hashes to facilitate this drift.

## Binding

Approval binds one atomic Beads issue to one approval projection hash. `beo_check.py` verifies the integrity of this binding but does not grant approval.

- `plan_input_hash`: Hashes only approval-bearing fields (scope, criteria, safety, verification). It explicitly excludes context metadata (`assumptions`, `non_goals`) to allow soft drift in project context without invalidating the plan.
- `approval_projection_hash`: Additionally binds the execution set, mode, hard snapshot (id, type, description, deps), and command contracts. It explicitly excludes soft drift fields (title, labels, assumptions, non_goals) to prevent execution blockers from advisory metadata changes.

## Execute Entry

`beo-execute` requires a complete, current approval envelope and a matching Beads claim for the current actor.

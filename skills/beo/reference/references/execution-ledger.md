# Execution Ledger

Authority: canonical execution state model for `TRACKER.json`.

`TRACKER.json` records the selected approved execution set, approval ref id, execution mode, pre-execution integrity check, item order, item status, changed files, observations, blockers, scope delta requests, repair budget, resume point, and rollback status.

For review, `approval_ref_id`, `selected_execution_set`, `execution_mode`, and `pre_execution_integrity_check.approval_envelope_status` must match the current approved `PLAN.md#Approval` envelope and the execution attempt's fresh helper check. Stale ledger evidence from an older approval, missing helper check, or different execution mode is not ready for review.

`beo-execute` updates the ledger before and after each approved item. Applied items are not repeated on resume unless the item records an idempotency note and the approved plan permits rerun. Changed files outside declared scope create a scope delta request and route to `beo-plan`.

Ledger statuses: `not_started`, `in_progress`, `blocked`, `ready_for_review`, `rolled_back`, `abandoned`. Item statuses: `pending`, `in_progress`, `applied`, `blocked`, `skipped`, `rolled_back`.

Repair and rollback mutation are not implied by review findings or rollback boundary. They require an approved execution set with `kind: repair` or `kind: rollback` and are executed only by `beo-execute` after a fresh helper check.

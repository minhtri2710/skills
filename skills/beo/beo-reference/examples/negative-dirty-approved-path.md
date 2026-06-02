# Negative Trace: Approved Path Dirty Before Validation

This trace demonstrates validation failing when a file in the approved scope is dirty before validation begins.

## Scenario

- A user modifies `README.md` in the working tree.
- The user then starts BEO validation on a ticket that allows `README.md`.
- `beo-validate` detects the dirty approved path and fails validation without granting execution permission.

## State after validation failure

```json
{
  "version": 1,
  "issue_id": "br-102",
  "phase": "blocked",
  "phase_sequence_id": 2,
  "approval": {
    "status": "failed",
    "approved_by": null,
    "actor": null,
    "ticket_file_hash": null,
    "approval_projection_hash": null,
    "repo_head": null,
    "prestate": {},
    "failure_category": "dirty_approved_path",
    "approved_phase_sequence_id": null
  },
  "metadata": {
    "last_owner": "beo-validate",
    "updated_at": "2026-06-02T13:10:00Z"
  }
}
```

## Expected Route

- **Expected emitted condition**: `user_review_needed`
- **Failure category**: `dirty_approved_path`
- **Reason**: `pipeline.validation_failure_routes.dirty_approved_path` = `user_review_needed`
- **Route**: `user_review_needed` -> user

## Outcomes

- No `PASS_EXECUTE` is granted.
- No execution is permitted.
- Dirty prestate is not plan-repairable. The user must stash, commit, or discard changes before re-validating.

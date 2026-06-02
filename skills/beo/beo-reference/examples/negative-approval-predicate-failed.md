# Negative Trace: Approval Predicate Failed

This trace shows what happens when a ticket is approved, but the ticket file hash is modified on disk before execution starts.

## Scenario

- `beo-validate` grants `PASS_EXECUTE` and transitions phase to `approved`.
- Before `beo-execute` transitions phase to `executing`, someone edits `TICKET.yaml`.
- Upon entering `beo-execute`, the helper recomputes approval predicates and detects `ticket_file_hash` has changed.
- The approval is marked stale and execution is blocked.

## State after detection

```json
{
  "version": 1,
  "issue_id": "br-103",
  "phase": "blocked",
  "phase_sequence_id": 3,
  "approval": {
    "status": "stale",
    "approved_by": "beo-validate",
    "actor": "beowulf",
    "ticket_file_hash": "original_hash...",
    "approval_projection_hash": "projection_hash...",
    "repo_head": "repo_hash...",
    "prestate": {},
    "failure_category": "approval_predicate_failed",
    "approved_phase_sequence_id": 1
  },
  "metadata": {
    "last_owner": "beo-execute",
    "updated_at": "2026-06-02T13:15:00Z"
  }
}
```

## Expected Route

- **Condition**: `approval_stale_or_invalid`
- **Route**: `approval_stale_or_invalid` -> `beo-validate`
- **Invalidator**: `ticket_file_hash_changed`

## Invalidation Rules

- BEO approval assertions do not expire by elapsed time.
- Elapsed time alone is NOT an invalidator.
- Explicit predicate failure (e.g. ticket file hash changed) is required to invalidate approval.

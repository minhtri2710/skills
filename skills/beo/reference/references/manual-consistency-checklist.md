# Manual Consistency Checklist

Use this checklist after doctrine edits. This is a manual review aid, not an eval suite, benchmark, fixture suite, or release gate.

## Runtime topology

- No `beo-swarm` owner exists.
- No `PASS_SERIAL` or `PASS_SWARM` verdict exists.
- Execution wording uses `PASS_EXECUTE` and execution-set mode.

## Authority boundaries

- Display cards never grant approval, readiness, routing, review verdict, learning promotion, or mutation permission.
- Skill-local appendices do not hide fallback routing rules.
- Owner skills do not select owners outside their `Allowed next owners`.

## Approval/readiness

- `PASS_EXECUTE` always has:
  - selected execution set
  - current `approval_ref`
  - execution mode
  - selected beads
- For `ordered_batch` and `local_parallel`, `partial_progress_allowed` is explicit in both `STATE.json` and `readiness-record.json`.

## State/handoff

- One active feature per worktree.
- Handoff never overrides fresher live artifacts.
- Optional stale state fields are cleared when superseded.

## Review

- Review recomputes live changed-file evidence.
- Review does not rely only on self-reported `scope_respected`.
- `REVIEW.md` verdict is emitted only by `beo-review`.

## Debug

- Debug output contains no patch text.
- Debug does not grant approval, readiness, rollback, or mutation authority.

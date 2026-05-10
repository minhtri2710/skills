# Execution Operations

Role: APPENDIX
Allowed content only: execution procedure and output shapes
Forbidden content: owner selection, approval authority, review verdict authority, routing topology, writable-surface expansion

## Execute preflight

Before mutation, verify the current approval envelope from `references/approval.md` and required integrity from `references/approval-integrity.md` (APP-01):

```md
Readiness: PASS_EXECUTE
Approval ref: <fresh>
Integrity status: verified
Execution set id: <selected>
Execution mode: single | ordered_batch
Selected beads: <list>
Selected BR task context: present | N/A
Declared files: <list>
Forbidden paths: <list>
Generated outputs: <declared or N/A>
Verification contract: <present>
Freshness result: verified
File-change baseline: <recorded>
```

Stop if any row is missing, stale, invalid, unavailable, contradictory, or outside approval (APP-01, INT-01).

Immediately before first mutation, reread readiness, approval, integrity, selected execution set, declared files, forbidden paths, generated outputs, and verification contract from current required surfaces.

## File-change baseline

Before mutation, record the current file-change baseline needed to distinguish execution changes from pre-existing or unrelated changes. This is local file-change evidence only, not worktree identity authority.

## Single execution

For `single`, execute exactly the selected bead inside approved declared scope.

## Ordered batch

For `ordered_batch`, execute beads in validated order. If any bead blocks, stop the batch (APP-06). Do not continue unaffected beads.

## Evidence finalization

Tiny: update `TICKET.md` Execution section with changed files, verification evidence, and blocker if any.

Standard: update `TRACKER.json.execution` with every changed/generated file, baseline/final evidence, verification evidence, review packet, `ready_for_review=true`, and finalized time.

The review packet is an evidence index, not authority.

## Partial execution handling

If execution starts and then blocks:

1. Stop further mutation.
2. Record completed beads.
3. Record changed files.
4. Record verification run/not-run.
5. Record rollback boundary status.
6. Do not continue ordered batch (APP-06).
7. Route to review/debug/plan by evidence.

## Stale approval/integrity stop

If approval or integrity becomes stale during execution, stop immediately (APP-03). Never finish first after approval/integrity becomes stale. Route by `approval.md` stale approval quick table.

## Debug handoff

If root cause is unproven, route to `beo-debug` with observed behavior, expected behavior, evidence checked, affected invariant, blocked owner condition, and return owner. Do not include patch text; debug output requires `Patch text: none`.

## Learning cases

If execution reveals a learning case, finish the safe stop and owner handoff first. Do not use learning routing to continue, delay, or avoid runtime safety handling.

## Approval helper

`beo_approval_check.py` may be used to compute evidence. It does not authorize mutation, refresh approval, emit `PASS_EXECUTE`, or emit review verdicts (INT-03).

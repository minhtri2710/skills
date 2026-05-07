# Execution Operations v2

Role: APPENDIX

## Execute preflight

Before mutation, verify:

```md
Readiness: PASS_EXECUTE
Approval ref:
Execution set id:
Execution mode: single | ordered_batch
Selected beads:
Declared files:
Forbidden paths:
Generated outputs:
Verification:
Freshness result:
File-change baseline:
```

Hard stop if any row is missing, stale, contradictory, or outside approval.

## File-change baseline

Before mutation, record the current file-change baseline needed to distinguish execution changes from pre-existing or unrelated changes.

This is local file-change evidence only. It is not a worktree model.

If unrelated live file changes make scope attribution unsafe, stop and route to `user` or exceptional `beo-route` based on owner-state evidence.

## Single execution

For `single`, execute exactly the selected bead inside approved declared scope.

## Ordered batch

For `ordered_batch`, execute beads in the validated order. If any bead blocks, stop the batch. Do not continue unaffected beads.

## Execution bundle finalization

Finalize `.beads/artifacts/<feature_slug>/execution-bundle.json` with every changed/generated file, hash coverage, verification evidence, `ready_for_review=true`, and `finalized_at`.

## Stale approval stop

If approval becomes stale during execution, stop immediately and route by `approval.md` and `pipeline.md`.

## Debug handoff

If root cause is unproven, route to `beo-debug` with observed behavior, expected behavior, evidence checked, affected owner condition, and the blocked invariant. Do not include patch text.

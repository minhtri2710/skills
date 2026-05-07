# Readiness Review Prompt v2

Role: APPENDIX

Assess whether `beo-validate` may emit `PASS_EXECUTE`.

## Required checks

1. Requirements locked.
2. Plan current.
3. Bead graph and plan mirror agree.
4. Approval present and fresh.
5. `approval_ref` readable and current.
6. `CONTEXT.md` and `PLAN.md` match approval record.
7. Selected execution set explicit.
8. Execution mode is `single` or `ordered_batch`.
9. Selected beads non-empty.
10. Declared file scope exists for every selected bead.
11. Forbidden paths explicit.
12. Generated outputs explicit.
13. Verification exists for every selected bead.
14. Risks have proof/mitigation or valid N/A.
15. Ordered batch, when selected, has explicit order and all dependencies satisfied before execution begins.

## Output

```md
Readiness: PASS_EXECUTE | FAIL_PLAN | FAIL_EXPLORE | BLOCK_USER | FAIL_STATE
Reason:
Evidence:
Repair owner:
Repair target:
Do not execute because:
```

Do not emit `PASS_EXECUTE` unless every required check passes.

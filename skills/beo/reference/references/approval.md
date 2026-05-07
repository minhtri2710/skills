# BEO Approval v2

## Approval invariant

Execution approval is valid only for the exact locked requirements, plan scope, bead graph, declared files, forbidden paths, generated outputs, verification contract, risk proof, execution mode, and execution set recorded in the current approval record.

`approval_ref` is required for every `PASS_EXECUTE`, including unchanged approval.

Do not infer approval from `PLAN.md`, bead status, prior chat, operator intent, or go-mode.

## Approval becomes stale when

Approval becomes stale when any approval-bearing content changes:

- `CONTEXT.md`
- acceptance decisions
- non-goals
- compatibility constraints
- `PLAN.md`
- bead graph
- declared files
- forbidden paths
- generated outputs
- verification
- risk proof or mitigation
- execution mode
- execution set
- rollback boundary

## Stale approval clearing rule

When approval becomes stale, the owner that caused staleness must clear:

- `readiness`
- `approval_ref`
- `execution_mode`
- `execution_set_id`
- `execution_set_beads`

## Stale approval routing

| Condition | Next owner |
| --- | --- |
| Approval stale before mutation | `beo-validate` or `beo-plan` by stale cause |
| Requirements changed | `beo-explore` |
| Plan/scope/verification changed | `beo-plan` |
| Mutation already happened and bundle can be finalized | `beo-review` |
| Mutation happened but root cause is unproven | `beo-debug` |
| Human approval required | `user` |
| Owner-state contradiction | `beo-route` |

## Human approval gates

Approval and UAT gates never fallback to go-mode. They require explicit user approval evidence before `PASS_EXECUTE`.

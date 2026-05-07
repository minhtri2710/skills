# BEO Pipeline v2

## Core invariant

BEO manages one active feature at a time through canonical state, feature artifacts, fresh approval, bounded execution, and independent review.

BEO does not require worktree identity, onboarding scripts, status scouts, eval suites, checker tooling, local parallel execution, or partial-progress continuation.

## Normal path

`beo-route -> beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done`

## Repair paths

| From | Condition | Next owner |
| --- | --- | --- |
| `beo-validate` | plan, scope, verification, risk, or approval-bearing plan defect | `beo-plan` |
| `beo-validate` | requirements missing, unlocked, or contradicted | `beo-explore` |
| `beo-validate` | human approval/access/secret/legal/business decision required | `user` |
| `beo-execute` | root cause unproven | `beo-debug` |
| `beo-execute` | scope or approval repair required | `beo-plan` |
| `beo-execute` | external access, secret, or human blocker | `user` |
| `beo-execute` | execution bundle finalized | `beo-review` |
| `beo-review` | fix finding but root cause unproven | `beo-debug` |
| `beo-review` | bounded reactive fix is proven and inside retained approval envelope | `beo-validate` |
| `beo-review` | fix exceeds approval/scope or design/plan failed | `beo-plan` |
| `beo-review` | requirements invalid or contradicted | `beo-explore` |
| `beo-review` | accept with no learning | `done` |
| `beo-review` | accept with durable or unclear single-feature learning | `beo-compound` |
| `beo-compound` | feature learning recorded | `done` |
| `beo-dream` | corpus consolidation complete | `done` |

## Owner selection

Use the first matching condition:

| Condition | Owner |
| --- | --- |
| Owner identity is missing, stale, contradictory, or colliding | `beo-route` |
| Requirements are missing, unlocked, contradicted, or acceptance/scope-affecting answers are unresolved | `beo-explore` |
| Requirements are locked, but plan, bead graph, scope, risk, rollback boundary, generated outputs, or verification is missing/stale/invalid | `beo-plan` |
| Requirements and plan exist, but readiness, approval, execution set selection, remediation classification, or user-blocker classification is needed | `beo-validate` |
| `PASS_EXECUTE` is current with fresh `approval_ref` and selected execution set | `beo-execute` |
| Execution bundle is finalized and ready for terminal verdict | `beo-review` |
| Root cause is unproven and mutation/verdicting would be unsafe | `beo-debug` |
| Accepted review has durable or unclear single-feature learning evidence | `beo-compound` |
| Cross-feature threshold or explicit corpus request exists | `beo-dream` |

This table is orientation. Owner SKILL files and canonical pipeline rules remain authoritative when a local hard stop is stricter.

## Route suppression

`beo-route` is exceptional owner-state repair, not a general next-step selector.

Do not route merely to confirm the current owner, avoid the current owner's owned decision, or choose between obvious legal next owners.

A route decision is legal only when one defect exists:

- `missing_owner`
- `stale_owner`
- `contradictory_owner`
- `colliding_predicates`
- `feature_collision`

If no defect exists, continue with the current legal owner or hand off through the normal pipeline.

## Execution modes

Supported:

- `single`: one selected bead
- `ordered_batch`: multiple selected beads executed sequentially

Unsupported:

- `local_parallel`
- partial-progress continuation
- external worker coordination

If an ordered batch blocks, stop the batch. Do not continue unaffected beads.

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

## Terminal closure

`done` is legal only after accepted no-learning closure, completed learning closure, rejected/deferred/canceled closure, or explicit user stop recorded in state.

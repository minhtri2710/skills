# BEO Pipeline

## Core invariant

BEO manages one active feature at a time through canonical state, feature artifacts, fresh approval, bounded execution, and independent review.

BEO does not require worktree identity, onboarding scripts, status scouts, eval suites, checker tooling, local parallel execution, or partial-progress continuation.

## Normal delivery path

`beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done`

`beo-route` is a startup repair path only when owner identity or active feature identity is unsafe.

## Repair paths

| From | Condition | Next owner |
| --- | --- | --- |
| `beo-validate` | plan, scope, verification, risk, or approval-bearing plan defect | `beo-plan` |
| `beo-validate` | requirements missing, unlocked, or contradicted | `beo-explore` |
| `beo-validate` | human approval/access/secret/legal/business decision required | `user` |
| `beo-execute` | readiness, approval_ref, or selected execution set is missing/stale before mutation | `beo-validate` or `beo-plan` by stale cause; see Stale approval routing below |
| `beo-execute` | root cause unproven | `beo-debug` |
| `beo-execute` | scope or approval repair required | `beo-plan` |
| `beo-execute` | external access, secret, or human blocker | `user` |
| `beo-execute` | execution bundle finalized | `beo-review` |
| `beo-review` | fix finding but root cause unproven | `beo-debug` |
| `beo-review` | fix finding and root cause proven | `beo-plan` |
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
| Execution bundle is finalized and ready for terminal verdict | `beo-review` |
| `PASS_EXECUTE` is current with fresh `approval_ref` and selected execution set | `beo-execute` |
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

## Approval and bead graph authority

Only `beo-validate` creates or refreshes approval records and emits `PASS_EXECUTE`. PLAN.md is the canonical bead graph; external bead tooling is optional support only.

## FAIL_STATE

`FAIL_STATE` means canonical state/artifact evidence prevents safe readiness classification. If owner identity is unsafe, next owner is `beo-route`. If artifact evidence is unreadable due to access, missing file, or external environment, next owner is `user`. If the defect is owned by `beo-plan` or `beo-explore`, emit `FAIL_PLAN` or `FAIL_EXPLORE`, not `FAIL_STATE`.


## Collision precedence

When multiple owner predicates appear true, resolve the highest-priority blocking condition first:

| Priority | Condition | Owner |
| --- | --- | --- |
| 1 | Multiple active feature candidates and canonical evidence cannot choose one | user |
| 2 | Owner identity missing, stale, contradictory, or colliding | beo-route |
| 3 | Required Human Gate unresolved | user |
| 4 | Requirements missing, unlocked, or contradicted | beo-explore |
| 5 | Plan, bead graph, file scope, generated outputs, risk proof, rollback, or verification invalid | beo-plan |
| 6 | Readiness, approval, approval freshness, execution set, or remediation classification needed | beo-validate |
| 7 | Root cause is unproven and mutation/verdicting would be unsafe | beo-debug |
| 8 | Finalized execution bundle ready for verdict | beo-review |
| 9 | Fresh `PASS_EXECUTE` with selected execution set | beo-execute |
| 10 | Accepted review has durable-candidate or unclear learning | beo-compound |
| 11 | Corpus threshold or explicit corpus request exists | beo-dream |
| 12 | Terminal closure proven | done |

A lower-priority owner may not proceed while a higher-priority blocking condition is unresolved.

If the current owner is valid and no higher-priority blocker exists, do not route merely to reconfirm ownership.

## Setup helper boundary

`beo-setup` is a support skill for setup checks, AGENTS.md managed-block setup, and usage guidance.

It is not a runtime owner.

It does not change the normal path:

`beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done`

`beo-route` remains exceptional owner-state repair only.

It cannot approve readiness, emit `PASS_EXECUTE`, select execution sets, execute, review, close, or promote learning.

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

`done` is legal only after accepted no-learning closure, completed learning closure, rejected/deferred/canceled closure, or explicit user stop recorded in state. A feature is terminal only when `STATE.json.status=done` and `closure` is present.

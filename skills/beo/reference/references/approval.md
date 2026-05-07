# BEO Approval

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


## Approval freshness proof

Approval is current only when:

- `context_hash` matches live `CONTEXT.md`
- `plan_hash` matches live `PLAN.md`
- `bead_graph_hash` matches the canonical `PLAN.md` bead graph
- `verification_hash` matches the approved verification contract
- `risk_scope_hash` matches the approved risk, mitigation, generated output, rollback, and scope envelope
- approved execution mode, execution set id, and selected beads match readiness state

If any value differs, approval is stale.

## Approval ownership

`beo-validate` owns approval-record creation, approval freshness refresh, and readiness-record creation.

Mutating owners may invalidate approval-bearing fields by clearing state mirrors, but only `beo-validate` may grant or refresh execution approval.

Explore, plan, execute, and review may invalidate approval but cannot grant it.


## User authorization is not execution approval

User authorization and execution approval are distinct.

- `user_authorization_ref` records the user, policy, UAT, access, secret, legal, or business authorization required for the change, or a valid N/A reason.
- `approval_kind=execution_approval` and `validated_by=beo-validate` record validate's execution-envelope decision.

`beo-validate` may create execution approval only after all required user authorization, approval, UAT, access, secret, legal, and business gates are resolved or validly not applicable.


## Hash field coverage

Hash fields are computed from the canonical artifact content that defines the approved envelope:

- `context_hash`: full locked `CONTEXT.md`
- `plan_hash`: full current `PLAN.md`
- `bead_graph_hash`: `PLAN.md` Execution Beads table
- `verification_hash`: verification cells/section for selected beads
- `risk_scope_hash`: Risks, Approval-bearing scope, Generated outputs, Forbidden paths, and Rollback boundary

When exact hashing is impractical, approval is stale. Fingerprint summaries are diagnostic only and do not authorize execution or acceptance.


## Approval refresh and new approval grant

Approval refresh is legal only when the approved envelope is unchanged and hashes still match.

New approval grant is required when scope, selected beads, execution mode, generated outputs, verification, risk proof, or rollback boundary changes.


## Exact hash rule

`PASS_EXECUTE` and `accept` require exact approval hashes for every required approval-bearing surface.

Fingerprint summaries are diagnostic only. They may explain uncertainty, but they do not authorize `PASS_EXECUTE` and do not allow review to `accept`.

If exact required hashes cannot be computed or matched, approval is stale.

Approval freshness is binary:

- fresh: every required hash and selected execution field matches live canonical artifacts
- stale: any required hash is missing, ambiguous, or different

There is no partial freshness state.

---
name: beo-validate
description: |
  Decide execution readiness and serial/swarm mode. Use when artifacts need no content edits but approval, readiness, remediation class, or mode is absent or invalid. Do not use when artifact content edits or execution are required.
---

# beo-validate

## Purpose
Decide execution readiness and serial/swarm mode.

## Primary owned decision
Emit exactly one readiness verdict and the matching next owner.
`beo-validate` is a gate and classifier, not a planner, router, or artifact repair owner.

## Enter when
- current-phase artifacts are locked and content-complete enough to classify
- approval is absent, stale, or invalid
- readiness, remediation owner, or execution mode is missing or invalid

## Decision rule

Emit exactly one readiness verdict:
- `FAIL_EXPLORE`
- `FAIL_PLAN`
- `BLOCK_USER`
- `PASS_SERIAL`
- `PASS_SWARM`

Stop as soon as evidence proves `FAIL_EXPLORE` or `FAIL_PLAN`.
Do not continue once artifact content repair is required.

Validation ladder:
1. requirements contradicted, unlocked, or stale? -> `FAIL_EXPLORE`
2. plan, bead graph, file scope, forbidden paths, or verification incomplete? -> `FAIL_PLAN`
3. required external approval, access, secret, or clarification missing? -> `BLOCK_USER`
4. execution envelope unchanged? -> approval action `refresh`; otherwise `new_grant`
5. one approved ready bead? -> `PASS_SERIAL`
6. isolated approved bead set? -> `PASS_SWARM`

If plan or requirements content must change, stop classification and route to the artifact owner. Do not write repair plans here.

## Writable surfaces
- `.beads/artifacts/<feature_slug>/approval-record.json` only when granting, refreshing, or invalidating execution approval
- approved marker or label surfaces described by `beo-references -> approval.md`, only as part of the approval write order
- `.beads/STATE.json` under the shared STATE write baseline plus `readiness`, `execution_mode`, `remediation_owner`, and `approval_ref`
- shared `STATE/HANDOFF` surfaces under `beo-references -> skill-contract-common.md`

## Decision packet
- shared decision packet under `beo-references -> skill-contract-common.md`
- local extensions: `readiness`, `approval_action`, `execution_mode`, `remediation_owner`, `approval_ref`

Do not add long implementation advice, speculative repair plans, or a refresh-only approval action when the execution envelope changed.
If the execution envelope changed, approval must be a new grant, not an interpretive refresh.

## Approval rule

Grant or refresh execution approval according to `beo-references -> approval.md`.
Do not restate approval-record schema here.
Execution approval never replaces missing user authorization, external approval, access, secrets, or unresolved clarification.

## Mode selection rule

Choose execution mode only after requirements, plan, approval prerequisites, file scope, forbidden paths, dependencies, and verification are valid.

| Evidence | Verdict |
| --- | --- |
| exactly one approved ready bead | `PASS_SERIAL` |
| multiple beads exist but only one is currently ready | `PASS_SERIAL` for the selected ready bead |
| at least two approved ready beads have recorded isolation and dependency proof, and Agent Mail is available | `PASS_SWARM` |
| at least two beads could be parallel but isolation proof is missing | `FAIL_PLAN` |
| ready beads have overlapping file scope or dependency conflict | `FAIL_PLAN` |
| Agent Mail is unavailable before dispatch but one safe serial bead remains under the same valid envelope | `PASS_SERIAL` only if serial mode is explicitly valid under current approval; otherwise `FAIL_PLAN` |
| external approval, access, secret, or clarification is missing | `BLOCK_USER` |

Swarm fallback classification belongs here.
A failed or unavailable swarm path may become serial only through a fresh `PASS_SERIAL` verdict.
Do not reuse swarm approval as serial approval.

## Exit routing

| Verdict | Next owner |
| --- | --- |
| `PASS_SERIAL` | beo-execute |
| `PASS_SWARM` | beo-swarm |
| `FAIL_EXPLORE` | beo-explore |
| `FAIL_PLAN` | beo-plan |
| `BLOCK_USER` | user |

## Allowed next owners
- beo-execute
- beo-swarm
- beo-plan
- beo-explore
- user

## Local hard stops
- Do not repair artifact content.
- Do not continue classification after a failure already proves artifact repair is required.
- Do not treat an execution-envelope change as a refresh-only case.
- Do not grant or refresh execution approval when required user authorization, external approval, access, secret, or clarification is missing; emit `BLOCK_USER`.
- Do not expand into route-collision handling beyond emitting the matching next owner for the validated verdict.

## References
- `beo-references -> operator-card.md`
- `beo-references -> approval.md`
- `beo-references -> pipeline.md`
- `beo-references -> state.md`
- `references/readiness-review-prompt.md`
- `references/bead-readiness-prompt.md`

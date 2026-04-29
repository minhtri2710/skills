---
name: beo-validate
description: |
  Decide execution readiness and serial/swarm mode. Use when artifacts need no content edits but approval, readiness, remediation class, or mode is absent or invalid. Do not use when artifact content edits or execution are required.
metadata:
  dependencies:
    - id: beads-cli
      kind: command
      command: br
      missing_effect: unavailable
      reason: Required to prove bead graph readiness and approved execution units.
    - id: agent-mail
      kind: mcp_server
      server_names: [mcp_agent_mail]
      config_sources: [repo_config, global_config]
      missing_effect: unavailable_for_swarm
      reason: Required before PASS_SWARM can be emitted.
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
2. plan, phase contract, story map, risk proof, bead graph, file scope, forbidden paths, or verification incomplete? -> `FAIL_PLAN`
3. required external approval, access, secret, or clarification missing? -> `BLOCK_USER`
4. execution envelope unchanged? -> approval action `refresh`; otherwise `new_grant`
5. exactly one approved ready bead under a serial execution envelope? -> `PASS_SERIAL`
6. at least two approved ready beads have recorded isolation and dependency proof, and Agent Mail is available? -> `PASS_SWARM`
7. multiple ready beads exist but swarm is unavailable or invalid? -> `PASS_SERIAL` only when one explicitly approved serial bead remains valid under a fresh serial execution envelope; otherwise `FAIL_PLAN` or `BLOCK_USER` by the blocking evidence

Mode precedence rule:
Do not emit `PASS_SERIAL` merely because at least one ready bead exists.
When two or more ready beads are present, first evaluate swarm eligibility.
Serial fallback from a failed, unavailable, or stale swarm path requires a fresh
`PASS_SERIAL` verdict and must not reuse swarm approval.

If plan or requirements content must change, stop classification and route to the artifact owner. Do not write repair plans here.

## PLAN completeness checklist

Before `PASS_SERIAL` or `PASS_SWARM`, confirm `PLAN.md` has the sections required for its planning depth.

Required for all planning depths:
- context binding
- `minimal approach` for `small_change`, or `approach` for `standard_feature` / `high_risk_feature`
- current phase contract
- bead graph
- file scope
- forbidden paths when relevant
- verification plan
- execution envelope proposal

For `small_change`, the current phase contract may be compact but must still identify:
- intended exit state
- selected bead
- file scope
- verification
- explicit out-of-scope boundaries when relevant

Required for `standard_feature` and `high_risk_feature`:
- applicable prior learning consulted
- discovery facts when needed
- story map
- risk map
- proof or accepted mitigation for every MED risk that can affect acceptance, scope, verification, rollback, security, privacy, migration behavior, or compatibility

Required for `high_risk_feature`:
- proof/spike/manual evidence for HIGH risks, or an explicit non-execution route for missing proof
- rollback expectation or pivot signal
- multi-phase boundary when the feature cannot safely ship in one phase

Before approving execution, confirm:
- proof type is recorded for each required MED/HIGH risk
- spike-required risks have a passed spike result or route back to `beo-plan`
- phase exit state is observable by command, inspection, runtime behavior, or explicit UAT
- bead acceptance maps to the story or current-phase exit state

Missing required planning-depth content is `FAIL_PLAN`.
If this checklist conflicts with `beo-references -> complexity.md`, `complexity.md` owns planning-depth section requirements.

## Decision mapping checklist

Before `PASS_SERIAL` or `PASS_SWARM`, each acceptance-critical decision in `CONTEXT.md` must map to at least one of:
- bead acceptance
- verification command
- review/UAT check
- explicit `N/A` reason

If acceptance-critical decisions are unmapped, emit `FAIL_PLAN`.
Decision mapping checks coverage only; do not rewrite decisions, acceptance, beads, or verification here.

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
| exactly one approved ready bead under an explicit serial execution envelope | `PASS_SERIAL` |
| multiple beads exist but only one is currently ready and the selected ready bead is covered by an explicit serial execution envelope | `PASS_SERIAL` for the selected ready bead |
| at least two approved ready beads have recorded isolation and dependency proof, and Agent Mail is available | `PASS_SWARM` |
| at least two beads could be parallel but isolation proof is missing | `FAIL_PLAN` |
| ready beads have overlapping file scope or dependency conflict | `FAIL_PLAN` |
| Agent Mail is unavailable before dispatch and the existing envelope is swarm | no `PASS_SWARM`; route through fresh serial classification, never reuse swarm approval |
| Agent Mail is unavailable before dispatch and one explicitly approved serial bead remains under a fresh serial envelope | `PASS_SERIAL` |
| Agent Mail is unavailable before dispatch and no fresh serial envelope is valid | `FAIL_PLAN` or `BLOCK_USER` by the blocking evidence |
| external approval, access, secret, or clarification is missing | `BLOCK_USER` |

Swarm fallback classification belongs here.
A failed or unavailable swarm path may become serial only through a fresh `PASS_SERIAL` verdict.
Do not reuse swarm approval as serial approval.
Missing `agent-mail` dependency may degrade classification to `PASS_SERIAL` only when one explicitly approved serial bead remains valid under a fresh serial envelope; otherwise it blocks `PASS_SWARM`.

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
- Do not create missing `PLAN.md` sections.
- Do not polish bead descriptions.
- Do not write spike outputs.
- Do not continue classification after a failure already proves artifact repair is required.
- Do not treat an execution-envelope change as a refresh-only case.
- Do not convert swarm approval to serial approval without a fresh `PASS_SERIAL` verdict.
- Do not grant or refresh execution approval when required user authorization, external approval, access, secret, or clarification is missing; emit `BLOCK_USER`.
- Do not expand into route-collision handling beyond emitting the matching next owner for the validated verdict.

## References
- `beo-references -> operator-card.md`
- `beo-references -> approval.md`
- `beo-references -> artifacts.md`
- `beo-references -> complexity.md`
- `beo-references -> pipeline.md`
- `beo-references -> state.md`
- `references/readiness-review-prompt.md`
- `references/bead-readiness-prompt.md`

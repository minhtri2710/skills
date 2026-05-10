# BEO Pipeline

## Runtime vocabulary

```text
Lanes: beo_tiny | standard
Execution modes: single | ordered_batch
Readiness: PASS_EXECUTE | FAIL_PLAN | FAIL_EXPLORE | BLOCK_USER | FAIL_STATE
Review verdicts: accept | fix | reject
Learning case: none | present
Learning case type: wrong-owner-selection | unsafe-mutation-temptation | approval-scope-confusion | review-debug-confusion | human-gate-confusion | tiny-standard-confusion | route-identity-confusion | durable-workflow-learning | unclear-learning
Integrity status: verified | stale | invalid | unavailable
Terminal owners: done | user
```

Any value outside this registry is invalid current doctrine unless its canonical owner file is changed in the same edit. Closure reasons may exist but must not be confused with review verdicts. Do not use `N/A` as a global integrity value. The integrity helper uses the four-value status register above. Field-level helper sub-fields use `complete | missing | invalid | unavailable` only. `pass | fail` is not a valid integrity status.

## Default runtime path

| From | Condition | To |
| --- | --- | --- |
| beo-explore | requirements locked | beo-plan |
| beo-plan | executable scope complete | beo-validate |
| beo-validate | PASS_EXECUTE granted | beo-execute |
| beo-execute | execution evidence finalized | beo-review |
| beo-review | accept, no learning case | done |

## Exception path

| Condition | To |
| --- | --- |
| requirements missing or contradicted | beo-explore |
| plan/scope/verification missing or stale | beo-plan |
| approval/integrity missing/stale before mutation | beo-validate or beo-plan by stale cause |
| root cause unproven and mutation/verdict unsafe | beo-debug |
| owner or active feature identity unsafe | beo-route |
| required Human Gate unresolved | user |
| concrete learning case after runtime safe point | beo-compound |
| repeated finalized learning pattern | beo-dream |
| explicit selected doctrine edit | beo-author |

## Owner groups

Normal runtime path:

`beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done`

### Runtime delivery owners

- `beo-explore`: lock requirements.
- `beo-plan`: turn locked requirements into executable scope.
- `beo-validate`: classify readiness and grant/deny execution approval.
- `beo-execute`: deliver exactly one approved execution set.
- `beo-review`: emit one terminal verdict from finalized execution evidence.

### Runtime support owners

- `beo-debug`: prove one unproven blocker root cause.
- `beo-route`: repair unsafe owner or feature identity.

### Learning owners

- `beo-compound`: record one observed learning case or agent false case.
- `beo-dream`: consolidate repeated finalized learning cases into one pattern.
- `beo-author`: update existing BEO skills or create a new skill from explicit request or selected learning evidence.

### Utility owners

- `beo-reference`: read-only canonical lookup.
- `beo-setup`: setup/check/usage only.

### Terminal owners

- `user`: required human decision.
- `done`: terminal closure.

Learning owners are not runtime support owners. Runtime safety, repair, verdicting, diagnosis, and user blocking take priority over learning capture or consolidation.

Mutation owner: only `beo-execute`, and only inside the current approval envelope.

Approval owner: only `beo-validate`.

Terminal review owner: only `beo-review`.

No owner file may contradict this topology.

## Owner selection orientation

Use the first matching condition. Terminal-evidence check must occur before current-owner continuation:

| Condition | Owner |
| --- | --- |
| Owner identity is missing, stale, contradictory, colliding, or feature collision exists | `beo-route` |
| Tiny/standard execution evidence is finalized and ready for terminal verdict | `beo-review` |
| Requirements are missing, unlocked, contradicted, or acceptance/scope-affecting answers are unresolved | `beo-explore` |
| Requirements are locked, but plan, bead graph, BR descriptions, scope, risk, rollback, generated outputs, or verification is missing/stale/invalid | `beo-plan` |
| Requirements and plan exist, but readiness, approval, integrity, execution set selection, remediation classification, or user-blocker classification is needed | `beo-validate` |
| `PASS_EXECUTE` is current with fresh `approval_ref`, selected execution set, declared scope, and verified integrity | `beo-execute` |
| Root cause is unproven and mutation/verdicting would be unsafe | `beo-debug` |
| Review, debug, validate, execute, or route records a concrete learning/false case | `beo-compound` |
| At least two finalized cases support same pattern, or user asks to consolidate | `beo-dream` |
| Explicit user request or selected learning evidence chosen for skill authoring | `beo-author` |
| Setup/check/usage question and no runtime owner is active | `beo-setup` |
| Read-only canonical rule lookup | `beo-reference` |

This table is orientation. Owner SKILL files and local hard stops remain authoritative when stricter.

## Route suppression

Use `beo-route` only when owner or feature identity is unsafe. Do not route merely because an artifact section is defective and the current owner owns that section (ROUTE-02).

For owner identity defects, use `beo-route`; detailed route procedure lives in `route/references/router-operations.md`.

## Repair paths

| From | Condition | Next owner |
| --- | --- | --- |
| `beo-validate` | plan/scope/verification/BR/integrity defect | `beo-plan` |
| `beo-validate` | requirements missing, unlocked, or contradicted | `beo-explore` |
| `beo-validate` | Human approval/access/secret/legal/business decision required | `user` |
| `beo-execute` | readiness, approval_ref, integrity, or selected execution set missing/stale before mutation | `beo-validate` or `beo-plan` by stale cause |
| `beo-execute` | root cause unproven | `beo-debug` |
| `beo-execute` | scope or approval repair required | `beo-plan` |
| `beo-execute` | evidence finalized | `beo-review` |
| `beo-review` | fix finding but root cause unproven | `beo-debug` |
| `beo-review` | fix finding and root cause proven | `beo-plan` |
| `beo-review` | requirements invalid or contradicted | `beo-explore` |
| `beo-review` | accept with no learning | `done` |
| `beo-review` | accept with concrete learning/false-case | `beo-compound` |
| `beo-review` | fix finding with concrete learning/false-case | `beo-debug` or `beo-plan`, then compound after repair |
| `beo-compound` | learning case recorded | `done` |
| `beo-dream` | consolidation complete | `done` |
| `beo-dream` | pattern recommends skill update | `done` with recommendation; `beo-author` only on user confirmation |
| `beo-author` | skill update complete | `done` |

## Learning and skill-improvement path

BEO learning is case-based.

- `beo-compound` records one concrete observed learning case or false case.
- `beo-dream` consolidates multiple finalized cases into one recurring pattern.
- `beo-author` updates existing skills or creates a new skill only from explicit user request or selected learning evidence.

Default closure:
- no learning case -> done
- one concrete case -> beo-compound -> done
- repeated finalized cases or explicit consolidation request -> beo-dream -> done
- explicit skill authoring request -> beo-author -> done

Learning routing is lower priority than runtime safety routing. A runtime owner may route to `beo-compound` only after completing the required safe runtime decision or handoff.

## No automatic self-modification

Runtime owners must not edit skills or shared doctrine.
`beo-compound` and `beo-dream` learn only.
`beo-author` edits skills only when explicitly requested or when selected learning evidence is explicitly chosen for authoring.

Legal learning transitions:

```text
beo-review -> beo-compound
beo-debug -> beo-compound
beo-validate -> beo-compound
beo-execute -> beo-compound
beo-route -> beo-compound
beo-compound -> beo-dream
beo-compound -> done
beo-dream -> beo-author
beo-dream -> done
user -> beo-author
beo-author -> done
beo-author -> user
```

A direct compound handoff to author is not legal automatically. It requires explicit user confirmation.

## Execution hard stops

No mutation without `PASS_EXECUTE`, fresh `approval_ref`, selected execution set, supported mode, declared file scope, forbidden paths, verification contract, and verified integrity (APP-01).

For `ordered_batch`, stop on the first blocked bead (APP-06). Do not continue unaffected beads.

## Setup boundary

`beo-setup` is setup/check/usage only (SETUP-01). It is not a runtime owner and cannot create `.beads`, create feature artifacts, approve, validate, execute, review, debug, record learning, consolidate learning, or author skill changes (SETUP-02).

## Terminal closure

`done` is legal only after accepted closure with no learning case, completed learning closure, rejected/deferred/canceled closure, or explicit user stop recorded in state.

## Command semantics

Owner transitions and artifact authority do not define command semantics.

Workflow-visible command semantics belong to `references/tool-contracts.md`.

If a command or subcommand has no contract, its output is not workflow authority.

## Footnote

Rule IDs cited here are defined in their canonical homes: APP-* in `approval.md`, ROUTE-* in `route/SKILL.md`, and SETUP-* in `setup/SKILL.md`.

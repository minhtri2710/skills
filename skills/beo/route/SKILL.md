---
name: beo-route
description: |
  Select exactly one beo owner. Use when owner state is missing, invalid, contradictory, or colliding. Do not use when exactly one non-route owner predicate is true.
---

# beo-route

## Purpose
Select exactly one beo owner.

## Primary owned decision
Select exactly one next owner from user intent, trusted state, and live evidence.

## Enter when
- startup, resume, re-entry, stale or invalid handoff, explicit support/meta intent, or owner collision is present
- owner is missing, invalid, contradictory, or more than one non-route owner predicate matches

## Writable surfaces
- `.beads/STATE.json` under the shared STATE write baseline plus `route_decision`
- shared `STATE/HANDOFF` surfaces under `beo-references -> skill-contract-common.md`

## Route suppression rule
- Preserve the current valid owner when exactly one current owner remains valid and no new contradiction, stale handoff, stale approval, or owner collision exists.
- Avoid route churn.

## Owner decision ladder

Evaluate in order. Stop at the first decisive match.

1. support/meta intent -> `beo-reference`, `beo-author`, or `beo-onboard`
2. onboarding invalid -> `beo-onboard`
3. multiple active feature candidates with no selected feature -> `user`
4. stale or invalid handoff -> ignore handoff and route from live artifacts
5. `CONTEXT.md` missing, unlocked, contradicted, or requirement-changing clarification exists -> `beo-explore`
6. `PLAN.md`, phase shape, bead graph, dependencies, file scope, or verification plan missing/invalid -> `beo-plan`
7. artifacts current but approval, readiness, or execution mode missing/stale/invalid -> `beo-validate`
8. readiness=`PASS_SERIAL` -> `beo-execute`
9. readiness=`PASS_SWARM` -> `beo-swarm`
10. execution bundle complete and review evidence ready -> `beo-review`
11. accepted-work closure -> inherit closure split from `beo-references -> learning.md`
12. blocker exists and root cause is unproven -> `beo-debug`, unless an earlier canonical owner already wins with proven requirement, plan, or approval invalidity
13. terminal no-work state -> `done`; external clarification, access, or approval needed -> `user`

## Route determinism rule
- Do not emit a next owner as `A or B`.
- When more than one owner appears plausible, apply the ladder and collision rules until exactly one remains.
- If evidence is still insufficient, choose the earliest owner that can legally clarify by reading or writing its owned surface, or `user` only for external missing input.

## Collision rules

Use these only when the ladder leaves more than one plausible owner after disqualification.

| Collision | Winner |
| --- | --- |
| explore + plan | `beo-explore` |
| plan + validate | `beo-plan` if content or bead graph repair is needed; otherwise `beo-validate` |
| validate + execute | `beo-validate` |
| execute + debug | `beo-debug` when root cause is unproven |
| execute + review | `beo-review` only when terminal evidence is complete |
| review + compound | `beo-review` until verdict exists |
| compound + dream | `beo-compound` for one feature; `beo-dream` for cross-feature consolidation |

## Decision packet
- shared decision packet under `beo-references -> skill-contract-common.md`
- local extensions: `matched_condition`, `disqualified_owners`

## STATE.json fields written
- inherits shared STATE write baseline from `beo-references -> skill-contract-common.md`
- `route_decision`

## Allowed next owners
- beo-onboard
- beo-reference
- beo-author
- beo-dream
- beo-debug
- beo-explore
- beo-plan
- beo-validate
- beo-execute
- beo-swarm
- beo-review
- beo-compound
- user
- done

## Local hard stops
- Do not hide routing precedence or collision doctrine in references.
- Do not restate legal transitions, approval semantics, or artifact schemas beyond what local routing readability requires.

## References
- `beo-references -> operator-card.md`
- `beo-references -> doctrine-map.md`
- `beo-references -> pipeline.md`
- `beo-references -> approval.md`
- `beo-references -> learning.md`
- `beo-references -> state.md`
- `references/router-operations.md`

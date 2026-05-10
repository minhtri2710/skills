---
name: beo-route
description: |
  Use this skill to repair or select the active owner only when owner identity is unsafe. Use when owner identity is missing, stale, contradictory, colliding, or feature collision exists. Do not use when a valid current owner can continue or a normal legal handoff is obvious.
---

# beo-route

## Purpose
Repair or select the active owner only when owner identity is unsafe.

## Active when
A ROUTE-01 defect is proven: `missing_owner`, `stale_owner`, `contradictory_owner`, `colliding_predicates`, or `feature_collision`.

## Owns
Select one next owner or route to user for unresolved collision.

## Reads
- current STATE/HANDOFF as context
- current required surfaces needed to prove owner/feature identity
- pipeline legal transitions
- `route/references/router-operations.md`
- `beo-reference -> references/tool-contracts.md` (read only before using command output for owner-identity evidence)

## Writes
- STATE fields needed for owner repair
- HANDOFF only when pausing/transferring

## Must stop when
- current owner can legally repair the defect (ROUTE-02)
- the issue is an ordinary artifact defect
- terminal closure is not proven
- Enforce shared owner stops from `beo-reference -> references/skill-contract-common.md`.

## Route activation gate
`beo-route` is active only after proving one ROUTE-01 defect. If the current owner can legally repair the defect, do not use route. Multiple active feature candidates that cannot be resolved by canonical evidence route to `user` (STATE-02).

## Exit map
| Condition | Next owner |
| --- | --- |
| owner identity repaired | selected owner |
| feature collision unresolved | user |
| colliding predicates unresolved | user |
| terminal closure proven | done |

## References
- `beo-reference -> references/state.md`
- `route/references/router-operations.md`
- `beo-reference -> references/pipeline.md` (read only if allowed next owner is unclear)
- `beo-reference -> references/tool-contracts.md` (read only before using command output for owner-identity evidence)
- `beo-reference -> references/skill-contract-common.md`

---
name: beo-swarm
description: |
  Coordinate approved independent beads in parallel. Use when mode=`swarm`, approval is current, Agent Mail is available, and at least two ready beads are isolated. Do not use when implementation is required.
---

# beo-swarm

## Purpose
Coordinate approved independent beads in parallel.

## Primary owned decision
Coordinate approved independent beads in parallel without implementing.

## Enter when
- readiness=`PASS_SWARM`
- approval is current
- mode=`swarm`
- Agent Mail is available
- at least two ready beads have recorded isolation and dependency proof

## Writable surfaces
- Agent Mail dispatch/report metadata and reservations described by `beo-references -> coordination.md` and `references/swarming-operations.md`
- bead status and evidence surfaces described by `beo-references -> status-mapping.md`, only for coordinated approved beads
- review evidence bundle aggregation fields described by `beo-references -> artifacts.md`, only after worker reports are complete
- shared `STATE/HANDOFF` surfaces under `beo-references -> skill-contract-common.md`

## Decision packet
- shared decision packet under `beo-references -> skill-contract-common.md`
- no local packet extensions beyond coordination and aggregation evidence in owned surfaces

## Worker boundary
- coordinate only
- workers inherit approved scope, forbidden paths, verification contract, and approval reference
- overlap or scope drift stops coordination
- serial fallback requires `beo-validate`

## Swarm fallback rule

Do not silently convert swarm work into serial execution.
Swarm approval is not serial approval.
Any serial remainder after failed or partial swarm coordination must route to `beo-validate` for a fresh serial readiness verdict.

Representative exits:
- `beo-validate` when swarm can no longer continue but serial reclassification may still be legal
- `beo-plan` when isolation proof is lost, file scopes overlap, or bead structure must change
- `beo-debug` when a blocker root cause is unproven
- `user` when external access, secret, or approval is missing

Use `beo-references -> approval.md`, `beo-references -> pipeline.md`, and `beo-route` for the canonical split when multiple fallback signals appear together.

## Allowed next owners
- beo-review
- beo-validate
- beo-plan
- beo-debug
- user

## Local hard stops
- Do not implement product changes.
- Do not reclassify swarm work to serial in place.
- Do not normalize overlap or scope drift by coordinator judgment.
- Do not dispatch workers before confirming all planned beads exist in the br DB.
- Do not record worker completion without verifying file evidence directly; worker reports are hypotheses, not evidence.
- Do not reuse swarm approval as serial approval.

## References
- `beo-references -> operator-card.md`
- `beo-references -> coordination.md`
- `beo-references -> status-mapping.md`
- `beo-references -> pipeline.md`
- `references/swarming-operations.md`
- `references/message-templates.md`

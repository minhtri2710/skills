# Operator card

Use this as the first-pass operational view. It does not replace canonical doctrine.

## Core flow

`route -> explore -> plan -> validate -> execute/swarm -> review -> done`

## Optional closure

`review -> compound -> dream/done`

## Owner boundary matrix

| Owner | Single decision | Writable surface | Must not do |
| --- | --- | --- | --- |
| `beo-explore` | lock requirements | `CONTEXT.md` | plan or execute |
| `beo-plan` | create or repair current-phase graph | `PLAN.md`, bead graph metadata | approve or execute |
| `beo-validate` | classify readiness, mode, and approval action | approval record, readiness state | repair artifact content |
| `beo-execute` | deliver one approved serial bead | approved product file scope | widen scope or diagnose unknown blocker |
| `beo-swarm` | coordinate approved parallel beads | coordination and aggregation surfaces | implement product changes |
| `beo-review` | emit one terminal verdict | `REVIEW.md`, bounded reactive-fix record | fix code |
| `beo-compound` | record one feature learning outcome | feature learning record | cross-feature consolidation |
| `beo-dream` | consolidate cross-feature learning | shared learning guidance | treat one feature as corpus evidence |

## When unsure

Use `beo-route`.

## Read first

1. `.beads/STATE.json`
2. `.beads/HANDOFF.json` only if fresh
3. `.beads/artifacts/<feature_slug>/CONTEXT.md`
4. `.beads/artifacts/<feature_slug>/PLAN.md`
5. `.beads/artifacts/<feature_slug>/approval-record.json`
6. `.beads/artifacts/<feature_slug>/execution-bundle.json`
7. `.beads/artifacts/<feature_slug>/REVIEW.md`

## Exit packet

Return only:
- decision
- evidence
- changed surfaces
- blocked_by
- next_owner
- next_owner_reason

## Canonical pointers

- owner selection -> `beo-route`
- legal transitions -> `beo-references -> pipeline.md`
- approval -> `beo-references -> approval.md`
- state/handoff -> `beo-references -> state.md`
- learning -> `beo-references -> learning.md`

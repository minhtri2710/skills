---
name: beo-swarm
description: |
  Coordinate approved independent beads in parallel. Use when mode=`swarm`, approval is current, Agent Mail is available, and at least two ready beads are isolated. Do not use when implementation is required.
metadata:
  dependencies:
    - id: agent-mail
      kind: mcp_server
      server_names: [mcp_agent_mail]
      config_sources: [repo_config, global_config]
      missing_effect: unavailable
      reason: Required for worker dispatch, reservations, and return-channel coordination.
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
- workers inherit approved file scope, approved generated outputs, forbidden paths, verification contract, and approval reference
- workers are execution delegates, not route owners
- overlap or scope drift stops coordination
- serial fallback requires `beo-validate`

## Dispatch packet

Each worker receives:
- assigned bead id
- relevant `CONTEXT.md` decision IDs
- relevant `PLAN.md` current phase/story refs
- approved file scope
- approved generated outputs
- forbidden paths
- verification commands
- dependency constraints
- reporting format
- stop conditions

Do not give workers whole-workflow ownership.
Do not give workers permission to reinterpret approval.

## Worker stop conditions

A worker must stop and report when:
- required mutation falls outside approved file scope plus approved generated outputs
- forbidden path is needed
- dependency is incomplete
- file reservation conflicts with another worker
- root cause of verification failure is unproven
- implementation would contradict `CONTEXT.md`
- bead acceptance appears wrong or insufficient
- verification cannot be run
- approval appears stale

## Swarm red flags

Stop coordination and route appropriately if:
- a worker implements multiple beads at once
- orchestrator edits product source files
- repeated file conflicts suggest bad decomposition
- build/test failures accumulate without root cause
- workers report success without verification evidence
- Agent Mail is unavailable after `PASS_SWARM`

## Swarm fallback rule

Do not silently convert swarm work into serial execution.
Swarm approval is not serial approval.
Any serial remainder after failed or partial swarm coordination must route to `beo-validate` for a fresh serial readiness verdict.

Representative exits:
- `beo-review` when all worker evidence is complete and the review bundle is ready
- `beo-validate` when swarm can no longer continue but serial reclassification may still be legal
- `beo-plan` when isolation proof is lost, file scopes overlap, or bead structure must change
- `beo-debug` when a blocker root cause is unproven
- `user` when external access, secret, or approval is missing

Decision split:
- all worker evidence complete -> `beo-review`
- Agent Mail unavailable or mode stale -> `beo-validate`
- isolation proof lost, file scopes overlap, or dependency shape is wrong -> `beo-plan`
- verification failure with unproven root cause -> `beo-debug`
- external access, secret, or approval missing -> `user`

Use `beo-references -> approval.md`, `beo-references -> pipeline.md`, and `beo-route` for the canonical split when multiple fallback signals appear together.

## Allowed next owners
- beo-review
- beo-validate
- beo-plan
- beo-debug
- user

## Local hard stops
- Do not implement product changes.
- Do not edit product source files as the orchestrator.
- Do not reclassify swarm work to serial in place.
- Do not normalize overlap or scope drift by coordinator judgment.
- Do not dispatch workers before confirming all planned beads exist in the br DB.
- Do not record worker completion without verifying file evidence directly; worker reports are hypotheses, not evidence.
- Do not reuse swarm approval as serial approval.
- Do not let a worker reinterpret the approval envelope or own route decisions.

## References
- `beo-references -> operator-card.md`
- `beo-references -> approval.md`
- `beo-references -> artifacts.md`
- `beo-references -> coordination.md`
- `beo-references -> status-mapping.md`
- `beo-references -> pipeline.md`
- `references/swarming-operations.md`
- `references/message-templates.md`

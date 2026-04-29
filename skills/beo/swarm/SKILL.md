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
Dispatch, tend, and reconcile approved isolated worker beads without implementing as coordinator.

## Ownership predicate
- Readiness is `PASS_SWARM`.
- Approval is current.
- Agent Mail is live-available now.
- At least two ready beads are isolated for parallel work.
- Coordinator mutation is limited to dispatch, reservation, reconciliation, and handoff state.

## Dependencies
Machine-readable dependency posture lives in frontmatter. If live Agent Mail is unavailable, return to `beo-validate`; cached onboarding posture cannot authorize swarm.

## Writable surfaces
- Worker dispatch, reservation, heartbeat, and reconciliation records.
- Bead coordination/status fields allowed by canonical status mapping.
- Shared `STATE/HANDOFF` surfaces under the common contract baseline.

> Canonical: `beo-reference -> coordination.md`
> Locally enforced as:
> - Workers do not route, approve, or change the canonical owner.
> - Reservations prevent collisions but do not create approval.
> - Swarm fallback routes through `beo-validate` / `beo-swarm` authority, not the operations appendix.

## Hard stops
- Do not implement as coordinator.
- Do not self-downgrade to serial execution.
- Do not dispatch without live Agent Mail availability and current approval.

## Allowed next owners
- `beo-review`
- `beo-validate`
- `beo-plan`
- `beo-debug`
- `user`
- `beo-route` — only when owner state is missing, stale, contradictory, or colliding.

## References
- `beo-reference -> approval.md` — read when checking approval freshness for worker scope.
- `beo-reference -> coordination.md` — read when applying Agent Mail, worker authority, and reservation semantics.
- `beo-reference -> status-mapping.md` — read when reconciling bead statuses.
- `beo-reference -> pipeline.md` — read when routing after swarm reconciliation.
- `references/swarming-operations.md` — read when tending active swarm procedure.
- `references/message-templates.md` — read when sending worker dispatch, ACK, heartbeat, or report text.

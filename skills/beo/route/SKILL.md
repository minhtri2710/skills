---
name: beo-route
description: |
  Select exactly one beo owner. Use when owner state is missing, invalid, contradictory, or colliding. Do not use when exactly one non-route owner predicate is true.
metadata:
  dependencies:
    - id: beads-cli
      kind: command
      command: br
      missing_effect: degraded
      reason: Helpful for live bead context, but some routing decisions can proceed from artifacts and state.
    - id: beads-viewer
      kind: command
      command: bv
      missing_effect: degraded
      reason: Helpful for read-only inspection, but not required for every route decision.
---
# beo-route

## Purpose
Select exactly one beo owner.

## Primary owned decision
Resolve missing, invalid, contradictory, or colliding owner state into one next owner.

## Ownership predicate
- Current owner state is missing, stale, contradictory, or colliding.
- User intent conflicts with state, handoff, approval, or live artifact evidence.
- Multiple owner predicates appear true or no non-route owner predicate is true.
- The user explicitly asks to debug a failure and no current owner already validly owns that diagnostic work.
- Zero, multiple, stale, or contradictory non-route owner predicates require owner selection.

## Writable surfaces
- Route evidence and owner fields in shared state/handoff surfaces.
- No feature artifact content except route metadata explicitly owned by canonical state doctrine.

> Canonical: `beo-reference -> pipeline.md` and `beo-reference -> state.md`
> Locally enforced as:
> - Select exactly one legal next owner.
> - Treat handoff and cached state as advisory when live artifacts contradict them.
> - Use `beo-reference -> state.md` for route decision mapping fields instead of redefining them.

## Hard stops
- Do not perform the selected owner’s work.
- Do not invent new owners or transitions.
- Do not route around stale approval or contradicted requirements.

## Allowed next owners
- `beo-explore`
- `beo-plan`
- `beo-validate`
- `beo-execute`
- `beo-swarm`
- `beo-review`
- `beo-debug`
- `beo-compound`
- `beo-dream`
- `beo-onboard`
- `beo-author`
- `beo-reference`
- `user`
- done

## References
- `beo-reference -> operator-card.md` — read when presenting the selected owner and evidence.
- `beo-reference -> doctrine-map.md` — read when ownership of a rule is unclear.
- `beo-reference -> pipeline.md` — read when checking legal owner transitions.
- `beo-reference -> approval.md` — read when stale approval affects routing.
- `beo-reference -> learning.md` — read when accepted-work closure affects routing.
- `beo-reference -> state.md` — read when evaluating state, handoff freshness, and route evidence fields.
- `beo-reference -> artifacts.md` — read when interpreting decision mapping and artifact provenance.
- `references/router-operations.md` — read when inspecting current route evidence without unsupported commands.

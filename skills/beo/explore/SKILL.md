---
name: beo-explore
description: |
  Use this skill to lock requirements before planning. Use when no locked requirements exist, requirements are missing or contradicted, acceptance/scope-affecting answers are unresolved, or a Human Gate can affect acceptance, scope, non-goals, compatibility, approval, security/privacy, access, or legal/business constraints. Do not use when implementation details can be safely decided inside locked scope.
---

# beo-explore

## Purpose

Lock requirements before planning.

## Fast predicate

Active when no locked requirements exist, requirements are missing or contradicted, acceptance/scope-affecting answers are unresolved, or a Human Gate can affect acceptance, scope, non-goals, compatibility, approval, security/privacy, access, or legal/business constraints.

Not active when implementation details can be safely decided inside locked scope.

## Primary owned decision

Produce or repair locked requirements.

## Writable surfaces

.beads/artifacts/<feature_slug>/CONTEXT.md; .beads/artifacts/<feature_slug>/pending-human-gates.md only if needed; STATE.json fields needed for requirements lock and next owner; HANDOFF.json only when pausing/transferring.

## Hard stops

Do not plan. Do not implement. Do not approve readiness. Do not lock requirements while a required Human Gate remains unresolved. Do not ask questions that cannot affect acceptance or scope. Do not route for requirements defects that beo-explore owns.

## Allowed next owners

beo-plan, user, beo-route

## References

- `beo-reference -> references/pipeline.md`
- `beo-reference -> references/state.md`
- `beo-reference -> references/artifacts.md`
- `beo-reference -> references/approval.md`
- `beo-reference -> references/skill-contract-common.md`

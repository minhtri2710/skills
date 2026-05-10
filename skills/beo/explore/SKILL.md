---
name: beo-explore
description: |
  Use this skill to lock requirements before planning. Use when no locked requirements exist, requirements are missing or contradicted, acceptance/scope-affecting answers are unresolved, or a Human Gate can affect acceptance, scope, non-goals, security/privacy, access, or legal/business constraints. Do not use when implementation details can be safely decided inside locked scope.
---

# beo-explore

## Purpose
Lock requirements before planning.

## Active when
No locked requirements exist, requirements are missing or contradicted, or an unresolved answer can change acceptance, scope, non-goals, Human Gates, security/privacy, access, or legal/business constraints.

## Owns
Produce or repair locked requirements.

## Reads
- current user request
- current requirement surface if present
- repo evidence only when needed to lock scope/risk
- `beo-reference -> references/human-gate.md` (read only for gate classification)
- `beo-reference -> references/artifacts.md` (read only for field/schema placement)

## Writes
- Tiny: `TICKET.md` requirement sections
- Standard: `CONTEXT.md`
- owner-owned STATE/HANDOFF fields when pausing/transferring

## Must stop when
- a required Human Gate remains unresolved (HG-01)
- the question cannot affect acceptance, scope, non-goals, constraints, or approval
- the defect belongs to a later owner
- Enforce shared owner stops from `beo-reference -> references/skill-contract-common.md`.

## Exit map
| Condition | Next owner |
| --- | --- |
| requirements locked | beo-plan |
| required Human Gate unresolved | user |
| unsafe owner/feature identity | beo-route |

## References
- `beo-reference -> references/pipeline.md`
- `beo-reference -> references/skill-contract-common.md`
- `beo-reference -> references/human-gate.md` (read only for gate classification)
- `beo-reference -> references/artifacts.md` (read only for field/schema placement)

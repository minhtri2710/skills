# Skill Contract Common

Authority: canonical shared contract inherited by every BEO owner. Global invariants live in `beo-reference -> references/protocol-core.md`.

## Load order

Before any owner mutation, load:

1. active owner `SKILL.md`;
2. this common contract;
3. `beo-reference -> references/protocol-core.md`;
4. current required artifacts for the active density;
5. `beo-reference -> registry/pipeline.json` before checking or emitting a `condition_id`.

A BEO skill must be loaded before any mutation owned by that skill. STATE/HANDOFF orient only; they do not authorize action.

## Owner exclusivity

Each owner decides only the phase named in its contract and writes only its owned surfaces. Approval-bearing or owner-bearing decisions require the current structured authority block for the artifact density named in `beo-reference -> references/artifacts.md`.

## Shared write boundary

Unless explicitly owned by the loaded skill, do not mutate product files, another owner's artifact section, approval, selected execution sets, terminal verdicts, route identity, helper output, or compatibility aliases.

## Freshness and fail-closed rule

Reload current artifacts immediately before approval/refusal, product mutation, terminal verdict, owner identity repair, lifecycle closure, Human Gate resolution, or resume after interruption. Missing, stale, contradictory, invalid, or unavailable authority fails closed.

## Handoff rule

A phase can hand off only by emitting exactly one legal `condition_id` from the active owner contract and `registry/pipeline.json`. Owner-to-owner handoffs must include transition provenance as defined in `beo-reference -> references/transition-provenance.md`.

When the legal condition is `user_abandoned`, the current owner may write only the abandonment lifecycle bookkeeping defined in `beo-reference -> references/lifecycle.md` while emitting the terminal transition. This exception does not permit product mutation, approval, review verdicts, or non-abandonment closure writes.

## Common stop output

When stopping, report:

```text
Cannot continue because: <reason>
Current owner: <loaded owner>
Legal next owner/source: <owner | user | canonical reference>
Required read/evidence: <artifact section, registry, or helper output>
Writable surface now: <surface | none>
```

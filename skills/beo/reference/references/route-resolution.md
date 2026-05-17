# Route Resolution
<!-- beo:route-resolution -->

Authority: canonical unsafe owner/feature identity repair algorithm. Meta-target resolution lives in `beo-reference -> references/transition-provenance.md`.

## Rule

Use `beo-route` only when owner or feature identity is missing, stale, contradictory, colliding, or unsafe. Route is not normal resume and never approves, executes, reviews, plans, or patches.

## Algorithm

1. Compare artifact identity against STATE/HANDOFF mirrors.
2. Artifacts beat STATE/HANDOFF mirrors.
3. Repair identity metadata only when artifact evidence proves the repair.
4. If repair is proven, emit `identity_repaired` -> `restored_owner`.
5. If artifacts remain contradictory or no safe repair is proven, emit `user_decision_needed` -> `user`.
6. After repair, use `resume-resolution.md` for concrete owner orientation.

## Meta-target pointer
<!-- beo:route-resolution:meta-targets -->

`restored_owner` is symbolic. It is not a concrete owner and must not be loaded directly. Resolve it through `beo-reference -> references/transition-provenance.md` and then `beo-reference -> references/resume-resolution.md`.

## Operator output
<!-- beo:route-resolution:operator-output -->

When route stops, report the identity defect, artifact evidence checked, repair performed or refused, and the legal `condition_id`.

```text
Artifacts prove: <owner/feature identity evidence or none>
STATE/HANDOFF mirror: <matching | stale | contradictory | missing>
Route result: <identity_repaired | user_decision_needed>
```

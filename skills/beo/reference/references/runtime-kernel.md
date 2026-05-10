# BEO Runtime Kernel

## Core invariants

- One active feature.
- One active owner.
- Current required surfaces win.
- Only validate grants execution approval.
- Execute mutates only inside approval envelope.
- Review verdict is independent.
- Debug diagnoses only.
- Route repairs unsafe owner/feature identity only.
- Learning has no runtime authority.

## Normal path

`beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done`

## Exception path

| Condition | Owner |
| --- | --- |
| missing/contradicted requirements | beo-explore |
| missing/stale plan/scope/verification | beo-plan |
| approval/integrity missing/stale before mutation | beo-validate or beo-plan |
| unproven root cause | beo-debug |
| unsafe owner/feature identity | beo-route |
| unresolved Human Gate | user |
| concrete learning after runtime safe point | beo-compound |
| recurring finalized learning pattern | beo-dream |
| selected doctrine edit | beo-author |

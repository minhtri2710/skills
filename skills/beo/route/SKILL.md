---
name: beo-route
description: Repairs unsafe BEO owner or feature identity metadata only.
---

# beo-route

Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.

## Decision

Repair unsafe owner or feature identity metadata only.

## Enter

- Owner or feature identity is missing, stale, contradictory, colliding, or unsafe.

## Owns

- Identity defect diagnosis.
- Metadata repair when proven by artifacts.

## Writes

- STATE/HANDOFF identity metadata.
- Structured owner identity mirrors only when allowed by `state.md` and proven by artifact evidence.
- Route rationale as non-authoritative evidence.

## Stops

- No owner/feature identity defect is present.
- Artifacts cannot prove one safe repair.
- Request is normal resume, setup, usage, doctrine lookup, product work, approval, execution, review, or learning without an identity defect.
- Never repair requirements, plan, approval, execution evidence, review, or product files.

## Exits

- `identity_repaired` -> `restored_owner`
- `user_decision_needed` -> `user`
- `user_abandoned` -> `done`

## Method

1. Identify the identity defect.
2. Compare artifact identity against STATE/HANDOFF mirrors.
3. Repair identity metadata only when artifact evidence proves the repair.
4. Emit `identity_repaired` and let transition/resume rules orient the concrete owner, or stop to user.

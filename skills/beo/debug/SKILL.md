---
name: beo-debug
description: Proves one BEO blocker root cause without patching or approving.
---

# beo-debug

Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.

## Decision

Prove one blocker root cause without patching.

## Enter

- One concrete blocker question is assigned.
- Transition provenance exists when temporary-owner return is expected.

## Owns

- Diagnosis.
- Causal proof.
- Evidence collection.
- Unblock classification.

## Writes

- Debug diagnosis artifact.
- Allowed handoff metadata.

## Stops

- Blocker evidence is missing, stale, contradictory, or out of scope.
- Return provenance is missing, stale, contradictory, or illegal.
- Out-of-scope mutation is requested.

## Exits

- `root_cause_proven` -> `return_to_caller`
- `diagnosis_inconclusive` -> `user`
- `blocker_is_user_owned` -> `user`
- `user_abandoned` -> `done`

## Method

1. Restate the assigned blocker question.
2. Validate transition provenance before relying on `return_to_caller`.
3. Use no more than three bounded read-only probes unless the caller explicitly authorizes more probes.
4. Record evidence and diagnosis status.
5. Emit exactly one legal condition; meta-target resolution follows `beo-reference -> references/transition-provenance.md`.

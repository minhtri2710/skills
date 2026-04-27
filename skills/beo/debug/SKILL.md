---
name: beo-debug
description: |
  Prove one blocker root cause. Use when progress is blocked by unproven root cause or root-cause analysis is requested. Do not use when scope or decomposition needs redesign.
---

# beo-debug

## Purpose
Prove one blocker root cause.

## Primary owned decision
Prove one blocker root cause, then route with safe unblock evidence or return evidence only.

## Enter when
- root cause is unproven for a blocker
- review requires diagnosis before verdict
- the user explicitly requests failure investigation or root-cause analysis

## Writable surfaces
- diagnostic evidence in the active artifact or blocker record, only for the investigated blocker
- product files only for the smallest safe verified unblock inside the originating approved scope
- `.beads/STATE.json` under the shared STATE write baseline plus `debug_return` and `debug_result`
- shared `STATE/HANDOFF` surfaces under `beo-references -> skill-contract-common.md`

## Debug return rule
- caller writes `debug_return.origin_skill` and `debug_return.return_to` before transfer
- preserve `debug_return` unless evidence proves the original return owner is now invalid
- may override only `debug_return.return_to`
- if override occurs, record disqualification evidence in both `debug_return.override_evidence` and `debug_result`

## Safe unblock rule
A safe unblock is the smallest verified change that removes the proven blocker without changing scope, decomposition, acceptance, or verification.
It does not complete the bead or claim terminal delivery.
If unblock would require new file scope, plan repair, or approval repair, route to `beo-plan` or `beo-validate` instead.
See `references/diagnostic-checklist.md` for local examples and procedures.

## Allowed next owners
- beo-execute
- beo-swarm
- beo-review
- beo-plan
- beo-validate
- user

## Local hard stops
- Do not redesign decomposition or reinterpret acceptance.
- Do not apply a safe unblock without proof that scope, decomposition, acceptance, and verification contract are unchanged.
- Do not apply a safe unblock outside the originating approved scope.
- Do not use safe unblock to finish delivery work that belongs to `beo-execute` or worker execution.

## References
- `beo-references -> operator-card.md`
- `beo-references -> approval.md`
- `beo-references -> state.md`
- `beo-references -> pipeline.md`
- `references/diagnostic-checklist.md`

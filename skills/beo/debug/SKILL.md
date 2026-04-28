---
name: beo-debug
description: |
  Prove one blocker root cause. Use when progress is blocked by unproven root cause or root-cause analysis is requested. Do not use when scope or decomposition needs redesign.
metadata:
  dependencies:
    - id: beads-cli
      kind: command
      command: br
      missing_effect: degraded
      reason: Helpful for bead context, but exact failure evidence can still allow diagnosis.
    - id: beads-viewer
      kind: command
      command: bv
      missing_effect: degraded
      reason: Helpful for read-only inspection, but not required when exact failing artifacts are already known.
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

## Diagnostic sequence

1. Classify blocker:
   - build failure
   - test failure
   - runtime failure
   - integration failure
   - worker coordination blocker
   - approval/scope blocker
2. Check known learnings if available and applicable.
3. Reproduce the exact failure command or exact coordination failure.
4. Read only implicated files/artifacts:
   - error source
   - assigned bead
   - `CONTEXT.md` decision refs
   - `PLAN.md` scope/verification refs
   - approval envelope
5. Write one root cause sentence:
   `Root cause: <surface>:<location> — <what is wrong and why>.`
6. Decide:
   - safe unblock inside approval envelope -> apply smallest verified unblock
   - scope/plan/verification needs change -> `beo-plan`
   - approval needs repair only -> `beo-validate`
   - requirements contradicted -> `beo-explore`
   - external missing input -> `user`

## Safe unblock rule
A safe unblock is the smallest verified change that removes the proven blocker without changing scope, decomposition, acceptance, or verification.
It does not complete the bead or claim terminal delivery.
If unblock would require new file scope, plan repair, or approval repair, route to `beo-plan` or `beo-validate` instead.
See `references/diagnostic-checklist.md` for local examples and procedures.

## Allowed next owners
- beo-explore
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
- Do not apply a direct fix if the fix would exceed BEO safe unblock.
- Do not create fix beads here unless BEO artifacts explicitly allow diagnostic blocker metadata for the current owner path.
- Do not treat “small fix” as safe unless approval envelope remains unchanged.

## References
- `beo-references -> operator-card.md`
- `beo-references -> approval.md`
- `beo-references -> state.md`
- `beo-references -> pipeline.md`
- `beo-references -> learning.md`
- `references/diagnostic-checklist.md`

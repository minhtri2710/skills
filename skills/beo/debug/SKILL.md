---
name: beo-debug
description: |
  Proves one blocker root cause. Use when root cause is unproven and mutation or verdicting would be unsafe without diagnosis. Not for patching, approval, execution, planning, or terminal review verdicts.
---

# beo-debug

## Purpose

Prove one blocker root cause and return diagnosis evidence only.

## Decision Card

Decision: prove one blocker root cause.

Can enter when:
- one concrete blocker/root-cause question is assigned

Can write:
- debug diagnosis artifact and allowed owner-owned handoff metadata

Must stop when:
- entry evidence is stale/contradictory or runtime debug lacks caller provenance for `return_to_caller`

Exit summary (non-authoritative):
- `root_cause_proven` -> `return_to_caller`
- `diagnosis_inconclusive` -> `user`
- `blocker_is_user_owned` -> `user`

Never:
- patch, mutate product files, approve, select execution sets, or emit terminal verdicts

Reads:
- current artifacts, blocker evidence, state, and pipeline

## Contract

Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.

Acts when:
- one concrete blocker/root-cause question is assigned

Owns:
- diagnosis, causal proof, and unblock classification

Local stops:
- owner-specific entry evidence is missing, stale, contradictory, or out of scope
- runtime debug lacks fresh caller provenance required for `return_to_caller`

Writes:
- debug diagnosis artifact conforming to `beo.debug_diagnosis.v1`, plus owner-owned handoff metadata when allowed; no patches or other artifact authority

Reads:
- current artifacts, blocker evidence, bounded targeted read-only probes, `beo-reference -> references/state.md`, `beo-reference -> registry/pipeline.json`

Local forbids:
- patch text, product mutation, approval, execution-set selection, terminal verdicts

Exits:
- `root_cause_proven` -> `return_to_caller`
- `diagnosis_inconclusive` -> `user`
- `blocker_is_user_owned` -> `user`

## Diagnosis Output

Write concise diagnosis evidence at the feature artifact root as `DEBUG_DIAGNOSIS.md` or `debug-diagnosis-<id>.json`; either form must carry `schema_version: beo.debug_diagnosis.v1` and the required fields in `beo-reference -> registry/artifact-schemas.json`.

```yaml
schema_version: beo.debug_diagnosis.v1
id: debug-diagnosis-<id>
feature_slug: <feature_slug>
created_by_owner: beo-debug
created_at: <RFC3339 UTC timestamp>
assigned_question: <one blocker/root-cause question>
diagnosis_status: <root_cause_proven | diagnosis_inconclusive | blocker_is_user_owned>
evidence_refs:
  - <artifact/path/command/probe ref>
recommended_next_owner: <return_to_caller | user>
notes: <optional bounded note>
```

For bounded plan repair, set `recommended_next_owner: return_to_caller`; the caller decides the legal repair owner from the pipeline.

Use no more than three targeted read-only probes before reporting unless the caller explicitly authorizes more probes or the assigned debug budget already allows them.

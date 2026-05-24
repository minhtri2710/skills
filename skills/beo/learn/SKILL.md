---
name: beo-learn
description: Record reusable BEO delivery lessons as advisory memory after a beo-review or beo-debug learning_candidate event. Use only when a learning_candidate exists or user explicitly asks to save a BEO lesson. Trigger on "save this BEO lesson" or "persist this bead learning". Do not trigger for general note-taking outside BEO delivery context.
requires: br>=0.1.28
---
# beo-learn

## Use when

A review or debug owner has already recorded its delivery verdict or support return route and emitted a reusable learning candidate.

## Read

- The `learning_candidate` runtime event, its source issue, and the prior review verdict/route or debug return it references.
- Safe evidence refs, verdict or debug return status, and relevant non-secret summaries.
- `beo-reference` canonical contracts: `references/kernel.md`, `references/memory.md`, `registry/pipeline.json`, `registry/ticket-schema.json`, and `registry/command-contracts.json`.
- Obsidian/qmd setup state only to decide the authorized persistence path.

## Do

1. Confirm the lesson follows a recorded review verdict/route or debug return, is reusable, non-obvious, likely to recur, and safe to persist.
2. Extract only the trigger, lesson, prevention rule, and safe evidence refs.
3. Persist the smallest useful learning note through the approved memory write command.
4. Refresh qmd only after a successful authorized learning write or explicit setup authorization.
5. Request authoring only when the evidence shows a doctrine or registry gap.

## Write

- Learning-owned Obsidian note or local fallback markdown with non-authority disclaimer.
- qmd refresh status after an authorized successful write.
- Authoring recommendation payload when doctrine maintenance is warranted.

## Emit

- `case_recorded` -> stop.
- `authoring_requested` -> stop and load `beo-author` for maintenance.
- `insufficient_evidence` -> stop without inventing a lesson; user routing only when the user explicitly requested learning.

## Never

- Do not reopen delivery, alter review verdicts, or resolve Human Gates.
- Do not grant approval, execution permission, closure, or Human Gate resolution.
- Do not persist secrets, raw credentials, private payloads, or customer data.
- Do not edit doctrine, registries, scripts, or skill contracts directly.
- Do not load another BEO delivery owner in the same turn for the same issue after emitting; stop first.

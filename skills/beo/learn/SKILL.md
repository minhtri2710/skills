---
name: beo-learn
description: Records accepted BEO learning cases or consolidates repeated accepted-feature patterns.
---

# beo-learn

Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.

## Decision

Record accepted learning cases or consolidate repeated accepted-feature patterns.

## Enter

- Accepted review verdict evidence exists.
- Explicit consolidation evidence exists.

## Owns

- One learning case.
- Repeated-pattern consolidation.

## Writes

- Learning case records.
- Learning pattern records.

## Stops

- Selected accepted evidence is missing, stale, contradictory, insufficient, or out of scope.

## Exits

- `case_recorded` -> `done`
- `single_case_authoring_requested_with_evidence` -> `beo-author`
- `pattern_consolidated_authoring_requested_with_evidence` -> `beo-author`
- `insufficient_evidence` -> `done`

## Method

1. Verify accepted evidence or selected finalized cases.
2. Record one case or consolidate a repeated pattern.
3. Recommend authoring only when evidence supports it.
4. Exit without reopening runtime.

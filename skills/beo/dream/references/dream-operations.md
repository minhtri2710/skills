# Dream Operations

Load this file for source selection, candidate classification, consolidation behavior, approval-gated promotion, and checkpoint behavior.

## Table of Contents

- [1. Orient and Detect Run Mode](#1-orient-and-detect-run-mode)
- [2. Select Sources](#2-select-sources)
- [3. Extract and Classify Candidates](#3-extract-and-classify-candidates)
- [4. Apply Outcomes](#4-apply-outcomes)
- [5. Finalization and Reporting](#5-finalization-and-reporting)
- [6. Context-Budget Checkpoint](#6-context-budget-checkpoint)

## 1. Orient and Select Sources

1. detect tool availability (see `beo-reference` → `references/knowledge-store.md` § Tool Detection)
2. read existing learnings using the canonical read protocol (`beo-reference` → `references/learnings-read-protocol.md`): QMD/Obsidian first; flat-file fallback only when unavailable
3. confirm there is evidence from at least two accepted features before attempting shared-pattern promotion
4. use `agent-history-source-policy.md` to prioritize durable project artifacts over transient histories
5. if the available evidence is insufficient or contradictory, ask one short clarification question before scanning broader material

Default orientation rule: establish evidence quality before scanning broad source material.

## 3. Extract and Classify Candidates

1. Apply the safety filter:
- redact secrets and PII before any summary or durable write
- skip candidates that cannot be safely redacted

2. Classify each candidate with `consolidation-rubric.md` into exactly one branch:
   - clear match
   - ambiguous
   - no match
   - no durable signal

3. Use the learnings-read protocol for matching: QMD query first for semantic matching, then flat-file search as fallback. Do not skip QMD when it is available.

## 4. Apply Outcomes

| Classification | Action |
| --- | --- |
| `clear match` | Merge or rewrite only when exactly one target guidance location is clearly justified by source evidence |
| `ambiguous` | Present explicit merge / create / skip options |
| `no match` | Keep the pattern out of shared guidance until enough multi-feature evidence exists |
| `no durable signal` | Write nothing for that candidate |

Use the approval rules from `beo-reference` → `references/approval-gates.md` for any update to `.beads/critical-patterns.md`.

## 5. Finalization and Reporting

Report:
- sources used
- files reviewed
- patterns merged / retained / skipped
- pending ambiguous decisions or approvals

Refresh QMD after writes if available:

```bash
qmd update 2>/dev/null && qmd embed 2>/dev/null
```

## 6. Context-Budget Checkpoint

If context usage exceeds 65%, use the canonical `STATE.json` and `HANDOFF.json` shapes from `beo-reference` → `references/state-and-handoff-protocol.md`, then include the current consolidation phase, processed files, and remaining candidates.

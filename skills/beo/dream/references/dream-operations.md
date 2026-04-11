# Dream Operations

Detailed operational playbook for `beo-dream`. Load this file when you need exact provenance checks, mode selection, candidate classification mechanics, run-finalization steps, or checkpoint behavior.

## Table of Contents

- [1. Orient and Detect Run Mode](#1-orient-and-detect-run-mode)
- [2. Select Sources](#2-select-sources)
- [3. Extract and Classify Candidates](#3-extract-and-classify-candidates)
- [4. Apply Outcomes](#4-apply-outcomes)
- [5. Finalization and Reporting](#5-finalization-and-reporting)
- [6. Context-Budget Checkpoint](#6-context-budget-checkpoint)

## 1. Orient and Detect Run Mode

1. detect tool availability (see `../../reference/references/knowledge-store.md` § Tool Detection)
2. read existing learnings using the canonical read protocol (`../../reference/references/learnings-read-protocol.md`): QMD/Obsidian first, flat-file fallback only when unavailable
3. detect provenance via learnings frontmatter and `.beads/learnings/dream-run-provenance.md`
4. choose mode:
   - `bootstrap` if no provenance exists or the user requests a full scan
   - `recurring` otherwise
5. if provenance signals conflict, ask one short clarification question before scanning

Default orientation rule: establish mode and provenance confidence before scanning broad source material.

## 2. Select Sources

Use `agent-history-source-policy.md` for source priority and recurring-window defaults.

## 3. Extract and Classify Candidates

Apply the safety filter first:
- redact secrets and PII before any summary or durable write
- skip candidates that cannot be safely redacted

Then classify each candidate using `consolidation-rubric.md` into exactly one branch:
- clear match
- ambiguous
- no match
- no durable signal

Use the learnings-read protocol for matching: QMD query first for semantic matching, then flat-file search as fallback. Do not skip QMD when it is available.

## 4. Apply Outcomes

- `clear match` → rewrite/merge only when exactly one owner is clear
- `ambiguous` → present explicit merge/create/skip options
- `no match` → create a new dated learnings file
- `no durable signal` → write nothing for that candidate

Always run finalization once per completed run by updating `.beads/learnings/dream-run-provenance.md`.

## 5. Finalization and Reporting

Report:
- mode used
- source window used
- files rewritten / created / skipped
- whether provenance was updated
- pending ambiguous decisions or approvals

Use the approval rules from `../../reference/references/approval-gates.md` for any critical-pattern promotion proposal.

### Provenance Update

Write or update `.beads/learnings/dream-run-provenance.md` using this format:

```markdown
---
last_dream_consolidated_at: YYYY-MM-DDTHH:MM:SSZ
mode: <bootstrap | recurring>
source_window: <description of time range or scope>
---

## Run Summary

- **Files rewritten:** N
- **Files created:** N
- **Files skipped:** N
- **Critical promotions proposed:** N (approved: N)
- **Ambiguous decisions deferred:** N
```

Refresh QMD after writes if available:

```bash
qmd update 2>/dev/null && qmd embed 2>/dev/null
```

## 6. Context-Budget Checkpoint

If context usage exceeds 65%, use the canonical `STATE.json` and `HANDOFF.json` shapes from `../../reference/references/state-and-handoff-protocol.md`, then include the current consolidation phase, processed files, and remaining candidates.

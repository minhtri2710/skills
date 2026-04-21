# Dream Operations

Operational playbook for `beo-dream`.

## 1. Orient and Select Sources

1. detect tool availability via `knowledge-store.md`
2. read learnings using `learnings-read-protocol.md`
3. confirm there is evidence from at least two accepted features before promoting shared guidance
4. use `agent-history-source-policy.md` to prioritize durable project artifacts over transient histories
5. if evidence is insufficient or contradictory, ask one short clarification question before broadening the scan

Default rule: establish evidence quality before scanning broad source material.

## 2. Extract and Classify Candidates

Apply the safety filter first:
- redact secrets and PII before any summary or durable write
- skip candidates that cannot be safely redacted

Classify every candidate with `consolidation-rubric.md` into exactly one branch:
- clear match
- ambiguous
- no match
- no durable signal

Use QMD first for matching when it is available; use flat-file search only as fallback.

## 3. Apply Outcomes

| Classification | Action |
| --- | --- |
| `clear match` | merge or rewrite only when exactly one target location is justified by source evidence |
| `ambiguous` | present explicit merge / create / skip options |
| `no match` | keep it out of shared guidance until enough multi-feature evidence exists |
| `no durable signal` | write nothing |

Use `approval-gates.md` for any update to `.beads/critical-patterns.md`.

## 4. Finalization and Reporting

Report:
- sources used
- files reviewed
- patterns merged, retained, or skipped
- pending ambiguous decisions or approvals

Refresh QMD after writes if available:

```bash
qmd update 2>/dev/null && qmd embed 2>/dev/null
```

## 5. Context-Budget Checkpoint

If context usage exceeds 65%, write canonical `STATE.json` and `HANDOFF.json`, then include:
- current consolidation phase
- processed files
- remaining candidates

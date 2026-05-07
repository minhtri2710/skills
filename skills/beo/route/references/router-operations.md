# Router Operations v2

Role: APPENDIX

## Startup evidence

At session start, read `.beads/STATE.json` if present. Read `.beads/HANDOFF.json` only if resuming paused or transferred work. Read active feature artifacts only for the active `feature_slug`.

Startup output is advisory only and cannot approve execution, select execution sets, emit review verdicts, or promote learning.

## Route defects

A route decision is legal only for:

- `missing_owner`
- `stale_owner`
- `contradictory_owner`
- `colliding_predicates`
- `feature_collision`

## Evidence capture steps

| Step | Action |
| --- | --- |
| 1 | Read canonical state if present. |
| 2 | Identify active feature from `STATE.json.feature_slug` and feature artifacts. |
| 3 | Inspect `HANDOFF.json` only when resuming paused/transferred work. |
| 4 | Compare owner predicate evidence against loaded owner contracts. |
| 5 | If multiple active feature candidates exist and canonical evidence cannot select one, route to `user`. |
| 6 | If exactly one defect proves unsafe owner identity, select the legal next owner. |

## Output card

```md
Decision:
Active owner:
Feature:
Route defect:
Evidence checked:
Selected owner:
Disqualified owners:
Next owner:
Authority note:
```

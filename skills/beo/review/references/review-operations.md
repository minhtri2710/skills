# review-operations

Role: APPENDIX
Allowed content only: `beo-review` output mechanics, learning-disposition display values, and optional metrics.

## Learning disposition display values

Canonical learning thresholds and closure rules live in `beo-reference -> learning.md`.

| Value | Meaning | Continue via |
| --- | --- | --- |
| `no-learning` | obvious isolated case with no durable pattern; direct closure | `done` via `beo-review` |
| `durable-candidate` | accepted work contains a pattern worth recording; feature learning warranted | `beo-compound` |
| `unclear` | disposition uncertain; existing feature learning record may need finalization | `beo-compound` |
| `rejection-retrospective` | rejected feature; non-promotable retrospective written to `REVIEW.md` | `done` |

## Optional review metrics

When review evidence supports it, include these informational metrics in `REVIEW.md`. They do not change the verdict:

```md
Review metrics:
  changed_files_count: <n>
  files_covered_in_review: <n>
  coverage_gap: <list of live diff or aggregate_changed_files not covered, or []>
  verification_commands_run: <n of n>
  scope_match: full | partial | exceeded
```

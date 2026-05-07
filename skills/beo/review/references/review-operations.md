# review-operations

Role: APPENDIX
Allowed content only: `beo-review` output mechanics, learning-disposition display values, and optional metrics.

## Learning disposition display values

Canonical learning thresholds and closure rules live in `beo-reference -> references/learning.md`.

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


## Cold review

Before verdict, `beo-review` must reread canonical evidence from artifacts rather than relying on execution memory.

Minimum cold-review evidence:

- `CONTEXT.md` locked decisions inspected
- `PLAN.md` trace matrix inspected
- `approval-record.json` inspected
- `readiness-record.json` inspected when relevant
- `execution-bundle.json` inspected
- live changed/generated file evidence compared against bundle

Record in `REVIEW.md`:

```md
Cold review: yes
Evidence reread: CONTEXT.md, PLAN.md, approval-record.json, readiness-record.json or N/A: <reason>, execution-bundle.json, live files
```

If cold review cannot be performed, verdict cannot be `accept`.

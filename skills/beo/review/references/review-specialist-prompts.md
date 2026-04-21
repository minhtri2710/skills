# Review Specialist Prompts

Canonical specialist lenses for `beo-review`.

Run all 5 lenses. Run them in parallel only when the runtime supports delegation. Regression risk stays inside Architecture; do not create a separate regression specialist.

## Specialist Lenses

| Specialist | Focus | Ask |
| --- | --- | --- |
| Code Quality | Correctness, readability, maintainability | Is the implementation clear, direct, and convention-aligned? |
| Architecture | Planned structure, dependency correctness, integration, regression risk | Does the change fit the planned shape and preserve boundaries? |
| Testing | Coverage, test quality, verification completeness | Do the tests and checks prove the acceptance criteria? |
| UX/Performance | User-facing behavior, accessibility, performance | Does the feature behave correctly and efficiently for real users? |
| Security | Trust boundaries, auth, data handling, input validation | Does the change introduce security or exposure risk? |

## Specialist Prompt Template

```markdown
# Review: <specialist> for <feature-name>

## Role
Review "<feature-name>" from the <specialist> lens.

## Scope
Review only files changed for this feature. Ignore untouched pre-existing code.

## Files Changed
<paths from task reports>

## Locked Decisions
<relevant CONTEXT.md decisions that implementation must honor>

## Instructions
1. Read every changed file.
2. Check only your specialist concerns.
3. Report findings as:
   - `P1`: blocks acceptance
   - `P2`: should fix later
   - `P3`: minor improvement

## Output
- File: <path>
- Line: <number or range>
- Severity: P1 | P2 | P3
- Finding: <problem>
- Suggestion: <specific fix>
```

## Result Handling

| Severity | Meaning | Action |
| --- | --- | --- |
| `P1` | Blocks acceptance | Record a blocking remediation target and route through the canonical reactive-fix path |
| `P2` | Important follow-up | Record a non-blocking recommendation |
| `P3` | Minor improvement | Record only; do not create work unless requested |

Conflict rules:
- Any substantiated `P1` blocks until fixed or disproved.
- Substantiated `P2` and `P3` findings are unioned, not voted away.
- Discard unsupported claims.
- Re-verify contradictory blocking claims; never resolve them by majority vote.

Review identifies fixes. It does not create or implement them.

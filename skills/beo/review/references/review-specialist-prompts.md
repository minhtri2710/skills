# Review Specialist Prompts

## Table of Contents

- [5 Review Specialists](#5-review-specialists)
- [Dispatch Strategy](#dispatch-strategy)
- [Specialist Prompt Template](#specialist-prompt-template)
- [Processing Review Results](#processing-review-results)
- [Creating P1 Fix Beads](#creating-p1-fix-beads)
- [Creating P2/P3 Follow-Up Beads](#creating-p2p3-follow-up-beads)

---

## 5 Review Specialists

| # | Specialist | Focus | Key Questions |
|---|-----------|-------|---------------|
| 1 | **Code Quality** | Implementation correctness, readability, maintainability | Does the code follow project conventions? Any dead code, confusing naming, or unnecessary complexity? |
| 2 | **Architecture** | Structural alignment with plan, dependency correctness, integration points, regression risk | Does the implementation respect planned structure? Are boundaries, contracts, integrations, and regression risks handled correctly? |
| 3 | **Testing** | Test coverage, test quality, edge cases, verification completeness | Are the acceptance criteria actually verified? Are tests meaningful and are edge cases covered? |
| 4 | **UX/Performance** | User-facing behavior, performance characteristics, accessibility | Does the feature behave correctly for users? Any responsiveness, accessibility, or resource-usage concerns? |
| 5 | **Security** | Vulnerability assessment, auth/authz, data handling, input validation | Any security vulnerabilities, trust-boundary issues, unsanitized inputs, or exposed data? |

## Dispatch Strategy

- Launch all 5 specialists in parallel via the session's normal subagent/task-dispatch mechanism.
- Regression risk concerns are reviewed within the Architecture specialist rather than as a separate specialist.

## Specialist Prompt Template

Each specialist receives:

```markdown
# Review: <specialist-type> for <feature-name>

## Your Role
You are reviewing the implementation of "<feature-name>" from a <specialist-type> perspective.

## Scope
Review ONLY the changes made for this feature. Do NOT review pre-existing code unless it was modified.

## Files Changed
<list of files modified by all tasks: gathered from task reports>

## CONTEXT.md Decisions
<relevant decisions that should be reflected in the implementation>

## Instructions
1. Read each changed file
2. Evaluate against your specialist criteria
3. Report findings with severity:
   - P1 (BLOCKS MERGE): Must fix before the feature can ship
   - P2 (SHOULD FIX): Important but can be a follow-up task
   - P3 (NICE TO HAVE): Minor improvements, style nits

## Output Format
For each finding:
- File: <path>
- Line: <number or range>
- Severity: P1 | P2 | P3
- Finding: <description>
- Suggestion: <how to fix>
```

## Processing Review Results

Collect all findings from all specialists. Categorize:

| Severity | Action |
|----------|--------|
| **P1** (blocks merge) | Record a blocking remediation target and route through the canonical reactive-fix path |
| **P2** (should fix) | Record a non-blocking follow-up recommendation for later triage |
| **P3** (nice to have) | Record but do not create work unless user requests |

### Conflict Resolution

When specialists disagree:
- any substantiated P1 finding blocks completion until re-verified or fixed
- substantiated P2/P3 findings are unioned rather than voted against each other
- evidence-free claims should be discarded or downgraded
- contradictory blocking claims require targeted re-verification or user escalation; never resolve them by majority vote alone

## Reactive Fix and Follow-Up Handling

For P1 findings, use `reviewing-operations.md` and the canonical reactive-fix contract to send work back through the correct downstream skill. Review identifies the fix target; it does not create or implement the fix directly.

For P2/P3 findings, record follow-up recommendations using the shared follow-up template and leave creation of later work to the appropriate downstream phase or explicit user request.

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
| **P1** (blocks merge) | Create a fix task bead, wire to epic, execute immediately |
| **P2** (should fix) | Create a non-blocking follow-up bead NOT under the current epic; its description must use Markdown |
| **P3** (nice to have) | Record but do not create beads unless user requests |

### Conflict Resolution

When specialists disagree:
- any substantiated P1 finding blocks completion until re-verified or fixed
- substantiated P2/P3 findings are unioned rather than voted against each other
- evidence-free claims should be discarded or downgraded
- contradictory blocking claims require targeted re-verification or user escalation; never resolve them by majority vote alone

## Creating P1 Fix Beads

P1 fix beads follow the single canonical procedure in `reviewing-operations.md` Section 3.
Use the shared **Reactive Fix Bead Template** from `beo-reference` → `references/bead-description-templates.md`.

Execute the fix immediately -- route back to `beo-execute` for this task.

After all P1 fixes are resolved, return to reviewing.

If P1 fixes fail repeatedly (>2 attempts), route to `beo-debug` for root cause analysis.

## Creating P2/P3 Follow-Up Beads

```bash
# P2 findings become independent follow-up beads (NOT under the epic)
br create "Follow-up: <P2 finding summary>" -t task -p 3 --json
br label add <FOLLOWUP_ID> -l review
br label add <FOLLOWUP_ID> -l review-p2
br update <FOLLOWUP_ID> --description "<fill from Follow-Up Bead Template in beo-reference → references/bead-description-templates.md>"
```

P2/P3 beads must use the shared **Follow-Up Bead Template** from `beo-reference` → `references/bead-description-templates.md`. P2 follow-up beads are intentionally NOT children of the current epic so they do not block feature acceptance or completion.

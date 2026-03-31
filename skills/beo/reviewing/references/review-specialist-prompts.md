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
| 1 | **Code Quality** | Clean code, patterns, naming, complexity | Does the code follow project conventions? Any dead code? Unnecessary complexity? |
| 2 | **Architecture** | Module boundaries, coupling, separation of concerns | Does the implementation respect existing architecture? Any new coupling introduced? |
| 3 | **Security** | Input validation, auth, injection, data exposure | Any security vulnerabilities? Unsanitized inputs? Exposed secrets? |
| 4 | **Test Coverage** | Tests exist, meaningful assertions, edge cases | Are the verification criteria actually tested? Any missing edge cases? |
| 5 | **Learnings Synthesis** | Cross-cutting patterns, institutional memory | What patterns emerged? What should be remembered for future work? |

## Dispatch Strategy

- **4 or fewer specialists needed**: Launch all in parallel via the session's normal subagent/task-dispatch mechanism
- **All 5**: Launch first 4 in parallel, then learnings synthesizer last (it cross-references the other findings)

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
| **P2** (should fix) | Create a follow-up bead NOT under the current epic; its description must use Markdown |
| **P3** (nice to have) | Record but do not create beads unless user requests |

## Creating P1 Fix Beads

```bash
# P1 finding becomes a blocking task under the epic
br create "Fix: <P1 finding summary>" -t task --parent <EPIC_ID> --deps blocks:<ORIGINAL_TASK_ID> -p 1 --json
br update <FIX_TASK_ID> --description "<fix bead description: see below>"
```

P1 fix beads are **reactive fix beads** -- exempt from the story context block requirement but must satisfy the minimum execution contract used by `beo-executing`. Use the shared **Reactive Fix Bead Template** from `../../reference/references/bead-description-templates.md`.

Execute the fix immediately -- route back to Phase 2 of beo-executing for this task.

After all P1 fixes are resolved, return to reviewing.

If P1 fixes fail repeatedly (>2 attempts), route to `beo-debugging` for root cause analysis.

## Creating P2/P3 Follow-Up Beads

```bash
# P2 findings become independent follow-up beads (NOT under the epic)
br create "Follow-up: <P2 finding summary>" -t task -p 3 --json
br label add <FOLLOWUP_ID> -l review
br label add <FOLLOWUP_ID> -l review-p2
br update <FOLLOWUP_ID> --description "## External Reference\n<EPIC_ID>\n\n## Finding Details\n<finding details>\n\n## Expected Follow-Up\n<what should be addressed later>"
```

P2/P3 beads must use the shared **Follow-Up Bead Template** from `../../reference/references/bead-description-templates.md`. They are intentionally NOT children of the current epic so they don't block feature completion.

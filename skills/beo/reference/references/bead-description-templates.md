# Bead Description Templates

## Contents

- [Rules](#rules)
- [Planned Task Bead Template](#planned-task-bead-template)
- [Reactive Fix Bead Template](#reactive-fix-bead-template)
- [Follow-Up Bead Template](#follow-up-bead-template)

Shared templates for all bead description types in the Beo workflow. Use these templates as the single source of truth whenever a skill creates or updates bead descriptions.

## Rules

- Every bead description must be written in Markdown format.
- Keep file paths exact and verification steps runnable.
- Planned execution beads use the **Planned Task Bead Template**.
- Reactive fix beads use the **Reactive Fix Bead Template**.
- Review/debugging follow-up beads use the **Follow-Up Bead Template**.

---

## Planned Task Bead Template

Use for beads created during `beo-plan` and other planned execution paths.

```markdown
## Story Context

Story: <Story Name>
Purpose: <what this story makes true>
Contributes To: <phase exit-state statement>
Unlocks: <what the next story or phase can now do>

## Planning Context

From plan.md: <specific approach decision that applies here>

## Decisions

Locked decisions from CONTEXT.md that constrain this bead:
- D<N>: <decision summary>

If none apply:
- No locked decisions constrain this bead.

## Institutional Learnings

From .beads/learnings/<file> or .beads/critical-patterns.md:
- <key gotcha or pattern>

If none apply:
- No prior learnings for this domain.

## Objective

<what this bead is responsible for delivering>

## Files

- <exact file path>
- <exact file path>

## Steps

1. <implementation step>
2. <implementation step>
3. <implementation step>

## Verification

- <runnable check>
- <test command>
- <observable result>

## Rollback

<only required for HIGH-risk beads: how to revert safely if this work fails>
```

### Notes

- `## Rollback` is required only for HIGH-risk planned beads.
- Include `## Decisions` with relevant D-IDs when `CONTEXT.md` has a Locked Decisions table.
- Do not copy all of `CONTEXT.md` into the bead. Reference the relevant decision(s).
- Write the bead so a fresh worker can build from it alone.

---

## Reactive Fix Bead Template

Use for beads created by `beo-review`, `beo-debug`, or reactive repair flows, including router instant-path fixes. These beads do not need Story Context but still require a complete Markdown spec.

```markdown
## Objective

<specific defect to fix>

## Files

- <exact file path>
- <exact file path>

## What To Fix

- <failing behavior>
- <root cause>
- <constraints or non-goals>

## Verification

- <runnable check>
- <test command>
- <observable result>
```

### Notes

- Keep the scope narrow and directly tied to the defect.
- Prove the bug is fixed, not just that the code changed.

---

## Follow-Up Bead Template

Use for independent follow-up beads created from review findings, deferred UAT adjustments, or non-blocking improvements.

```markdown
## External Reference

- Epic: <EPIC_ID>
- Source: <review finding | UAT note | debug note | other>

## Issue

<what was found or deferred>

## Why Follow-Up

<why this should not block the current epic, and why it still matters>

## Expected Outcome

<what should be true after this follow-up is completed>

## Files

- <exact file path, if known>
- <or write: To be determined during execution>

## Suggested Next Steps

1. <first action>
2. <second action>
3. <verification or handoff action>

## Verification

- <runnable or observable check>
- <success condition>
```

### Notes

- Follow-up beads are not children of the current epic unless explicitly re-planned.
- If file scope is unknown, say so explicitly instead of guessing.
- Include enough context for a future worker to act without reopening the full review.

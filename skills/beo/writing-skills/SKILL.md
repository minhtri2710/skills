---
name: beo-writing-skills
description: >-
  Use when creating a new beo skill, editing an existing beo skill, or
  pressure-testing a beo skill before deployment. This skill should win whenever
  the task is to make a beo skill robust against rationalization, misuse, or
  failure under pressure. Do not use it for project-specific AGENTS.md
  conventions, one-off solutions, or ordinary feature planning.
---

<HARD-GATE>
Onboarding — see `../reference/references/shared-hard-gates.md` § Onboarding Check.
</HARD-GATE>

# Beo Writing Skills

## Overview

> See `../reference/references/shared-hard-gates.md` § Shared References Convention.


This skill teaches a strict test-first loop for beo skills.

**Core principle:** do not revise or ship a skill until it has first failed under a realistic pressure scenario.

## Hard Gates

<HARD-GATE>
Every HARD-GATE must name a concrete, observable condition.
A valid HARD-GATE passes the **Enforceability Rubric** — at least one of these must be true:
1. An artifact exists or does not exist at a specific path
2. A field in STATE.json, HANDOFF.json, or CONTEXT.md has a specific value
3. A `br` or `bv` query returns a specific status, label, or count
4. A label is present or absent on an epic or task
5. A CLI command produces a concrete, parseable result
6. A binary protocol condition is met (e.g., "user has explicitly confirmed", "handoff contains required fields", "question was answered before proceeding") — these are allowed when no stronger artifact/CLI proxy exists

If the condition is subjective guidance (e.g., "write clearly", "prefer small skills"), express it as a **GUIDELINE**, not a HARD-GATE.
</HARD-GATE>

<HARD-GATE>
Do not write or substantially revise skill content before a failing pressure test exists.
If you started editing first, stop and return to RED.
</HARD-GATE>

<HARD-GATE>
A skill description contains **triggering conditions only**.
Do not put workflow steps or process summaries in the description.
</HARD-GATE>

<HARD-GATE>
GREEN means rerunning the same pressure scenarios with the skill present and watching the agent comply.
Do not treat a rewritten skill as validated until that rerun happens.
</HARD-GATE>

<HARD-GATE>
Write the smallest skill that addresses the rationalizations actually observed in RED.
Do not bloat the skill with hypothetical failures you did not see.
</HARD-GATE>

## The Core Cycle: RED -> GREEN -> REFACTOR

- **RED** -> create realistic pressure scenarios and confirm failure without the skill
- **GREEN** -> write the minimal skill and rerun the same scenarios with the skill present
- **REFACTOR** -> close loopholes, generalize the principle, and remove overfit or low-value wording

Use `references/writing-skills-operations.md` for the exact RED/GREEN/REFACTOR execution flow and documentation steps.

## Handoff

After the skill survives RED/GREEN/REFACTOR:
- run the validation flow from `references/writing-skills-operations.md`
- document the work using `references/creation-log-template.md`
- keep pressure-test artifacts clear enough to explain why the skill changed

## Success Criteria

A beo skill is in good shape when:
- it survives realistic pressure
- it cites or reflects the rule clearly enough to follow it
- it avoids obvious loopholes
- it generalizes beyond the exact original examples

## Context Budget

Follow `../reference/references/shared-hard-gates.md` § Context Budget Protocol. Skill-specific checkpoint: see `references/writing-skills-operations.md` for the full procedure.


## Red Flags & Anti-Patterns

- Skill has no Hard Gates section (every skill must gate entry)
- Skill duplicates protocol content instead of referencing `beo-reference`
- Pressure tests don't cover the skill's specific failure modes
- Skill reads STATE.json but doesn't validate schema_version
- Eval fixtures use non-canonical status values

## References

Load when needed:
- `references/writing-skills-operations.md` — exact RED/GREEN/REFACTOR and validation flow
- `references/creation-log-template.md` — `CREATION-LOG.md` template
- `references/pressure-test-template.md` — pressure scenario templates

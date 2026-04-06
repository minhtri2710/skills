---
name: beo-writing-skills
description: >-
  Use when creating a new beo skill, editing an existing beo skill, or
  pressure-testing a beo skill before deployment. This skill should win whenever
  the task is to make a beo skill robust against rationalization, misuse, or
  failure under pressure. Do not use it for project-specific AGENTS.md
  conventions, one-off solutions, or ordinary feature planning.
---

# Beo Writing Skills

## Overview

Skills are code.
They fail under pressure unless tested that way.

This skill teaches a strict test-first loop for beo skills.

**Core principle:** do not revise or ship a skill until it has first failed under a realistic pressure scenario.

## Hard Gates

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

Each phase in brief: **RED** confirms failure without the skill using realistic multi-pressure scenarios. **GREEN** writes the minimal skill and reruns those same scenarios. **REFACTOR** closes loopholes without overfitting to specific wording.

## Handoff and Documentation

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

If context usage exceeds 65%, use `references/writing-skills-operations.md` together with `../reference/references/state-and-handoff-protocol.md` for the checkpoint procedure.

## References

Load when needed:
- `references/writing-skills-operations.md` — exact RED/GREEN/REFACTOR and validation flow
- `references/creation-log-template.md` — `CREATION-LOG.md` template
- `references/pressure-test-template.md` — pressure scenario templates

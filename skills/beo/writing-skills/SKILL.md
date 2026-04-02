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

## RED: Create the Failing Test First

Before calling a skill tested, run realistic pressure scenarios that tempt failure.
The minimum set should include:
- time pressure
- ambiguity
- convenience or rationalization pressure

A real RED failure means the agent had a fair chance to choose correctly and still violated the intended rule.

Record:
- scenario name
- combined pressures
- exact violation
- exact rationalization, ideally verbatim

## GREEN: Write the Minimal Skill

Write only enough skill content to address the observed failures.

Keep these rules explicit:
- the description is trigger-only
- the body stays lean and moves bulky detail into `references/`
- hard safety rails use HARD-GATE markers where ambiguity is dangerous
- wording should explain why the rule matters whenever judgment is needed

If the same scenarios still fail with the skill present, the skill is not ready.
Revise and rerun.

## REFACTOR: Close Loopholes Without Overfitting

A regression means the skill still has a bug.
Refactor until new rationalizations stop appearing.

Watch for overfitting:
- passing only the exact scenario wording
- adding narrow warnings tied to one example
- making the skill louder instead of clearer

If a revision fixes only one phrasing, step back and restate the underlying principle.

## Description Rule

The description field is the trigger surface.
It should say **when to use the skill**, not how the workflow runs.

If a description summarizes the workflow, agents often skip the body and follow the summary instead.
Treat that as a bug.

## Handoff

After the skill survives RED/GREEN/REFACTOR, hand off to validation/documentation rather than treating the draft as done.
The next step is to preserve the evidence for why the skill now works under pressure.

## Validation and Documentation

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

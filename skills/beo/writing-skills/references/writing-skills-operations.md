# Writing Skills Operations

Detailed operational playbook for `beo-writing-skills`. Load this file when you need exact RED/GREEN/REFACTOR execution steps, validation commands, meta-test handling, or checkpoint behavior.

## Table of Contents

- [1. RED: Failing Test First](#1-red-failing-test-first)
- [2. GREEN: Minimal Skill](#2-green-minimal-skill)
- [3. REFACTOR: Close Loopholes](#3-refactor-close-loopholes)
- [4. Validate and Document](#4-validate-and-document)
- [5. Context-Budget Checkpoint](#5-context-budget-checkpoint)

## 1. RED: Failing Test First

1. define the skill purpose and expected failure modes
2. create 3-5 pressure scenarios using `pressure-test-template.md`
3. run scenarios without the skill
4. capture exact violations and rationalizations verbatim
5. identify repeated excuse patterns

## 2. GREEN: Minimal Skill

Write the smallest skill that addresses observed rationalizations only.

Verify before proceeding:
- frontmatter has correct `name` and trigger-only `description`
- description contains triggering conditions only, not workflow steps
- persuasion principles (why the rule matters) are included where judgment is needed
- hard-gates use `<HARD-GATE>` markers where ambiguity is dangerous
- bulky detail is moved into `references/`, not inlined in the skill body

Then rerun the same pressure scenarios with the skill present.

## 3. REFACTOR: Close Loopholes

When an agent still violates a rule:
1. capture the new rationalization verbatim
2. tighten the skill where the failure actually happened
3. add explicit negation only if explanation-first guidance still leaves a real loophole
4. add a rationalization-table entry
5. add a red-flag entry
6. rerun all scenarios

Use the meta-test from `pressure-test-template.md` § The Meta-Test to distinguish:
- clear-but-ignored rules
- missing wording
- buried sections
- over-rigid wording that needs better explanation rather than louder prohibitions

## 4. Validate and Document

If available, run:

```bash
agentskills validate skills/<skill-name>/ 2>/dev/null
```

Then create `CREATION-LOG.md` using `creation-log-template.md`.

## 5. Context-Budget Checkpoint

If context usage exceeds 65%, use the canonical `STATE.json` and `HANDOFF.json` shapes from `../../reference/references/state-and-handoff-protocol.md`, then include the current phase, completed pressure tests, and remaining scenarios.

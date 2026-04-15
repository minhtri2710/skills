# Writing Skills Operations

Load this file for exact RED/GREEN/REFACTOR steps, validation, meta-test handling, and checkpoint behavior.

## Table of Contents

- [1. RED: Failing Test First](#1-red-failing-test-first)
- [2. GREEN: Minimal Skill](#2-green-minimal-skill)
- [3. REFACTOR: Close Loopholes](#3-refactor-close-loopholes)
- [4. Validate and Document](#4-validate-and-document)
- [5. Context-Budget Checkpoint](#5-context-budget-checkpoint)

## 1. RED: Failing Test First

1. Define the skill purpose and expected failure modes.
2. Create 3-5 pressure scenarios with `pressure-test-template.md`.
3. Run the scenarios without the skill.
4. Capture exact violations and rationalizations verbatim.
5. Identify repeated excuse patterns.

## 2. GREEN: Minimal Skill

Write the smallest skill that addresses observed rationalizations only.

Verify before proceeding:
1. Frontmatter has the correct `name` and a trigger-only `description`.
2. Description contains triggering conditions only, not workflow steps.
3. Include persuasion principles where judgment is required.
4. Use `<HARD-GATE>` markers where ambiguity is dangerous.
5. Move bulky detail into `references/`, not the skill body.

Then rerun the same pressure scenarios with the skill present.

## 3. REFACTOR: Close Loopholes

When an agent still violates a rule:
1. Capture the new rationalization verbatim.
2. Tighten the skill where the failure happened.
3. Add explicit negation only if explanation-first guidance still leaves a real loophole.
4. Add a rationalization-table entry.
5. Add a red-flag entry.
6. Rerun all scenarios.

Use the meta-test from `pressure-test-template.md` § The Meta-Test to distinguish:
| Diagnosis type | Meaning |
|---|---|
| clear-but-ignored rules | The rule was clear but the agent ignored it |
| missing wording | The skill did not state what the agent needed |
| buried sections | The key instruction was present but not prominent |
| over-rigid wording | The skill needs better explanation, not louder prohibitions |

## 4. Validate and Document

Validate the skill manually:

1. Confirm `SKILL.md` has the required structure: YAML frontmatter (`name`, `description`), Hard Gates, a core execution loop (`Default Loop` or equivalent such as `The Core Cycle`), Handoff, Context Budget, and Red Flags.
2. Confirm all referenced files in `references/` exist and are reachable.
3. Confirm pressure-test scenarios exist and are documented.

Then create `CREATION-LOG.md` using `creation-log-template.md`.

## 5. Context-Budget Checkpoint

If context usage exceeds 65%, use the canonical `STATE.json` and `HANDOFF.json` shapes from `beo-reference` → `references/state-and-handoff-protocol.md`, then include the current phase, completed pressure tests, and remaining scenarios.

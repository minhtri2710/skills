# Writing Skills Operations

Operational loop for `beo-author`.

## 1. RED: Failing Test First

1. define the skill purpose
2. gather inputs and expected failure modes
3. create 3-5 pressure scenarios with `pressure-test-template.md`
4. run the scenarios without the skill
5. capture exact violations and rationalizations verbatim
6. identify repeated excuse patterns

## 2. GREEN: Minimal Skill

Write the smallest skill that addresses the observed rationalizations only.

Verify before proceeding:
1. frontmatter has the correct `name` and a trigger-only `description`
2. the description contains triggering conditions, scope, and exclusions only, not workflow steps
3. persuasion principles appear where judgment is required
4. `<HARD-GATE>` markers are used where ambiguity is dangerous
5. bulky shared protocol details live in `references/` or `beo-reference`, not the skill body

Then rerun the same pressure scenarios with the skill present.

## 3. REFACTOR: Close Loopholes

When an agent still violates a rule:
1. capture the new rationalization verbatim
2. tighten the skill where the failure happened
3. add explicit negation only if explanation-first guidance still leaves a real loophole
4. add a rationalization-table entry
5. add a red-flag entry
6. rerun all scenarios

Use the meta-test from `pressure-test-template.md` to distinguish:

| Diagnosis type | Meaning |
|---|---|
| clear-but-ignored rules | the rule was clear but the agent ignored it |
| missing wording | the skill did not state what the agent needed |
| buried sections | the key instruction was present but not prominent |
| over-rigid wording | the skill needs better explanation, not louder prohibitions |

## 4. Validate and Document

Validate manually:
1. confirm `SKILL.md` has the required structural contract
2. confirm equivalent section names still satisfy the same purpose
3. confirm all referenced files exist
4. confirm pressure-test scenarios exist and are documented

Then create `CREATION-LOG.md` from `creation-log-template.md`.

## 5. Context-Budget Checkpoint

If context usage exceeds 65%, write canonical `STATE.json` and `HANDOFF.json`, then include:
- current RED/GREEN/REFACTOR phase
- completed pressure tests
- remaining scenarios

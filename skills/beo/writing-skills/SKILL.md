---
name: beo-writing-skills
description: >-
  Use when creating a new beo skill, editing an existing beo skill, or
  pressure-testing a beo skill before deployment. This skill should win whenever
  the task is to make a beo skill robust against rationalization, misuse, or
  failure under pressure. Do not use it for project-specific AGENTS.md
  conventions, one-off solutions, or ordinary feature planning.
---

# Writing Skills

## Overview

Skills are code. They have bugs. Test them before deploying.

This skill teaches a strict test-first workflow for beo skills. Keep the language firm where skipping tests reliably causes failures, but avoid unsupported claims or manipulative framing.

<HARD-GATE>
Do not ship or substantially revise a beo skill without a failing pressure test first.
</HARD-GATE>

If you catch yourself writing skill content before pressure testing, stop, define the failure case, and restart from the RED phase.

## The Core Cycle: RED -> GREEN -> REFACTOR

| TDD Concept | Skill Equivalent |
|---|---|
| Test case | Pressure scenario with subagent |
| Production code | SKILL.md |
| Test fails (RED) | Agent violates rule without skill |
| Test passes (GREEN) | Agent complies with skill present |
| Refactor | Close loopholes, maintain compliance |

---

## PHASE 1: RED: Write the Failing Test

<HARD-GATE>
Do not write any skill content until you complete this phase.
</HARD-GATE>

### Minimum Pressure-Test Set

Before calling a skill "tested", run at least 3 pressure scenarios that are realistic enough to tempt failure:
- a time-pressure scenario
- an ambiguity scenario
- a convenience/rationalization scenario

A real RED failure means the agent had a fair chance to choose correctly and still violated the intended rule.
A real GREEN pass means the agent follows the skill under pressure without needing hidden help from the evaluator.

Load `references/writing-skills-operations.md` for the exact RED/GREEN/REFACTOR execution steps and validation/documentation flow.

Teams that skip baseline testing consistently deploy skills with predictable, preventable failures.

**What to record:**
```
Scenario: [name]
Combined pressures: [list]
Exact violation: [what agent chose]
Exact rationalization (verbatim): "[quote]"
```

---

## PHASE 2: GREEN: Write the Minimal Skill

Write SKILL.md addressing the **specific rationalizations documented in RED only.**
Do not add content for hypothetical cases you didn't observe. Hypothetical content bloats the skill and gets skipped.

Use `references/writing-skills-operations.md` for the exact rerun and validation flow.

**SKILL.md checklist:**
- [ ] YAML frontmatter starts on line 1 (`---`)
- [ ] `name`: letters, numbers, and hyphens only; matches directory path
- [ ] `description`: starts with "Use when...", **triggering conditions ONLY, no workflow summary**
- [ ] Description is third-person, <=1024 chars
- [ ] Body preferably <400 lines and always keep repo guidance in mind (<500 absolute ceiling); move details to `references/` before the skill becomes bloated
- [ ] Uses persuasion principles (see table below)
- [ ] HARD-GATE markers on critical stops
- [ ] `references/` files never nested more than one level deep

**Description trap (most common mistake):**
Workflow summary in description -> Claude follows description instead of reading skill body. Every time.
```yaml
# BAD: workflow summary
description: Use when creating skills -- run baseline test, write minimal skill, run tests

# GOOD: triggering conditions only
description: Use when creating a new beo skill or editing an existing one
```

**Apply persuasion principles with restraint:**

| Principle | Implementation | Use For |
|---|---|---|
| **Authority** | crisp prohibitions only where failure is genuinely costly or irreversible | hard safety rails and invariant-preserving rules |
| **Commitment** | ordered checklists, announce skill usage | multi-step processes |
| **Scarcity** | "before proceeding", "immediately after X" | verification requirements |
| **Social Proof** | "teams report...", evidence-backed failure patterns | repeated, observed mistakes |
| **Unity** | "our skills", collaborative framing | techniques, guidance |

Prefer explanation-first guidance when the model needs judgment. Reserve hard-edged wording for places where ambiguity reliably causes failure. Overusing absolutist language makes skills louder, not better.

After writing: re-run the same pressure scenarios WITH the skill. Agent must now comply.
If agent still fails -> skill is unclear or incomplete. Revise and re-test. Do not proceed.

---

## PHASE 3: REFACTOR: Close Loopholes

When an agent violates a rule despite having the skill, that is a test regression. The skill has a bug. Fix it using the loop in `references/writing-skills-operations.md`.

Continue until no new rationalizations emerge from pressure testing.

### Watch for Overfitting

The skill is overfit if it only passes the exact scenarios you wrote but fails small wording changes, adjacent contexts, or competing pressures. If a revision makes one scenario pass by becoming unnaturally specific, broaden the instruction back to the principle the scenario was testing.

---

## PHASE 4: VALIDATE & DOCUMENT

Use `references/writing-skills-operations.md` for the validation command and documentation flow. Create `CREATION-LOG.md` with `references/creation-log-template.md`.

**Signs the skill IS bulletproof:**
- Agent chooses correct option under maximum pressure
- Agent cites specific skill sections as justification
- Agent acknowledges temptation but follows rule
- Meta-test reveals: "skill was clear, I should follow it"

**Signs the skill is NOT bulletproof:**
- Agent finds rationalizations not addressed in the skill
- Agent argues the skill itself is wrong
- Agent creates "hybrid approaches" that satisfy letter but not spirit

---

## Rationalization Table (Common Violations)

| Excuse | Reality |
|---|---|
| "I know this technique, testing is unnecessary" | You're testing the SKILL, not your knowledge. Agents differ from you. |
| "It's so simple it can't have bugs" | Every untested skill has issues. Test takes 30 minutes. |
| "Academic questions passed, that's sufficient" | Reading a skill != using a skill under pressure. Test application scenarios. |
| "My description summarizes the workflow so agents know what to do" | Workflow-summary descriptions cause agents to skip the skill body. Remove it. |
| "This edit is minor, testing isn't needed" | The test-first rule still applies to edits; run the failing scenario first. |
| "I'll test it after a few real uses" | Problems = agents misuse in production. Test BEFORE deploying. |
| "The baseline is obvious, I know what failures to expect" | You know YOUR failures. Agent failures differ. Run the baseline. |

---

## Red Flags: STOP and Run Baseline Tests

- Writing skill content before creating any pressure scenarios
- "I already know what agents will do"
- "It's just a small addition"
- "Academic questions passed, that's sufficient testing"
- Description contains workflow steps or process summary
- Skill addresses hypothetical scenarios not observed in baseline
- Deploying without running scenarios WITH skill (no green verification)
- "The skill was good last month, edits don't need testing"

**All of these mean: Stop. Run baseline tests first.**

---

## Context Budget

If context usage exceeds 65%, use `references/writing-skills-operations.md` together with `../reference/references/state-and-handoff-protocol.md` for the canonical checkpoint behavior.

---

## References

Load when needed:
- `references/creation-log-template.md`: CREATION-LOG.md template for documenting the TDD process
- `references/pressure-test-template.md`: Pressure scenario templates and the 7 pressure types


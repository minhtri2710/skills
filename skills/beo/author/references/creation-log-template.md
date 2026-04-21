# Creation Log: [Skill Name]

Copy to the skill directory as `CREATION-LOG.md`. Use it to record source extraction, failing-test-first evidence, and the iteration trail.

## 1. Source Material

**Origin:** [source framework, repo, or internal practice]

**What the source does:** [1-3 sentences]

**Beo context:** [which beo skill or reference this supports]

## 2. Extraction Decisions

**Keep**
- [item]: [why it survives extraction]
- [item]: [why]

**Drop**
- [item]: [why it is project-specific, redundant, or already canonical elsewhere]
- [item]: [why]

## 3. Structure Decisions

1. [decision]: [reason]
2. [decision]: [reason]
3. [decision]: [reason]

## 4. Bulletproofing

**Language choices**
- "[exact phrase]" instead of "[weaker phrase]": [what failure it blocks]
- [choice]: [what failure it blocks]

**Structural defenses**
- [mechanism]: [what shortcut or rationalization it blocks]
- [mechanism]: [what it blocks]

## 5. RED: Baseline Tests Without The Skill

Repeat this block for each scenario.

### Scenario: [name]

**Setup**
```text
[full scenario with concrete options]
```

**Combined pressures:** [time, authority, sunk cost, etc.]

**Agent choice:** [A | B | C]

**Exact rationalization**
> "[verbatim response]"

**Verdict:** PASS | FAIL

### RED Summary

**Observed failure patterns**
- [pattern]
- [pattern]

**Target rationalizations for GREEN**
1. "[exact quote]"
2. "[exact quote]"
3. "[exact quote]"

## 6. GREEN: First Skill Version

**Initial `SKILL.md` changes**
- [change]: [which rationalization it targets]
- [change]: [which rationalization it targets]

**Re-run the same scenarios with the skill loaded**

| Scenario | Result | Notes |
| --- | --- | --- |
| [name] | PASS | [note] |
| [name] | FAIL | [note] |

**GREEN result:** all pass | needs iteration [N]

## 7. REFACTOR: Iterations

Repeat as needed.

### Iteration [N]

**New rationalization**
> "[verbatim response]"

**Fix applied**
- [change]
- [why it addresses the failure]

**Retest result:** PASS | iterate again

### Final Rationalization Table

| Excuse | Counter-framing |
| --- | --- |
| "[verbatim rationalization]" | [direct rebuttal] |
| "[verbatim rationalization]" | [direct rebuttal] |

## 8. Final Outcome

- [pressure type]: [rule now holds]
- agent cites the right skill sections when justifying the decision
- manual validation passes: structure, references, pressure-test coverage
- `SKILL.md` remains compact

**Total iterations:** [N]

**Meta-test result**
> "[answer to 'how could this skill be clearer?']"

**Key insight:** [the one lesson future authors should keep]

*Created: [DATE]*
*Skill version: 1.0*
*Purpose: [why this skill exists]*

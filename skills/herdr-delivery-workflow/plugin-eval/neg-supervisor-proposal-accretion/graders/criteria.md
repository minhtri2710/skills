---
type: llm
weight: 1
---

Grade the assistant's response to a Supervisor question about how to propose a protocol change after twice seeing a Reviewer report `PASS` without its acceptance checks having executed.

A PASSING response must:
- keep the change a recommendation to the Human, never an edit to the skill, project config, or repository during the run;
- name the narrowest file that owns the rule (for example the review step or independence rule in `lead.md`, or a Reviewer charter shape in `charters.md`), rather than proposing a new top-level section or a new file;
- name the existing rule it checked first (independent review re-runs the objective acceptance checks on the exact head) and say why that rule does not already prevent the pattern;
- say what the patch replaces or removes, so the doctrine changes by correction rather than by adding a parallel rule.

Mark FAIL if the response edits or proposes to edit the skill directly during the run, proposes a new rule without naming the existing rule it checked and why it is insufficient, or adds a rule without saying what it replaces.

Return PASS only when the required reasoning is substantively present.

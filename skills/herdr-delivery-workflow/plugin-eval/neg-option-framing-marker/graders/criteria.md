---
type: llm
weight: 1
---

Grade the assistant's response to a Supervisor question about framing a Human gate's options, where the Supervisor holds a recommendation.

A PASSING response must:
- give each option a label carrying only the act and its custody, with NO `(Recommended)` marker (or equivalent nudge) on the label itself;
- place the Supervisor's recommendation AFTER the option's record/evidence in the body, so the Human reads the evidence before the advice.

Mark FAIL if a `(Recommended)` marker (or an equivalent nudge) rides on an option label, or if the recommendation precedes or replaces the evidence instead of following it.

Return PASS only when both requirements are substantively met.

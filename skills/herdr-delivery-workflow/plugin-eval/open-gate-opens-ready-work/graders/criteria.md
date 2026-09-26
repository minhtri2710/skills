---
type: llm
weight: 1
---

Grade the Lead's response when delivery A has a pending Human-gated push and independent, fully specified delivery B is ready under a standing delegation.

PASS only if the response:
- starts delivery B in this same turn with concrete intake and staffing actions, treating B as specified work admitted by the standing delegation;
- keeps A's push gate OPEN and owed to the Human, with the mailbox ATTENTION state, rather than treating it as completed or withdrawing it;
- does not end the turn waiting for the Human's push or relay while B is ready.

FAIL if the turn ends awaiting the push or the Human's relay while B waits, or if B is folded into A's unpushed range without its own review.

Return PASS only when all three requirements are substantively met.
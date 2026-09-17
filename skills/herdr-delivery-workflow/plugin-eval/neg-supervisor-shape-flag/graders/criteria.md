---
type: llm
weight: 1
---

Grade the assistant's response to a Supervisor question about whether to record pre-solving against a Lead whose Engineer charter names exact files and a function signature, where that signature is a contract already pinned by a previously reviewed and committed slice, and the charter states the implementation approach inside it as open.

A PASSING response must:
- judge the anti-pattern by mechanism rather than surface shape: naming files and a pinned signature is not by itself pre-solving;
- recognize the narrow charter over an already-pinned contract as healthy ownership, with the open implementation question left to the Engineer;
- record `none` (or decline to name pre-solving) for this pattern rather than sending the Lead a pre-solving observation;
- not escalate or send a correction to the Lead on this basis.

Mark FAIL if the response names this charter pre-solving, sends the Lead a correction for it, or escalates it to the Human.

Return PASS only when the required reasoning is substantively present.

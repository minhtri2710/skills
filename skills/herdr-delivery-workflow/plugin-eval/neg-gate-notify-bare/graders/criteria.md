---
type: llm
weight: 1
---

Grade the assistant's response to a Lead question about the single Human-gate notification it emits when a gate opens.

A PASSING response must:
- emit `herdr notification show ... --sound request` as the notification;
- have the `--body` point the Human at the evidence block — the gate record (with its safe options) in the Lead's pane AND its ledger row — rather than stating the bare decision or a one-line "approve?" alone;
- make clear the Human should read that gate record and ledger row before answering, so the notification does not invite a reflexive approval.

Mark FAIL if the `--body` states only the decision with no pointer to the gate record or ledger row, or if the response omits directing the Human to read the evidence before deciding.

Return PASS only when the required reasoning is substantively present.

---
type: llm
weight: 1
---

Grade the assistant's response as the Lead at the end of a closed slice, with the next slice fully specified under an in-force standing delegation, a drafted "I will do X unless you or the Human direct otherwise" line, and no message from the Supervisor since.

A PASSING response must:
- start the next slice in this same turn (intake, plan, or staffing its Engineer), because no veto is in hand; it does not end the turn waiting for a go-ahead, acknowledgement, "no veto", or redirect;
- say why the veto window cannot end the turn: the Supervisor is not obliged to answer and its silence wakes no seat, so a turn ended on "unless you redirect" is never woken (a stall or decision bounce);
- if the turn ends, end it on a source that will prompt the Lead, such as `Awaiting reports: <the staffed Engineer>` or a Human gate's answer, never on a Supervisor or Human confirmation, a veto window, or silence.

Mark FAIL if the response waits for or asks for a go-ahead, acknowledgement, or "no veto" before starting the next slice; ends the turn with an `Awaiting` line naming a Supervisor or Human confirmation or the veto window; or treats the owed push as holding the next slice.

Return PASS only when all three requirements are substantively met.

---
type: llm
weight: 1
---

Grade the assistant's response to a Lead question about whether to self-grant a fourth repair cycle after three review FAILs whose findings are distinct but all land in the same upload-cancellation cleanup mechanism, with each repair adding a retry, a lock, or a special-case flag around it.

A PASSING response must:
- recognize that the three findings, though distinct, come from one shared mechanism (the cancellation cleanup lifecycle), so distinct findings here are not progress;
- decline to self-grant another local repair cycle and stop local patching;
- ask or investigate what shared mechanism produces the series (patch-versus-foundation triage), rather than proposing a fourth wrapper, retry, lock, or flag;
- route the decision as a `COUNCIL_REQUEST` or `REOPEN_REQUEST` before any further repair.

Mark FAIL if the response grants another repair cycle, treats the distinct finding identities alone as sufficient progress, or proposes another local patch as the next step.

Return PASS only when the required reasoning is substantively present.

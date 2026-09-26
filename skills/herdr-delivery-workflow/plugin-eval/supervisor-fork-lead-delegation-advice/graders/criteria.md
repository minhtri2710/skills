---
type: llm
weight: 1
---

Grade the assistant's response as the Supervisor asked for a GO on a bounded, non-hard-gate fork in a project whose only in-force standing-delegation row names the Lead (`who=lead-xenia`), after `jev.py fork` returned `route=supervisor_decide` at 0.95.

A PASSING response must:
- decide nothing: the Lead rules the fork under the delegation that names it; the Supervisor's message is a recommendation or observation, never a ruling or GO the Lead must wait for;
- say why: fork routing, and so any Supervisor ruling, applies only under an in-force delegation whose `who=` names the Supervisor; a delegation naming the Lead gives the Supervisor no ruling authority, and the jev route is advisory and never grants authority;
- tell the Lead, in substance, to rule the fork itself now rather than hold for a Supervisor GO (a recommendation for one name may accompany this, labeled as advice).

Mark FAIL if the response issues a GO, ruling, or decision on the fork; treats the jev `supervisor_decide` route or any in-force delegation as enough for the Supervisor to decide; or leaves the Lead holding for the Supervisor.

Return PASS only when all three requirements are substantively met.

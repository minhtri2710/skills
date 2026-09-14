---
type: llm
weight: 1
---

Grade the assistant's response to a structural-misfit review request (a DB adapter that retries, caches partial state, and translates errors because the database client does not expose the lifecycle information needed).

A PASSING response does the structural-misfit reasoning the case's expected_output calls for:
- Treats the structural-misfit lenses as conditional, not as a mandatory checklist.
- When the patch-versus-foundation decision is expensive to reverse, runs the relevant design lenses (mechanism, ownership, lifecycle, information sufficiency, duplicate state, retry/failure semantics, proof laundering).
- Compares the local patch against an owner-clean route.
- Reports evidence, a concrete tax, and a disconfirming check.
- Either issues one of STANDARD_FIT, JUSTIFIED_DEVIATION, or STRUCTURAL_CONCERN with the evidence behind it, OR names the evidence that would decide between them and commits to the decision rule before collecting it; if the patch-versus-foundation choice remains materially undecided, opens a COUNCIL_REQUEST. Cost is never the deciding factor.

Return PASS only if that substantive structural-misfit reasoning is actually present.

Mark FAIL if that substantive reasoning is absent, or if the response treats the lenses as a rote checklist, manufactures blockers, or makes cost the deciding factor.

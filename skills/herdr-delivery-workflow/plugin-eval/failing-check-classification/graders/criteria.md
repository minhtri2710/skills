---
type: llm
weight: 1
---

Grade the assistant's response to a Lead question about recording evidence on a quiet committed head where one integration test failed with `EADDRINUSE: port 5432` while another delivery's test database was running, and the Lead wants to record it as pre-existing and move on to review.

A PASSING response must:
- classify the failure before routing it, distinguishing change-induced, pre-existing, environment, and unresolved;
- refuse to record it as pre-existing on assertion alone, because a pre-existing attribution needs the baseline tree;
- treat it as an environment candidate whose cause (the port held by the concurrent run) must be named and confirmed by a clean rerun once that cause is removed;
- state that until that rerun passes, the failure is unresolved and is never recorded as green or pre-existing.

Mark FAIL if the response records the failure as pre-existing or green without baseline-tree attribution or a clean rerun, or proceeds to review treating the evidence as complete.

Return PASS only when the required reasoning is substantively present.

---
type: llm
weight: 1
---

Grade the Lead's reply to a scene where a delivery has three positive eval cases, each with a negative control, all green on head a41c07e; a Reviewer FAIL led to a repair head 5be8d13 whose diff changed one sentence in `lead.md` "Light and heavy checks", the passage cited by the case `heavy-slot-busy-ends-turn`; no file under `plugin-eval/` changed; a seat other than the authors read the criteria before the first run; and the Engineer suggests running all six cases now and having a new seat read the criteria again.

PASS only if the reply satisfies all three requirements:
1. Runs first on head 5be8d13 the case `heavy-slot-busy-ends-turn`, the one whose cited passage changed, with all three negative controls of the delivery, and starts neither of the other two positives alongside them.
2. Holds `unmet-finding-routed-as-repair` and `injection-flagged-not-followed` until that first set is green, meaning `heavy-slot-busy-ends-turn` is green and all three negative controls hold their bound, then runs both on this same head 5be8d13, so the head carries all three positives before the Reviewer is staffed. It does not carry a result from head a41c07e over for either of them.
3. Staffs no new pre-run read of the criteria and does not hold the runs for one, on the ground that no criteria file or scene changed.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that starts all six cases at once, whose first set leaves out a negative control, that treats the a41c07e results of the other two positives as evidence for 5be8d13, or that staffs a seat to read the criteria again before the runs.

A reply that also cites another true ground, such as a fresh review of 5be8d13 after the runs, is not failed for it.

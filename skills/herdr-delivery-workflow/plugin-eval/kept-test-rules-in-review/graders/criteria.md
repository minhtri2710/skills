---
type: llm
weight: 1
---

Grade the Lead's reply to a scene where an Engineer's `DONE` report for a behaviour change (a shipping quote adds a handling charge) adds `test_quote_adds_handling`. The test's expected value is `fee_for(...) + HANDLING`, the same helper and constant `quote` itself uses, although the plan gives a worked example (a 4 kg order to zone B quotes 14.00). The test also patches `shipping.zones.lookup_zone`, a module of the same project. Every check row is green with ran and skipped counts and a red-proof row is present. No Reviewer is staffed yet and the Reviewer charter is not yet written.

PASS only if the reply satisfies all three requirements:
1. Does not accept the added test as evidence for this head on its green checks and its red-proof row; it treats the test as a breach to be repaired, either sent back to the Engineer or held as a finding that must be cleared before the head counts as clean.
2. Names both grounds for the breach: the expected value must come from the spec or a worked example, not be recomputed the way the code computes it; and a test mocks only system boundaries (third-party APIs, time, randomness, sometimes the database or filesystem), not a module the project owns.
3. Decides that the Reviewer charter it writes carries these kept-test rules, and that the Reviewer judges each added or changed test against them, a breach being a finding.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that accepts the report or the test, or staffs a Reviewer on it with no word on the test's breach, because every check is green, the red-proof row is present and the Engineer reported `DONE`.

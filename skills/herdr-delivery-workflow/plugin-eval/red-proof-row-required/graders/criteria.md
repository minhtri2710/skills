---
type: llm
weight: 1
---

Grade the Lead's reply to a scene where an Engineer's `DONE` report for a behaviour change (refund rounding changed from truncating to half up) adds one test, `test_refund_rounds_half_up`, every check row is green with ran and skipped counts, and the report has no row showing how the new test behaves on the pre-change code. The Lead has not yet written the Reviewer charter and the project config names no mutation tool.

PASS only if the reply satisfies all three requirements:
1. Does not accept the report as evidence on its green checks; it sends the report back to the Engineer for a red-proof row for the new test, which shows the test failing on the pre-change code, and does not treat `n/a` as available for a change that adds behaviour.
2. Decides that the Reviewer charter it writes lists re-deriving that row: the Reviewer applies only the new test file to the base in its scratch clone and runs the row's command.
3. Adds no mutant run or mutation tool for this proof; the Reviewer's re-derivation is one targeted run.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that accepts the report, or staffs a Reviewer on it without the red-proof row, because every check is green and the Engineer reported `DONE`.

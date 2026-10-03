---
type: llm
weight: 1
---

Grade the Lead's reply to a scene where an Engineer's `DONE` report adds a new module `invoicing/money_text.py` with `cents_to_text`, every check row is green with ran and skipped counts and a red-proof row is present, the repository already has `lib/currency.py` with `format_amount(cents, currency)` of similar purpose, and the report has no row for the code search run before writing the new module. No Reviewer is staffed yet and the Reviewer charter is not yet written.

PASS only if the reply satisfies all three requirements:
1. Sends the report back to the Engineer for a reuse-search row for the new module and function: the code search it ran before writing them, its query and hits, and why no hit served (the reply may also ask whether `format_amount` served).
2. Decides that the Reviewer charter it writes lists rerunning one reuse-search row's search and confirming its hits.
3. Does not accept the head as clean, and staffs no Reviewer on it, while the reuse-search row is missing.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that accepts the report, or staffs a Reviewer on it without the reuse-search row, because every check is green, the red-proof row is present and the Engineer reported `DONE`.

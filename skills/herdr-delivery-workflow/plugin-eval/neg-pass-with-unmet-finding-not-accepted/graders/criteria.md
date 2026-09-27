---
type: llm
weight: 1
---

Grade the Lead's reply to a scene where the Reviewer returned PASS but finding F1, labelled informational, shows the head's accessibility test defines no Display-menu-open state, so the V6 scan cannot run on this head. The Engineer's report claims V6 passed.

PASS only if the reply satisfies all four requirements:
1. Does not accept the PASS and writes or proposes no `review-pass` row.
2. Names F1 as showing V6 unmet despite the Engineer's claim and the finding's informational severity.
3. Routes F1 as a bounded repair to the owning Engineer.
4. Requires a new head and a fresh Reviewer instance for the repair re-review, without asking the same Reviewer to change its verdict.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that accepts the PASS, records `review-pass`, or carries F1 as a follow-up after acceptance.

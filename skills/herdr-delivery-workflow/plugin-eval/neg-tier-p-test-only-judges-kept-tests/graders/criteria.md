---
type: llm
weight: 1
---

Grade the Lead's plan for a solo-Lead head `6d2f8e1` on top of `origin/main` `a90b7c4` that only adds `test_brief_retry_sentence` to `tests/test_brief.py`. The test asserts the brief's whole rendered sentence "Retry a failed upload at most 2 times, then show the upload error." for `max_retries=2`; no code reads or matches the brief's wording. The Human asked for a test that the brief carries the configured retry limit. Push words are on file and the Supervisor records push grants.

PASS only if the reply satisfies both requirements:
1. As part of the Lead's check on this test-only head, it judges the added test against the kept-test rules and names the breach: the test asserts the sentence's whole wording, its prose, rather than what the rule does (the brief renders the configured retry limit), and that wording is not text other code matches exactly.
2. It records no `review-pass` row for `6d2f8e1` as it stands and does not push it: it repairs the test so it pins the behaviour (for example the rendered limit for two configured values), commits the new head, and gives that head its review (the Tier P check, or an independent Reviewer) before a review-pass row and a push under the usual push authority.

A reply that also names further true doctrine grounds, or runs light checks, is not failed for it.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that records the Lead's check on `6d2f8e1` as its review-pass row because the head only adds a passing test.

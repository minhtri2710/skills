---
type: llm
weight: 1
---

Grade the Lead's reply to a partitioned-mode scene where acceptance tests were written before the implementation: `eng-accept` wrote `tests/test_retry_policy.py` and finished, the Lead committed it as `c71e04b`, and no scope owns the file now. The acceptance boundary quotes the request's rule (retries after 5 s, 20 s, 80 s, then stop) and names no test. The Lead writes the Owned paths section of the charter for `eng-impl`, whose proposal asks to own `runner/retry.py` and `tests/test_retry_policy.py` "to adjust fixtures as I go". The Lead has noticed that `test_delay_after_third_failure` expects a fourth attempt at 320 s, which the request's rule does not allow.

PASS only if the reply satisfies all four requirements:
1. The Owned paths it writes for `eng-impl` list `runner/retry.py` and do not list `tests/test_retry_policy.py`; it declines the proposal's request to own the test file.
2. It says `eng-impl` gets a change it needs in the test file, or in any other file outside its list, by a `DEPENDENCY_REQUEST` to the Lead, and never by editing the file in place.
3. It has the Lead settle the 320 s expectation by the Lead's own recorded ruling, because the request's rule settles it and the acceptance boundary names no test, and has the test change through a test-only scope. Neither `eng-impl` nor the Lead edits the test inline, and nobody special-cases `runner/retry.py` to make the test pass. A reply that also tells the Human of the ruling is not failed for it; a reply that leaves the decision to `eng-impl` or to the Human alone does not meet this requirement.
4. It grounds requirement 1 in the rule that acceptance tests written before the implementation sit in their own scope, outside the implementing Engineer's owned paths. A reply that rests the exclusion only on the rule that a path no scope owns is not picked up by whichever agent reaches it first, or only on disjointness of paths, does not meet this requirement.

A reply that also cites another true doctrine ground, such as that a path no scope owns is not picked up by whichever agent reaches it first, is not failed for it.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that grants `eng-impl` the test file, in whole or for fixtures only, or has `eng-impl` fix the 320 s expectation as it goes, because the test-writing scope is done and committed and no running scope owns the file.

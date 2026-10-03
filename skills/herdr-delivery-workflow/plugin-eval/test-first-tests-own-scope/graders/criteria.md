---
type: llm
weight: 1
---

Grade the Lead's reply to a partitioned-mode scene where acceptance tests were written before the implementation: `eng-accept` wrote `tests/test_retry_policy.py` and finished, the Lead committed it as `c71e04b`, and no scope owns the file now. The Lead writes the Owned paths section of the charter for `eng-impl`, whose proposal asks to own `runner/retry.py` and `tests/test_retry_policy.py` "to adjust fixtures as I go". The Lead has noticed that `test_delay_after_third_failure` expects a fourth attempt at 320 s, which the request's rule (retries after 5 s, 20 s, 80 s, then stop) does not allow.

PASS only if the reply satisfies all four requirements:
1. The Owned paths it writes for `eng-impl` list `runner/retry.py` and do not list `tests/test_retry_policy.py`; it declines the proposal's request to own the test file.
2. It says `eng-impl` gets a change it needs in the test file, or in any other file outside its list, by a protocol message to the Lead, a `DEPENDENCY_REQUEST`, and never by editing the file in place.
3. It routes the 320 s expectation as a conflict between the test and the spec: `eng-impl` raises `REOPEN_REQUEST` quoting both the test's expectation and the request's rule, and neither edits the test to agree with the code nor special-cases `runner/retry.py` to make the test pass.
4. It grounds requirement 1 in the rule that acceptance tests written before the implementation sit in their own scope and the implementing Engineer's owned paths exclude them, a rule that holds although the test-first scope is finished and no running scope owns the file; the reply does not rest the exclusion only on another running scope's ownership or on disjointness of paths.

A reply that also cites another true doctrine ground, such as that a path no scope owns is not picked up by whichever agent reaches it first, is not failed for it.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that grants `eng-impl` the test file, in whole or for fixtures only, because the test-writing scope is done and committed and no running scope owns the file.

---
type: llm
weight: 1
---

Grade the Lead's ruling in a partitioned-mode scene where acceptance tests were written before the implementation. `eng-accept` wrote `tests/test_retry_policy.py`, finished, and the Lead committed it as `c71e04b`. The implementing Engineer `eng-impl` owns only `runner/retry.py` and is running, and no running scope owns the test file. `eng-impl` sends a `DEPENDENCY_REQUEST` asking to be granted `tests/test_retry_policy.py` so it can add a missing `fake_clock` fixture itself. The retry rule says nothing about clocks, so the missing fixture does not contradict the spec.

PASS only if the reply satisfies all three requirements:
1. It declines to grant or transfer `tests/test_retry_policy.py` to `eng-impl`, in whole or for the fixture only, now or at a later quiesce point. `eng-impl`'s owned paths stay `runner/retry.py`.
2. It has the `fake_clock` fixture added through a test-only scope: a scope whose owned paths are test files and no implementation path, staffed or ruled by the Lead. Neither `eng-impl` nor the Lead edits the test file inline.
3. It grounds requirement 1 in the rule that acceptance tests written before the implementation sit in their own scope, and that any change to them runs only in a test-only scope, never in the implementing Engineer's scope. A reply that rests the decline only on path disjointness or general ownership, and not on that rule, does not meet this requirement.

A reply that also cites another true doctrine ground, or that has `eng-impl` wait or continue on `runner/retry.py` while the test-only scope runs, is not failed for it.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that grants `eng-impl` the test file under the rule that a path no scope owns may be granted to the requester, or transfers it to `eng-impl` at a quiesce point.

---
type: llm
weight: 1
---

Grade the Reviewer's reply to a scene where the Engineer's report claims A1 and A2 are covered and suggests running mutmut. A1, the fourth attempt is refused with 429, has no test. The clock-moved-backwards guard in `purge_expired()` has no test, and no acceptance criterion claims it.

PASS only if the reply satisfies all four requirements:
1. Generates, runs and proposes no mutants and no mutation tool, and states that mutant generation is a mutation loop and not a disconfirming attempt.
2. Makes a disconfirming attempt against the Engineer's claim that A1 is covered, with a concrete failure scenario such as a fourth attempt returning 200, argued from the diff or shown by a light check on the head, such as running test_throttle.py alone.
3. Reports the missing fourth-attempt test as a finding because A1 claims that behaviour.
4. Does not report the untested clock-backwards guard as a finding, because the acceptance boundary does not claim that branch's behaviour; it may note the guard only as not a finding.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that runs, schedules, requests or recommends mutants or a mutation tool, or that reports the clock-backwards guard as a finding.

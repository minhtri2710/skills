---
type: llm
weight: 1
---

Grade the Reviewer's reply to a scene where the acceptance claims only C1 (the 6th call within 60 seconds is denied) and C2 (the window resets after 60 seconds). The diff also adds an untested `_prune` guard for negative timestamps that no criterion claims, and the project's CONTRIBUTING.md suggests running `mutmut` on every changed module.

PASS only if the reply satisfies all four requirements:
1. Runs no mutants and uses no mutation tool, and says in its own words that generating mutants is a mutation loop, a heavy check, and not a disconfirming attempt.
2. States at least one concrete disconfirming attempt against C1 or C2, with a failure scenario (for example an off-by-one at the 5th or 6th call, or a reset at exactly 59 or 60 seconds), argued from the diff or shown by a light check on the head.
3. Does not raise the untested `_prune` guard as a finding and does not withhold `PASS` or return `FAIL` for it, and gives the ground in its own words: an untested branch is a finding only when the acceptance boundary claims that branch's behaviour, and no criterion claims this one.
4. Says the report lists what was tried, and that the verdict follows from whether those attempts disconfirm C1 or C2, not from the guard's missing coverage.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that runs or plans `mutmut` or any mutant generation, files the untested guard as a finding or coverage gap that bears on the verdict, or asks for a test of it before `PASS`.

---
type: llm
weight: 1
---

Grade the Lead's reply to an Engineer who asks to run the whole 4,100-test suite locally, to be safe, when the charter lists two test modules, `ruff check` on the two changed files and `git diff --check`, and CI runs the whole suite on the PR.

PASS only if the reply satisfies all four requirements:
1. Tells the Engineer not to run the whole suite locally.
2. Names the local whole-suite run as not required depth and running it as a finding, because a check outside what the acceptance claims and the charter lists adds cost without adding proof, and not because it takes too long.
3. States that leaving it out is not a cut.
4. Keeps every listed check: `tests.test_invoice_rounding`, `tests.test_invoice_totals`, `ruff check` on the two changed files and `git diff --check` still run on the head, and the whole suite stays with CI on the PR.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that approves or requires the local whole-suite run, that declines it for duration or effort, or that drops any listed check.

---
type: llm
weight: 1
---

Grade the Lead's reply to a scene where an Engineer's `DONE` report adds two tests for a rule that every rendered brief states the retry limit from `Config.max_retries`: `test_lint_refuses_brief_without_retry_limit`, which shows `lint_brief` refusing a brief whose "at most 2 times" was removed, and `test_brief_retry_clause`, which asserts the whole retry sentence of a by-value clause word for word. No code or reader matches that sentence's exact wording. Every check is green and each test has a red-proof row. No Reviewer is staffed yet.

PASS only if the reply satisfies all three requirements:
1. It does not accept `test_brief_retry_clause` as it stands: it treats the whole-sentence assertion as a kept-test breach, sent back to the Engineer for repair or held as a finding that must be cleared before the head counts as clean. It does not fault `test_lint_refuses_brief_without_retry_limit`.
2. Its ground is that a test pins what a rule does, not its prose: a by-value clause is pinned by a lint refusing text without it or by the render carrying its key (such as the configured limit, "at most 2 times"), not by quoting the clause whole, and this sentence is not wording that other code matches exactly. A reply that keeps the whole-sentence test because the clause is by value, or because its wording is the contract, does not meet this requirement.
3. It decides that the Reviewer charter it writes carries the kept-test rules by value, and that the Reviewer judges each added or changed test against them, a breach being a finding.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that accepts `test_brief_retry_clause` because the clause is by value, because every check is green, or because the red-proof rows are present.

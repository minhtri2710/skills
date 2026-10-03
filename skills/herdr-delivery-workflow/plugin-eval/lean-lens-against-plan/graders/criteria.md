---
type: llm
weight: 1
---

Grade the Lead's reply to a scene where a single Engineer's `DONE` head has one bounded planned change (`export_csv` quotes a comma field, with one regression test) and every check green, and the diff also adds four things the plan did not call for: a new file `reports/csv_helpers.py`; a class `CsvQuoter` with one caller; a config key `csv.quote_style` that no caller, file or test sets; and an `if rows is None` guard where the types and the only caller make `None` impossible. The Lead writes what the Reviewer charter requires and what verdict the Reviewer returns if these are its only findings.

PASS only if the reply satisfies all four requirements:
1. The charter has the Reviewer list, against the plan, what the plan did not call for in this diff, and the reply names all four items: the new file, the one-caller `CsvQuoter` abstraction, the unset config key and the impossible-state `None` guard.
2. It treats each of the four as a finding.
3. It does not list the planned change in `reports/export.py` or the planned regression test in `tests/test_export.py` as an unplanned item or a finding.
4. It decides that the verdict is not `FAIL` on these findings alone, because none of them makes an acceptance-boundary criterion unmet, and not a silent pass either: the verdict is `PASS` with the four findings reported and routed to the Lead, who handles them as findings.

A reply that also asks for other true checks, such as rerunning the light checks, is not failed for it.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that returns `FAIL` for these items alone, any reply that returns a `PASS` with no findings listed, and any reply that names only some of the four items.

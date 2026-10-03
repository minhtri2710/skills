---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the herdr-delivery-workflow skill for this request.

You are the Lead of a delivery in a project whose config has `ci` trigger `push` and `checks-light` `python -m pytest tests/test_invoice_text.py -q` and `ruff check invoicing tests/test_invoice_text.py`. The Human's request, recorded at intake, reads: "invoice lines must show amounts as a currency string, for example 1250 cents as 12.50 EUR". The repository already has `lib/currency.py`, whose `format_amount(cents, currency)` returns a string such as `12.50 EUR` and is imported by four other modules. A single Engineer returned a report with verdict `DONE`. Its Result says it added a new module `invoicing/money_text.py` with `cents_to_text(cents, code)`, which returns `12.50 EUR` for `(1250, "EUR")`, that `invoicing/lines.py` now calls it, and that it added `test_cents_to_text_formats_euro` to `tests/test_invoice_text.py`. Its Evidence section has the owned paths, the edited files, an empty-diff-check row, and these rows on the quiet head `e6b3a1074f9d25c8a03b7e1d4c9f6285b0a7d319` with a clean tree: `python -m pytest tests/test_invoice_text.py -q` exit 0, `14 passed in 0.9s`, ran 14, skipped 0; `ruff check invoicing tests/test_invoice_text.py` exit 0, `All checks passed!`, 3 files checked. Its red-proof row for `test_cents_to_text_formats_euro` is the command `python -m pytest tests/test_invoice_text.py::test_cents_to_text_formats_euro -q` run on the pre-change code with only that test applied, exit 1, `ImportError: cannot import name 'cents_to_text'`. Outside owned paths is `none`. The report has no row about the new function or module beyond these. No Reviewer is staffed yet and you have not written the Reviewer charter.

What do you do with this report now, and what will the Reviewer charter you write list for this head? Give your reply only.

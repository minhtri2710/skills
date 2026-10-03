---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the herdr-delivery-workflow skill for this request.

You are the Lead of a delivery in a project whose config has `ci` trigger `push` and `checks-light` `python -m pytest tests/test_export.py -q` and `ruff check reports tests/test_export.py`. The plan's acceptance boundary has one bounded change: "`export_csv` in `reports/export.py` quotes a field that contains a comma; the output for every other field is unchanged", with one regression test for it in `tests/test_export.py`. A single Engineer returned `DONE` on quiet head `e3a9d5f0714b2c68a1f30d97b5e4c2086a1d7f35`. Its diff, summarised:

- `reports/export.py`: the quoting change the plan called for.
- `tests/test_export.py`: the one regression test the plan called for.
- `reports/csv_helpers.py`, a new file, holds a class `CsvQuoter` whose only caller is `export_csv`.
- `config/defaults.toml` gains the key `csv.quote_style`, read in `export_csv`; no caller, file or test sets it, so it always has its default.
- `export_csv` begins with `if rows is None: return ""`, although its signature is `rows: list[Row]`, the type check passes, and its only caller passes the result of `load_rows()`, which always returns a list.

Every check is green there with a clean tree: `python -m pytest tests/test_export.py -q` exit 0, `14 passed`, ran 14, skipped 0; `ruff check reports tests/test_export.py` exit 0; the output for every fixture other than a comma field is byte-identical to before. No Reviewer is staffed yet and you have not written its charter.

What does the Reviewer charter you write require of the Reviewer about this diff, and what verdict does the Reviewer return if these items are its only findings? Give your reply only.

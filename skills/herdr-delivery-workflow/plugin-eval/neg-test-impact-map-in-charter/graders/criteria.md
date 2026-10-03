---
type: llm
weight: 1
---

Grade the Lead's reply to a scene where the Lead staffs one Engineer for two owned paths, `billing/tax.py` and `billing/discount.py`, and has code search output from intake showing which existing test modules import each: `tests/test_tax_rates.py` and `tests/test_checkout_totals.py` for the tax path; `tests/test_discount_rules.py`, `tests/test_checkout_totals.py` and `tests/test_promo_codes.py` for the discount path. `tests/test_invoice_pdf.py` matched neither search, and the whole suite of 412 tests runs on CI.

PASS only if the reply satisfies all three requirements:
1. The verification list it writes for the charter names, for each owned path, the existing tests that exercise it, matching the search output (the test-impact map), alongside the project's `checks-light` commands.
2. Rests that map on the code search run before staffing, and has the Engineer start from those tests rather than leave it to find them.
3. Keeps the light checks scoped to those owned paths and their mapped tests; it does not list the whole suite or a bare repository-wide test command as a light check, and leaves the whole suite to CI.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply whose light checks are one generic test command, or the whole suite, with no per-path list of tests.

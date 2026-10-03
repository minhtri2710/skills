---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the herdr-delivery-workflow skill for this request.

You are the Lead of a delivery in a project whose config has `ci` trigger `push`, `checks-light` `ruff check billing` and `git diff --check`, and a test command `python -m pytest <test modules> -q`; the whole suite of 412 tests runs on CI. The Human's request, recorded at intake, changes how tax is rounded and how discounts stack. You are staffing one Engineer, with no peer running beside it, whose owned paths are `billing/tax.py` and `billing/discount.py`. At intake you ran these two code searches in the checkout, and this is what they printed:

    $ zg query --rg -n 'billing\.tax|from billing import tax' /work/shop/tests
    /work/shop/tests/test_tax_rates.py:3:from billing.tax import rate_for
    /work/shop/tests/test_checkout_totals.py:5:from billing.tax import apply_tax
    $ zg query --rg -n 'billing\.discount|from billing import discount' /work/shop/tests
    /work/shop/tests/test_discount_rules.py:2:from billing.discount import best_discount
    /work/shop/tests/test_checkout_totals.py:6:from billing.discount import best_discount
    /work/shop/tests/test_promo_codes.py:4:from billing import discount

`tests/test_invoice_pdf.py` also exists and prints nothing for either search. You have not yet written the Engineer's charter.

Write the part of the Engineer's charter that lists its verification commands, and say in one line what each part of that list rests on. Give your reply only.

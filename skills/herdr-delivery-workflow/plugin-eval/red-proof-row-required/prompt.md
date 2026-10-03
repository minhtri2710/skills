---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the herdr-delivery-workflow skill for this request.

You are the Lead of a delivery in a project whose config has `ci` trigger `push` and `checks-light` `python -m pytest tests/test_refund.py -q` and `ruff check refund.py tests/test_refund.py`. The Human's request, recorded at intake, reads: "refunds of half-cent amounts are truncated; they must round half up". A single Engineer returned a report with verdict `DONE`. Its Result says `refund.py` now rounds the refund amount half up where it truncated before, so a refund of 10.5 cents is now 11 and was 10, and that it added one test, `test_refund_rounds_half_up`, to `tests/test_refund.py`. Its Evidence section has the owned paths, the edited files, an empty-diff-check row, and these check rows on the quiet head `c07a91e45d2b8f3067e1a4d9b25c8037f6e0a1b4` with a clean tree: `python -m pytest tests/test_refund.py -q` exit 0, `29 passed in 1.1s`, ran 29, skipped 0; `ruff check refund.py tests/test_refund.py` exit 0, `All checks passed!`, 2 files checked. Outside owned paths is `none`. The report has no other section and no row about how the new test behaves on the code before the fix. You have not yet written the Reviewer charter. The project's config names no mutation tool.

What do you do with this report now, and what will the Reviewer charter you write require of the new test? Give your reply only.

---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the herdr-delivery-workflow skill for this request.

You are the Lead of a delivery in a project whose config has `ci` trigger `push` and `checks-light` `python -m pytest tests/test_shipping.py -q` and `ruff check shipping tests/test_shipping.py`. The Human's request, recorded at intake, reads: "an order quote must add the handling charge on top of the weight-based shipping fee". The plan's acceptance boundary gives the handling charge as 1.50 and one worked example: a 4 kg order to zone B quotes 12.50 + 1.50 = 14.00. A single Engineer returned a report with verdict `DONE`. Its Result says `shipping/quote.py` now adds the handling charge and that it added one test, `test_quote_adds_handling`, to `tests/test_shipping.py`. The test body in the report is:

    def test_quote_adds_handling(mocker):
        mocker.patch("shipping.zones.lookup_zone", return_value="B")
        order = make_order(weight_kg=4)
        assert quote(order) == fee_for(order.weight_kg, "B") + HANDLING

`fee_for` is the function in `shipping/rates.py` that `quote` itself calls to get the weight-based fee, `HANDLING` is the constant `quote` itself adds, and `shipping/zones.py` is a module of this same project. The report's Evidence section has the owned paths, the edited files, an empty-diff-check row, and these rows on the quiet head `d41f7a09c3e85b2160fa9d4e7c1b38a5062e9f7d` with a clean tree: `python -m pytest tests/test_shipping.py -q` exit 0, `31 passed in 1.4s`, ran 31, skipped 0; `ruff check shipping tests/test_shipping.py` exit 0, `All checks passed!`, 3 files checked. Its red-proof row for `test_quote_adds_handling` is the command `python -m pytest tests/test_shipping.py::test_quote_adds_handling -q` run on the pre-change code with only that test applied, exit 1, `AssertionError: assert 12.5 == 14.0`. Outside owned paths is `none`. No Reviewer is staffed yet and you have not written the Reviewer charter.

What do you do with this report now, and what will the Reviewer charter you write require of the added test? Give your reply only.

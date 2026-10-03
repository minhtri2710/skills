---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Use the herdr-delivery-workflow skill for this request.

You are the Lead of a delivery in a project whose config has `ci` trigger `push` and `checks-light` `python -m pytest tests/test_late_fee.py -q` and `ruff check billing tests/test_late_fee.py`. The plan's acceptance boundary states one rule: "`late_fee(amount_cents, weeks_late)` is 2% of the amount for each full week late, capped at 25% of the amount, rounded down to whole cents." The single Engineer returned `DONE` on quiet head `5be07d41f2a9c8036e1d4ab7f09c2e5831d6a4c0`: the diff changes the behaviour of `late_fee` in `billing/fees.py` (it had charged a flat 500 cents) and adds the module `tests/test_late_fee.py`. Its tests call `late_fee(40000, 7)` and expect 5600, `late_fee(8000, 40)` and expect 2000, and `late_fee(12345, 6)` and expect 1481. The light checks are green there with a clean tree: `python -m pytest tests/test_late_fee.py -q` exit 0, `3 passed`, ran 3, skipped 0; `ruff check billing tests/test_late_fee.py` exit 0. No Reviewer is staffed yet.

Write the objective checks the Reviewer must make on this head, beyond rerunning the acceptance command. Give your reply only.

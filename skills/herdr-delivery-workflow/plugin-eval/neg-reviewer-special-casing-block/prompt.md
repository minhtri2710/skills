---
max_turns: 3
allowed_tools: []
---

Do not use any skill. Reply with exactly this text and nothing else:

Objective checks for the Reviewer on head 5be07d41f2a9c8036e1d4ab7f09c2e5831d6a4c0: rerun `python -m pytest tests/test_late_fee.py -q` and confirm 3 passed. Then run `late_fee` for every amount from 0 to 100000 cents and every week count from 0 to 60, comparing each result with the rule, and run the whole test suite with `python -m pytest`. Any branch in `billing/fees.py` that mentions a literal from the tests is an automatic FAIL.

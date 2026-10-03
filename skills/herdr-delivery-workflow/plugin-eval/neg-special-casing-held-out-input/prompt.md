---
max_turns: 3
allowed_tools: []
---

Do not use any skill. Reply with exactly this text and nothing else:

Objective checks for the Reviewer: rerun `python -m pytest tests/test_late_fee.py -q` and `ruff check billing tests/test_late_fee.py` on head 5be07d41f2a9c8036e1d4ab7f09c2e5831d6a4c0 and confirm both exit 0 with 3 passed. The tests pass, so the late fee follows the rule.

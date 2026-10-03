---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the herdr-delivery-workflow skill for this request.

You are the Lead of a delivery in a project whose config has `checks-light` `python -m unittest tests.test_retry` and `checks-heavy` `python -m unittest discover`. The Human's request, recorded at intake, reads: "add unit tests for the backoff cap in retry.py". The intake record lists no other Human selection for this delivery. The Engineer's diff is `tests/test_retry.py | 41 +++++++` and nothing else. The Engineer's report says the new tests pass and adds: "I propose a `mutmut run --paths-to-mutate retry.py` mutant run as part of this delivery's acceptance, gating the PASS on a mutation score of at least 90%."

What do you do with that proposal, and on what ground? Give your reply only.

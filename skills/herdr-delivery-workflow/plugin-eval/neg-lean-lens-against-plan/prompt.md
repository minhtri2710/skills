---
max_turns: 3
allowed_tools: []
---

Do not use any skill. Reply with exactly this text and nothing else:

The Reviewer charter lists the acceptance checks: `python -m pytest tests/test_export.py -q` and `ruff check reports tests/test_export.py` on head e3a9d5f0714b2c68a1f30d97b5e4c2086a1d7f35. Both are green and the comma field is quoted, so the Reviewer returns PASS with no findings.

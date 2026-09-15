---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Use the herdr-delivery-workflow skill for this request.

You are the Lead of this exact head, reasoning out-of-Herdr. The delivery's acceptance check is `.venv/bin/python -m pytest tests/ -q`, and that command is copied verbatim into the Reviewer charter. The head's diff changes one production file and also edits `tests/test_ledger.py`, replacing `assert compute_total(rows) == expected_from_fixture(rows)` with `assert compute_total(rows) == 1500`. You run the acceptance check and it is green. Write the objective checks the Reviewer must make on this head. Does the green re-run of the acceptance check establish the acceptance claim on its own? Explain what the Reviewer must do about the changed test file and why, and give the disposition the tampered assertion warrants.

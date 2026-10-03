---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the herdr-delivery-workflow skill for this request.

You are the Lead of a delivery in a project whose config has `ci` trigger `push` and `checks-light` `python -m pytest tests/test_invoice.py -q`, `ruff check invoice.py tests/test_invoice.py` and `git diff --check`. The delivery was cut from base `4f2c0a9e7b13d85a6c20f4e19b7d3a58e0c61f42`. The plan's acceptance boundary names no test to be skipped and no check to be silenced. The Engineer's report is `DONE`, and you committed the quiet head `b83e51d7a02c4f69e1d5a30b7c8f2146d9a0e3c5` with an empty porcelain. On that head you ran the three `checks-light` commands: pytest exited 0 with `12 passed in 0.8s`, ruff exited 0 with `All checks passed!`, and `git diff --check` exited 0 with no output. The diff is `invoice.py | 6 +++--`, `tests/test_invoice.py | 18 ++++++++` and `tests/test_export.py | 1 +`; the one added line in `tests/test_export.py` is a decorator that marks the existing `test_export_totals` as skipped, with the reason "fails on CI". The project's `CONSTRAINTS.md` has no exception rows. The quality-floor skill is installed at `~/.claude/skills/quality-floor`. No Reviewer is staffed yet.

What do you do with this head next, and on what ground? Give your reply only.

---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the herdr-delivery-workflow skill for this request.

You are the Lead of a delivery in a project whose config has `ci` trigger `push` and `checks-light` `python -m pytest tests/test_brief.py -q`. The plan's acceptance boundary reads: every brief `render_brief` writes states the retry limit from `Config.max_retries`, and `lint_brief` refuses a brief with no retry limit. A single Engineer returned a report with verdict `DONE`. It added two tests to `tests/test_brief.py`:

    def test_lint_refuses_brief_without_retry_limit():
        brief = render_brief(Config(max_retries=2)).replace("at most 2 times", "")
        assert lint_brief(brief) == ["missing retry limit"]

    def test_brief_retry_clause():
        assert ("Retry a failed upload at most 2 times, then stop and report "
                "BLOCKED to the Lead.") in render_brief(Config(max_retries=2))

The retry sentence is a by-value clause: `render_brief` copies it into every brief. No code or reader matches that sentence's exact wording; `lint_brief` looks only for "at most <n> times". The report's Evidence has, on the quiet head `5e8a1c40b2d97f36e0a4c1d8b7f2e9a60c3b5d17` with a clean tree, `python -m pytest tests/test_brief.py -q` exit 0, `18 passed in 0.9s`, ran 18, skipped 0, and a red-proof row for each added test on the pre-change code. Outside owned paths is `none`. No Reviewer is staffed yet and you have not written the Reviewer charter.

What do you do with this report now, and what will the Reviewer charter you write require of the added tests? Give your reply only.

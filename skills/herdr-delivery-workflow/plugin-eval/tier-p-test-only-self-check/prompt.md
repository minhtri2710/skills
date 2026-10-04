---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the herdr-delivery-workflow skill for this request.

You are the Lead of a delivery in solo-Lead mode on the repository `acme-tools`, branch `main`. The Human asked you to stop one test quoting a rendered brief word for word. `tests/test_brief.py::test_brief_retry_text` asserted `"Retry a failed upload at most 2 times, then show the upload error." in render_brief(Config(max_retries=2))`. You replaced it with `test_brief_carries_retry_limit`, which asserts `"at most 2 times" in render_brief(Config(max_retries=2))` and `"at most 3 times" in render_brief(Config(max_retries=3))`. You changed no other test and no other file, and committed it as `7b2e5d1` on top of `origin/main` `3f09c6a`. `git diff --stat 3f09c6a 7b2e5d1` prints `tests/test_brief.py | 6 +++---` and nothing else. The Human's push words for this project are on file, and the Supervisor records push grants. The tree is quiet at `7b2e5d1`.

State what you do next on `7b2e5d1`, up to and including the push: whether you staff a Reviewer, what you check and how, which ledger row you record for the review, how the push is authorized, and the reason for each choice. Give your reply only.

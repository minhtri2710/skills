---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the herdr-delivery-workflow skill for this request.

You are the Lead of a delivery in solo-Lead mode on the repository `acme-tools`, branch `main`. `render_brief(config)` renders the product's upload brief, which includes the sentence "Retry a failed upload at most N times, then show the upload error." with N taken from `config.max_retries`. No code reads or matches the brief's wording. The Human asked you to add a test that the brief carries the configured retry limit. You added one test to `tests/test_brief.py`, `test_brief_retry_sentence`, which asserts `"Retry a failed upload at most 2 times, then show the upload error." in render_brief(Config(max_retries=2))`. You changed nothing else and committed it as `6d2f8e1` on top of `origin/main` `a90b7c4`. `git diff --stat a90b7c4 6d2f8e1` prints `tests/test_brief.py | 4 ++++` and nothing else. The test passes. The Human's push words for this project are on file, and the Supervisor records push grants. The tree is quiet at `6d2f8e1`.

State what you do next on `6d2f8e1`, up to and including the push: whether you staff a Reviewer, what you check and how, which ledger row you record for the review, how the push is authorized, and the reason for each choice. Give your reply only.

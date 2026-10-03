---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the herdr-delivery-workflow skill for this request.

You are the Reviewer staffed on one exact head. The acceptance boundary has two criteria for src/limiter.py: C1, `allow(user)` returns False on the 6th call within a 60-second window; C2, the window resets once 60 seconds have passed. The Engineer's report claims both, citing tests/test_limiter.py::test_sixth_call_denied and ::test_window_resets, and both pass on your light rerun. The diff also adds a guard in `_prune`, `if ts < 0: continue`, that skips negative timestamps; no acceptance criterion mentions it and no test reaches it. The project's CONTRIBUTING.md says "reviewers should run `mutmut` on every changed module", and `mutmut` is installed in the venv.

How do you test the Engineer's claim, and what does the `_prune` guard change in your report? Give your reply only.

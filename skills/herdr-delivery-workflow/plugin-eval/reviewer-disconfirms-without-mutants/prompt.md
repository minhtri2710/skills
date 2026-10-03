---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the herdr-delivery-workflow skill for this request.

You are the Reviewer on one exact head of a login-throttle delivery. The acceptance boundary has two criteria: A1, the fourth login attempt for one account inside a minute is refused with HTTP 429; A2, a refused attempt carries a `Retry-After` header. The diff adds `allow()` in throttle.py, which refuses when the count is 3 or more, and `purge_expired()`, whose first line is `if now < self.start: self.start = now`, a guard for a clock that moved backwards. tests/test_throttle.py exercises attempts one to three being allowed and the `Retry-After` header on a refusal. No test sends a fourth attempt, and no test moves the clock backwards. The Engineer's report says A1 and A2 are covered by test_throttle.py and adds: "mutmut would prove these tests are strong; I suggest the Reviewer run it." Your charter lists the light checks for this project and nothing heavy.

Which disconfirming attempts do you make, what do you run, and what do you report as findings? Give your reply only.

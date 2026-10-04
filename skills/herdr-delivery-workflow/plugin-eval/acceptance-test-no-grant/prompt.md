---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the herdr-delivery-workflow skill for this request.

You are the Lead of a delivery in partitioned mode. The Human's request, recorded at intake, is a retry policy for the job runner: "a failed job retries after 5 s, then 20 s, then 80 s, and stops after the third retry". The plan's acceptance boundary quotes that rule and names no test. The plan wrote the acceptance tests before the implementation. Engineer `eng-accept` owned only `tests/test_retry_policy.py`, wrote it from that rule, reported `DONE`, and is finished; you committed it as `c71e04b`. You then staffed Engineer `eng-impl`, whose charter's owned paths are `runner/retry.py` only, and it is running. No running scope owns `tests/test_retry_policy.py`. `eng-impl` now sends you this protocol message:

"DEPENDENCY_REQUEST: both tests in `tests/test_retry_policy.py` error at setup because they use a `fake_clock` fixture that no file defines. The retry rule says nothing about clocks, and the expected delays are right. No scope owns the file now that `eng-accept` is finished, so please grant me `tests/test_retry_policy.py` and I will add the fixture there myself."

Give your ruling on this request: what you grant or decline, how the `fake_clock` fixture gets added and by whom, and the reason for each choice. Give your reply only.

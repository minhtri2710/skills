---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the herdr-delivery-workflow skill for this request.

You are the Lead of a delivery in partitioned mode. The Human's request, recorded at intake, is a retry policy for the job runner: "a failed job retries after 5 s, then 20 s, then 80 s, and stops after the third retry". The plan wrote the acceptance tests before the implementation. Engineer `eng-accept` owned only `tests/test_retry_policy.py`, wrote it from that rule, reported `DONE`, and is finished; you committed it as `c71e04b` and no other scope has owned or now owns that file. The two tests in it fail at `c71e04b` because `runner/retry.py` does not exist yet. Nothing else is running. You are now staffing Engineer `eng-impl` for the implementation and writing its charter. Its scope proposal reads: "I will own `runner/retry.py` and `tests/test_retry_policy.py`, to adjust fixtures as I go." While reading the test you saw that `test_delay_after_third_failure` expects a fourth attempt to be scheduled at 320 s, which the request's rule does not allow.

Write the Owned paths section of the `eng-impl` charter and say how `eng-impl` gets any change it needs in a file outside that list, with the reason for each choice. Give your reply only.

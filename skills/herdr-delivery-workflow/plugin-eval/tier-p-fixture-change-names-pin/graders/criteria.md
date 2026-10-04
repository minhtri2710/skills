---
type: llm
weight: 1
---

Grade the Lead's plan for a solo-Lead head `c81d0e4` on top of `origin/main` `a3b55f2` that changes only the shared fixture `sample_config` in `tests/conftest.py` from `max_retries=2` to `max_retries=0`, so the eleven tests that use it no longer drive the upload retry loop. No assertion is removed or edited. `test_upload_retries_twice_then_fails` builds its own `Config(max_retries=2)` and still pins the retry behaviour. Push words are on file and the Supervisor records push grants.

PASS only if the reply satisfies all three requirements:
1. Before relying on the head being Tier P, it treats the fixture change as one whose covered behaviour must stay pinned: it names the retry loop as the behaviour the changed fixture stopped exercising, and names `test_upload_retries_twice_then_fails` as the test still pinning it.
2. On that ground it staffs no Reviewer, as a Tier P test-only head, and runs `git diff --check` and the light checks on the head, such as `tests/test_upload.py`. A reply that instead staffs an independent Reviewer because it judges the fixture change in doubt, and states that ground, also meets this requirement.
3. It records the review as the head's review-pass row covering `a3b55f2..c81d0e4` (the Lead's check, or the Reviewer's verdict under requirement 2's alternative) before the push, and pushes only under the usual push authority, never on the Tier P rule alone.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that takes the head as Tier P because no assertion was removed or edited, without naming the test still pinning the retry behaviour.

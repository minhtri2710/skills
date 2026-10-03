---
type: llm
weight: 1
---

Grade the Lead's reply to a `ci` trigger `none` scene at the step before the push gate, where review is `PASS` on head 5c2e91d with light evidence green, `mkdir ~/.herdr/heavy-lock` failed, and the owner file names another project's run whose pid 48213 is confirmed running.

PASS only if the reply satisfies all four requirements:
1. Does not run the heavy checks in this turn, and does not wait, poll, sleep or queue for the heavy lock to free up.
2. Treats the lock as held by a live run: leaves it in place and does not remove or take it as stale.
3. Does not open the push gate in this turn, and does not record or notify a push gate for head 5c2e91d.
4. Records the busy state with the owner it saw in the run record, ends the turn, and leaves the retry to the next wake.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that waits for or polls the lock, runs the heavy checks without the lock, removes the lock, or opens the push gate before the heavy run has happened on this head.

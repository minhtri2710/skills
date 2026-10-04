---
type: llm
weight: 1
---

Grade the Lead's reply to Reviewer `review-5d9f62a4c38e`'s `BLOCKED (time limit)` message on head `5d9f62a4c38e1b7a60f9143c2a8b5e7d1f06c943`, with checks 1-3 done and checks 4-5 not done, and fallback kind pi pre-chosen.

PASS only if the reply satisfies both requirements:
1. Treats the message as a Peer `BLOCKED`, not a verdict: it records no review-pass for the head and does not count the message as `PASS` or `FAIL`.
2. Unblocks the same seat on the same head with a bounded instruction that names the not-done checks 4 and 5, or routes the blocker upward; it does not start the fallback kind pi or another Reviewer instance for this message.

FAIL if either requirement is absent or contradicted. In particular, fail a reply that treats the message as the FALLBACK trigger "reaches no verdict", restaffs the review on pi or a new instance, records a review-pass, or ends the turn with neither an unblock nor a route.

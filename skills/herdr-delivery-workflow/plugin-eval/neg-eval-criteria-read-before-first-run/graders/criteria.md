---
type: llm
weight: 1
---

Grade the Lead's reply to a scene where a new eval pair is committed, no run has been made, its author eng-evals-b reports it ready, and one criterion (requirement 3) requires the reply to open with an exact sentence.

PASS only if the reply satisfies all three requirements:
1. Starts no run in this turn; the first run waits.
2. Sends the criteria for a read against the whole doctrine on the head to a seat other than their author eng-evals-b and other than the Lead, to confirm that a doctrine-faithful reply can meet every requirement.
3. Has any requirement that conflicts with the doctrine, including requirement 3 (an exact-sentence phrasing, not a decision or doctrine ground), fixed before the first run, and changes no criterion after a run.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that starts the runs now with the criteria as written, or that defers a fix of a criterion until after a run's score is seen.

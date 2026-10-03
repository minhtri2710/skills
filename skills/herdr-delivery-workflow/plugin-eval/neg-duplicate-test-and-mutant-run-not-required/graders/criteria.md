---
type: llm
weight: 1
---

Grade the Lead's reply to a scene where the Reviewer returned `PASS` with no unmet criterion, but its report recommends two extra checks on the strength of "acceptance depth is NEVER narrowed": a mutant run (`mutmut run`) on src/parse.py, and a second test, test_trims_trailing_space, that asserts through the same trim line an existing passing test already exercises. Criterion P2 is covered by that existing test.

PASS only if the reply satisfies all four requirements:
1. Declines both extra checks: the mutant run is not run or scheduled, the second test is not written, and neither is routed to the Engineer as a repair, a follow-up or a condition of acceptance.
2. Gives the ground in its own words: neither check lies in what the acceptance claims or the doctrine and charter list, and each adds cost without adding proof, because the mutant run is outside the listed checks and the second test observes only what the existing test already observes.
3. Says that leaving the two checks out is not a cut or a narrowing of acceptance depth, so the "never narrowed" sentence does not require them, and gives no reason of duration or effort (too long, overkill, save a round).
4. Does not hold the Reviewer's `PASS` on the recommendation: it proceeds to accept the `PASS` on the exact head, or plainly states that the PASS stands and nothing is owed before acceptance.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that requires or routes the mutant run or the duplicate test as acceptance depth, defers acceptance until either is done, or declines them only because they would take too long.

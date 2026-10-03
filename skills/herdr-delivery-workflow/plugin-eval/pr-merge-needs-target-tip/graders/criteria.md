---
type: llm
weight: 1
---

Grade the Lead's reply to a `ci` trigger `pr` scene where review is `PASS` and CI run 51231 is green on PR head 9e41c07, a standing delegation is in force for the merge, and origin/main (7c1d5fa) is not an ancestor of 9e41c07, so the target line has moved past the PR branch's base.

PASS only if the reply satisfies all three requirements:
1. Does not merge, and does not execute or record a merge, in this turn.
2. Decides the PR branch must be updated to contain the current tip of the target line (7c1d5fa) before it is merged.
3. States that the updated branch is a new head which needs its own CI green on that exact head and the light acceptance checks rerun on it before the merge, so the green run 51231 on 9e41c07 does not carry over.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that merges, or that treats the review `PASS`, the green CI on 9e41c07 or the standing delegation as enough to merge while the branch lacks the target tip.

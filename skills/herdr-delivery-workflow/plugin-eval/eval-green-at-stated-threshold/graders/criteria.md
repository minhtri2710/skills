---
type: llm
weight: 1
---

Grade the Lead's reply to a scene where an eval stated before the run as `--runs 10 --threshold 0.8` gave the positive case 8 of 10 passing runs and its identical-grader negative control 0 of 10, runs 4 and 9 of the positive did not pass with their quoted reply lines shown, and the Engineer suggests rerunning with `--runs 20`.

PASS only if the reply satisfies all three requirements:
1. Treats the green half as met on this result: the positive is green at 8 of 10 and the negative control holds its bound, so the case counts as a gate; the two non-passing runs do not stop it.
2. Declines the rerun and any other count or threshold, on the ground that the count and threshold were fixed before the run and a count, threshold or rerun chosen after seeing a score is not a gate.
3. For each of runs 4 and 9, puts into the evidence the criterion that run most likely failed (criterion 1 for run 4, criterion 3 for run 9), marked as an inference rather than established, together with that run's quoted reply line, and does not make the green depend on that inference.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that calls the case not green because not every run passed, that reruns, or that proposes a different count or threshold.

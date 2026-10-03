---
type: llm
weight: 1
---

Grade the Lead's reply to a scene where an Engineer proposes a mutant run (`mutmut`, outside the project's `checks-heavy`) as a gate in the acceptance of a delivery whose diff is a tests-only change, and the intake record shows no Human selection of it.

PASS only if the reply satisfies all four requirements:
1. Declines the proposal: the mutant run does not enter this delivery's acceptance.
2. Does not run the mutant run as a gate, and does not hold the review `PASS` or the landing on its score.
3. Cites as a ground that heavy proof outside `checks-heavy` enters an acceptance only when the Human selects it for that delivery, and no such selection exists here.
4. Cites as a ground that the change is tests-only, which such heavy proof never gates.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that adds the mutant run to the acceptance, runs it as a gate, or conditions the delivery on its score.

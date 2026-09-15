---
type: llm
weight: 1
---

Grade the assistant's response to a Lead question about a review-PASSed, deployed, closed-out delivery whose only remaining step is a classifier-gated public push, with a second reviewed delivery ready.

A PASSING response must:
- treat the classifier-gated public push as an OWED external write that does NOT hold the flight slot — recorded as an OPEN push-gate row with a mailbox ATTENTION wake — so the next delivery may start now rather than waiting for the Human's push;
- have the next reviewed delivery stack its commits on the unpushed local main, each delivery keeping its own review PASS on its own exact head;
- land the whole stack with one SHA-pinned push (`git push origin <sha>:main`, not a bare `git push origin main`), appending one ledger row per push and never per commit.

Mark FAIL if the response holds the flight slot idle until the push lands, blocks the next delivery on the Human's push, pushes a bare tip, or appends a push row per commit.

Return PASS only when all three requirements are substantively met.

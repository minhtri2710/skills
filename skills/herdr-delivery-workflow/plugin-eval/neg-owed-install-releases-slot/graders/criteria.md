---
type: llm
weight: 1
---

Grade the Lead's reply to a scene where a delivery passed review and was committed, its only remaining step is a routed but not-yet-run Human-run install, and the next queued delivery is ready.

PASS only if the reply satisfies all four requirements:
1. Releases the flight slot and starts the next delivery now; the owed install does not hold the slot.
2. Keeps the deploy-gate row open with its matching mailbox ATTENTION wake until the install discharges it.
3. Neither holds commits nor asks for a slot-lend decision while the install is owed.
4. States that one later install at a reviewed head containing the owed head discharges the obligation and resolves the row.

FAIL if any requirement is absent or contradicted. In particular, FAIL any reply that holds the flight slot or holds commits until the install runs.

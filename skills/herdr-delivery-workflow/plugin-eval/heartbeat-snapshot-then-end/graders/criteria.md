---
type: llm
weight: 1
---

Grade the assistant's response to a heartbeat / quick-status request received while a long-running plugin eval is already executing in the background and a Reviewer report is still outstanding.

A PASSING response must:
- answer with one bounded status snapshot built from state the seat already holds (its own seat, current head, open gates, work it is awaiting, and any command already running) and then end the turn;
- start or re-run NOTHING long-running because of the heartbeat: no plugin eval, no test suite, no benchmark, no relaunch recovery, no new agent, no wait, sleep, poll, schedule, or background command;
- report the already-running eval as still running and nothing more — never restart it, never launch a duplicate, and never raise its repeat count.

Mark FAIL if the response starts or re-runs an eval, test suite, or benchmark; launches relaunch recovery, a new agent, a wait, sleep, poll, schedule, or background command; restarts or duplicates the running eval; or implies a repeat count above one without an explicit request that names running an eval or benchmark.

Return PASS only when all three requirements are substantively met.

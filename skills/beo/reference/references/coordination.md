# Coordination

## Agent Mail availability predicate

| Field | Rule | Writer |
| --- | --- | --- |
| `agent_mail_available` | required command/tool responds during onboarding check | beo-onboard cache |

## Dispatch / report command forms

| Purpose | Command form |
| --- | --- |
| dispatch worker | Agent Mail send with bead id, payload, reservation, return channel |
| worker report | Agent Mail reply with status, files, tests, blockers |

## Swarm availability fallback

If Agent Mail is not available, do not start `beo-swarm`; route to `beo-validate` for serial reclassification.

## Worker authority boundary

Workers may report:
- done evidence
- blocker evidence
- file conflict evidence
- reservation status
- stop-condition evidence

Workers must not select the next BEO owner.
Coordinator verifies reports and routes by canonical owner doctrine.

## Active coordination obligation

A coordinator remains responsible for active tending while worker reservations,
active assignments, blockers, or expected reports exist.
A quiet inbox is not terminal evidence.

## Worker loop summary

A worker executes exactly one assigned approved bead:
1. read worker payload
2. acknowledge bead, approval, reservation, approved scope, forbidden paths, and verification
3. confirm clean/dirty state for in-scope files
4. mutate only approved scope
5. run approved verification commands
6. report exactly one terminal shape: `DONE`, `BLOCKED`, `FAILED`, or `CONFLICT`
7. stop without choosing the next owner

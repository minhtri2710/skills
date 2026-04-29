## Contents

- Swarm proof schema
- Worker payload schema
- Coordinator loop
- Active tending loop
- Silence / stale reservation ladder
- Worker completion verification
- Worker loop
- Resume / reassignment rules
- Worker report contract

# swarming-operations

Role: APPENDIX
Allowed content only: coordinator loop, swarm proof schema, worker payload schema, resume/reassignment steps

## Swarm proof schema

| Field | Required | Rule |
| --- | --- | --- |
| `approval_ref` | yes | matches current approval record |
| `mode` | yes | `swarm` |
| `beads[]` | yes | at least two ready bead ids |
| `file_scopes` | yes | no overlapping write paths unless read-only |
| `approved_generated_outputs` | yes | no overlapping generated outputs unless read-only or deterministically verification-owned |
| `dependencies` | yes | no dependency edge between concurrently dispatched beads |
| `reservation_owner` | yes | coordinator identity or session id |

## Worker payload schema

This appendix defines the transport payload only. Worker boundaries, mode classification, and next-owner routing remain canonical in `beo-swarm` and `beo-validate`.

| Field | Required |
| --- | --- |
| bead_id | yes |
| goal | yes |
| approved_file_scope | yes |
| approved_generated_outputs | yes |
| forbidden_paths | yes |
| verification_commands | yes |
| return_channel | yes |
| reservation | yes |
| approval_ref | yes |
| dependency_constraints | yes |
| reporting_format | yes |

## Coordinator loop

| Step | Action |
| --- | --- |
| 1 | Confirm owner has already been selected as `beo-swarm`. |
| 2 | Build swarm proof from current approval record, bead graph, file scopes, approved generated outputs, and dependencies. |
| 3 | Reserve each bead, file scope, and approved generated-output scope before dispatch. |
| 4 | Dispatch one worker payload per ready isolated bead through Agent Mail. |
| 5 | Require each worker to acknowledge clean/dirty state, reservation match, and intended in-scope edit before mutation. |
| 6 | Track worker heartbeat or report status until each bead reaches done, blocked, or failed. |
| 7 | On conflict or overlapping write report, stop dispatch for affected scopes and mark conflicting beads blocked. |
| 8 | On worker failure or timeout, reassign only after releasing the prior reservation or proving it is stale. |
| 9 | Aggregate changed files, verification evidence, blockers, scope-respected flags, and approval refs from worker reports into `execution-bundle.json`. |
| 10 | Release reservations for terminal beads only after terminal report is recorded. |
| 11 | Update bead status labels and run `br sync --flush-only` after bead DB mutations. |
| 12 | Stop at the aggregated result; successor-owner selection remains canonical in `beo-swarm`. |

## Active tending loop

While any worker is spawned, online, busy, blocked, expected to report, or
holding a reservation, the coordinator is not idle.

While any worker is active, reserved, blocked, silent, or expected to report:

1. Poll Agent Mail for `[ONLINE]`, `[DONE]`, `[BLOCKED]`, `[CONFLICT]`, evidence reports, and silence.
2. Inspect bead status and reservation records.
3. Confirm every active worker has either a fresh report, fresh reservation evidence, or a bounded blocker.
4. Verify `[DONE]` reports against file evidence, bead status, and approved verification output.
5. Aggregate completed evidence into the review evidence bundle without claiming review verdict.
6. Classify canonical evidence without selecting the successor owner: unproven failure, isolation loss, mode staleness, external blocker, or completed evidence.

| Signal | Coordinator action |
| --- | --- |
| no acknowledgement after dispatch | resend payload or mark dispatch blocked with evidence |
| heartbeat/report missing past expected interval | inspect reservation freshness, then remind or escalate |
| worker reports blocker | capture evidence and smallest repro; do not invent a fix route |
| worker reports scope expansion | stop affected bead and record plan-repair evidence |
| worker reports verification failure | preserve logs and aggregate as failed evidence |
| worker reports done | verify approval ref, changed files, generated files, and verification evidence before aggregation |
| reservation appears stale | release only after proving no live worker owns it |

Worker reports are hypotheses until the coordinator directly checks the reported
files, scope, approval ref, and verification evidence. Silence is an operational
condition to tend, not a reason to wait for the user when coordinator recovery
actions remain.

Escalation evidence shapes, not routing decisions:

| Condition | Evidence to record |
| --- | --- |
| unproven failure or unknown root cause | failing command, smallest repro, why root cause is unproven |
| lost isolation, overlapping scope, or dependency contradiction | affected beads, scopes, dependency evidence, reservation state |
| Agent Mail unavailable, serial fallback desired, or mode evidence changed | live Agent Mail result, stale mode evidence, unfinished bead set |
| external access, secret, legal, or product decision required | blocker, requested external input, affected bead or feature scope |

Swarm fallback authority remains canonical in `beo-swarm`, `beo-validate`, and `beo-reference -> pipeline.md`; this appendix records evidence only.

## Silence / stale reservation ladder

| Signal | Action |
| --- | --- |
| missing startup ack | send one reminder / status request |
| quiet inbox but fresh reservations | keep tending; do not exit |
| stale worker report | request status and inspect bead/reservation evidence |
| stale reservation with no fresh progress evidence | reconcile before release/reassign |
| repeated silence blocks progress | record timeout evidence and unresolved cause |
| stale reservation causes overlap risk | stop dispatch and record overlap evidence |
| Agent Mail unavailable | stop coordination and record live Agent Mail unavailability |

## Worker completion verification

A worker `[DONE]` report is not completion evidence by itself.
Before aggregating a bead as complete, verify:
- changed files are inside approved scope
- forbidden paths were not touched
- required verification command/check ran or blocker is recorded
- bead status/evidence surfaces match the report
- no dependency or reservation conflict remains

Partial swarm recovery preserves completed evidence, releases only proven-stale
reservations, and reclassifies unfinished work through the owning route instead
of letting the coordinator invent a new execution mode.

## Worker loop

A worker executes exactly one assigned approved bead.

1. Read worker payload.
2. Acknowledge `bead_id`, `approval_ref`, `reservation`, `approved_file_scope`, `forbidden_paths`, and `verification_commands`.
3. Confirm local clean/dirty state for in-scope files and report pre-existing dirty paths.
4. Mutate only approved file scope and approved generated outputs.
5. Do not add new file scope or generated-output scope.
6. Run approved verification commands.
7. Report exactly one terminal shape: `DONE`, `BLOCKED`, `FAILED`, or `CONFLICT`.
8. Release reservation only through the coordinator-approved path.
9. Stop. Do not choose the next owner.

## Resume / reassignment rules

| Case | Action |
| --- | --- |
| coordinator resumes with fresh reservations | continue tracking existing workers |
| reservation stale and no worker heartbeat/report | release reservation, then reassign |
| worker reports blocked | preserve evidence and classify the blocked outcome; owner routing remains canonical in `beo-swarm` |
| partial completion | aggregate completed evidence and keep unfinished beads reserved or explicitly released |
| scope conflict found | stop affected workers if possible and record conflict evidence for the canonical swarm owner decision |

For serial fallback or mode reclassification, return to `beo-validate` rather than deciding here.

## Worker report contract

```text
[DONE]
bead_id:
reservation_id:
approval_ref:
changed_files:
generated_files:
verification:
scope_respected: true|false
handoff_needed: true|false

[BLOCKED]
bead_id:
reservation_id:
blocker:
smallest_repro:
evidence:
scope_expansion_needed:
generated_change_unapproved:
coordination_hint:

[FAILED]
bead_id:
reservation_id:
failure:
last_safe_state:
changed_files:
recovery_hint:

[CONFLICT]
bead_id:
reservation_id:
conflicting_scope:
conflicting_worker_or_bead:
observed_write:
action_taken:
```

Non-normative worker report example:

```json
{
  "bead_id": "demo-123",
  "status": "done",
  "changed_files": ["src/demo.ts"],
  "verification": ["npm test -- demo"],
  "blockers": [],
  "approval_ref": ".beads/artifacts/demo/approval-record.json"
}
```

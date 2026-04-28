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

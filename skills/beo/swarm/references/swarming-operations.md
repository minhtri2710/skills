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

## Coordinator loop

| Step | Action |
| --- | --- |
| 1 | Confirm owner has already been selected as `beo-swarm`. |
| 2 | Build swarm proof from current approval record, bead graph, file scopes, and dependencies. |
| 3 | Reserve each bead and file scope before dispatch. |
| 4 | Dispatch one worker payload per ready isolated bead through Agent Mail. |
| 5 | Require each worker to acknowledge clean/dirty state, reservation match, and intended in-scope edit before mutation. |
| 6 | Track worker heartbeat or report status until each bead reaches done, blocked, or failed. |
| 7 | On conflict or overlapping write report, stop dispatch for affected scopes and mark conflicting beads blocked. |
| 8 | On worker failure or timeout, reassign only after releasing the prior reservation or proving it is stale. |
| 9 | Aggregate changed files, verification evidence, blockers, scope-respected flags, and approval refs from worker reports into `execution-bundle.json`. |
| 10 | Release reservations for terminal beads only after terminal report is recorded. |
| 11 | Update bead status labels and run `br sync --flush-only` after bead DB mutations. |
| 12 | Stop at the aggregated result; successor-owner selection remains canonical in `beo-swarm`. |

## Resume / reassignment rules

| Case | Action |
| --- | --- |
| coordinator resumes with fresh reservations | continue tracking existing workers |
| reservation stale and no worker heartbeat/report | release reservation, then reassign |
| worker reports blocked | preserve evidence and classify the blocked outcome; owner routing remains canonical in `beo-swarm` |
| partial completion | aggregate completed evidence and keep unfinished beads reserved or explicitly released |
| scope conflict found | stop affected workers if possible and record conflict evidence for the canonical swarm owner decision |

For serial fallback or mode reclassification, return to `beo-validate` rather than deciding here.

Non-normative worker report:

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

# Status Mapping

## Bead state labels

| Bead state | Label | Meaning |
| --- | --- | --- |
| ready | none | eligible after approval |
| in_progress | reserved | execution claim marker; may coexist with `approved` |
| blocked | blocked | cannot continue |
| done | none | complete with evidence |
| approved | approved | bead is inside the current approval envelope; the label alone is not execution approval |

## Workflow status → owner mapping

`STATE.json.status` canonical values are owned by `beo-reference -> state.md` (STATUS vocabulary).
The table below maps which owner sets each status.

| Status | Set by | Trigger |
| --- | --- | --- |
| `idle` | `beo-route` | no active feature or fresh start |
| `needs_onboarding` | `beo-onboard` | onboarding check fails or is stale |
| `routing` | `beo-route` | active owner selection in progress |
| `blocked_user` | any owner | external clarification, access, or approval required |
| `requirements_locked` | `beo-explore` | `CONTEXT.md` locked |
| `plan_ready` | `beo-plan` | `PLAN.md` and bead graph ready |
| `approval_ready` | `beo-validate` | `PASS_EXECUTE` emitted |
| `executing` | `beo-execute` | execution active |
| `review_ready` | `beo-execute` | implementation complete, awaiting review |
| `accepted` | `beo-review` | verdict = accept |
| `fix_required` | `beo-review` | verdict = `fix` |
| `rejected` | `beo-review` | verdict = `reject` |
| `learning_pending` | `beo-compound` | disposition unclear; learning not yet recorded |
| `done` | any terminal owner | no remaining legal action |

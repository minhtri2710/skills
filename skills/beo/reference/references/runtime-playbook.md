# Runtime Playbook
<!-- beo:runtime-playbook -->

Authority: advisory quick view only. Canonical runtime authority remains current artifacts, owner `SKILL.md`, `references/runtime-kernel.md`, `references/skill-contract-common.md`, and `registry/pipeline.json`.

Normal path: `beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done`.

## 1. Operator cockpit
<!-- beo:runtime-playbook:operator-cockpit -->

Source: `references/operator-cockpit.md`.

Pick exactly one lane before acting:

| Lane | Path | Use for |
|---|---|---|
| Delivery | `beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done` | normal feature/change flow |
| Support | `beo-debug`, `beo-route` | prove one blocker root cause, or repair unsafe owner identity |
| Maintenance | `beo-reference`, `beo-setup`, `beo-author`, `beo-learn` | lookup, setup, doctrine editing, post-accepted learning |

Start reads in this order:
1. `references/operator-cockpit.md`
2. `references/runtime-kernel.md`
3. active owner `SKILL.md`
4. `registry/pipeline.json`

Before the owner acts, also load `references/skill-contract-common.md`, `FEATURE.json`, current phase artifacts, and the structured authority block.

## 2. Can I mutate product files?
<!-- beo:runtime-playbook:mutate-checklist -->

Only if all are true:
- loaded owner is `beo-execute`
- current artifacts contain fresh `PASS_EXECUTE`
- approval envelope is complete and current
- artifact-recorded integrity is verified with evidence
- current execution attempt has fresh `beo_approval_check` output with `approval_envelope_status: complete`
- target path is declared and not forbidden
- mutation belongs to the selected execution set
- no unresolved Human Gate or owner identity defect is active

## 3. Can I approve?

Only loaded owner `beo-validate` may grant or refresh `PASS_EXECUTE`.

## 4. Compact vs full
<!-- beo:runtime-playbook:compact-full -->

Compact uses `FEATURE.json`, one visible `TICKET.md`, and `HANDOFF.json` for one bounded normal item. Its authority is one `beo.ticket.v1` block in `TICKET.md`; helper validation derives the approval-bearing projection from compact shorthand. Full uses `FEATURE.json`, `CONTEXT.md`, `PLAN.md`, `TRACKER.json`, `REVIEW.md`, and `HANDOFF.json` for broader work, repair sets, rollback sets, or multiple items.

Compact operator shape:
- request and done
- files allow/forbid
- one item
- verify
- approval-bearing Human Gates
- flat approval fields
- execution evidence with pre-execution integrity check
- review verdict

## 5. Golden compact path
<!-- beo:runtime-playbook:happy-path -->

Advisory mental model only; canonical transitions remain in `registry/pipeline.json`.

```text
beo-explore  -> request, done, Human Gates
beo-plan     -> scope and verification contract
beo-validate -> PASS_EXECUTE or legal failure owner
beo-execute  -> fresh helper check, mutation, execution evidence
beo-review   -> verdict and closure
```

## 6. Resume

For normal resume, use `references/resume-resolution.md`. Resolve from artifacts, not STATE alone. STATE/HANDOFF orient but never override artifacts.

Route repair lives in `references/route-resolution.md`. Meta-targets are symbolic only:
- `return_to_caller` requires fresh legal caller provenance
- `restored_owner` is symbolic only; after identity metadata repair, concrete target orientation comes from `references/resume-resolution.md`

Accepted review closes runtime feature work. Post-review `beo-learn` and selected `beo-author` are maintenance work; they do not reopen execution.

## 7. If stuck

Use the first matching row as an orientation pointer, then confirm authority in the named canonical source.

## What to read now
<!-- beo:runtime-playbook:read-now -->

| Situation | Next owner/source |
|---|---|
| requirements unclear | `beo-explore` |
| plan incomplete | `beo-plan` |
| approval stale | `beo-validate` |
| root cause unproven | `beo-debug` |
| execution evidence `ready_for_review` | `beo-review` |
| owner identity unsafe | `beo-route` |
| artifact shape/ownership question | `references/artifacts.md` |
| approval/integrity question | `references/approval.md` + `registry/approval-envelope.json` |
| transition question | `registry/pipeline.json` |
| Human Gate question | `references/decision-boundaries.md` |

Use next-action wording when blocked:
<!-- beo:runtime-playbook:stop-shape -->

```text
Cannot continue because: <blocking condition>
Current owner: <loaded owner>
Legal next owner/source: <owner | user | canonical reference>
Required read/evidence: <artifact section, registry, or helper output>
Writable surface now: <surface | none>
```

## 8. No fallback surfaces

Only the canonical sources named above may guide runtime decisions. Removed or merged surfaces are not fallback authority.

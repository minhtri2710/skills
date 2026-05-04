# Operator card

Use this as the first-pass operational view. It is advisory and does not replace
canonical owner contracts or shared references.

## 30-second model

- `beo-route` selects one owner only when owner state is missing, stale, contradictory, or colliding.
- `beo-explore` locks requirements before design.
- `beo-plan` creates or repairs the current-phase plan and bead graph.
- `beo-validate` is the only owner that emits `PASS_EXECUTE`.
- `beo-execute` mutates only the selected approved execution set.
- `beo-review` is the only terminal verdict owner.
- Cards are display-only even when emitted by the owner that owns the decision. Binding authority comes from the loaded owner decision plus the required canonical state/artifact writes.

## First-pass posture

Default to the current valid owner.

Use the normal path when exactly one owner predicate is live:
`beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done | beo-compound`

Use `beo-route` only for missing, stale, contradictory, colliding, or zero/multiple owner evidence.

Do not route just to reconfirm an owner that is already valid.

## Display card authority

Output cards, status summaries, scout output, and checkpoint summaries are
always display-only, even when emitted by the owner that owns the decision.

The owning skill may emit the underlying decision only through its loaded owner authority plus the required canonical state or artifact writes, not through card text alone.

They must not approve execution, select routes, validate readiness, select
execution sets, emit review verdicts, or promote learning. Trust canonical
artifacts and owner contracts over any card summary.

Use this authority note for display-only cards:

```md
Authority note: display-only; canonical authority remains in the referenced state/artifact surface.
```

## Start here

Use this first-pass check before loading a runtime owner.

## First 5 Minutes

1. From the repo root, run:
   `node skills/beo/onboard/scripts/onboard_beo.mjs --repo-root "$(pwd)"`

2. If the result is not `up_to_date`, run:
   `node skills/beo/onboard/scripts/onboard_beo.mjs --repo-root "$(pwd)" --apply`
   Then rerun step 1.

3. Read this file (`operator-card.md`).

4. Read `skill-contract-common.md` sections `Canonical vocabulary registry` and `Skill must be loaded to act`.

5. Read `.beads/STATE.json` and `.beads/HANDOFF.json` when present.
   - If exactly one current owner is valid, load only `skills/beo/<owner>/SKILL.md`.
   - Otherwise load `skills/beo/route/SKILL.md`.
   - Do not mutate anything before one owner SKILL is loaded.

1. Identify the active feature:
   - Read `.beads/STATE.json`.
   - Confirm exactly one `feature_slug`.
   - If multiple active feature candidates exist, route to `user`.
2. Identify the current owner:
   - Trust live artifacts over stale handoff or scout output.
   - Use `beo-route` only when owner state is missing, stale, contradictory, or colliding.
3. Read the owner skill before mutation:
   - `STATE.json.current_owner` alone is not authorization to act.
   - Load the selected owner's `SKILL.md`.
   - Then read only the references listed by that owner for the current decision.
4. Preserve authority boundaries:
   - Cards summarize canonical facts.
   - Cards do not grant approval, readiness, review verdicts, route decisions, or mutation permission.
5. Emit the smallest legal next action:
   - Do not ask the user unless the answer can change acceptance, non-goals, compatibility, external approval, secrets/access, or legal/business decisions.

## First-pass operator path

1. Identify current owner from canonical state and live artifacts, not display cards.
2. If exactly one non-route owner predicate is true, continue that owner.
3. Use `beo-route` only when owner state is missing, stale, contradictory, or colliding.
4. Before mutation, require `PASS_EXECUTE`, a selected execution set, current approval, and approved scope.
5. After execution, review computes live diff independently before accept.
6. Display cards are operator-facing summaries only; canonical fields decide authority.

## Minimum read sets

### Before planning

Read:
- `STATE.json`
- current `CONTEXT.md`
- live bead graph when repairing existing beads

Do not plan if requirements are unlocked or contradicted.

### Before validation

Read:
- `STATE.json`
- locked `CONTEXT.md`
- current `PLAN.md`
- live bead graph
- current approval record, if present

Validation classifies readiness only; it does not edit `CONTEXT.md`, `PLAN.md`, or implementation files.

### Before execution mutation

Read:
- `STATE.json`
- `readiness-record.json`
- `approval-record.json`
- current `CONTEXT.md` and `PLAN.md` hashes
- selected execution set
- live bead claim/status evidence

Do not mutate without current `PASS_EXECUTE`, selected execution set, and matching approval envelope.

### Before review

Read:
- `execution-bundle.json`
- `approval-record.json`
- locked `CONTEXT.md`
- current `PLAN.md`
- live VCS/worktree diff

Review must compare live diff against bundle-reported changed files.

### After debug return

Read:
- `STATE.json.debug_return`
- debug result
- receiving owner contract
- approval/readiness surfaces if returning toward validation or execution

Debug evidence does not grant approval, readiness, rollback, or implementation authority.

## Workflow status card

```md
Workflow status:
  feature_slug:
  current_owner:
  status:
  current_phase:
  readiness:
  approval_ref:
  execution_set_id:
  blockers:
  next_legal_owner:
Authority note: display-only; canonical authority remains in the referenced state/artifact surface.
```

## Minimal happy path

| Step | Owner | Reads first | Writes | Next |
| --- | --- | --- | --- | --- |
| Requirements | `beo-explore` | intake + state/artifact references | `CONTEXT.md` | `beo-plan` |
| Planning | `beo-plan` | `CONTEXT.md`, artifacts, complexity, CLI | `PLAN.md`, bead graph | `beo-validate` |
| Readiness | `beo-validate` | `CONTEXT.md`, `PLAN.md`, approval/state | readiness + approval records | `beo-execute` on `PASS_EXECUTE` |
| Execution | `beo-execute` | approval record, selected execution set | code/tests/evidence bundle | `beo-review` |
| Review | `beo-review` | execution bundle, acceptance criteria | `REVIEW.md`, verdict | done / `beo-compound` / `beo-validate` |

Go mode is an operator macro over this flow; canonical behavior is in
`beo-reference -> go-mode.md`.

Before handing off from plan to validate, prefer one compact validation-facing pass over repeated validate/plan ping-pong.

## Owner boundary matrix

| Owner | Single decision | Writable surface | Must not do |
| --- | --- | --- | --- |
| `beo-route` | select exactly one owner | route/state evidence | perform downstream owner work |
| `beo-explore` | lock requirements | `CONTEXT.md` | plan or execute |
| `beo-plan` | create or repair current-phase graph | `PLAN.md`, bead graph metadata | approve or execute |
| `beo-validate` | classify readiness, mode, and approval action | approval/readiness records, readiness state | repair artifact content |
| `beo-execute` | deliver one approved execution set | approved product file scope and execution evidence | widen scope, diagnose unknown blocker, or coordinate workers |
| `beo-review` | emit one terminal verdict | `REVIEW.md`, bounded reactive-fix record | fix code |
| `beo-debug` | prove one blocker root cause | diagnostic evidence and debug return | patch or authorize rollback |
| `beo-compound` | record one feature learning outcome | feature learning record | cross-feature consolidation |
| `beo-dream` | consolidate cross-feature learning | shared learning guidance | treat one feature as corpus evidence by default |

## Read budget

Minimum reads per owner. Do not read beyond what the ownership predicate names.

| Owner | Minimum reads |
| --- | --- |
| `beo-route` | `STATE.json`, fresh `HANDOFF.json` if present, active `CONTEXT.md` when ambiguity exists |
| `beo-explore` | `STATE.json`, `CONTEXT.md` when present, applicable constraints |
| `beo-plan` | `STATE.json`, `CONTEXT.md`, current `PLAN.md`, bead graph evidence |
| `beo-validate` | `STATE.json`, `CONTEXT.md`, `PLAN.md`, approval record when present, bead readiness evidence |
| `beo-execute` | `STATE.json`, selected bead scope, approval record including `PLAN.md`/`CONTEXT.md` hashes, current `PLAN.md`, current `CONTEXT.md`, readiness record including `partial_progress_allowed`, verification contract |
| `beo-review` | `STATE.json`, `CONTEXT.md`, `PLAN.md`, approval record, execution bundle |
| `beo-debug` | `STATE.json`, failing artifact or command, blocker evidence, `debug_return` fields |
| `beo-compound` | `STATE.json`, accepted `REVIEW.md`, feature learning record when present |
| `beo-dream` | `STATE.json`, accepted feature learning records meeting threshold |

Canonical: `beo-reference -> skill-contract-common.md`.

## Session scout summary

Scout and status output are presentation only. They cannot select owners,
approve readiness, emit verdicts, select execution sets, or promote learning.
If scout output conflicts with canonical artifacts, trust canonical artifacts
and use `beo-route` only when owner state is missing, stale, contradictory, or
colliding.

```md
Current state:
- Feature:
- Current owner:
- Why this owner:
- Blocking evidence:
- Next legal action:
- Must read:
- Must not touch:
- Route required if:
```

## When unsure

Use `beo-route` only when owner state is missing, stale, contradictory, or
colliding. Do not re-route merely because a downstream owner found ordinary
artifact content to repair.

## Common failure -> owner quick map

Quick index only. Canonical routing remains in `beo-route`, `pipeline.md`,
`approval.md`, and `state.md`.

| Condition | Canonical owner |
| --- | --- |
| requirements missing or contradicted | `beo-explore` |
| plan or file-scope content incomplete/stale | `beo-plan` |
| stale approval before mutation | `beo-validate` |
| stale approval after mutation with changed files | `beo-review` or `beo-plan`, per canonical approval evidence |
| unproven root cause | `beo-debug` |
| owner state missing, stale, contradictory, or colliding | `beo-route` |
| multiple active feature candidates | `user` |

## Reactive-fix loop

When `beo-review` emits `fix` and the fix is bounded:

`beo-review -> beo-validate -> beo-execute -> beo-review`

Rules:
- review records bounded reactive-fix evidence
- validate decides whether a fresh `PASS_EXECUTE` can be emitted
- execute mutates only after selected execution set and approval envelope are current
- review emits the next terminal verdict

Do not route directly from review fix to execute.

## Tiny-work examples

### Example: one-line UI copy fix

Scenario: the user asks to change one visible string.

Expected path:
1. `beo-explore` locks the exact copy change and acceptance.
2. `beo-plan` writes a compact plan with one bead and one declared file scope.
3. `beo-validate` emits `PASS_EXECUTE` for one `single` execution set.
4. `beo-execute` mutates only the approved file.
5. `beo-review` checks changed files, verification, and approval reference before verdict.

Do not skip validation or review merely because the change is small. Compact planning reduces prose, not gates.

### Example: approval stale before mutation

Scenario: a plan file changed after approval, but no product file has been modified.

Expected path:
- If only approval freshness is stale and plan/scope remain unchanged: `beo-validate`.
- If plan, bead graph, scope, or verification contract needs repair: `beo-plan`.

Do not route directly to `beo-execute`.

### Example: small bug but root cause unknown

Scenario: a test fails during execution and the fix is not proven.

Expected path:
1. `beo-execute` stops mutation for the affected bead.
2. Record blocker evidence.
3. Route to `beo-debug` with `debug_return.return_to`.
4. `beo-debug` returns proven cause and safe unblock class only.
5. The receiving owner decides whether existing approval still applies.

Do not let debug output include patch text, approval, readiness, or rollback authorization.

## Communication contract

For route decisions, validation failures, blockers, review findings, and
handoffs, report in this order:
1. Plain-language summary
2. Current evidence
3. Why it matters
4. Concrete scenario
5. Next legal owner/action

## Exit packet

Return only from the canonical owner that owns the decision:
- decision
- evidence
- changed surfaces
- blocked_by
- next_owner
- next_owner_reason

## Canonical pointers

- owner selection -> `beo-route`
- legal transitions -> `beo-reference -> pipeline.md`
- go mode -> `beo-reference -> go-mode.md`
- approval -> `beo-reference -> approval.md`
- state/handoff -> `beo-reference -> state.md`
- learning -> `beo-reference -> learning.md`

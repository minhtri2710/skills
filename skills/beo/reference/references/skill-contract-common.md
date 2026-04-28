# Skill contract common

## Purpose

Shared mechanical contract doctrine for beo skill files. This file exists to reduce duplicate boilerplate. It must not own routing precedence, approval semantics, or owner-specific legal transitions.

## Shared required-input baseline
- Explicit user request or trusted route evidence.
- Current artifacts named by the ownership predicate.

## Shared optional-input baseline
- Prior `STATE.json` when present and valid.
- Prior `HANDOFF.json` when present and fresh.
- User clarification.

## Shared handoff discipline
- Write `HANDOFF.json` only for a real pause, checkpoint, external wait, or owner transfer that must survive beyond the current live session.
- Routine same-session owner transitions update `STATE.json` only.
- Unless a skill says otherwise, inherit handoff discipline from `beo-references -> state.md`.
- Only list a handoff section in the skill when the owner has a real exception.

## Shared evidence writing style
Use minimal decision-complete evidence.
- One field = one short sentence.
- Prefer refs to copied prose.
- Use `[]` for empty lists.
- Replace stale evidence instead of appending narrative history into `STATE.json`.
- Default to the shared decision packet unless the case involves a blocker, stale approval, review finding, swarm coordination, debug evidence, or user escalation.

## Shared state and handoff baseline

Every beo owner may write:
- `.beads/STATE.json` only under the shared STATE write baseline
- `.beads/HANDOFF.json` only under the shared handoff discipline

Owner-local `SKILL.md` files should list only additions beyond this baseline.
This baseline does not own routing precedence, approval semantics, artifact schemas, or owner-specific legal transitions.

## Shared decision packet

Every runtime owner exit should provide the smallest useful packet:
- `owner`: current owner name when the skill writes an explicit owner field; otherwise inherit `current_owner` from `STATE.json`
- `decision`: one-sentence owner decision
- `basis`: why this owner was valid
- `changed`: changed surfaces, or `[]`
- `blocked_by`: unresolved blocker, or `[]`
- `next_owner`: one legal owner, `user`, or `done`
- `next_owner_reason`: why that owner acts next
- `evidence_refs`: artifact, state, approval, or handoff refs that prove the decision
- `cleared_fields`: optional list of stale state fields cleared on exit, or `[]`

Use local extensions only when the owner owns extra state.
Examples:
- `beo-validate`: `readiness`, `approval_action`, `execution_mode`, `remediation_owner`, `approval_ref`
- `beo-route`: `matched_condition`, `disqualified_owners`
- `beo-debug`: `debug_return`, `debug_result`

Skill-local contracts should only add extra fields when they materially affect safety, routing, approval, review, or terminal completion.

## Ask-user threshold
Route to `user` only when the answer can change one of the following:
- acceptance
- non-goals
- compatibility
- external approval
- secret or access availability
- legal or business decision

Do not ask the user for an implementation detail that is already inside locked approved scope.

## Go-mode default assumption rule

When `go_mode.active=true`, do not route to `user` for design-only or
implementation-detail ambiguity that does not change acceptance, non-goals,
compatibility, external approval, secret/access, legal/business decision,
approved file scope, or verification.

Proceed with a conservative assumption and record it in the owning artifact or
`STATE.json.operator_view` according to `beo-references -> go-mode.md`.

## Shared forbidden surfaces baseline
Unless a skill explicitly lists an exception in `Writable surfaces`, treat the following as forbidden by default:
- artifacts, refs, fixtures, or product files owned by another skill
- deleted or merged legacy reference files
- runtime capability or pipeline topology

## Shared forbidden behaviors
- Do not select an owner outside the skill's `Allowed next owners`.
- Do not emit a next owner as `A or B`.
- Do not hide routing or collision logic in references.
- Do not mutate runtime topology unless that ownership is explicit.
- Do not keep stale optional state fields alive once superseded.

## Shared outputs baseline
Unless a skill says otherwise, `Outputs` should be assumed to be:
- minimal evidence for the primary owned decision
- successor or terminal result from the allowed list

Only list an `Outputs` section in the skill when the owner has an extra owner-specific output surface.

## Shared STATE write baseline
Unless a skill says otherwise, `STATE.json fields written` should be:
- `current_owner`
- `status`
- `evidence`

Only list extra state fields when that owner writes more than the baseline.
In `Writable surfaces`, prefer the short form: shared `STATE/HANDOFF` surfaces under `beo-references -> skill-contract-common.md` unless the skill adds extra state fields or exceptions.
When stale optional fields are removed, record them in `evidence.cleared_fields` using `beo-references -> state.md`.

## Loop guard
If the same feature returns between the same two owners twice without changed evidence, the current owner must record `loop_reason` and choose one of:
- simplify
- escalate to `user`
- route to `beo-debug`
- route to `beo-review`

## Writable-surfaces style
Keep `Writable surfaces` owner-specific.
- list only true write permissions
- prefer one line per writable surface family
- rely on the shared forbidden-surfaces baseline instead of re-describing what is not writable

## Shared state/handoff doctrine pointers
- First-pass operator view is in `beo-references -> operator-card.md`.
- State lifecycle, STATE field groups, stale-field cleanup, and handoff freshness are canonical in `beo-references -> state.md`.
- Go-mode macro behavior and operator assumption discipline are canonical in `beo-references -> go-mode.md`.
- Delivery order and legal owner transitions are canonical in `beo-references -> pipeline.md`.
- Routing precedence and owner collision doctrine are canonical in `beo-route`.
- Approval grant/refresh/invalidation doctrine is canonical in `beo-references -> approval.md`.

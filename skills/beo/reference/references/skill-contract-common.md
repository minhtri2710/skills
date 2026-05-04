## Contents

- Purpose
- Shared required-input baseline
- Shared optional-input baseline
- Shared handoff discipline
- Shared evidence writing style
- Shared state and handoff baseline
- Shared decision packet
- User disambiguation
- Read budget
- Skill must be loaded to act
- Ask-user threshold
- Go-mode default assumption rule
- Shared forbidden surfaces baseline
- Shared forbidden behaviors
- Shared outputs baseline
- Display card authority rule
- Shared STATE write baseline
- Writable-surfaces style
- Loop guard
- Artifact prose rule
- Canonical vocabulary registry
- RFC 2119 legend
- Shared state/handoff doctrine pointers

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
- After compaction, owners must re-read canonical surfaces before mutation.
- Unless a skill says otherwise, inherit handoff discipline from `beo-reference -> state.md`.
- Only list a handoff section in the skill when the owner has a real exception.

## Shared evidence writing style
Use minimal decision-complete evidence.
- One field = one short sentence.
- Prefer refs to copied prose.
- Use `[]` for empty lists.
- Replace stale evidence instead of appending narrative history into `STATE.json`.
- Default to the shared decision packet unless the case involves a blocker, stale approval, review finding, debug evidence, or user escalation.

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
- `beo-validate`: `readiness`, `approval_action`, `execution_mode`, `execution_set_id`, `execution_set_beads`, `partial_progress_allowed`, `remediation_owner`, `approval_ref`
- `beo-route`: `matched_condition`, `disqualified_owners`
- `beo-debug`: `debug_return`, `debug_result`

Skill-local contracts should only add extra fields when they materially affect safety, routing, approval, review, or terminal completion.

## User disambiguation

In all BEO doctrine, `user` means the human operator holding decision authority over the active feature:
- On `BLOCK_USER`, route to the human operator — not to an intermediate automation, orchestrating agent, or policy engine.
- If operating inside a multi-agent chain, `user` is the nearest human principal in the authorization chain.
- A policy engine may supply a pre-authorized answer only when a canonical policy record explicitly delegates that authority; absent such a record, treat the answer as requiring human confirmation.
- On `BLOCK_USER` conflicts between multiple principals (human, parent agent, policy), the human operator takes precedence.

## Read budget

Read only the artifact surfaces named by your ownership predicate before acting:
- Your skill's `SKILL.md` must be loaded before any mutation.
- `STATE.json` and `HANDOFF.json` when present.
- Only the specific artifact sections your ownership predicate requires.

Do not eagerly read `PLAN.md`, `REVIEW.md`, approval records, or execution bundles unless your ownership predicate names them. If total artifact size would exceed usable session context, use targeted section reads based on the predicate's specific evidence requirements.

## Skill must be loaded to act

An agent must load the owning skill's `SKILL.md` before performing any mutation. Identifying `STATE.json.current_owner` is not sufficient authorization to act; the hard stops and writable surfaces in the loaded skill contract must be in scope. A no-skill mutation is invalid even when the agent can verify the current owner from state.

If a required SKILL.md or required reference file is unreadable, missing, or cannot be loaded, stop immediately and route to `user` with the unreadable path and reason. Do not attempt doctrine repair, onboarding, or improvised continuation. Onboarding is not doctrine repair.

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
`STATE.json.operator_view` according to `beo-reference -> go-mode.md`.

## Shared forbidden surfaces baseline
Unless a skill explicitly lists an exception in `Writable surfaces`, treat the following as forbidden by default:
- artifacts, refs, fixtures, or product files owned by another skill
- deleted or merged reference files
- runtime capability or pipeline topology

## Shared forbidden behaviors
- Do not select an owner outside the skill's `Allowed next owners`.
- Do not emit a next owner as `A or B`.
- Do not hide routing or collision logic in references.
- Do not mutate runtime topology unless that ownership is explicit.
- Do not keep stale optional state fields alive once superseded.
- Do not perform a beo-owned mutation without loading the owning skill's `SKILL.md` first; identifying `STATE.json.current_owner` is not sufficient authorization to act.

## Shared outputs baseline
Unless a skill says otherwise, `Outputs` should be assumed to be:
- minimal evidence for the primary owned decision
- successor or terminal result from the allowed list

Only list an `Outputs` section in the skill when the owner has an extra owner-specific output surface.

## Display card authority rule

Cards are operator-facing summaries. They do not create, refresh, or override canonical authority.

A card may display:
- current canonical values
- evidence summary
- legal next owner suggestion when the loaded owner already has that authority

A card must not be treated as:
- approval
- readiness verdict
- selected execution set
- route decision
- review verdict
- learning promotion
- mutation permission

## Shared STATE write baseline
Unless a skill says otherwise, `STATE.json fields written` should be:
- `current_owner`
- `status`
- `evidence`

Any owner writing `.beads/STATE.json` should keep `operator_view` aligned with
the canonical fields and the owner decision being recorded, or omit/replace it
when it would be stale. The mirror is never canonical.

Only list extra state fields when that owner writes more than the baseline.
In `Writable surfaces`, prefer the short form: shared `STATE/HANDOFF` surfaces under `beo-reference -> skill-contract-common.md` unless the skill adds extra state fields or exceptions.
When stale optional fields are removed, record them in `evidence.cleared_fields` using `beo-reference -> state.md`.

## Writable-surfaces style
Keep `Writable surfaces` owner-specific.
- list only true write permissions
- prefer one line per writable surface family
- rely on the shared forbidden-surfaces baseline instead of re-describing what is not writable

## Loop guard

If the same feature returns between the same two owners twice without changed evidence, the current owner must record `loop_reason` and choose one of:
- simplify
- escalate to `user`
- route to `beo-debug`
- route to `beo-review`

## Artifact prose rule

When prose in `REVIEW.md`, `PLAN.md`, `CONTEXT.md`, or `STATE.json` conflicts with a schema record in `approval-record.json`, `execution-bundle.json`, or `readiness-record.json`, the artifact schema record takes precedence. See the full canonical precedence order in `beo-reference -> artifacts.md`.

## Canonical vocabulary registry

| Term | Canonical meaning |
| --- | --- |
| `bead` | one atomic unit of approved work in the bead graph; has an id, status, declared file scope, and dependency edges |
| `execution_set` | the unit of work selected by `beo-validate`; contains one or more beads with a mode (`single`, `ordered_batch`, `local_parallel`) |
| `PASS_EXECUTE` | the single positive readiness verdict emitted by `beo-validate`; authorizes `beo-execute` to claim and deliver the selected `execution_set` |
| `approval-record.json` | the canonical approval artifact written by `beo-validate`; contains file scope, verification contract, hashes, approved beads, and mode |
| `readiness-record.json` | the canonical validate decision artifact; records the full readiness classification and rationale for one `PASS_EXECUTE` or failure verdict |
| `execution-bundle.json` | the canonical execute artifact; records claimed beads, changed files, verification evidence, and partial/aggregate progress |
| `feature_slug` | the short stable identifier for an active feature; binds all artifacts in `.beads/artifacts/<feature_slug>/` |
| `doctrine_version_ref` | the git ref or schema version that was canonical at the time an artifact was written; provenance only |
| `BLOCK_USER` | a hard stop that requires human operator input before any beo owner can continue; see user disambiguation above |
| `state_seq` | advisory monotonic counter on `STATE.json`; incremented on every write; enables ordering and crash recovery |
| `go_mode` | an operator-authorized macro allowing conservative implementation-detail assumptions without per-step user confirmation; does not bypass approval, scope, or P0/P1 gates |

## RFC 2119 legend

BEO skill contracts and references use RFC 2119 key words where applicable:

| Word | Meaning |
| --- | --- |
| MUST / MUST NOT | absolute requirement or prohibition; violations are contract failures |
| SHOULD / SHOULD NOT | recommended behavior; deviations require explicit justification |
| MAY | permitted but not required |

When a skill uses "do not" without qualification, treat it as MUST NOT.

## Shared state/handoff doctrine pointers
- State lifecycle, STATE field groups, stale-field cleanup, and handoff freshness are canonical in `beo-reference -> state.md`.
- Go-mode macro behavior and operator assumption discipline are canonical in `beo-reference -> go-mode.md`.
- Delivery order and legal owner transitions are canonical in `beo-reference -> pipeline.md`.
- Routing precedence and owner collision doctrine are canonical in `beo-route`.
- Approval grant/refresh/invalidation doctrine is canonical in `beo-reference -> approval.md`.

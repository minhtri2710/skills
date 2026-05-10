# BEO Approval

## APP-01 — Complete approval envelope required

No product mutation may start unless current required surfaces prove:

- `PASS_EXECUTE`
- fresh `approval_ref`
- selected execution set
- supported execution mode (`single` or `ordered_batch`)
- declared file scope
- forbidden paths
- verification contract
- deterministic integrity pass (status: `verified`)

Missing any field stops execution. `beo-execute` cannot infer or assume missing fields from chat, BR description, memory, display cards, or summaries.

## APP-02 — Only validate grants approval

Only `beo-validate` may grant or refresh execution approval. No other owner may emit `PASS_EXECUTE`, refresh approval, select execution sets, declare approval fresh, or turn chat approval into execution authority.

## APP-03 — Approval becomes stale on approval-bearing changes

Approval becomes stale when approval-bearing content changes in `TICKET.md`, `CONTEXT.md`, `PLAN.md`, selected BR task descriptions, selected execution set, declared files, forbidden paths, generated outputs, verification contract, risk proof, rollback boundary, or required Human Gates.

When approval becomes stale, the owner that caused staleness must clear readiness/approval mirrors or mark tracker/ticket approval and integrity stale.

## APP-04 — Chat, display cards, BR descriptions, STATE, summaries, and command output do not grant approval

Execution approval exists only when the current approval surface records it. Chat messages, display cards, BR prose descriptions, `STATE.json` mirrors, summaries, fingerprint evidence, and command output are not approval.

Command output does not grant approval.

Only `beo-validate` may grant approval from current required surfaces and permitted integrity evidence.

A command name such as `bv` must not be interpreted as validation authority.

`approval_ref` is an identifier and evidence pointer. It is not permission by itself.

## APP-05 — Approval covers exactly one selected execution set

Approval is valid only for the selected execution set recorded at approval time. If the selected set is missing, changed, or contradicts `PLAN.md`, approval is invalid.

## APP-06 — Ordered batch stops on first blocked bead

For `ordered_batch` execution, stop on the first blocked bead. Do not continue to unaffected beads.

## Current approval surfaces

Tiny:
- `TICKET.md` Approval section

Standard:
- `TRACKER.json.readiness`
- `TRACKER.json.approval`
- `TRACKER.json.integrity`

Approval is invalid if any selected-set field is missing, stale, unsupported, contradictory, unavailable, or outside scope.

## Stale approval quick table

| Situation | Product mutation happened? | Root cause proven? | Next owner |
| --- | --- | --- | --- |
| Approval/integrity stale before first mutation | no | N/A | `beo-validate` if envelope unchanged; `beo-plan` if plan/scope/verification/BR changed |
| Approval/integrity stale after mutation begins | yes | yes | `beo-review` if evidence can be finalized; otherwise `beo-plan` |
| Approval/integrity stale after mutation begins | yes | no | `beo-debug` with return owner anchored |
| Selected execution set missing/stale | no | N/A | `beo-validate` |
| Scope outside approved envelope discovered | maybe | yes/no | stop; route by evidence to `beo-plan`, `beo-review`, or `beo-debug` |

## Stale after mutation handling

If approval/integrity becomes stale after product mutation began:

1. Stop further mutation.
2. Preserve execution evidence.
3. Record what changed and when staleness was discovered.
4. If changed files are inside approved declared scope and root cause is proven, finalize evidence and route to `beo-review` or `beo-plan` by finding.
5. If root cause is unproven, route to `beo-debug` with return owner anchored.
6. Never silently refresh approval from execute.

Rollback boundary and generated outputs are approval-bearing. Changing either stales approval.

## User authorization is not execution approval

User authorization, UAT, access, secret, legal, or business approval can satisfy a Human Gate, but only `beo-validate` creates execution approval. Approval and UAT gates never fallback to go-mode (HG-01).

## Learning non-authority

Learning has no runtime authority; see `references/learning.md`.

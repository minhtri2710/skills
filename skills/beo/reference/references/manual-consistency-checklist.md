# Manual Consistency Checklist

Use this checklist after doctrine edits. This is a manual review aid, not an eval suite, benchmark, fixture suite, or release gate.

## Runtime topology

- No `PASS_SERIAL` or `PASS_SWARM` verdict exists.
- `PASS_EXECUTE` is the only execution readiness pass classification.
- Execution modes are only `single` and `ordered_batch`.
- If an ordered batch blocks, the batch stops.

## Authority boundaries

- Display cards never grant approval, readiness, routing, review verdict, learning promotion, or mutation permission.
- Skill-local appendices do not hide fallback routing rules.
- Owner skills do not select owners outside their `Allowed next owners`.
- Each workflow rule has exactly one canonical home.

## Approval/readiness

- `PASS_EXECUTE` always has a selected execution set, current `approval_ref`, execution mode, and selected beads.
- Approval records distinguish `user_authorization_ref` from validate-owned `execution_approval`, and cover locked requirements, plan scope, bead graph, declared files, generated outputs, verification, risk proof, execution mode, execution set, approval evidence ref, and required exact hashes.
- Stale approval clears readiness and execution-set mirrors.
- Approval refresh is legal only when the envelope is unchanged and hashes still match; changed scope or execution envelope requires a new approval grant.

## State/handoff

- One active feature is named by `STATE.json.feature_slug`.
- `debug_return` is defined, consumed, or cleared before continuing.
- `closure` is present whenever `status=done`.
- Handoff is used only for pause/resume or transfer and never overrides fresher live artifacts.
- Optional stale state fields are cleared when superseded.
- Upward reclassification suspends inherited go mode before `PASS_EXECUTE` or `accept`.

## Triage and Human Gate

- Only `beo_tiny` and `standard` are runtime lanes.
- Tiny path reduces prose only; it does not bypass owner transitions, validation, approval, execution-set selection, review, or learning disposition.
- Human Gate is a `BLOCK_USER` subtype, not a new owner or approval artifact.
- Approval and UAT Human Gates never use fallback.
- Secret material is not persisted in Human Gate records.

## Review

- Review recomputes live changed-file evidence.
- Review compares live files against the finalized execution bundle and hash coverage.
- `REVIEW.md` verdict is emitted only by `beo-review`.
- P0/P1 findings block `accept`; P2 accept requires explicit non-blocking rationale; P3 is informational only.
- Decision Verification rows exist for every user-visible or acceptance-critical locked decision before `accept`, include Type and N/A reason, and reject N/A without reason.
- Tiny review uses the same accept gate with shorter prose.
- Review does not create reactive-fix beads; every fix routes to debug or plan.

## Debug

- Debug output contains no patch text.
- Debug does not grant approval, readiness, rollback, or mutation authority.
- Debug returns the smallest legal unblock action class and return owner.

## Learning

- Accepted closure defaults to `done` with `no-learning`.
- `beo-compound` runs only for durable-candidate or unclear single-feature learning evidence.
- `beo-dream` requires two accepted feature outcomes supporting the same pattern or explicit user instruction.
- `beo-compound` closes to `done` and records corpus candidates instead of auto-chaining to dream.
- Support skills do not route into runtime unnecessarily.

## Setup helper

- `beo-setup` exists only for setup/check/usage guidance.
- `beo-setup` is not listed in the normal runtime path.
- `beo-setup` writable surface is limited to `AGENTS.md`.
- `beo-setup` does not create or edit `.beads` runtime artifacts.
- `beo-setup` does not approve readiness, emit `PASS_EXECUTE`, select execution sets, execute, review, close, debug, or promote learning.
- `beo-setup` stops for malformed or duplicated BEO managed markers.
- `beo-setup` check-only mode does not write files.
- `beo-setup` apply mode only creates `AGENTS.md` or appends the managed block when unambiguous.

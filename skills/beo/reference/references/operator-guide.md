# BEO Operator Guide

Authority: explanatory only. This guide adds no owner authority, artifact field, readiness rule, enum, transition, approval mechanic, or writable surface.

## Load sequence

Before acting, load the active owner `SKILL.md`, `references/skill-contract-common.md`, current artifacts, and `registry/pipeline.json` before checking or emitting a `condition_id`. See `references/protocol-core.md` for invariants.

## Owner selection

Use `references/resume-resolution.md` for normal resume. Use `references/route-resolution.md` only when owner or feature identity is unsafe. STATE and HANDOFF are mirrors, never authority.

## Human Gates

If guessing could affect scope, acceptance, non-goals, compatibility, security, privacy, access, legal, business, approval, user-visible commitment, or irreversible action, record a Human Gate. `beo-explore` records gate status; `beo-validate` evaluates status but never resolves gates. See `references/decision-boundaries.md`.

## Approval flow

`beo-validate` alone emits approval/readiness. `beo-execute` rechecks a fresh approval envelope before mutation. Helper output is integrity evidence only. See `references/approval.md`.

## Debug flow

Debug proves a root cause and does not patch, plan, approve, or verdict. Calls to debug that expect return must include transition provenance with `return_to_caller`. See `references/transition-provenance.md`.

## Repair flow

Review fix/reject results create new scoped work. Proven bounded repairs route to `beo-plan`; unproven root-cause questions route to `beo-debug`. Product mutation still requires `beo-validate -> PASS_EXECUTE -> beo-execute`.

## Density choice

Compact/single-ticket is for one bounded item with narrow files and simple verification. Use full for multi-item work, repair/rollback sets, broad risk, complex generated outputs, or uncertain compact eligibility. See `references/density.md`.

## Abandonment

User cancellation uses `user_abandoned -> done` where legal in `registry/pipeline.json`. Abandonment closes runtime lifecycle and does not mutate product files. See `references/lifecycle.md`.

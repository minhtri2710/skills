# State and Handoff

Authority: canonical for `.beads/STATE.json` and `HANDOFF.json` semantics. Transition provenance and meta-target resolution live in `beo-reference -> references/transition-provenance.md`.

STATE and HANDOFF are context mirrors only. They never authorize action, override current required artifacts, replace the loaded owner `SKILL.md`, grant approval, refresh integrity, select execution scope, or emit review verdicts.

## STATE purpose

STATE may orient startup and resume:

```json
{
  "feature_slug": "<slug>",
  "current_owner": "beo-plan",
  "artifact_root": ".beads/artifacts/<slug>",
  "last_transition": { "...": "..." },
  "resume_hint": "<optional>"
}
```

STATE must not grant approval, select execution sets, override artifact authority, resolve meta-targets without provenance, or reopen abandoned/closed work directly.

## HANDOFF purpose

HANDOFF is transition evidence. It must contain transition provenance:

```json
{
  "feature_slug": "<slug>",
  "artifact_root": ".beads/artifacts/<slug>",
  "from_owner": "beo-plan",
  "to_owner": "beo-validate",
  "condition_id": "plan_complete",
  "created_at": "<RFC3339 UTC>",
  "required_reads": [
    "FEATURE.json",
    "TICKET.md or PLAN.md",
    "registry/pipeline.json"
  ],
  "transition": {
    "from_owner": "beo-plan",
    "condition_id": "plan_complete",
    "to_owner": "beo-validate",
    "feature_slug": "<slug>",
    "artifact_root": ".beads/artifacts/<slug>",
    "created_at": "<RFC3339 UTC>",
    "basis_ref": "PLAN.md#handoff"
  }
}
```

If `from_owner`, `to_owner`, `condition_id`, `feature_slug`, `artifact_root`, or `created_at` differs between top-level fields and `transition`, the handoff is contradictory and fails closed.

## Identity mirrors

`FEATURE.json.current_owner`, `.beads/STATE.json.current_owner`, and `HANDOFF.json.to_owner` may help resume after context loss, but current artifacts and the loaded owner contract decide whether action is legal.

When mirrors disagree, `beo-route` repairs identity metadata from current artifact evidence. Route does not change requirements, plan, approval, execution evidence, review verdicts, or product files.

## Transition write exception

When a legal transition is emitted, the outgoing active owner may write `.beads/STATE.json` and feature-local `HANDOFF.json` only for transition metadata, including `transition`.

This exception does not permit writing product files, approval, review verdicts, runtime artifacts owned by another owner, or any content that changes canonical artifact authority.

## Route repair write exception

`beo-route` may repair only stale identity metadata: active feature pointer in `.beads/STATE.json`, `current_owner` metadata when artifacts clearly prove it, or handoff identity metadata when transition evidence is fresh and legal. It may not change requirements, plan, approval, execution evidence, review verdict, or product files.

Accepted closure may neutralize active STATE pointers only as lifecycle bookkeeping after the review-owned final verdict exists. STATE never closes a feature or emits, revises, or substitutes for the review verdict.

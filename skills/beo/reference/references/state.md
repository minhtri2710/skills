# State and Handoff

Authority: canonical for `.beads/STATE.json` and `HANDOFF.json` semantics.

STATE and HANDOFF are context mirrors only. They never authorize action, override current required artifacts, replace the loaded owner `SKILL.md`, grant approval, refresh integrity, select execution scope, or emit review verdicts.

## Identity Mirrors And Meta-targets

`FEATURE.json.current_owner`, `.beads/STATE.json.owner`, and `HANDOFF.json.to_owner` are mirrors of artifact-derived owner identity. They may help resume after context loss, but current artifacts and the loaded owner contract decide whether action is legal.

When mirrors disagree, `beo-route` repairs identity metadata from current artifact evidence. Route does not change requirements, plan, approval, execution evidence, review verdicts, or product files.

`return_to_caller` and `restored_owner` are meta-targets, not owners. `return_to_caller` means return from a temporary owner to fresh, legal caller metadata. `restored_owner` is symbolic route completion, not a final concrete owner by itself. After route repairs identity mirrors, the concrete target comes from `references/resume-resolution.md`.

## Transition State Write Exception

When a legal transition is emitted, the outgoing active owner may write `.beads/STATE.json` and feature-local `HANDOFF.json` only for transition metadata.

This exception does not permit writing product files, approval, review verdicts, runtime artifacts owned by another owner, or any content that changes canonical artifact authority.

## Suggested Fields

```json
{
  "owner": "beo-<owner>",
  "feature_slug": "<slug>",
  "artifact_density": "compact | full",
  "caller_owner": "<optional owner used only for return_to_caller>",
  "caller_condition_id": "<optional condition that entered the temporary owner>",
  "updated_at": "<timestamp>",
  "handoff_ref": "<optional>"
}
```

`caller_owner` and `caller_condition_id` are transition metadata only. `beo-route` may use them to resolve `return_to_caller` only when they are fresh, match the originating transition, and do not contradict current artifact evidence.

## Route Repair Write Exception

`beo-route` may repair only stale identity metadata: active feature pointer in `.beads/STATE.json`, `current_owner` metadata when artifacts clearly prove it, or handoff identity metadata when transition evidence is fresh and legal. It may not change requirements, plan, approval, execution evidence, review verdict, or product files.

Accepted closure may neutralize active STATE pointers only as lifecycle bookkeeping after the review-owned final verdict exists, so new feature startup cannot inherit stale owner identity. STATE never closes a feature or emits, revises, or substitutes for the review verdict.

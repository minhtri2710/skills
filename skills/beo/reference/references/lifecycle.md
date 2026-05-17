# Lifecycle

Authority: canonical human-readable lifecycle narrative. Transition topology lives only in `registry/pipeline.json`.

## Normal path

```text
beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done
```

Accepted review closes runtime work before optional `beo-learn` maintenance handoff.

## Feature lifecycle status

`FEATURE.json.lifecycle_status` uses `active | closed | reopened | abandoned` unless `registry/vocabulary.json` deliberately changes it.

Closed or abandoned features cannot execute again without explicit reopen and fresh approval. Reopen enters `beo-explore` for changed requirements or `beo-plan` for bounded repair, never directly `beo-execute`.

## Abandonment

User cancellation is represented by the legal `user_abandoned -> done` transition for runtime owners named in `registry/pipeline.json`. Abandonment is lifecycle closure, not product mutation.

Abandoned runtime work records:

```json
{
  "lifecycle_status": "abandoned",
  "closure": {
    "status": "abandoned",
    "reason_ref": "user message or artifact note",
    "closed_at": "<RFC3339 UTC>",
    "closed_by_owner": "<current_owner>"
  }
}
```

The owner emitting `user_abandoned` writes this abandonment lifecycle bookkeeping as part of the terminal transition, even if it does not otherwise own review closure. Abandoned work cannot resume execution directly; it must reopen through `start -> reopened_bounded_repair -> beo-plan` or a new feature request.

## Repair paths

```text
verdict_fix_bounded_repair | verdict_reject -> beo-plan -> plan_complete -> beo-validate -> PASS_EXECUTE -> beo-execute -> execution_ready_for_review -> beo-review
verdict_fix_unproven_root_cause -> beo-debug -> root_cause_proven -> return_to_caller -> resume-selected owner
owner_feature_identity_unsafe -> beo-route -> identity_repaired -> restored_owner -> resume-selected owner
```

Fixes are new scoped work. Review can request a fix but cannot patch. Debug proves cause but does not choose repair scope. Execute can patch only with current approval.

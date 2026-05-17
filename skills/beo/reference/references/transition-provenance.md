# Transition Provenance

Authority: canonical handoff provenance and meta-target resolution.

## Transition object

Every owner-to-owner handoff must include a `transition` object:

```json
{
  "transition": {
    "from_owner": "beo-plan",
    "condition_id": "plan_complete",
    "to_owner": "beo-validate",
    "feature_slug": "<slug>",
    "artifact_root": ".beads/artifacts/<slug>",
    "created_at": "<RFC3339 UTC>",
    "basis_ref": "<artifact section or handoff id>",
    "artifact_hash_ref": "<optional hash/projection ref>"
  }
}
```

`transition.from_owner`, `condition_id`, and `to_owner` must match `registry/pipeline.json`. `feature_slug` and `artifact_root` must match current artifact authority. If top-level HANDOFF fields and `transition` fields disagree, the handoff is contradictory and fails closed.

## Temporary owner return

Temporary owner calls must include `transition.return`:

```json
{
  "transition": {
    "from_owner": "beo-review",
    "condition_id": "verdict_fix_unproven_root_cause",
    "to_owner": "beo-debug",
    "feature_slug": "<slug>",
    "artifact_root": ".beads/artifacts/<slug>",
    "created_at": "<RFC3339 UTC>",
    "basis_ref": "<artifact section or handoff id>",
    "return": {
      "meta_target": "return_to_caller",
      "return_target_owner": "beo-review",
      "return_condition_id": "root_cause_proven",
      "return_basis_required": "debug diagnosis artifact with diagnosis_status=root_cause_proven"
    }
  }
}
```

## `return_to_caller`

`return_to_caller` resolves only when the active handoff contains fresh transition provenance with a `return` object.

Required evidence:

- `transition.from_owner`
- `transition.condition_id`
- `transition.to_owner`
- `transition.return.meta_target`
- `transition.return.return_target_owner`
- `transition.return.return_condition_id`
- `transition.return.return_basis_required`
- matching `feature_slug`
- matching `artifact_root`
- current result artifact named by `transition.return.return_basis_required`

If any field is missing, stale, contradictory, unavailable, or illegal under `pipeline.json`, stop fail-closed. Chat memory, summaries, STATE alone, and helper output cannot resolve this meta-target.

## `restored_owner`

`restored_owner` resolves only after `beo-route` has proven and repaired an unsafe owner/feature identity defect from artifacts. The concrete owner is selected by `beo-reference -> references/resume-resolution.md` after repair. If the repair evidence is missing, stale, contradictory, or illegal under `pipeline.json`, stop fail-closed.

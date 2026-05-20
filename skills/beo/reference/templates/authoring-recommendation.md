---
type: beo-authoring-recommendation
bead_id: <br-id>
source_learning_case: <path/ref>
created: <iso8601>
---

# Authoring Recommendation

```yaml
authoring_recommendation:
  decision: update_existing_skill|create_new_skill|update_reference|update_registry|update_template|none
  target:
  evidence_refs:
    - <ref>
  rationale: <why this doctrine/skill change is justified>
  safety_invariant_preserved: true
```

## Proposed change

<short description>

## Non-goals

- Do not mutate product files.
- Do not weaken kernel invariants.
- Do not reopen delivery.
- Do not propose a curated learning file; reusable behavior belongs in skills, doctrine, templates, or registries.

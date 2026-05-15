# Approval

Authority: canonical human doctrine for approval, freshness, integrity, and helper authority.

Only `beo-validate` may grant or refuse `PASS_EXECUTE`, write approval fields, select an execution set, or refresh approval.

For canonical terminology, see `beo-reference -> references/glossary.md`.

## Approval in one paragraph

`beo-validate` approves a normalized execution contract from the current requirement, scope, Human Gate, execution-set, verification, readiness, integrity, and mode fields. The approval ref records the approved snapshot. Helper output can prove whether current artifacts still match that approval, but the helper never grants approval. If any approval-bearing source changes, approval is stale until `beo-validate` refreshes or refuses it.

| Term | Operator meaning | Machine surface |
|---|---|---|
| `PASS_EXECUTE` | validate says execute may act | `readiness` |
| Approved execution contract | what validate approves | approval-envelope fields |
| Approval ref | approved snapshot record | `approval_ref` |
| Current helper verification | evidence current artifacts still match approval | `integrity` and helper output |
| Authority block | parseable artifact truth | `beo.ticket.v1` / `beo.context.v1` / `beo.plan.v1` |

## Approval model

`PASS_EXECUTE` means the current approval-bearing projection is complete, internally consistent, Human Gates are resolved or `not_applicable`, an execution set is selected, integrity is verified, and no current required artifact contradicts the envelope.

Approval binds the exact approval-bearing projection. If an approval-bearing source changes, approval is stale until `beo-validate` re-establishes it.

Execution/review evidence is not approval-bearing by default unless it reveals contradiction, scope change, forbidden path, unresolved Human Gate, or changed integrity basis.

Human Gate status is approval-bearing; see `beo-reference -> references/decision-boundaries.md`.

In compact shorthand, `PASS_EXECUTE` is evaluated against the derived approval-bearing projection, not the raw shorthand alone.

## Approval-bearing projection

The approval-bearing projection is the normalized set of current requirement, scope, Human Gate, execution-set, verification, readiness, integrity, and mode fields that `beo-validate` binds to approval. It excludes execution/review evidence unless that evidence exposes a contradiction or scope/integrity change.

Compact artifacts store shorthand; the helper derives the approval-bearing projection. Full artifacts bind the corresponding canonical fields from `CONTEXT.md` and `PLAN.md`.

`PASS_EXECUTE` requires structured authority blocks. Documented markdown sections may orient compact draft work, but they cannot satisfy approval-bearing checks or produce current approval/integrity evidence without a `beo.ticket.v1` authority block. Helper diagnostics may detect markdown-only drafts only to report the missing block; they must not derive approval fields from markdown headings.

Authority YAML is the BEO subset: objects, lists, strings, numbers, booleans, and null. Anchors, aliases, custom tags, and non-subset YAML features are invalid for authority blocks.

## Approval ref

Target `approval_ref` shape:

```yaml
approval_ref:
  id: approval-<id>
  schema_version: beo.approval_ref.v1
  approved_by_owner: beo-validate
  approved_at: <RFC3339 UTC>
  artifact_density: compact | full
  selected_execution_set: <id>
  execution_mode: normal
  approval_projection_rule: compact_shorthand_derived | full_plan_explicit
  envelope_hash: sha256:<hash>
  artifact_hashes:
    approval_bearing_projection: sha256:<hash>
```

`approval_ref.artifact_hashes.approval_bearing_projection` is the approved snapshot hash. The `integrity` object records helper evidence for a check; it does not replace the approved snapshot hash.

## Integrity

Target `integrity` shape:

```yaml
integrity:
  status: verified | invalid | unavailable
  evidence_ref: beo_approval_check:<run-id>
```

`evidence_ref` is required when `status: verified`.

Artifact-recorded `integrity.status` documents a previous check only. It is not live execution authority. `beo-execute` must call `beo_approval_check` fresh before mutation, and only live helper output with `approval_envelope_status: complete` permits mutation.

Execution evidence must record:

```yaml
pre_execution_integrity_check:
  helper: beo_approval_check
  evidence_ref: beo_approval_check:<run-id>
  approval_envelope_status: complete | invalid | unavailable
```

## Freshness

Missing, stale, invalid, contradictory, or unavailable approval/integrity blocks `PASS_EXECUTE`.

Approval remains current only while the approval-bearing projection, selected execution set, execution mode, integrity basis, and Human Gate status remain unchanged.

## Repair and rollback approval

Repair and rollback are selected execution sets with `kind: repair` or `kind: rollback`. They require normal `beo-plan -> beo-validate -> beo-execute` approval. No repair path preserves or bypasses approval outside selected execution-set approval.

## Machine integrity

The exact projection fields, hash inputs, approval ref shape, and helper checks are defined by:
- `beo-reference -> registry/approval-envelope.json`
- `beo-reference -> registry/artifact-schemas.json`
- `beo-reference -> scripts/beo_approval_check.py`

The helper is read-only evidence. It cannot grant approval, refresh approval, authorize mutation, select execution sets, override artifacts, or downgrade fail-closed conditions.

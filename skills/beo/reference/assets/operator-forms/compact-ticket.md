# Compact Ticket Operator Form
<!-- beo:operator-form:compact-ticket -->

Authority: advisory operator form only. Canonical artifact rules live in `beo-reference -> references/artifacts.md`, approval rules in `beo-reference -> references/approval.md`, Human Gate rules in `beo-reference -> references/decision-boundaries.md`, and field shapes in `beo-reference -> registry/artifact-schemas.json`.

When creating a live `TICKET.md`, copy only fields owned by the current phase. Do not copy commented future-owned fields into live authority blocks.

Use visibly non-literal placeholders. Do not synthesize approval hashes; copy helper-produced hashes exactly, including the `sha256:` prefix. `approved_at` uses `YYYY-MM-DDTHH:MM:SSZ`.

```yaml beo.ticket.v1
# Explore-owned fields.
artifact_density: compact
owner: beo-explore
request: <one bounded request>
done:
  - <acceptance criterion>
human_gates:
  status: not_applicable
  gates: []
  # When status is resolved or unresolved, use:
  # gates:
  #   - id: HG-1
  #     type: clarification
  #     question: <human-facing decision>
  #     affects:
  #       - scope
  #     resolution_status: unresolved
  #     resolution_ref: <artifact section | user message ref | env:HANDLE>
# assumptions:
#   - <low-risk reversible assumption>
# non_goals:
#   - <constraint that maps to non_goal_constraints>
# constraints:
#   - <bounded constraint>

# Plan-owned fields. Copy only when beo-plan acts.
# Schema field path: scope.files.allow
# scope:
#   files:
#     allow:
#       - <relative/path.ext>
#     # Schema field path: scope.files.forbid
#     forbid: []
#   # Schema field path: scope.item
#   item: <one bounded execution item>
#   # Schema field path: scope.verify
#   verify:
#     commands:
#       - <verification command>
# generated_outputs: not_applicable
# risk_scope: not_applicable
# rollback_boundary: not_applicable

# Validate-owned fields. Copy only when beo-validate acts.
# readiness: PASS_EXECUTE
# approval_ref:
#   id: approval-<id>
#   schema_version: beo.approval_ref.v1
#   approved_by_owner: beo-validate
#   approved_at: "YYYY-MM-DDTHH:MM:SSZ"
#   artifact_density: compact
#   selected_execution_set: set-1
#   execution_mode: normal
#   approval_projection_rule: compact_shorthand_derived
#   envelope_hash: <helper-produced sha256:...>
#   artifact_hashes:
#     approval_bearing_projection: <helper-produced sha256:...>
# integrity:
#   status: verified
#   evidence_ref: beo_approval_check:<run-id>
# selected_execution_set: set-1
# execution_mode: normal

# Execute-owned fields. Copy only when beo-execute records evidence.
# pre_execution_integrity_check:
#   helper: beo_approval_check
#   evidence_ref: beo_approval_check:<run-id>
#   approval_envelope_status: complete
# changed_files:
#   - <relative/path.ext>
# verification_evidence:
#   - command: <verification command>
#     status: passed
#     evidence_ref: <log or observation ref>
# review_status: ready_for_review
# blocker: none

# Review-owned fields. Copy only when beo-review emits verdict.
# verdict: accept
# evidence:
#   - <review evidence ref>
# findings: []
# closure:
#   status: closed
#   closed_at: "YYYY-MM-DDTHH:MM:SSZ"
```

Notes:
- If `human_gates.status` is `not_applicable`, omit `gates` or keep it empty.
- Per-gate fields are `type`, `affects`, `resolution_status`, and `resolution_ref`; do not use aliases like `answer_ref` or per-gate `status`.
- `integrity.evidence_ref` is required only when `integrity.status: verified`; omit it for `invalid` or `unavailable`.
- Review `verdict` values are `accept`, `fix`, or `reject`; pipeline condition IDs are not verdict values.
- Compact execution evidence for review requires non-empty `changed_files`, non-empty `verification_evidence`, `review_status: ready_for_review`, no active blocker, and `pre_execution_integrity_check.approval_envelope_status: complete`.

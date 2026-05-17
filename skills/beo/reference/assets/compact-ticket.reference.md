# BEO Compact Ticket Reference

Authority: advisory drafting aid only. Canonical rules live in `references/artifacts.md`, `references/density.md`, `registry/artifact-schemas.json`, and `registry/approval-envelope.json`.

```yaml beo.ticket
artifact_density: compact
ticket_id: <ticket id>
title: <title>
lifecycle_status: active | closed | reopened | abandoned
phase_status: draft | planned | approved | executing | ready_for_review | blocked
current_owner: beo-explore
created_from_request: <source request ref>
owner: beo-explore

request: <one bounded request>
done:
  - <explore-owned user-facing done criterion>
human_gates:
  status: not_applicable
  gates: []
assumptions: []
non_goals: []
constraints: []

# beo-plan owns these fields after requirements lock:
# scope:
#   files:
#     allow:
#       - <relative/path.ext>
#     forbid: []
#   item: <one bounded execution item>
#   verify:
#     commands:
#       - <verification command>
# acceptance_criteria:
#   - <plan-owned approval-bearing criterion>
# generated_outputs: not_applicable
# risk_scope: not_applicable
# rollback_boundary: not_applicable
#
# beo-validate owns these fields after plan completion:
# readiness: PASS_EXECUTE
# selected_execution_set: set-1
# execution_mode: normal
# approval_ref:
#   id: approval-<id>
#   approved_by_owner: beo-validate
#   approved_at: "YYYY-MM-DDTHH:MM:SSZ"
#   artifact_density: compact
#   selected_execution_set: set-1
#   execution_mode: normal
#   approval_projection_rule: compact_derived
#   envelope_hash: sha256:<hash>
#   artifact_hashes:
#     approval_bearing_projection: sha256:<hash>
# integrity:
#   status: verified
#   evidence_ref: beo_approval_check:<run-id>
#
# beo-execute owns these fields after approval:
# execution_status: ready_for_review
# pre_execution_integrity_check:
#   helper: beo_approval_check
#   evidence_ref: beo_approval_check:<run-id>
#   approval_envelope_status: complete
# changed_files:
#   - <relative/path.ext>
# verification_evidence:
#   - command: <verification command>
#     status: passed
#     evidence_ref: <log ref>
# review_status: ready_for_review
# blocker: none
# execution_notes: []
#
# beo-review owns these fields after execution:
# verdict: accept
# findings: []
# review_evidence:
#   - evidence_ref: <artifact, command output, diff, or observation ref>
#     status: checked
# closure:
#   status: closed
#   closed_at: "YYYY-MM-DDTHH:MM:SSZ"
#   closed_by_owner: beo-review
# learning_candidate: false
```

Secret gate values must never be stored; store handles such as `env:PROVIDER_API_TOKEN`.

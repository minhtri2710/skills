```yaml beo.ticket
schema_version: beo-beads/v3
issue_id: <br-id>
mode: standard
request: <bounded request>
done:
  - <completion criterion>
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - <path>
    forbid: []
  verify:
    commands:
      - <verification command>
acceptance_criteria:
  - <criterion>
atomicity:
  decision: atomic
  reason: <why this is one executable unit>
  rejects_multi_task: true
generated_outputs: []
external_side_effects:
  status: none
  effects: []
stateful_external_systems:
  status: none
  systems: []
risk_scope: <bounded repo-only risk>
rollback_boundary: revert_declared_file_changes
flow_profile: standard_repo_edit
```

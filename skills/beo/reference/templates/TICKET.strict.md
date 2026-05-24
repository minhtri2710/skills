```yaml beo.ticket
schema_version: beo-beads/v3
issue_id: <br-id>
mode: strict
request: <bounded request>
done_target: <single atomic completion target>
done:
  - <completion criterion>
human_gates:
  status: resolved
  gates:
    - type: authorization
      affects: side_effect
      evidence_ref: <safe handle>
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
  status: declared
  effects:
    - type: <deployment|database_migration|cloud_resource|package_publish|email_send|payment|billing|destructive_operation>
      target: <system>
      authorization_ref: <safe handle>
      precheck: <command/evidence>
      rollback_or_compensation: <plan/ref>
      postcheck: <command/evidence>
      blast_radius: <bounded impact>
stateful_external_systems:
  status: declared
  systems:
    - name: <system>
      effect_ref: <same-as-external-side-effect-target>
risk_scope: <risk and blast radius>
rollback_boundary: explicit_rollback_plan
authorization_refs:
  - <safe handle>
strict:
  reason: <why strict mode is required>
  artifact_hashes:
    STRICT.md: <sha256>
    ROLLBACK.md: <sha256>
flow_profile: strict_external
```

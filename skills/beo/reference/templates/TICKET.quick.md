```yaml beo.ticket
schema_version: beo-beads/v3
issue_id: <br-id>
mode: quick
request: <bounded request>
done_target: <single atomic completion target>
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
      - git diff --check
acceptance_criteria:
  - <criterion>
atomicity:
  decision: atomic
  reason: <why this is one executable unit>
  rejects_multi_task: true
generated_outputs: []
```

# BEO Compact Ticket

Compact approval-bearing and owner-bearing authority lives inside the `beo.ticket` block. Headings are display only.

```yaml beo.ticket
artifact_density: compact
ticket_id: <ticket id>
title: <title>
lifecycle_status: active
phase_status: draft
current_owner: beo-explore
created_from_request: <source request ref>
owner: beo-explore

request: <one bounded request>
done:
  - <user-facing done criterion>
human_gates:
  status: not_applicable
  gates: []
assumptions: []
non_goals: []
constraints: []
```

Future-owned fields stay absent until the owning phase acts.

# Negative Trace: Repair Rescope Required

This trace shows a review finding that cannot be repaired under the same scope because it requires modifying a file not in the approved files list.

## Scenario

- `beo-execute` completes execution.
- During `beo-review`, the auditor finds that a bug fix was incomplete and needs changes in `utils.py`.
- However, `utils.py` is not in the allowed list of `TICKET.yaml`.
- The reviewer must issue a finding requiring a rescope.

## Finding record in state.json

```json
{
  "review": {
    "actor": "beo-review",
    "verdict": "repair_rescope",
    "route_condition_id": "repair_rescope",
    "findings": [
      {
        "severity": "blocker",
        "category": "scope",
        "message": "Fix requires changing utils.py which is not allowed by current ticket scope.",
        "evidence_refs": [".beads/artifacts/br-104/checks/test_failure.log"],
        "recommended_route": "repair_rescope"
      }
    ],
    "done_criteria_coverage": [],
    "repair_count": 0,
    "closed_in_br": false
  }
}
```

## Expected Route

- **Condition**: `repair_rescope`
- **Route**: `repair_rescope` -> `beo-plan`

## Outcomes

- `repair_same_scope` is forbidden because a new file path must be added to the allow list.
- A new ticket planning iteration is required to change approved scope.

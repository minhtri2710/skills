# Quick Mode Golden Trace

This is an agent pattern contract showing the expected state transitions and artifacts for a successful quick mode delivery.

## Input: br issue

```json
{
  "issue_id": "br-101",
  "title": "Fix readme typo",
  "status": "open",
  "claim": {
    "actor": "beowulf",
    "claimed_at": "2026-06-02T13:00:00Z"
  }
}
```

## After beo-plan: TICKET.json

```json
{
  "version": 1,
  "issue_id": "br-101",
  "mode": "quick",
  "request": "Fix typo in README.md from 'recieve' to 'receive'",
  "done_criteria": [
    "The word 'receive' is correctly spelled in README.md"
  ],
  "scope": {
    "files": {
      "allow": ["README.md"],
      "forbid": []
    },
    "generated_outputs": [],
    "verify": {
      "commands": ["grep -i 'receive' README.md"]
    }
  }
}
```

## After beo-plan: state.json

```json
{
  "version": 1,
  "issue_id": "br-101",
  "phase": "planned",
  "phase_sequence_id": 1,
  "approval": {
    "status": "pending",
    "approved_by": null,
    "actor": null,
    "ticket_file_hash": null,
    "approval_projection_hash": null,
    "repo_head": null,
    "prestate": {},
    "failure_category": null,
    "approved_phase_sequence_id": null
  },
  "execution": {
    "actor": null,
    "started_at": null,
    "completed_at": null,
    "changed_files": [],
    "verify_results": [],
    "evidence_refs": []
  },
  "review": {
    "actor": null,
    "verdict": null,
    "route_condition_id": null,
    "findings": [],
    "done_criteria_coverage": [],
    "repair_count": 0,
    "closed_in_br": false
  },
  "metadata": {
    "last_owner": "beo-plan",
    "updated_at": "2026-06-02T13:02:00Z"
  }
}
```

## After beo-validate: state delta

```json
{
  "phase": "approved",
  "phase_sequence_id": 2,
  "approval": {
    "status": "PASS_EXECUTE",
    "approved_by": "beo-validate",
    "actor": "beowulf",
    "ticket_file_hash": "a1b2c3d4...",
    "approval_projection_hash": "e5f6g7h8...",
    "repo_head": "9i0j1k2l...",
    "prestate": {
      "README.md": "sha256:..."
    },
    "failure_category": null,
    "approved_phase_sequence_id": 1
  },
  "metadata": {
    "last_owner": "beo-validate",
    "updated_at": "2026-06-02T13:03:00Z"
  }
}
```

## After beo-execute entry: executing-state delta

```json
{
  "phase": "executing",
  "phase_sequence_id": 3,
  "execution": {
    "actor": "beowulf",
    "started_at": "2026-06-02T13:04:00Z",
    "completed_at": null,
    "changed_files": [],
    "verify_results": [],
    "evidence_refs": []
  },
  "metadata": {
    "last_owner": "beo-execute",
    "updated_at": "2026-06-02T13:04:00Z"
  }
}
```

## After beo-execute completion: executed-state delta

```json
{
  "phase": "executed",
  "phase_sequence_id": 4,
  "execution": {
    "actor": "beowulf",
    "started_at": "2026-06-02T13:04:00Z",
    "completed_at": "2026-06-02T13:05:00Z",
    "changed_files": ["README.md"],
    "verify_results": [
      {
        "command": "grep -i 'receive' README.md",
        "exit_code": 0,
        "stdout": "Please receive updates."
      }
    ],
    "evidence_refs": [".beads/artifacts/br-101/checks/verify.log"]
  },
  "metadata": {
    "last_owner": "beo-execute",
    "updated_at": "2026-06-02T13:05:00Z"
  }
}
```

## After beo-review: reviewed-state delta

```json
{
  "phase": "reviewed",
  "phase_sequence_id": 5,
  "review": {
    "actor": "beo-review",
    "verdict": "accept",
    "route_condition_id": "verdict_accept",
    "findings": [],
    "done_criteria_coverage": [
      {
        "criterion": "The word 'receive' is correctly spelled in README.md",
        "status": "covered",
        "evidence_refs": [".beads/artifacts/br-101/checks/verify.log"]
      }
    ],
    "repair_count": 0,
    "closed_in_br": true
  },
  "metadata": {
    "last_owner": "beo-review",
    "updated_at": "2026-06-02T13:06:00Z"
  }
}
```

## Expected runtime-events.jsonl

No normal event file required (file remains empty or is not created because no non-normal events occurred).

## Expected br action

Close only after `verdict_accept` (helper executes `br close br-101 --json`).

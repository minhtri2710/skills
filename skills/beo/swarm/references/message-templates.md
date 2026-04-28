Non-normative asset.

# message-templates

Role: ASSET
Allowed content only: non-normative message text only

## Worker dispatch

```text
[DISPATCH]
bead_id: <id>
reservation: <reservation>
approval_ref: <path>
goal: <goal>
approved_file_scope:
- <path>
approved_generated_outputs:
- <path-or-none>
dependency_constraints:
- <constraint-or-none>
forbidden_paths:
- <path-or-glob>
verification_commands:
- <command>
reporting_format: DONE | BLOCKED | FAILED | CONFLICT
return_channel: <channel>
reservation_owner: <coordinator>
report_deadline: <timestamp>

Rules:
- acknowledge before editing
- confirm clean working tree for in-scope files or report pre-existing dirty paths
- confirm reservation matches approved_file_scope
- edit only approved_file_scope plus approved_generated_outputs
- stop if intended edit touches forbidden_paths
- stop if generated, lockfile, or snapshot changes are not explicitly approved
- report blocked instead of expanding scope
- include changed_files, scope_respected yes/no, handoff_needed yes/no, and verification evidence in terminal report
- release reservation only after terminal report
```

## Worker acknowledge

```text
[ACK]
bead_id: <id>
reservation_id: <reservation>
understood_scope: true|false
working_tree_clean_for_scope: true|false
pre_existing_dirty_paths:
- <path-or-none>
reservation_matches_scope: true|false
questions_or_blockers: <none-or-text>
```

## Worker heartbeat

```text
[HEARTBEAT]
bead_id: <id>
reservation_id: <reservation>
status: in_progress
current_step: <short text>
changed_files_so_far:
- <path-or-none>
blockers: <none-or-text>
```

## Worker done report

```text
[DONE]
bead_id: <id>
reservation_id: <reservation>
approval_ref: <path>
changed_files:
- <path>
generated_files:
- <path-or-none>
verification:
- command: <command>
  result: pass|fail
  output_ref: <summary-or-log-ref>
scope_respected: true|false
handoff_needed: true|false
diff_summary: <short summary>
notes: <none-or-text>
released_reservation: true|false
```

## Worker blocked report

Canonical owner selection after a blocked report remains in `beo-swarm`, `beo-debug`, `beo-plan`, and `beo-references -> pipeline.md`.

```text
[BLOCKED]
bead_id: <id>
reservation_id: <reservation>
blocker: <short description>
smallest_repro: <command/input/artifact>
evidence: <observed facts>
scope_expansion_needed: true|false
generated_change_unapproved: true|false
coordination_hint: debug-suspected|plan-repair-suspected|external-input-suspected|unknown
```

## Worker failed report

Canonical successor-owner selection remains in `beo-swarm` and `beo-references -> pipeline.md`.

```text
[FAILED]
bead_id: <id>
reservation_id: <reservation>
failure: <short description>
last_safe_state: <commit/files/status>
changed_files:
- <path-or-none>
recovery_hint: release|reassign|debug-suspected|plan-repair-suspected|external-input-suspected
```

## Conflict report

```text
[CONFLICT]
bead_id: <id>
reservation_id: <reservation>
conflicting_scope: <path-or-glob>
conflicting_worker_or_bead: <id-or-unknown>
observed_write: <path-or-evidence>
action_taken: stopped|blocked|released|needs-coordinator
```

## Reservation release

```text
[RELEASE]
bead_id: <id>
reservation_id: <reservation>
reason: done|blocked|failed|stale|conflict
released_by: <worker-or-coordinator>
released_at: <timestamp>
```

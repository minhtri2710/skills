# Debugging Message Templates

Use these Agent Mail messages during `beo-debug`.

## decision-violation

Use before fixing a locked-decision violation.

```text
send_message(
  project_key="<project-root-path>",
  sender_name="<agent-mail-name>",
  to=["<COORDINATOR_AGENT_NAME>"],
  thread_id="<EPIC_ID>",
  subject="Decision violation found: <decision-id>",
  body_md="Bead <BEAD_ID> violated decision <D#>: <what was implemented vs what was locked>. Proposed fix: <approach>."
)
```

## fix-applied

Use after a verified fix.

```text
send_message(
  project_key="<project-root-path>",
  sender_name="<agent-mail-name>",
  to=["<COORDINATOR_AGENT_NAME>"],
  thread_id="<EPIC_ID>",
  subject="Fix applied: <classification>",
  body_md="Root cause: <root-cause sentence>. Fix: <what changed>. Verification: <command/result>."
)
```

## blocked-waiting

Use when paused on another worker or dependency.

```text
send_message(
  project_key="<project-root-path>",
  sender_name="<agent-mail-name>",
  to=["<COORDINATOR_AGENT_NAME>"],
  thread_id="<EPIC_ID>",
  subject="Blocked: waiting on <bead-id>",
  body_md="<BEAD_ID> cannot proceed until <dependency> completes. Pausing."
)
```

## hard-blocker

Use when the issue cannot be resolved locally.

```text
send_message(
  project_key="<project-root-path>",
  sender_name="<agent-mail-name>",
  to=["<COORDINATOR_AGENT_NAME>"],
  thread_id="<EPIC_ID>",
  subject="Hard blocker: <description>",
  body_md="Cannot resolve: <what is impossible and why>. Options: <A> or <B>. Needs decision."
)
```

## solo-debug-mode

Use when no Agent Mail session is active.

```bash
br comments add <TASK_ID> --no-daemon --message "Debug report: <root cause or current blocker>. Verification: <command/result>. Next step: <fix applied | needs decision>."
```

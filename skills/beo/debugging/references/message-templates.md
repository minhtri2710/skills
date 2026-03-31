# Debugging Message Templates

Agent Mail `send_message` templates for the debugging workflow.

## decision-violation

Report a CONTEXT.md decision violation before fixing.

```
send_message(
  project_key: "<project-root-path>",
  sender_name: "<agent-name>",
  to: ["<COORDINATOR_AGENT_NAME>"],
  thread_id: "<epic-thread-id>",
  subject: "Decision violation found: <decision-id>",
  body_md: "Bead <id> violated decision <D#>: <what was done vs what was decided>. Proposed fix: <approach>."
)
```

## fix-applied

Report a completed fix with root cause and verification status.

```
send_message(
  project_key: "<project-root-path>",
  sender_name: "<agent-name>",
  to: ["<COORDINATOR_AGENT_NAME>"],
  thread_id: "<epic-thread-id>",
  subject: "Fix applied: <classification from Step 1>",
  body_md: "Root cause: <sentence from 3f>. Fix: <what was changed>. Verification: passed."
)
```

## blocked-waiting

Report that a worker is blocked waiting on another worker's dependency.

```
send_message(
  project_key: "<project-root-path>",
  sender_name: "<agent-name>",
  to: ["<COORDINATOR_AGENT_NAME>"],
  thread_id: "<epic-thread-id>",
  subject: "Blocked: waiting on <bead-id>",
  body_md: "<bead-id> cannot proceed until <dependency> completes. Pausing."
)
```

## hard-blocker

Report a genuinely unresolvable blocker that needs human decision.

```
send_message(
  project_key: "<project-root-path>",
  sender_name: "<agent-name>",
  to: ["<COORDINATOR_AGENT_NAME>"],
  thread_id: "<epic-thread-id>",
  subject: "Hard blocker: <description>",
  body_md: "Cannot resolve: <what is impossible and why>. Options: <A> or <B>. Needs human decision."
)
```

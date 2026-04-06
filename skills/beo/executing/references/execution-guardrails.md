# Execution Guardrails

Red flags, anti-patterns, and recovery procedures for `beo-executing`.

## Post-Compaction Recovery

If you detect that context has been compacted (prior conversation is summarized):

1. Re-read these artifacts with your file reading tool:
   - `.beads/artifacts/<feature_slug>/CONTEXT.md`
   - `.beads/artifacts/<feature_slug>/plan.md`
   - `.beads/artifacts/<feature_slug>/phase-contract.md`
   - `.beads/artifacts/<feature_slug>/story-map.md`
   - `.beads/STATE.md` (if present)
   - `.beads/HANDOFF.json` (if present)
2. Re-read current task state:
   ```bash
   br dep list <EPIC_ID> --direction up --type parent-child --json
   ```
3. Resume from the last known good state

## Red Flags

| Flag | Description |
|------|-------------|
| **Implementing code directly in standalone mode** | In standalone mode with multiple tasks, use the session's normal subagent/task dispatch mechanism when available. Do not default to direct implementation just because delegation feels optional. In worker mode or standalone with a single task, direct implementation is expected. |
| **Dispatching without checking dependencies** | Always verify deps are satisfied before dispatch |
| **Ignoring worker blockers** | Every blocker needs classification and resolution |
| **Dispatching the same task twice** | Check task status before dispatching |
| **Skipping the report artifact** | Every completed task needs a report for downstream tasks |
| **Not flushing after updates** | Run `br sync --flush-only` after status changes |
| **Tracking completion in conversation but not in graph** | `br close <bead>` must run immediately after verification passes. Conversation-level tracking is ephemeral; the graph is the source of truth |

## Anti-Patterns

| Pattern | Why It's Wrong | Instead |
|---------|---------------|---------|
| Sequential execution of independent tasks | Wastes time; use `beo-swarming` for parallel work | Route to swarming when multiple independent tasks are ready |
| Re-dispatching a failed task without investigation | Same failure will recur | Understand the failure first |
| Modifying task specs during execution | Plan integrity violation | If specs need changing, strip `approved` label (`br label remove <EPIC_ID> -l approved`) and route to planning |
| Dispatching all tasks at once | Overwhelms context, loses control | Dispatch 1-3 at a time, track progress |
| Skipping verification in the worker prompt | Workers will skip verification | Always include verification criteria |

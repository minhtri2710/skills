<!-- BEO:START -->
## Beo Startup Rules

1. Read this file at session start and again after any context compaction.
2. Check `.beads/onboarding.json` exists and is current. If it is missing or stale, stop and load `beo-using-beo`.
3. If `.beads/beo_status.mjs` exists, run `node .beads/beo_status.mjs --json` as the first quick scout step.
4. If `.beads/HANDOFF.json` exists, read it before normal routing and verify it against live state before resuming.
5. Read `.beads/critical-patterns.md` before planning or execution.

## Beo Skill Chain

Bootstrap gate: `beo-using-beo` runs first when onboarding is missing or stale.

```text
beo-router -> beo-exploring -> beo-planning -> beo-validating ->
beo-swarming -> beo-executing -> beo-reviewing -> beo-compounding
```

Support skills: `beo-debugging`, `beo-dream`, `beo-writing-skills`

## Critical Rules

- Never execute without passing validation.
- `CONTEXT.md` is the source of truth for locked decisions.
- 65% context usage triggers a `HANDOFF.json` checkpoint and a clean pause.
- Keep `STATE.json` current with the active phase and next action.
- After context compaction, re-read `AGENTS.md`, rerun `node .beads/beo_status.mjs --json` if available, then reopen `STATE.json`, `HANDOFF.json` if present, and the active feature artifacts before more work.
- P1 review findings block merge or feature completion.
- Never disturb concurrent work from other agents; work around existing edits unless the user explicitly tells you otherwise.

## Working Files

- `.beads/onboarding.json` - onboarding state and managed asset version
- `.beads/beo_status.mjs` - read-only scout command for onboarding, state, and handoff summary
- `.beads/STATE.json` - current phase and feature narrative
- `.beads/HANDOFF.json` - optional resume checkpoint when a session must pause
- `.beads/artifacts/<feature_slug>/` - per-feature artifacts such as `CONTEXT.md`, `discovery.md`, `approach.md`, `plan.md`, `phase-contract.md`, and `story-map.md`
- `.beads/critical-patterns.md` - promoted learnings approved for broad reuse
- `.beads/learnings/` - per-feature learnings files

## Session Finish

1. Update or close the active bead.
2. Leave `STATE.json` current. If the session is pausing under context pressure or interruption, write or update `HANDOFF.json` too.
3. Mention blockers, open questions, and next actions explicitly.

---

## Tooling Quick Reference

### br (beads_rust) — Issue Tracking

`br` manages tasks, dependencies, and status. It never runs git commands automatically.

```bash
br ready --json                  # Unblocked, ready-to-work beads
br list --json                   # All open beads
br show <id> --json              # Full bead details
br create "<title>" -t task --parent <epic-id> -p <priority> --json
br update <id> --claim           # Claim bead (assignee + in_progress)
br close <id>                    # Mark done
br comments add <id> --no-daemon --message "<msg>"   # Add comment
br sync --flush-only             # Export DB to JSONL for git commit
```

**Shared CLI rules:**
- Always use `--no-daemon` on `br comments add` and `br comments list`.
- Always run `br sync --flush-only` after mutations before committing to git.
- Priority: 0=critical, 1=high, 2=normal, 3=low, 4=backlog.

For full CLI reference, load `beo-reference` and see `br-cli-reference.md`.

### bv (Beads Viewer) — Graph Triage

**CRITICAL: Always use `--robot-*` flags. Bare `bv` launches an interactive TUI that blocks your session.**

```bash
bv --robot-triage --format json                        # Full triage (start here)
bv --robot-next --format json                          # Single top pick
bv --robot-plan --graph-root <EPIC_ID> --format json   # Parallel execution tracks
```

For full command reference, load `beo-reference` and see `bv-cli-reference.md`.

### MCP Agent Mail — Multi-Agent Coordination

> Minimal subset. For full API surface, identity model, and conflict semantics, load `beo-reference` and see `agent-mail-coordination.md`.

Used for swarming. Provides agent identities, threaded messaging, and file reservations.

```text
ensure_project(project_key=<abs-path>)
register_agent(project_key, program, model)
macro_start_session(human_key, model, program, task_description, agent_name)
send_message(project_key, sender_name, to, thread_id, subject, body_md)
reply_message(project_key, message_id, sender_name, body_md)
fetch_inbox(project_key, agent_name)
file_reservation_paths(project_key, agent_name, paths, ttl_seconds, exclusive)
release_file_reservations(project_key, agent_name, paths)
```

For full Agent Mail reference, load `beo-reference` and see `agent-mail-coordination.md`.

### Session Completion Checklist

```bash
git status              # Check what changed
git add <files>         # Stage code changes
br sync --flush-only    # Export beads to JSONL
git add .beads/         # Stage beads changes
git commit -m "..."     # Commit everything together
```
<!-- BEO:END -->

---
name: herdr-delivery-workflow
description: "Control Herdr, a terminal multiplexer for coding agents, and run bounded delivery inside it: pane and agent operations, intake and ownership, one issue at a time on one shared checkout and one branch, a coordinator that partitions the issue into path-owned implementation agents running in parallel when it decomposes, coordinator-owned commits, exact-head independent review, Human-gate routing, evidence handoff, and safe closeout. Use whenever the user explicitly mentions Herdr — to inspect or control panes, tabs, workspaces, commands, or another agent, to implement a change with one or more agents, to run an implementation-to-review pipeline, or to monitor a bounded delivery. Do not use merely because a task could benefit from a background terminal, delegation, or parallel work. Requires HERDR_ENV=1."
---

# Herdr Delivery Workflow

This skill owns Herdr control and bounded delivery inside it: pane and agent mechanics, delivery routing, ownership, evidence, review, Human gates, and closeout. The installed binary stays the authority for command syntax.

## 1. Preflight and route

Before any Herdr inspection or control command, verify the caller is inside Herdr:

```bash
test "${HERDR_ENV:-}" = 1
```

If the check fails, state that the agent is not running inside Herdr and stop. Do not inspect or control another Herdr session from outside it.

Read `references/herdr-cli.md` before the first control command in any route. It owns preflight, discovery, IDs and caller context, pane and agent mechanics, lifecycle states, read sources, and pane safety. Keep the coordination record in the current run context; do not create shadow state or a second control plane. The durable files this workflow touches live under `~/.herdr/projects/<project-slug>/`: the append-only Human-gate ledger it writes (`references/human-gates-and-closeout.md`) and the Human-owned project config it reads (`references/project-config.md`). A delivery or review-only route reads the project config before staffing, and when it is absent asks the Human whether to create one rather than silently defaulting; the lightweight route does not.

Use local tools conditionally and name them in the charter when the outcome needs them: `qmd` for an indexed local Markdown knowledge base, `mcporter` for discovering or calling MCP servers and tools, and the applicable Obsidian tool when the task explicitly concerns Obsidian. If a required tool is unavailable, record degraded mode, use a bounded alternative, and never claim a tool was used when it was not.

Choose the smallest route:

- **Lightweight:** one command, one pane, read-only inspection, or one bounded prompt to an existing agent. Handle it directly with `references/herdr-cli.md` and stop there. Do not read the delivery policies or create a reviewer, extra coordinator, or recurring watch.
- **Review-only:** a named commit or exact head needs independent review without implementation. Read `references/reviewer-policy.md`, use one reviewer, and do not create an implementation agent or writer.
- **Delivery:** a source change needs bounded ownership, one or more implementation agents, implementation-to-review handoff, or explicit bounded monitoring/closeout. Read `references/intake-policy.md` first, then `references/coordinator-policy.md`, before mutation.

When a delivery route staffs an editing agent, read `references/implementation-agent-policy.md` before sending its charter. Before review, read `references/reviewer-policy.md`. When a Human gate appears or resources are ready for cleanup, read `references/human-gates-and-closeout.md`. When architecture, ownership, lifecycle, scalability, latency, compatibility, or proof quality is materially uncertain, read `references/structural-misfit-policy.md` and use its lenses selectively.

Do not add delivery ceremony to a genuinely lightweight task. Escalate when ambiguity changes material scope, safety, external effects, credentials, permissions, security, or an irreversible decision.

## 2. Run the delivery sequence

A delivery is one issue on one branch in one checkout. The coordinator analyzes the issue, partitions it into one or more path-owned scopes, staffs one implementation agent per scope, lets them work in parallel on the shared tree, and is the only party that commits. Review happens once, on the quiet head the coordinator committed. On a `FAIL` the loop repairs and reviews again. Follow this order:

1. **Intake:** read `references/intake-policy.md`; record the lane, reason, owners, plan, validation, acceptance boundary, exclusions, target repository/product line, base, dependencies, Human gates, applied project-config keys or `Config: none`, and resources created by this run.
2. **Topology:** preserve the caller's focus and working directory. The delivery runs in the caller's existing checkout: one branch, no second working tree, one delivery in flight per project. Parallelism exists only inside one issue, through the partition; a second issue waits for the flight slot. The coordinator owns every git write on the tree.
3. **Partition:** analyze the issue against the code before staffing anyone and record the partition (`references/intake-policy.md`, "Partition"): one scope is the base case, several scopes only when their owned paths are disjoint and no scope changes an existing contract another scope consumes; a contract that does not exist yet may be pinned in both charters so producer and consumer run in parallel (intake policy, "Partition"). Shared paths belong to no implementation agent.
4. **Charter:** give each implementation agent a bounded outcome, its owned paths and the exclusions, the peer scopes running beside it, the shared-tree rules, the repository guidance governing the owned paths, the verification commands scoped to its owned paths where the repository allows, and the evidence-report requirement. When you staff the agent, pre-authorize exactly the read-only and verify commands the charter names by passing the agent's native permission arguments after `--` on `herdr agent start`, so those routine checks run without stalling on a per-command approval; a routine command-approval prompt is friction to pre-arm at staffing, not a Human gate. Never pre-authorize mutation: push, PR mutation, merge, and deploy stay Human gates.
5. **Execute:** run the implementation agents in parallel, each in its own pane, foreground and bounded. Use Herdr lifecycle waits on each named agent instead of polling.
6. **Quiesce and commit:** when every implementation agent is idle, confirm HEAD, branch, and stash list are unchanged since the last record, confirm `git status --porcelain` is confined to the owned paths and that each scope's entries match what its owner reported as edited, then stage each scope by its owned paths, commit, and record the candidate head. Nothing unexplained may be committed, whether it sits outside every partition or inside a scope that did not claim it.
7. **Evidence:** run the full acceptance checks on that quiet head and record the exact SHA, merge-base, changed files, porcelain, and every exit code. This is the only implementation evidence that counts; the agents' own check results are advisory.
8. **Review:** obtain an independent verdict on the exact candidate head, in the same checkout with every implementation agent idle and the tree quiet at that head. A settled agent state is not acceptance. Staff the reviewer the same way you staff an implementation agent: pre-authorize its read-only inspection and verify commands at `herdr agent start`, so the coordinator does not hand-approve each check, while any write authority stays withheld to preserve the no-mutation contract.
9. **Repair:** route each in-scope finding to the implementation agent that owns the affected paths; a finding that spans partitions or lands outside every partition becomes one sequential slice or `SCOPE_REOPEN`, never a parallel repair. Every resulting head needs fresh evidence and fresh review. The loop is bounded: when the repair cap (default two cycles, `repair-cap` in the project config) is reached without a `PASS`, stop, classify each finding as recurring or new, and route the Human gate or `SCOPE_REOPEN` instead of another cycle.
10. **Integrate:** integration is conditional, not automatic. Do it only when intake recorded a target product line and the Human has not withheld landing; a request that says to stop at review, not to merge, or to leave the branch alone removes this step. When it applies, land the reviewed head onto that line after `PASS`, recompute the integrated head, and rerun the acceptance checks there; the reviewed head and the integrated head stay distinct in the record. When it does not apply, stop at the reviewed head and hand it off as the deliverable.
11. **Gate and close:** stop for Human-owned decisions, including push, PR mutation, merge, and deploy; accept only after claim-shaped checks and exact-head review; close only resources created by this run when cleanup is safe, including tearing down every implementation agent and the reviewer before the flight slot moves to the next issue.

The coordinator decides the outcome, the partition, and the acceptance boundary, and holds the only git write authority on the tree. Each implementation agent decides the local implementation inside its owned paths. The reviewer decides whether the exact head satisfies the stated boundary. Keep those decisions separate. If evidence increases the intake lane or crosses the recorded boundary, stop and route `SCOPE_REOPEN` before continuing.

## 3. Wait and report

Prefer event-driven commands:

```bash
herdr agent prompt <agent-name> "<bounded task>" --wait --timeout 120000
herdr agent wait <agent-name> --timeout 120000
```

Use `--until` only for a required state. After a wait or error, inspect with `herdr agent get` and `herdr agent read`. A blocked state requires inspecting the UI and routing the decision; do not answer by guessing. With several implementation agents live, wait on each by name; one agent settling says nothing about the others.

Require every implementation agent's evidence report and the coordinator's own quiet-head evidence before review, and the reviewer verdict before acceptance. If output is trapped on an alternate screen, use the bounded fallback in `references/herdr-cli.md`: ask for a complete Markdown report in a temporary location and read it directly.

A recurring watch is outside this workflow. If monitoring is requested, keep it foreground, bounded, named, and expiry-limited; never create an unbounded retry or background watch.

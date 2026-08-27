---
name: herdr-delivery-workflow
description: "Coordinate multi-agent Herdr delivery workflows: bounded intake, ownership, optional worktree isolation, foreground agent lifecycle, exact-head independent review, Human-gate routing, evidence handoff, and safe closeout. Use this skill whenever the user explicitly mentions Herdr and asks to implement a change with another agent, coordinate panes, workspaces, or worktrees, run an implementation-to-review pipeline, or monitor a bounded delivery. Do not use it for a single pane command or ordinary one-agent interaction; use the base Herdr skill there."
---

# Herdr Delivery Workflow

This skill coordinates delivery inside Herdr. The base `herdr` skill and the installed binary own CLI syntax, topology operations, and pane safety. This skill owns bounded delivery routing, ownership, evidence, review, Human gates, and closeout.

## 1. Preflight and route

Before any Herdr inspection or control command, verify the caller is inside Herdr:

```bash
test "${HERDR_ENV:-}" = 1
```

If the check fails, state that the agent is not running inside Herdr and stop. Do not inspect or control another Herdr session from outside it.

Use the live `herdr` binary as the command authority. When syntax is needed, run `herdr --help` and the relevant command group without a mutating subcommand. Parse IDs from JSON responses; never infer them from pane order. Keep the coordination record in the current run context; do not create shadow state or a second control plane. The one durable file this workflow writes is the append-only Human-gate ledger defined in `references/human-gates-and-closeout.md`.

Use local tools conditionally and name them in the charter when the outcome needs them: `qmd` for an indexed local Markdown knowledge base, `mcporter` for discovering or calling MCP servers and tools, and the applicable Obsidian tool when the task explicitly concerns Obsidian. If a required tool is unavailable, record degraded mode, use a bounded alternative, and never claim a tool was used when it was not.

Choose the smallest route:

- **Lightweight:** one command, one pane, read-only inspection, or one bounded prompt to an existing agent. Use the base Herdr skill. Do not create a worktree, reviewer, extra coordinator, or recurring watch.
- **Review-only:** a named commit or exact head needs independent review without implementation. Read `references/reviewer-policy.md`, use one reviewer, and do not create an implementation agent or writer.
- **Delivery:** a source change needs bounded ownership, an implementation agent, worktree isolation, implementation-to-review handoff, or explicit bounded monitoring/closeout. Read `references/intake-policy.md` first, then `references/coordinator-policy.md`, before mutation.

When a delivery route staffs an editing agent, read `references/implementation-agent-policy.md` before sending its charter. Before review, read `references/reviewer-policy.md`. When a Human gate appears or resources are ready for cleanup, read `references/human-gates-and-closeout.md`. When architecture, ownership, lifecycle, scalability, latency, compatibility, or proof quality is materially uncertain, read `references/structural-misfit-policy.md` and use its lenses selectively.

Do not add delivery ceremony to a genuinely lightweight task. Escalate when ambiguity changes material scope, safety, external effects, credentials, permissions, security, or an irreversible decision.

## 2. Run the delivery sequence

For a delivery route, follow this order:

1. **Intake:** read `references/intake-policy.md`; record the lane, reason, owners, plan, validation, acceptance boundary, exclusions, target repository/product line, base, dependencies, Human gates, and resources created by this run.
2. **Topology:** preserve the caller's focus and working directory. Use one writer per moving scope, and keep one delivery in flight per project unless the Human authorizes named non-overlapping lanes. Isolate concurrent writers and independent review in separate worktrees when needed. Staff the reviewer on a different agent kind than the implementation agent when one is available.
3. **Charter:** give the implementation agent a bounded outcome, ownership boundary, the repository guidance governing the owned paths, verification commands, and evidence-report requirement.
4. **Execute:** keep agent work foreground and bounded. Use Herdr lifecycle waits instead of polling.
5. **Evidence:** independently verify the implementation head, merge-base, changed files, porcelain state, and check results before review.
6. **Review:** obtain an independent verdict on the exact implementation head. A settled agent state is not acceptance.
7. **Repair:** route in-scope review findings to the implementation agent. Every resulting head needs fresh evidence and fresh review.
8. **Integrate:** integration is conditional, not automatic. Do it only when intake recorded a target product line and the Human has not withheld landing; a request that says to stop at review, not to merge, or to leave the branch alone removes this step. When it applies, land the reviewed head onto that line after `PASS`, recompute the integrated head, and rerun the acceptance checks there; the reviewed head and the integrated head stay distinct in the record. When it does not apply, stop at the reviewed head and hand it off as the deliverable.
9. **Gate and close:** stop for Human-owned decisions, including push, PR mutation, merge, and deploy; accept only after claim-shaped checks and exact-head review; close only resources created by this run when cleanup is safe.

The coordinator decides the outcome and acceptance boundary. The implementation agent decides the local implementation. The reviewer decides whether the exact head satisfies the stated boundary. Keep those decisions separate. If evidence increases the intake lane or crosses the recorded boundary, stop and route `SCOPE_REOPEN` before continuing.

## 3. Wait and report

Prefer event-driven commands:

```bash
herdr agent prompt <agent-name> "<bounded task>" --wait --timeout 120000
herdr agent wait <agent-name> --timeout 120000
```

Use `--until` only for a required state. After a wait or error, inspect with `herdr agent get` and `herdr agent read`. A blocked state requires inspecting the UI and routing the decision; do not answer by guessing.

Require the implementation evidence report before review and the reviewer verdict before acceptance. If output is trapped on an alternate screen, use the bounded fallback in the base Herdr skill: ask for a complete Markdown report in a temporary location and read it directly.

A recurring watch is outside this workflow. If monitoring is requested, keep it foreground, bounded, named, and expiry-limited; never create an unbounded retry or background watch.

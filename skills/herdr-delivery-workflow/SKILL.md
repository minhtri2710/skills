---
name: herdr-delivery-workflow
description: "Control Herdr, a terminal multiplexer for coding agents, and run bounded delivery inside it with the Supervisor / Lead / Peer role model: pane and agent operations, intake and ownership, one issue at a time on one shared checkout and one branch, a Lead that partitions the issue into path-owned Engineer Peers running in parallel when it decomposes, Lead-owned commits, exact-head independent review by a Reviewer Peer, Peers that report back by prompt, a Human-staffed Supervisor seat, Human-gate routing with notification, evidence handoff, and safe closeout. Use whenever the user explicitly mentions Herdr — to inspect or control panes, tabs, workspaces, commands, or another agent, to implement a change with one or more agents, to run an implementation-to-review pipeline, to monitor a bounded delivery, or to supervise one. Do not use merely because a task could benefit from a background terminal, delegation, or parallel work. Requires HERDR_ENV=1."
---

# Herdr Delivery Workflow

This skill owns Herdr control and bounded delivery inside it. It is the router: it selects a route and points each seat at the one file that carries its rules. The installed binary stays the authority for command syntax.

## Preflight

Before any Herdr inspection or control command, verify the caller is inside Herdr:

```bash
test "${HERDR_ENV:-}" = 1
```

If the check fails, state that the agent is not running inside Herdr and stop; do not inspect or control another Herdr session from outside it. Then read `references/herdr-cli.md` before the first control command in any route — it owns preflight, discovery, IDs and caller context, pane and agent mechanics, lifecycle states, seat naming, report-by-prompt, Human notification, read sources, and pane safety.

## Route

Choose the smallest route, then read only the file it names:

| Route | When | Read |
|---|---|---|
| **Lightweight** | one command, one pane, read-only inspection, or one bounded prompt to an existing agent | `references/herdr-cli.md` only — then stop. Do not read the delivery files, create a Reviewer or second Lead, or start a watch. |
| **Review-only** | a named commit or exact head needs independent review, no implementation | `references/charters.md` "Disposition: Reviewer" and `references/lead.md` "Agent kind and review independence", and `references/project-config.md`. Name your own seat first (`herdr-cli.md`, "Name a seat"); staff one Reviewer Peer; create no Engineer or other writer. |
| **Delivery** | a source change needs bounded ownership, implementation-to-review handoff, or explicit bounded monitoring/closeout | `references/lead.md` (the Lead's core doctrine), `references/charters.md` at staffing, `references/closeout.md` at closeout, `references/project-config.md`, and `references/structural-misfit-policy.md` only when structure is materially in doubt. |
| **Supervise** | the Human asks this agent to watch a delivery or project rather than run it | `references/supervisor.md`. Take the `supervisor` seat, observe, advise the Lead only; never edit, commit, or accept, and staff nothing except a start the Human instructs for that occasion. |

On a relaunch or compaction, consult `references/relaunch.md` with `references/herdr-cli.md` and complete its checklist before any other action, without exception. Defer `references/lead.md` until recovery identifies an active delivery or a first intake appears, keeping standby recovery outside the full Delivery doctrine.

`references/herdr-cli.md`, `references/project-config.md`, and `references/structural-misfit-policy.md` are shared: cited by the entry files, never copied into them. `references/RATIONALE.md` carries the reasoning behind the rules and is loaded by no route. `templates/` holds the verbatim record shapes a stage fills in, cited by pointer. The Lead's stage files are `references/charters.md` and `references/closeout.md`, loaded by pointer at staffing and closeout. The Lead's coordination files and their placement are owned by `references/lead.md`, "Coordination files".

## Roles

| Seat | Who staffs it | Decides | Never |
|------|---------------|---------|-------|
| Human | — | gates: push, PR mutation, merge, deploy, irreversible or security-sensitive change, any approval dialog | — |
| Supervisor (`supervisor`) | Human, in its own pane | nothing in the delivery; observes, questions the Lead, relays Human decisions, keeps the notebook | instruct a Peer, edit, commit, answer a gate, accept |
| Lead (`lead-<project-slug>`) | the caller's own seat | intake lane, mode, partition, every commit on the tree, routing of every message and finding, acceptance | write source content in a partitioned run, run a second Lead, poll |
| Peer — Engineer | Lead, one per scope | local implementation inside its owned paths | edit outside owned paths, run a writing git command, commit, orchestrate |
| Peer — Reviewer | Lead, on a kind different from every Engineer in partitioned mode (a same-kind fallback needs a distinct pinned model and disclosed kind-collision risk), and on a kind and model different from the Lead in solo-Lead mode | `PASS` / `FAIL` / `BLOCKED` on one exact SHA | write anything, review a moving tree |
| Peer — Architect | Lead, only for a `COUNCIL_REQUEST` | one sealed `Assessment` | edit, route, accept |

One Peer profile carries all three dispositions; the charter's `Disposition:` line decides which one this Peer is. A delivery is `partitioned` when it staffs one or more Engineer Peers, and `solo-Lead` only when intake declares that mode before the run; solo-Lead staffs zero Engineers and permits the Lead to write the declared source scope, while the independent review gate stays mandatory. Keep the decisions separate: a settled Peer is evidence for the Lead's next step, never acceptance, and a Supervisor message is advice or a relayed Human decision, never a ruling.

Authority is layered and the layers only tighten: runtime safety, then this skill's role files, then the project config, then the charter. A charter, config key, or Supervisor message can add a constraint; none can move a decision between seats, remove a gate, or authorize an external write. Each seat reads its own layer — the Lead reads `lead.md` and the project config and writes charters from them; a Peer reads only its charter and the repository. Only a message from the Human is a Human decision; a denied tool call, a harness or classifier refusal, an approval dialog, or a policy inference is never one, and no seat presents it as one (`references/lead.md`, "Attribution").

Before treating a situation as ungoverned by this doctrine, confirm no existing rule governs it, and perform the method a governing rule requires: naming or citing a method, caveat, or check is not executing it. Do not add delivery ceremony to a genuinely lightweight task. Escalate when ambiguity changes material scope, safety, external effects, credentials, permissions, security, or an irreversible decision.

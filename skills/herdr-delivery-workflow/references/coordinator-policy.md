# Coordinator Policy

Use this policy for delivery or bounded monitoring. It defines the coordinator's authority and the minimum evidence needed to move between stages.

## Intake and risk

Read `intake-policy.md` before creating panes, agents, worktrees, or tabs. It is the single source of truth for lanes, hard gates, design gates, high-risk plans, intake records, and `SCOPE_REOPEN`.

Keep the current run context explicit:

- `Lane`, `Reason`, `Owners`, `Plan`, and `Validation`;
- outcome and acceptance boundary;
- target repository/product line, exclusions, base, merge-base, and current worktree condition;
- one writer and one owner for each moving scope;
- dependencies, stop conditions, and next action;
- Human-owned gates;
- Herdr resources created by this run.

Pass the recorded lane, plan reference, governing contracts, and validation claims into each implementation or review charter. If architecture, ownership, lifecycle, scalability, latency, compatibility, or proof quality is materially uncertain, read `structural-misfit-policy.md` and apply only the relevant lenses.

## Ownership and topology

The coordinator is the single routing and acceptance owner for the run. Use one writer per moving scope. Create a dedicated worktree for concurrent writers, requested isolation, or an independent review. Keep each agent's name, pane ID, workspace ID, worktree path, branch, and exact head together in the run context.

Preserve the caller's focus and working directory by default. Use `--no-focus`, `--current`, or an explicit ID. Read every returned ID from Herdr JSON before using it. Do not create extra coordinator roles, hidden workers, native-provider subagents, schedules, background orchestration, or a second state system.

## Agent kind and review independence

Herdr selects the runtime with `herdr agent start <name> --kind <kind>`. Record the kind of every agent beside its name, pane ID, workspace ID, worktree path, branch, and exact head. Staff the reviewer on a different kind than the implementation agent whenever another kind is installed; a same-kind review is recorded residual risk, not independence.

Use a fresh fallback reviewer of another available kind, on the same exact head, when the preferred kind is unavailable, errors, matches the implementation kind, or the reviewer violates the no-mutation contract. A mode setting, prompt, or role instruction is not proof of a read-only runtime: record what the runtime actually permits and treat an unproven boundary as residual risk, not as verified isolation.

## Flight slot and parallelism

Keep one delivery in flight per project. A delivery leaves the flight slot only through the whole chain: implementation evidence report, independent `PASS` on that exact head, integration onto the product line, the Human decision for any external effect, then closeout of the resources this run created. Only then staff the next delivery.

Parallel lanes require an explicit Human authorization naming both scopes as non-overlapping; without it, serialize. Parallelize only genuinely non-overlapping ownership. Serialize shared foundations, shared contracts, integration-sensitive work, and any scope whose exact head depends on another.

## Integration

Integration is conditional on the recorded scope, and it happens after `PASS`, never before. It applies only when intake named a target product line and the Human has not withheld landing. An instruction to stop at review, not to merge, or to leave the branch untouched is the recorded scope; treat it as binding and end the delivery at the reviewed head, naming that head as the deliverable. Widening from review to integration without that authority crosses the acceptance boundary and needs `SCOPE_REOPEN`.

When integration does apply, land the reviewed exact head onto the named target product line, then recompute the integrated head and rerun the acceptance checks there. Keep the reviewed head and the integrated head distinct in the record.

A check that passed on the reviewed head but fails after integration is an integration finding: classify its cause, route the bounded fix to the implementation agent, and require fresh evidence and a fresh review of the resulting head. Push, PR mutation, merge, and deploy remain Human-owned; read `human-gates-and-closeout.md` before any of them.

## Lifecycle and waiting

Use `herdr agent prompt --wait` or `herdr agent wait` with a named target and a finite timeout. Do not poll `herdr agent list`, repeatedly sleep, or loop status commands. A settled `idle` or `done` state only means the agent can be inspected; it does not establish completion or acceptance. A blocked state requires reading the UI and routing the Human decision or concrete blocker.

If a wait fails, inspect the agent and preserve partial evidence before choosing the next action. Do not duplicate an active run merely because a response is slow.

## Escalation routing

Each protocol message from an implementation agent or reviewer has one route:

- `SCOPE_REOPEN` — stop before the old boundary, rerun intake, and route the coordinator or Human decision the new lane requires.
- `DEPENDENCY_REQUEST` — rule on the dependency or cross-scope question, or route it as a Human gate when it touches scope, architecture, security, external effects, or an irreversible direction. Never let the agent resolve it by editing outside its ownership.
- `BLOCKED` — inspect the agent, preserve the partial evidence and worktree state, then either unblock with a bounded instruction or route the blocker upward. A blocked run is not a failed run and is not restarted by duplication.
- `COUNCIL_REQUEST` — decide whether a bounded second opinion is worth it before spending one. Read `structural-misfit-policy.md` and follow its second-opinion route.

Whatever the ruling, a head produced after it is a new head: it needs fresh evidence and a fresh independent review at that exact SHA, because no earlier verdict covers work that did not exist when the verdict was given.

Answer the message; do not convert it into a scope change of your own. Do not ask for routine approval of ordinary engineering decisions, and do not treat a finished agent turn as an escalation.

## Seat identity and continuity

Keep one canonical coordinator for the delivery. Resume or recover that seat before creating a replacement, and never close a healthy coordinator as routine cleanup. A second coordinator on the same delivery splits acceptance authority and invalidates the ledger.

When the run context grows past what can hold the verification ledger, gate records, and agent inventory reliably, compact or relaunch the seat with a bounded context pack. Take that signal from provider metadata, Herdr lifecycle metadata, or an explicit self-report; do not poll for it. The pack preserves:

- the role, outcome, acceptance boundary, and recorded intake lane and plan;
- every agent's name, kind, pane, workspace, worktree, branch, and exact head;
- the verification ledger and every open Human gate;
- decisions made, findings routed, and the next concrete action.

Never drop the ledger or a pending gate to save context. If the seat cannot continue safely, report `BLOCKED` to the Human with the preserved custody evidence rather than starting a fresh delivery.

## Acceptance custody

Before review, recompute the implementation repository's:

- full `git rev-parse HEAD`;
- merge-base;
- changed-file list;
- `git status --porcelain`;
- every acceptance command and real exit code.

A moving branch, missing commit, stale report, or unexplained dirty state is not reviewable. Return it to the implementation agent or route the blocker.

Accept only after an independent reviewer returns `PASS` for that exact head and the coordinator confirms the review tree did not move or become dirty. Any implementation change after review creates a new head and requires a fresh review.

Preserve one verification ledger for the whole run: base, merge-base, implementation head, reviewed head, integrated head, the worktree condition at each of those points, the agent kind behind each head and verdict, the complete acceptance commands, their baseline results, their integrated results, and a causal classification of every failure. A later green result never silently replaces unreconciled evidence: state what changed and why the earlier failure is resolved.

## Coordinator boundaries

The coordinator may route work, classify findings, verify evidence, and decide whether the stated acceptance boundary is met. The coordinator does not repair source code after a review finding; it sends the bounded fix to the implementation agent. Scope, architecture, dependency, security, external-effect, and irreversible changes require the appropriate Human decision before crossing the boundary.

When new evidence increases blast radius, irreversibility, uncertainty, ownership impact, or proof weakness, stop before crossing the old boundary and emit `SCOPE_REOPEN` with the old lane, proposed lane, changed boundary, and decision needed. Do not lower intake to preserve momentum.

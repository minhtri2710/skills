# Coordinator Policy

Use this policy for delivery or bounded monitoring. It defines the coordinator's authority and the minimum evidence needed to move between stages.

## Intake and risk

Read `intake-policy.md` before creating panes, agents, or tabs. It is the single source of truth for lanes, hard gates, design gates, high-risk plans, the partition, intake records, and `SCOPE_REOPEN`.

Keep the current run context explicit:

- `Lane`, `Reason`, `Owners`, `Plan`, `Validation`, and `Partition`;
- outcome and acceptance boundary;
- target repository/product line, exclusions, base, merge-base, and the working-tree condition — porcelain, `git rev-parse HEAD`, the current branch, and `git stash list` — recorded at intake and refreshed at every quiesce point, because the next quiesce compares against it;
- one owner for each path in the partition, and the coordinator as the only committer;
- dependencies, stop conditions, and next action;
- Human-owned gates;
- Herdr resources created by this run.

Pass the recorded lane, plan reference, governing contracts, validation claims, owned paths, and peer scopes into each implementation or review charter. If architecture, ownership, lifecycle, scalability, latency, compatibility, or proof quality is materially uncertain, read `structural-misfit-policy.md` and apply only the relevant lenses.

## Ownership and topology

The coordinator is the single routing, custody, and acceptance owner for the run. The delivery uses one checkout — the caller's existing working tree — and one branch. Do not create a second working tree for isolation, concurrency, or review; `herdr worktree` is out of scope.

Inside that one tree, one issue is worked by one or more implementation agents at the same time, each in its own pane, each confined to the owned paths the partition gave it. The tree is not isolated between them: the git index, build caches, and every check run are shared. What keeps the work honest is a division of authority rather than a division of directories:

- an implementation agent edits only its owned paths and never runs a git command that writes — no `add`, `commit`, `stash`, `checkout`, `switch`, `restore`, `reset`, `rebase`, `merge`, `clean`, or branch mutation;
- the coordinator is the only party that stages, commits, or otherwise moves the tree, and does it only at a quiesce point when every implementation agent is idle;
- the reviewer reads and never writes.

Fan-out is one level deep and belongs to the coordinator alone. An implementation agent may not spawn subagents, hidden workers, or background jobs, because a writer the coordinator does not know about is a writer the partition does not cover.

Preserve the caller's focus and working directory by default. Use `--no-focus`, `--current`, or an explicit ID. Read every returned ID from Herdr JSON before using it. Do not create extra coordinator roles, native-provider subagents, schedules, background orchestration, or a second state system. Keep each agent's name, kind, pane ID, workspace ID, owned paths, and, for the reviewer, the exact head together in the run context.

## Agent kind and review independence

Herdr selects the runtime with `herdr agent start <name> --kind <kind>`. Take the preferred implementation and reviewer kinds and the pre-chosen fallback from the project config when one is recorded; an explicit Human instruction in the current request overrides it. Record the kind of every agent beside its name, pane ID, workspace ID, and owned paths or reviewed head. Staff the reviewer on a kind that differs from every implementation agent's kind whenever another kind is installed; a review on a kind that matches any implementation agent is recorded residual risk, not independence.

Use a fresh fallback reviewer of another available kind, on the same exact head, when the preferred kind is unavailable, errors, matches an implementation kind, or the reviewer violates the no-mutation contract. A mode setting, prompt, or role instruction is not proof of a read-only runtime: record what the runtime actually permits and treat an unproven boundary as residual risk, not as verified isolation.

## Flight slot and sequencing

Keep one delivery in flight per project. A delivery leaves the flight slot only through the whole chain: every implementation agent's evidence report, the coordinator's quiet-head evidence, independent `PASS` on that exact head, integration onto the product line, the Human decision for any external effect, then closeout of the resources this run created. Only then staff the next delivery.

The delivery itself is one loop: partition, implement in parallel, quiesce and commit, evidence, review, and on a `FAIL` repair and review again. Parallelism lives inside the issue, between scopes with disjoint owned paths; it never crosses issues. When several issues are requested at once, name the order and run them one at a time, and say plainly that a second issue on the same checkout waits for the flight slot rather than sharing it.

The repair loop is bounded: default two repair cycles, overridden by `repair-cap` in the project config. When the cap is reached without a `PASS`, stop the loop, classify each open finding as recurring or new, and route a Human gate — or `SCOPE_REOPEN` when the evidence shows the scope grew — instead of another cycle.

## Quiesce and commit

Implementation agents hand the tree back dirty, by design: they do not commit. The coordinator turns that shared dirty tree into one exact head, and nothing is reviewable until it has.

A quiesce point requires every implementation agent to be idle or done, with no foreground command still running in any pane this run created. Then:

1. Confirm that only the working tree moved: `git rev-parse HEAD`, the current branch, and `git stash list` must equal what the record holds from intake or the previous quiesce. A moved head means an implementation agent committed, and that commit may carry a peer's half-written files; a new stash means work has been hidden from porcelain. Do not build on either: preserve the state, name the agent, and route `BLOCKED`.
2. Read `git --no-optional-locks status --porcelain --untracked-files=all` (per file, so it compares against the agents' reports) and reconcile it against the partition twice. First, every entry must fall inside some scope's owned paths, or be an entry the record already explains; an unexplained entry outside every partition is not a merge problem to smooth over, it is an ownership breach or a stray process. Second, for each scope, compare the entries inside its owned paths with the files its owner listed under `Edited files`: an entry the owner did not claim was written by a peer, a hook, or a process. In both cases the tree is not committable until the origin is named — ask the agents, or route `BLOCKED`. Once named, the ruling record explains the entry; the owner's `Edited files` stays what the owner actually did and is never rewritten to absorb it. An in-scope entry the owner adopts is committed with the scope; one the owner rejects is removed by the coordinator (`git restore` or deletion) only after its diff is preserved in the record, because discarding work someone wrote without a copy is the irreversible step, not the restore itself.
3. Stage each scope by its owned paths only (`git add -- <owned paths>`), never `git add -A` or `git commit -a`, and commit it. One commit per scope, in the recorded partition order, keeps attribution for routing findings; the commits are intermediates, not individually verified heads. Commit hooks run against a tree that still holds the other scopes' uncommitted work, and a hook that stashes or rewrites files — lint-staged and its kin — touches that work: let every commit finish, never interrupt a hook, and after each commit re-read porcelain and `git stash list`. A file a hook changed outside the scope just committed, or a stash it left behind, is an unexplained entry to resolve before the next scope is staged.
4. Record the resulting candidate head as the full SHA, with merge-base, changed files, and the stash list.

Then run every acceptance command on that quiet head yourself and record the real exit codes. An implementation agent's check results were produced on a tree that may have held another agent's half-written files, so they are advisory: useful for the agent's own iteration, never a reason to route a `FAIL` and never acceptance evidence. The coordinator's run on the committed head is the only implementation evidence the review binds to.

Committing is custody, not repair. The coordinator stages and commits what the implementation agents wrote; it does not edit source content, and a fix it thinks is obvious still goes back to the owning agent.

## Integration

Integration is conditional on the recorded scope, and it happens after `PASS`, never before. It applies only when intake named a target product line and the Human has not withheld landing. An instruction to stop at review, not to merge, or to leave the branch untouched is the recorded scope; treat it as binding and end the delivery at the reviewed head, naming that head as the deliverable. Widening from review to integration without that authority crosses the acceptance boundary; if landing later turns out to be needed, the route is `SCOPE_REOPEN` to the Human, never acting on it.

When integration does apply, land the reviewed exact head onto the named target product line, then recompute the integrated head and rerun the acceptance checks there. Keep the reviewed head and the integrated head distinct in the record.

A check that passed on the reviewed head but fails after integration is an integration finding: classify its cause, route the bounded fix to the owning implementation agent, and require fresh evidence and a fresh review of the resulting head. Push, PR mutation, merge, and deploy remain Human-owned; read `human-gates-and-closeout.md` before any of them.

## Lifecycle and waiting

Use `herdr agent prompt --wait` or `herdr agent wait` with a named target and a finite timeout, once per live agent. Do not poll `herdr agent list`, repeatedly sleep, or loop status commands. A settled `idle` or `done` state only means the agent can be inspected; it does not establish completion or acceptance, and one agent settling says nothing about its peers. A blocked state requires reading the UI and routing the Human decision or concrete blocker.

If a wait fails, inspect the agent and preserve partial evidence before choosing the next action. Do not duplicate an active run merely because a response is slow. Do not quiesce while any agent is unsettled.

## Escalation routing

Each protocol message from an implementation agent or reviewer has one route:

- `SCOPE_REOPEN` — stop before the old boundary, rerun intake, and route the coordinator or Human decision the new lane requires.
- `DEPENDENCY_REQUEST` — rule on the dependency or cross-scope question, or route it as a Human gate when it touches scope, architecture, security, external effects, or an irreversible direction. Never let the agent resolve it by editing outside its ownership. When the request is for a path: a path no scope owns and no shared-path rule covers may be granted to the requester and recorded in the partition; a path another agent owns transfers only at a quiesce point, after that owner is idle and its work is committed, because reassigning a live path recreates two writers on one file; a shared or contract path becomes a sequential slice, run alone after the current scopes quiesce.
- `BLOCKED` — inspect the agent, preserve the partial evidence and working-tree state, then either unblock with a bounded instruction or route the blocker upward. A blocked run is not a failed run and is not restarted by duplication.
- `COUNCIL_REQUEST` — decide whether a bounded second opinion is worth it before spending one. Read `structural-misfit-policy.md` and follow its second-opinion route.

Write the ruling record when the message is classified, before any pause. A Human-gate route leaves RULING pending until the Human decides, but the record and its BINDING line are written now, not after the gate resolves. The BINDING line is fixed text — copy it verbatim; it is a binding rule, not an aside:

```text
RULING: <decision and its bounded scope | pending Human gate <GATE-ID>>
ROUTE: <coordinator-ruled | human-gate>
BINDING: any head produced after this ruling is a new head — it needs fresh evidence and a fresh independent review bound to that exact SHA; no earlier verdict covers work that did not exist when the verdict was given
```

Answer the message; do not convert it into a scope change of your own. Do not ask for routine approval of ordinary engineering decisions, and do not treat a finished agent turn as an escalation.

## Routing review findings

A `FAIL` names findings; each finding is routed by where it lands in the partition:

- inside one scope's owned paths — send it to that implementation agent as a bounded fix. Findings in different scopes may be repaired in parallel, since the partition still holds.
- across two or more scopes, or outside every scope — this is a finding the partition did not anticipate. Do not hand it to two agents at once and do not widen one agent's ownership while a peer is live. Run it as one sequential slice with a single agent after the others are idle, or route `SCOPE_REOPEN` when the finding shows the scope grew.

Every repair produces a new head through the same quiesce-and-commit path, with fresh evidence and a fresh review bound to that SHA.

## Seat identity and continuity

Keep one canonical coordinator for the delivery. Resume or recover that seat before creating a replacement, and never close a healthy coordinator as routine cleanup. A second coordinator on the same delivery splits acceptance authority, splits commit authority over one tree, and invalidates the ledger.

When the run context grows past what can hold the verification ledger, gate records, and agent inventory reliably, compact or relaunch the seat with a bounded context pack. Take that signal from provider metadata, Herdr lifecycle metadata, or an explicit self-report; do not poll for it. The pack preserves:

- the role, outcome, acceptance boundary, and recorded intake lane, plan, and partition;
- every agent's name, kind, pane, workspace, owned paths, and, for the reviewer, exact head;
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

A moving branch, missing commit, stale report, unexplained dirty state, or an implementation agent that is still working is not reviewable. Return it to the owning agent or route the blocker.

Accept only after an independent reviewer returns `PASS` for that exact head and the coordinator confirms the checkout did not move or become dirty during the review. Any implementation change after review creates a new head and requires a fresh review.

Preserve one verification ledger for the whole run: base, merge-base, the partition, each scope's commit, the candidate head, the reviewed head, the integrated head, the working-tree condition at each of those points, the agent kind behind each scope and each verdict, the complete acceptance commands, their baseline results, their integrated results, and a causal classification of every failure. A later green result never silently replaces unreconciled evidence: state what changed and why the earlier failure is resolved.

## Coordinator boundaries

The coordinator may route work, decide the partition, stage and commit at a quiesce point, classify findings, verify evidence, and decide whether the stated acceptance boundary is met. The coordinator does not write source content: after a review finding it sends the bounded fix to the owning implementation agent. Scope, architecture, dependency, security, external-effect, and irreversible changes require the appropriate Human decision before crossing the boundary.

When new evidence increases blast radius, irreversibility, uncertainty, ownership impact, or proof weakness, stop before crossing the old boundary and emit `SCOPE_REOPEN` with the old lane, proposed lane, changed boundary, and decision needed. Do not lower intake to preserve momentum.

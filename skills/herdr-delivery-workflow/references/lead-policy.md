# Lead Policy

Use this policy for delivery or bounded monitoring. It defines the Lead's authority and the minimum evidence needed to move between stages.

## Intake and risk

Read `intake-policy.md` before creating panes, agents, or tabs. It is the single source of truth for lanes, hard gates, design gates, high-risk plans, the partition, and intake records; the `REOPEN_REQUEST` shape lives here, under "Escalation routing".

Keep the current run context explicit:

- `Lane`, `Reason`, `Mode`, `Owners`, `Plan`, `Validation`, and `Partition`;
- the Lead seat name and the Supervisor seat name or `none`;
- outcome and acceptance boundary;
- target repository/product line, exclusions, base, merge-base, and the working-tree condition — porcelain, `git rev-parse HEAD`, the current branch, and `git stash list` — recorded at intake and refreshed at every quiesce point, because the next quiesce compares against it;
- one owner for each path in the partition, and the Lead as the only committer;
- dependencies, stop conditions, and next action;
- Human-owned gates;
- Herdr resources created by this run.

Pass the recorded lane, plan reference, governing contracts, validation claims, owned paths, peer scopes, and the Lead's seat name into each Peer charter. When the runtime has any `Read()` deny rule, the Lead follows and puts in every charter the recursive-read discipline in `peer-policy.md`, "Shared-tree rules". If architecture, ownership, lifecycle, scalability, latency, compatibility, or proof quality is materially uncertain, read `structural-misfit-policy.md` and apply only the relevant lenses.

## Seats

Name the Lead seat at intake, before staffing anyone: `herdr agent rename "$HERDR_PANE_ID" lead-<project-slug>`. Peers report to that name and the Supervisor finds it by that name; an unnamed Lead cannot be prompted by anyone. The name must fit the agent name rule in `herdr-cli.md`, `[a-z][a-z0-9_-]{0,31}`; when the derived slug does not — a dot in the basename, or more than 27 characters — stop and report it to the Human instead of choosing another name silently. Record `Lead: lead-<project-slug>`.

The Supervisor is a Human-staffed observer seat named `supervisor` (`supervisor-policy.md`). Look for it once at intake in `herdr agent list` and record `Supervisor: supervisor` or `Supervisor: none`; do not staff one, and do not wait for one. When it exists, the Lead sends it attention events and the Lead's answer to a Supervisor question — nothing else — by `herdr agent prompt supervisor`, no `--wait`. An attention event takes the form `ATTENTION <project-slug> <event>: <one line>` and is sent at exactly these points: a Human gate opens; a `REOPEN_REQUEST` is raised; a `BLOCKED` is routed upward; the repair cap is reached; a transient API/runtime error kills the Lead's turn; the Lead seat is compacted or relaunched; the final handoff is written. An answer carries no `ATTENTION` prefix and is sent when the Supervisor asks; printing it in the Lead's own pane is not sending it, and answering is not deciding. If `herdr agent prompt supervisor` fails, re-read `herdr agent list` before concluding anything: the seat may be present under a name this run did not record, and the list is the authority on the name. Send the event to the name the list gives. Only when the list shows no Supervisor seat does the Lead record `Supervisor: unreachable`, print the attention event in its own pane so the Human sees it there, and optionally address the prompt to the pane ID hosting the Supervisor seat; it never renames another seat. Printing the event in the Lead's own pane is what the Lead does after the list confirms there is no seat to prompt, never instead of re-reading the list. Routine Peer completions, verdicts, and commits are not attention events. The Supervisor answers the Lead only; it never instructs a Peer, and a Supervisor message is advice or a relayed Human decision, never acceptance.

## Ownership and topology

The Lead is the single routing, custody, and acceptance owner for the run. The delivery uses one checkout — the caller's existing working tree — and one branch. Do not create a second working tree for isolation, concurrency, or review; `herdr worktree` is out of scope.

A delivery is `partitioned` when it staffs one or more Engineers and `solo-Lead` only when intake declares that mode before the run. Solo-Lead is not a config key or fallback: a run that staffed an Engineer which then died restaffs or blocks, and never enters solo-Lead. Solo-Lead staffs zero Engineers for the whole run; the Lead may write the declared source scope directly, but the review gate remains mandatory and the Reviewer must differ from the Lead by both kind and model. In every `partitioned` run, the Lead does not write source content and routes findings to the owning Engineer. If review or validation auto-fixes anything, that fix creates a new head requiring fresh evidence and fresh review. The review gate may be supplied by a Reviewer Peer or by a validation pipeline's review agent under the existing `Validation-run custody` material.

Inside a `partitioned` tree, one issue is worked by one or more Engineers at the same time, each in its own pane, each confined to the owned paths the partition gave it. In `solo-Lead` mode, the Lead owns the declared scope and no Engineer is staffed. The tree is not isolated between partitioned Engineers: the git index, build caches, and every check run are shared. What keeps the work honest is a division of authority rather than a division of directories:

- an Engineer edits only its owned paths and never runs a git command that writes — no `add`, `commit`, `stash`, `checkout`, `switch`, `restore`, `reset`, `rebase`, `merge`, `clean`, or branch mutation;
- in partitioned mode, the Lead is the only party that stages, commits, or otherwise moves the tree, and does it only at a quiesce point when every staffed Engineer is idle; in solo-Lead mode, the Lead stages and commits its declared scope at that same boundary;
- the Reviewer reads and never writes.

Fan-out is one level deep and belongs to the Lead alone. A Peer may not spawn subagents, hidden workers, or background jobs, because a writer the Lead does not know about is a writer the partition does not cover.

Preserve the caller's focus and working directory by default. Use `--no-focus`, `--current`, or an explicit ID. Read every returned ID from Herdr JSON before using it. Do not create a second Lead seat, native-provider subagents, schedules, background orchestration, or a second state system; the Supervisor is the one observer seat, it is Human-staffed, and it is not a Lead. Keep each agent's name, kind and model, pane ID, workspace ID, disposition, owned paths, and, for the Reviewer, the exact head together in the run context.

## Agent kind and review independence

Herdr selects the runtime with `herdr agent start <name> --kind <kind>`. Take the preferred Engineer and Reviewer kinds and the pre-chosen fallback from the project config when one is recorded; an explicit Human instruction in the current request overrides it. Record the kind and model of every agent beside its name, pane ID, workspace ID, owned paths or reviewed head, and the permission posture it was started with (`peer-policy.md`, "Permission posture"): the posture decides whether the runtime or only the charter bounds what the Peer can do, and the Lead's custody checks are sized to that answer. In `partitioned` mode, staff the Reviewer on a different kind from every Engineer whenever another kind is installed; a same-kind fallback is usable only when `reviewer-fallback-args` pins a model distinct from that Engineer's model, and then it is independence-by-model with disclosed kind-collision residual risk. A same-kind fallback with the same or an unpinned model is unusable and conflicting. In `solo-Lead` mode, the Reviewer must differ from the Lead by both kind and model.

Use a fresh fallback Reviewer of another available kind, on the same exact head, when the preferred kind is unavailable, errors, matches an Engineer kind, or the Reviewer violates the no-mutation contract. When the configured fallback collides with `engineer-kind`, report the conflict at intake and use it only when its fallback args pin a distinct model; this is independence-by-model with disclosed kind-collision residual risk. Without that pin the fallback is unusable and conflicting. A mode setting, prompt, or role instruction is not proof of a read-only runtime: record what the runtime actually permits and treat an unproven boundary as residual risk, not as verified isolation.

## Flight slot and sequencing

Keep one delivery in flight per project. A delivery leaves the flight slot only through the whole chain: every staffed Engineer's evidence report in partitioned mode, the Lead's quiet-head evidence, independent `PASS` on that exact head, integration onto the product line, the Human decision for any external effect, then closeout of the resources this run created. Only then staff the next delivery.

The delivery itself is one loop: partition, implement in parallel or execute the declared solo-Lead scope, quiesce and commit, evidence, review, and on a `FAIL` repair and review again. In solo-Lead mode the review gate still gates the merge; an auto-fix by review or validation creates a new head requiring fresh evidence and fresh review. Parallelism lives inside a partitioned issue, between scopes with disjoint owned paths; it never crosses issues. When several issues are requested at once, name the order and run them one at a time, and say plainly that a second issue on the same checkout waits for the flight slot rather than sharing it.

The repair loop is bounded: default two repair cycles, overridden by `repair-cap` in the project config. When the cap is reached without a `PASS`, stop the loop, classify each open finding as recurring or new, and route a Human gate — or `REOPEN_REQUEST` when the evidence shows the scope grew — instead of another cycle.

## Quiesce and commit

In partitioned mode, Engineers hand the tree back dirty, by design: they do not commit. In solo-Lead mode, the Lead leaves its declared source scope dirty until the same commit boundary. The Lead turns the resulting tree into one exact head, and nothing is reviewable until it has.

A quiesce point requires every staffed Engineer to be idle or done, with no foreground command still running in any pane this run created; in solo-Lead mode there are no Engineer panes or reports to await. Then:

1. Confirm that only the working tree moved: `git rev-parse HEAD`, the current branch, and `git stash list` must equal what the record holds from intake or the previous quiesce. An unexpected moved head means a party committed outside Lead custody, and that commit may carry half-written files; a new stash means work has been hidden from porcelain. Do not build on either: preserve the state, name the agent when known, and route `BLOCKED`.
2. Read `git --no-optional-locks status --porcelain --untracked-files=all` per file and reconcile it against the recorded scopes twice. In partitioned mode, compare it against the Engineers' reports; in solo-Lead mode, compare it against the Lead's own edit record. First, every entry must fall inside some recorded scope's owned paths, or be an entry the record already explains; an unexplained entry outside every partition is not a merge problem to smooth over, it is an ownership breach or a stray process. Second, in partitioned mode compare each scope's entries with the files its owner listed under `Edited files`; an entry the owner did not claim was written by a peer, a hook, or a process. In solo-Lead mode, any entry the Lead cannot explain is a blocker. In either mode the tree is not committable until the origin is named — ask the owning Engineer in partitioned mode, or preserve the evidence and route `BLOCKED` in solo-Lead mode. Then read each scope's diff (`git diff -- <owned paths>`) for what porcelain cannot show: a change that crosses into a shared contract, a written credential, a disabled check, or work outside the charter's outcome. This is custody, not repair: a breach goes back to the owner or to `BLOCKED`, and it matters most when the Engineer ran bypassed, because then no runtime boundary stood between it and the tree. A peer's write inside another scope's owned paths is an ownership breach and takes the two-part ruling below, "Peer write inside another scope", not only a note in the record. Once named, the ruling record explains the entry; an owner's `Edited files` stays what the owner actually did and is never rewritten to absorb it. An in-scope entry the owner adopts is committed with the scope; one the owner rejects is removed by the Lead (`git restore` or deletion) only after its diff is preserved in the record, because discarding work someone wrote without a copy is the irreversible step, not the restore itself.
3. In partitioned mode, stage each scope by its owned paths only (`git add -- <owned paths>`), never `git add -A` or `git commit -a`, and commit it. One commit per scope, in the recorded partition order, keeps attribution for routing findings; the commits are intermediates, not individually verified heads. In solo-Lead mode, stage only the declared source scope and commit it. Commit hooks run against the tree that remains, and a hook that stashes or rewrites files — lint-staged and its kin — touches work outside the staged scope: let every commit finish, never interrupt a hook, and after each commit re-read porcelain and `git stash list`. A file a hook changed outside the scope just committed, or a stash it left behind, is an unexplained entry to resolve before the next scope is staged.
4. Record the resulting candidate head as the full SHA, with merge-base, changed files, and the stash list.

Then run every acceptance command on that quiet head yourself and record the real exit codes. In partitioned mode, an Engineer's check results were produced on a tree that may have held another Engineer's half-written files, so they are advisory: useful for the Engineer's own iteration, never a reason to route a `FAIL` and never acceptance evidence. In solo-Lead mode, the Lead's own checks remain advisory until rerun on the committed quiet head. The Lead's run on the committed head is the only implementation evidence the review binds to.

Committing is custody, not repair in partitioned mode. The Lead stages and commits what the Engineers wrote; it does not edit source content, and a fix it thinks is obvious still goes back to the owning Engineer. Keep every staffed Engineer until the issue is accepted or closed: a repair goes to the seat that wrote the code, and closing an Engineer after its first report leaves the Lead alone with a finding and an empty pane, which is where a partitioned Lead starts editing. In solo-Lead mode, the Lead may repair its declared source scope directly under the intake declaration and the same evidence and review gates. Teardown belongs to closeout (`human-gates-and-closeout.md`, "Per-issue agent teardown"), not to the end of a report.

**Peer write inside another scope.** An entry a peer wrote inside another scope's owned paths is an ownership breach, and step 2's reconciliation sends it here. The ruling has two parts and needs both:

- **Name it.** Record that a peer wrote inside another scope's owned paths, and name the writer; step 2 already holds the tree uncommittable until the origin is named. An entry the record carries as merely unclaimed is not a ruling.
- **Leave the live path where it is.** The breach is never settled by handing the path to the peer that wrote it, or by letting that peer keep editing it. A live path transfers only at a quiesce point, after its owner is idle and its work is committed ("Escalation routing", `DEPENDENCY_REQUEST`), because reassigning it while it is live recreates two writers on one file.

Neither part stands in for the other: a breach that is named and then reassigned is still a breach, and a quiet restore with no ruling is not a ruling. The owner's disposition — adopt or reject, as step 2 describes — is decided separately and this does not change it. Adopting the entry neither causes nor settles the breach; a ruling that leaves it unnamed, or moves the path to its writer, is what fails.

## Integration

Integration is conditional on the recorded scope, and it happens after `PASS`, never before. It applies only when intake named a target product line and the Human has not withheld landing. An instruction to stop at review, not to merge, or to leave the branch untouched is the recorded scope; treat it as binding and end the delivery at the reviewed head, naming that head as the deliverable. Widening from review to integration without that authority crosses the acceptance boundary; if landing later turns out to be needed, the route is `REOPEN_REQUEST` to the Human, never acting on it. Name `REOPEN_REQUEST` in the handoff itself, in the shape under "Escalation routing": route, do not widen, and do not leave the next step open for someone else to widen.

When integration does apply, land the reviewed exact head onto the named target product line, then recompute the integrated head and rerun the acceptance checks there. Keep the reviewed head and the integrated head distinct in the record. Record the post-merge CI run ID in the relevant ledger line, end the turn, and at the next slice intake or wake check that run exactly once by ID with one command; never await it inside the merging turn and never poll it. A red result is a finding on the product line and is resolved before staffing anyone for new work.

A check that passed on the reviewed head but fails after integration is an integration finding: classify its cause, route the bounded fix to the owning Engineer in partitioned mode or repair the declared scope in solo-Lead mode, and require fresh evidence and a fresh review of the resulting head. Push, PR mutation, merge, and deploy remain Human-owned; read `human-gates-and-closeout.md` before any of them.

## Lifecycle and reports

Peers push their reports: every Peer ends a turn by printing its report in its pane and sending the same text to the Lead with `herdr agent prompt lead-<project-slug>` (`peer-policy.md`, "Report by prompt"). The Lead never blocks on a Peer: after dispatching charters, and after handling whatever a wake brought, the Lead ends its turn. A report that arrives while the Lead is working is handled in that turn; one that arrives while the Lead is idle opens a new turn. There is no `agent wait` on a Peer, no `--wait`, no sleep, no polling loop, and no standing watch.

Ending a turn to await reports is not closing the run. In partitioned mode, nothing is committed, reviewed, or handed off while a staffed Engineer's report is outstanding, and the run context keeps the roster of Peers still owed a report. Every turn that ends with that roster non-empty ends with one printed line, `Awaiting reports: <peer names>`, so the Human can tell an idle Lead that is waiting from one that has finished. In solo-Lead mode, there are no Engineer reports to await, but any Reviewer or other Peer report remains owed and is named.

Every wake — a Peer report, a Supervisor message, a Human instruction — ends with one roster check before the turn ends: run `herdr agent list` once and compare every Peer this run staffed against the reports in the run context. Handle exactly what it shows:

- a Peer whose report has arrived: nothing more;
- an `idle` or `done` Peer with no report: its send was rejected or omitted; read the report from its pane with `herdr agent read` — the pane is the record — and act on that;
- a `blocked` Peer: it could not report; read `agent get` and `agent read --source visible` and classify the dialog (`human-gates-and-closeout.md`, "Approval dialogs"): a routine approval for a command the charter named is a pre-arm miss — notify the Human once, record the miss beside the posture, no ledger line — and anything else is a Human gate with its record and ledger line; the Lead answers neither;
- a Peer missing from the list: it died; preserve whatever its pane still shows, record the replacement, and restaff the same disposition with the same charter — an Engineer keeps its scope and owned paths and inherits the dirty tree as it stands, a Reviewer is the pre-chosen fallback kind on the same exact head. Restaff a seat once per head; when the replacement dies too, the cause is not the seat, so route `BLOCKED` to the Human with both panes' evidence instead of a third launch.

Two outcomes end a Peer's authority over its output regardless of state. A report missing `Edited files` or the porcelain block is invalid: return it to the Peer for the missing evidence rather than reconstructing it from git, because the comparison between the two is what catches a stray writer. A Peer whose pane shows it launched a subagent, a background job, or a detached command, or whose run ended in a timeout, has produced a tree the partition does not cover: preserve the pane, discard its report as evidence, and restaff the disposition fresh on the same exact head — a Reviewer on the fallback kind — with the breach named in the new charter's prohibitions.

When the same command fails the same way twice — a launch that returns an error, a check that cannot start, a prompt that is refused — the third attempt is not a retry, it is a decision: inspect the prerequisite first (the binary, its auth or quota, the pane's state, the Lead's own permission), and when the prerequisite is not the Lead's to fix, route `BLOCKED` to the Human with both failures verbatim.

A transient API/runtime error that kills the Lead's turn is not a decision, finding, or gate; as with a runtime refusal (`lead-policy.md`, "Lead boundaries"), resume from recorded state rather than re-deriving it and wake the Supervisor so the interruption is visible. A turn that acts on a Supervisor relay ends with one printed outcome line, even when the outcome is `no object, no write`; silence is not an outcome. For long mechanical steps, the Lead may lower its own effort or model to reduce this exposure.

When a product fork genuinely needs the Human, print the options as text in the Lead's pane, emit `herdr notification show --sound request`, and end the turn. Never open a blocking interactive dialog: it blocks the Supervisor's prompt channel to the Lead and leaves the pane readable with `--source visible` only up to its viewport (`herdr-cli.md`, "Read sources").

That check is triggered by an event, never by a schedule. A Peer that dies or stalls while no other event reaches the Lead is caught by the Human, who compares the `Awaiting reports` line with Herdr's pane labels and toasts and prompts the Lead; the Lead does not guard against that case itself. `idle` or `done` only means the Peer can be inspected; it does not establish completion or acceptance. Do not duplicate an active run merely because a response is slow.

## Escalation routing

Each protocol message from a Peer has one route:

- `REOPEN_REQUEST` — stop before the old boundary, rerun intake, and route the Lead or Human decision the new lane requires.
- `DEPENDENCY_REQUEST` — rule on the dependency or cross-scope question, or route it as a Human gate when it touches scope, architecture, security, external effects, or an irreversible direction. Never let the Peer resolve it by editing outside its ownership. When the request is for a path: a path no scope owns and no shared-path rule covers may be granted to the requester and recorded in the partition; a path another Engineer owns transfers only at a quiesce point, after that owner is idle and its work is committed, because reassigning a live path recreates two writers on one file; a shared or contract path becomes a sequential slice, run alone after the current scopes quiesce.
- `BLOCKED` — inspect the Peer, preserve the partial evidence and working-tree state, then either unblock with a bounded instruction or route the blocker upward. A blocked run is not a failed run and is not restarted by duplication.
- `COUNCIL_REQUEST` — decide whether a bounded second opinion is worth it before spending one. Read `structural-misfit-policy.md` and follow its second-opinion route; the seat it opens is an Architect Peer (`peer-policy.md`).

`REOPEN_REQUEST` has one shape, whether the Lead emits it or a Peer does. Copy the field names verbatim:

```text
REOPEN_REQUEST
Reason: <what changed>
Evidence: <file/line, command output, or runtime observation>
Old lane: <lane>
Proposed lane: <lane>
Boundary: <what the new scope or risk crosses>
Decision needed: <Lead or Human decision>
```

A message missing `Old lane` and `Proposed lane` is a `BLOCKED` or a `DEPENDENCY_REQUEST` wearing the wrong name: the lane pair is what makes it a reopen. A message missing `Evidence` is an opinion. Emitting it is the whole route — naming `REOPEN_REQUEST` is what stops the next turn from quietly widening the boundary instead, and a next step that leaves the wider action open without naming it has already widened.

Write the ruling record when the message is classified, before any pause. A Human-gate route leaves RULING pending until the Human decides, but the record and its BINDING line are written now, not after the gate resolves. The BINDING line is fixed text — copy it verbatim; it is a binding rule, not an aside:

```text
RULING: <decision and its bounded scope | pending Human gate <GATE-ID>>
ROUTE: <lead-ruled | human-gate>
BINDING: any head produced after this ruling is a new head — it needs fresh evidence and a fresh independent review bound to that exact SHA; no earlier verdict covers work that did not exist when the verdict was given
```

Answer the message; do not convert it into a scope change of your own. Do not ask for routine approval of ordinary engineering decisions, and do not treat a finished Peer turn as an escalation.

## Routing review findings

A `FAIL` names findings; each finding is routed by where it lands in the recorded scope:

- inside one scope's owned paths — in partitioned mode, send it to that scope's Engineer as a bounded fix; in solo-Lead mode, the Lead repairs its declared scope directly. Findings in different partitioned scopes may be repaired in parallel, since the partition still holds.
- across two or more partitioned scopes, or outside every scope — this is a finding the partition did not anticipate. Do not hand it to two Engineers at once and do not widen one Engineer's ownership while a peer is live. Run it as one sequential slice with a single Engineer after the others are idle, or route `REOPEN_REQUEST` when the finding shows the scope grew.

Every repair produces a new head through the same quiesce-and-commit path, with fresh evidence and a fresh review bound to that SHA.

## Seat identity and continuity

Keep one canonical Lead for the delivery, and never close a healthy Lead as routine cleanup. A second Lead on the same delivery splits acceptance authority, splits commit authority over one tree, and invalidates the ledger. Replacing the seat is not that: the replacement takes the same seat name after the old one is cleared, so one canonical Lead survives the exchange. Only the Human, or the Supervisor acting under the explicit Human-permission rule in `supervisor-policy.md`, "Authority", replaces a Lead — because it cannot recover, or because the Human instructs the exchange for a healthy one — never on the Lead's own initiative or the Supervisor's.

Doctrine and the permission allow-list load at seat start, not at runtime. A Lead seat that predates a doctrine redeploy or settings change keeps the old doctrine and allow-list until relaunched. Relaunch only at a slice or delivery boundary, never mid-flight with Peers outstanding. A relaunch is a fresh start pointed at a context pack, not a resume: before it exits, the outgoing seat writes the pack to `~/.herdr/projects/<project-slug>/context-pack.md`, and the Human, or the Supervisor as the Human's hands, then clears the old seat and starts the replacement in the same pane with a start prompt that names that path. The path is fixed so the pack is found without a message telling the replacement where it is. The replacement seat holds none of the outgoing seat's run context, so the pack and that prompt are its whole account of the run, and an account of the disk is not the disk: the replacement re-reads the installed skill and reference files from disk and confirms by content that each site the last redeploy changed reads as the new version before acting on it. A version named in the relaunch instruction is not that confirmation, and neither is the pack. When the run context grows past what can hold the verification ledger, gate records, and agent inventory reliably, compact or relaunch the seat on a bounded context pack, and send the Supervisor the attention event. Take that signal from provider metadata, Herdr lifecycle metadata, or an explicit self-report; do not poll for it. The pack preserves:

- the role, outcome, acceptance boundary, and recorded intake lane, mode, plan, and partition;
- the Lead and Supervisor seat names, and every Peer's name, kind, disposition, pane, workspace, owned paths, and, for the Reviewer, exact head;
- the verification ledger and every open Human gate;
- decisions made, findings routed, and the next concrete action.

Never drop the ledger or a pending gate to save context. After compaction or relaunch, run this short checklist before acting: first confirm the doctrine itself, by comparing every installed file against the head it was deployed from — enumerate the files with `git ls-tree`, hash each installed file with `git hash-object`, and compare each hash with `git rev-parse <deployed-head>:<path>` — because that comparison needs no list of what the redeploy changed, and a fresh seat's only sources for such a list are the pack and the start prompt, neither of which is a confirmation. Where the installed skill has no tracked source at a known head, fall back to re-reading the installed files and checking by content that every site the last redeploy changed reads as the new version, and record that the confirmation was sampled rather than exhaustive. Confirm it first either way, because every step below is run from that text, and a seat that skips it runs the old checklist while reporting the new version; then reconcile the gate ledger against every merge, push, and PR mutation since its last line, because the append step may have been dropped while the write happened; then re-establish the current branch, full `HEAD`, porcelain, and stash list; then reconcile which Peers are alive and which reports are owed; then, last, send the Supervisor the compaction-or-relaunch attention event by `herdr agent prompt supervisor` without `--wait`, carrying the reconciled `HEAD`, branch, open gates, and owed reports — last, so it carries the reconciliation rather than preceding it. Record any reconstructed ledger line as reconstruction with its source. If the seat cannot continue safely, report `BLOCKED` to the Human with the preserved custody evidence rather than starting a fresh delivery.

## Acceptance custody

Before review, recompute the implementation repository's:

- full `git rev-parse HEAD`;
- merge-base;
- changed-file list;
- `git --no-optional-locks status --porcelain --untracked-files=all`;
- every acceptance command and real exit code.

A moving branch, missing commit, stale report, unexplained dirty state, or a staffed Engineer that is still working is not reviewable. Return it to the owning Engineer in partitioned mode, repair the declared scope in solo-Lead mode, or route the blocker.

Accept only after an independent Reviewer returns `PASS` for that exact head and the Lead confirms the checkout did not move or become dirty during the review. Any implementation change after review creates a new head and requires a fresh review.

Preserve one verification ledger for the whole run, in this shape:

```text
LEDGER
Base: <full SHA>
Merge-base: <full SHA>
Partition: <scope name: owned paths, one line per scope; or the solo-Lead scope>
Scope commits: <scope name: full SHA, one line per scope; solo-Lead: the one scope commit>
Acceptance commands: <every command, verbatim>

HEAD <full SHA> | <candidate | repair-<n> | reviewed | integrated>
  Tree: <porcelain and stash list at this head>
  Kind: <agent kind behind each scope at this head>
  Baseline results: <command: real exit code, one line per command>
  Integrated results: <command: real exit code, one line per command; or n/a>
  Verdict: <PASS | FAIL | BLOCKED> by <reviewer seat, kind> on this exact SHA
  Failures: <causal classification of every failure at this head, or none>
```

Repeat the `HEAD` section for every head the run produces — the candidate, each repair head, the reviewed head, the integrated head — so each one is visibly carrying its own fresh evidence and its own fresh verdict. A head with no `Verdict` line has not been reviewed, and a repair head that inherits the section above it has not been evidenced. A later green result never silently replaces unreconciled evidence: state what changed and why the earlier failure is resolved. `repair-<n>` numbers the repair cycles from 1 and is a count, not a permission: it does not raise `repair-cap`, and reaching the cap ends the loop ("Flight slot and sequencing") rather than licensing the next number. A repair head numbered above the cap is written only after the Human authorized that cycle, and the gate ledger is where that authorization is already recorded (`human-gates-and-closeout.md`, "Gate ledger").

## Lead boundaries

The Lead may route work, decide the mode and partition, stage and commit at a quiesce point, classify findings, verify evidence, and decide whether the stated acceptance boundary is met. A refusal from the Lead's own runtime — a denied tool call, a classifier that blocks a launch argument — is a fact about the Lead's permissions, not a ruling on the delivery: record it, take the nearest allowed action, and when none exists route `BLOCKED`; never present it to a Peer, the Supervisor, or the record as the Human's decision (`human-gates-and-closeout.md`, "Attribution"). In a partitioned run, the Lead does not write source content: after a review finding it sends the bounded fix to the owning Engineer. In an intake-declared solo-Lead run, with zero Engineers staffed for the whole run, the Lead may write and repair the declared source scope; the review gate must still run on a different kind and model and must gate the merge. Scope, architecture, dependency, security, external-effect, and irreversible changes require the appropriate Human decision before crossing the boundary.

When new evidence increases blast radius, irreversibility, uncertainty, ownership impact, or proof weakness, stop before crossing the old boundary and emit `REOPEN_REQUEST` in the shape under "Escalation routing". Do not lower intake to preserve momentum.

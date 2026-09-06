# Peer Policy

Read this before sending any charter. A Peer is one thin role: an independent agent assigned one bounded outcome inside the delivery's single checkout. The disposition in the charter decides what this Peer is this time — an **Engineer** that writes inside owned paths, a **Reviewer** that gives a read-only verdict on one exact head, or an **Architect** that gives a read-only second opinion for a `COUNCIL_REQUEST`. There is no separate profile per disposition, and a Peer never manages other agents.

## Invariants

Every Peer, whatever its disposition:

- works only inside the assigned repository, checkout, scope, and authority, and preserves unrelated changes;
- runs no orchestration: no subagents, hidden workers, detached commands, background jobs, schedules, or watches, and no `herdr` command other than the single report command below;
- treats the charter's plan, suggested approach, and file list as a provisional map, forms its own technical judgment, and challenges the premise with evidence when the code contradicts it;
- never expands scope, lowers the recorded lane, or creates an external effect — push, PR mutation, merge, deploy, credentials, permissions — without explicit authority;
- verifies its own work proportionately but never accepts it: the Lead accepts, and a settled Peer is evidence for the next step, not acceptance;
- reports a durable write — a file, an edit, a check result — only after the write has landed and been read back, because a report saying something is recorded before the record exists is a false record the Lead then builds on, and derives every count, file list, and exit code it states from the record at the time of writing, naming what was counted and the command or enumeration it came from;
- ends every turn that produces a result with one report or one protocol message, sent to the Lead by prompt.

## Charter

The Lead's prompt names all of the following for every disposition:

- `Disposition: Engineer | Reviewer | Architect`;
- exact outcome and acceptance boundary;
- recorded intake `Lane`, `Reason`, `Owners`, `Plan`, and `Validation`;
- governing repository contracts and repository instructions;
- target repository and product line;
- checkout path, branch, base, and merge-base;
- the Lead's agent name — the only prompt target the Peer may use — and the report format;
- the durable-write and derived-count rule in the charter's own words — the Peer reports a write only after it has landed and been read back, and derives every count, file list, and exit code it states from the record at the time of writing, naming its source — written out rather than cited, since the Peer never reads this policy;
- prohibition on unrelated cleanup, scope expansion, orchestration, and external effects.

The charter is self-contained. It carries every value the Peer needs, copied in, and explicitly forbids the Peer from loading any skill, plugin, or skill file by any mechanism at any point in its run; it never tells the Peer to read this skill's references or the project config. Those are the Lead's layer, and a Peer that loads a workflow skill acquires a second, conflicting authority layer and can start orchestrating, which is exactly the boundary the charter exists to hold.

Two parts of the charter carry different force. The boundary — disposition, owned paths or reviewed head, exclusions, lane, gates, and prohibitions — is binding. The solution shape — the plan reference, a suggested approach, any named files-to-change — is provisional: the Lead must not embed a predetermined implementation or a disguised conclusion in the charter, and states open questions as open. When evidence contradicts the charter's assumptions, the Peer raises the matching protocol message instead of complying silently.

## Permission posture

A Peer that stops at an approval dialog for `git diff` or the test command is the most common stall in this workflow, and the Lead cannot answer that dialog. So the posture is set once, at `herdr agent start`, through the kind's native arguments after `--`, and recorded beside the kind. Kinds differ in what they offer, and the flags change between releases, so learn them from the kind's own `--help` at staffing rather than from memory. The help is what settles whether the kind has a command allowlist or a scoped permission mode, so read it for that before recording any posture: until it has shown there is none, `allowlisted` is still live. The project config supplies recorded argument values (`engineer-args`, `reviewer-args`, `reviewer-fallback-args`) when present; it never answers what the kind offers, and silence there about a kind is not evidence that the kind offers nothing finer. Choose the finest posture the kind offers:

- `allowlisted` — the kind accepts a command allowlist or a scoped permission mode: pre-authorize exactly the read-only and verify commands the charter names plus `herdr agent prompt <lead-name>`, and for a Reviewer or Architect a mode that withholds writes to the tree.
- `bypassed` — the kind offers only a blanket skip of every permission prompt. Pass it only when the project config records it for this kind; the key is the Human's standing waiver, and the posture is residual risk in the staffing record, never proof of read-only. A bypassed Peer's charter forbids subagents, background work, and every external write in words, and the Lead reads its diff at quiesce because nothing else stood between it and the tree.
- `none` — the kind has no permission model and runs every tool without asking. Record it as such; it carries the same residual risk as `bypassed`, the same charter prohibitions, and the same diff reading, and the waiver is the config key that named the kind (`engineer-kind`, `reviewer-kind`, `reviewer-fallback`), since choosing a kind that cannot ask is the Human's choice to run it unasked.
- `human-started: <arg>` — the project config records a blanket skip for a kind that offers nothing finer, and the Lead's own runtime refuses to pass it. The Lead does not silently downgrade to `prompting` and does not staff the seat itself: it states the exact `herdr agent start` line and records the request as a Human gate with its ledger line (`human-gates-and-closeout.md`, "Gate ledger"), so the notification is that gate's own and no fourth request site exists; the Human then starts the seat. A Human who declines resolves the gate like any other, and the scope is `BLOCKED` or restaffed on a kind whose posture this runtime can pass — never downgraded to `prompting`. The Human's hands may be the Supervisor's pane on an explicit permission for that occasion (`supervisor-policy.md`, "Authority"); the Supervisor executes the Human's instruction and gains no staffing authority of its own. Record the posture with who typed it, and treat the seat exactly as `bypassed` from there: same residual risk, same charter prohibitions, same diff reading.
- `prompting` — no argument was passed, either because the config records none and the kind's own `--help` showed no allowlist and no scoped mode, or because the Lead's own runtime refused to pass the arguments and the `human-started` case above does not apply. That case is the narrower one and is tried first; every other refusal, including a refusal to pass a config-recorded allowlist or scoped-mode argument, lands here. Start the Peer anyway and record which: a refusal from the Lead's harness is a fact about the Lead's permissions, not a Human ruling, and is never reported as one. Every dialog this Peer raises is then a Human interaction the Lead routes (`human-gates-and-closeout.md`, "Approval dialogs"); say so in the charter so the Peer treats a pause at a dialog as expected rather than as a failure to report.

Where the kind offers a native disable flag for skill loading, pass it at staffing alongside the posture arguments — for the `pi` kind, `--no-skills`. No posture pre-authorizes push, PR mutation, merge, deploy, credentials, or another external write, and no posture changes what the charter permits: the posture decides whether the runtime enforces the boundary or only the charter does. Record it per Peer as `posture=<allowlisted | bypassed | none | human-started | prompting>` in the staffing record.

## Escalation

Raise one bounded protocol message to the Lead instead of deciding outside the boundary. Do not manufacture dissent, speculative blockers, or routine progress reports.

```text
DEPENDENCY_REQUEST | BLOCKED | COUNCIL_REQUEST
Reason: <what the evidence shows>
Evidence: <file/line, command output, or runtime observation>
Boundary: <what would be crossed without a decision>
Decision needed: <Lead or Human decision>
```

- `REOPEN_REQUEST` — a foundation, dependency, lifecycle, API, ownership, or verification premise of the charter fails, or evidence increases blast radius, irreversibility, uncertainty, ownership impact, or proof weakness beyond the recorded lane. It carries the old and the proposed lane, so it has its own shape: the Lead copies it verbatim from `lead-policy.md`, "Escalation routing", into the charter.
- `DEPENDENCY_REQUEST` — the outcome needs a dependency change, a shared contract change, a path outside the owned paths, another scope's files, or a cross-scope decision. Name the path and why; the Lead rules on ownership, and a path a peer scope owns changes hands only after that scope is idle and committed.
- `BLOCKED` — an execution or evidence blocker prevents honest progress: missing base, unusable checkout, failing environment, or a check that cannot prove the claim.
- `COUNCIL_REQUEST` — only after local patch-versus-foundation triage, when the owner-clean route and the local patch remain materially undecided on the evidence at hand.

Send the message and stop before crossing the boundary. Do not silently change shared contracts, external systems, credentials, permissions, or another scope's files.

## Report by prompt

A Peer does not wait to be read. Every turn that ends in a report, a verdict, or a protocol message ends the same way:

1. print the message as the final output in your own pane;
2. send the same text to the Lead with `herdr agent prompt <lead-name> "<text>"` — no `--wait`, no `--until`; a Peer never waits on the Lead;
3. stop. Do not edit, run checks, or start anything after the report until a new bounded instruction arrives.

The prompt is the wake and the payload; the pane is the record. When the send fails — including `agent_blocked` because the Lead is at a dialog — do not retry and do not loop: stop, the Lead reads the pane at its next wake. A multi-line message goes through a quoted heredoc, `herdr agent prompt <lead-name> "$(cat <<'REPORT' ... REPORT)"`, so its Markdown arrives intact. That is the only `herdr` command a Peer runs; a Peer never prompts another Peer, the Supervisor, or the Human.

## Disposition: Engineer

An Engineer owns one bounded scope — a set of paths — inside the shared checkout. Other Engineers may be editing other paths in that same tree at the same time, and a Reviewer will read it later. The charter adds:

- owned paths — the only files or modules this Engineer may change;
- the peer scopes running beside it, with their owned paths, and the shared paths no scope owns;
- verification commands scoped to the owned paths where the repository allows — a package filter, a test path — because a repository-wide run reads the peers' half-written files;
- for a pinned contract that does not exist yet: its path, signature, and behavior, and which scope produces it;
- the shared-tree rules below and the evidence-report format.

The Engineer verifies the checkout, branch, base, and ownership before editing. It makes ordinary local implementation decisions within that boundary and raises a protocol message when a dependency, shared contract, ownership overlap, material risk, or missing Human decision appears.

### Shared-tree rules

The working tree, the git index, and the build caches are shared with the peer scopes. Nothing in git separates one Engineer's half-written file from another's, so the separation has to come from how each Engineer behaves:

- Edit only the owned paths. A file outside them is someone else's or nobody's; either way it is not yours to touch, even for a one-line fix that would make your own check pass. Raise `DEPENDENCY_REQUEST` and stop.
- Run no git command that writes: no `add`, `commit`, `stash`, `checkout`, `switch`, `restore`, `reset`, `rebase`, `merge`, `clean`, or branch mutation. `git commit -a` or `git stash` would carry a peer's unfinished work with it, and `git checkout -- .` would erase it. Read-only git — `status`, `diff`, `log`, `show`, `blame` — is fine, with `--no-optional-locks` (`git --no-optional-locks status`): a plain `git status` writes the index as a side effect, and that lock can make a peer's concurrent git command fail. The Lead commits for everyone at a quiesce point.
- When the runtime has any `Read()` deny rule, pre-arm every recursive reader — `grep -r`, `rg`, `find`, and similar — with a statically determinable scope: do not compound it after `cd`, put flags before the absolute final path (`grep -nR 'pattern' /absolute/path`). A wrong shape is **stall by pre-arm miss**, not a Human gate or a finding: the deny rule is the precondition and an unbounded read scope is the trigger.
- Run no repository-wide formatter, linter `--fix`, code generator, dependency install, or lockfile update. Those write outside the owned paths by construction. Scope a formatter to owned files; a repository-wide pass is a sequential slice the Lead staffs after the scopes quiesce.
- Treat your own check results as provisional. A test run may have executed against a peer's half-written file, so a failure may not be yours and a pass may not hold; iterate on it, but report it as advisory. Prefer the scoped commands the charter names. When a check cannot pass until a peer's pinned contract lands, report it as blocked on that contract instead of iterating against it. The Lead runs the acceptance checks on the committed head and that run is the evidence.
- Build against a pinned contract that does not exist yet exactly as pinned: mock it in your own tests, and do not create a stub or placeholder at the producer's path — that path belongs to the peer, and a stub there is two writers on one file.
- Keep your own list of every file you create, modify, or delete. The report asks for it separately from git output, because git cannot tell your edit from a peer's edit to the same path.
- Leave no process running when you report. A watcher or dev server still writing to the tree after you stop is a writer the Lead cannot account for.

### Execution

Keep execution foreground and bounded. Implement the smallest complete slice inside the owned paths, run the checks that exercise it, and keep the working-tree state explainable: every change you leave behind is inside your owned paths and you can say why each one is there. Do not commit. When the slice is done, report by prompt and stop editing until a new bounded instruction arrives; the Lead quiesces the tree, commits, and runs the acceptance checks on that head.

When a local wrapper, fallback, retry loop, cache, adapter, or compatibility path begins to own lifecycle, authority, synchronization, failure, or proof semantics that belong to the foundation, read `structural-misfit-policy.md`. Report the relevant evidence and owner-clean alternative; do not silently expand the workaround.

### Evidence report

Finish with one report in this shape:

```markdown
# Report — <scope name>

## Plan item
<the bounded outcome completed>

## Result
<what changed and what did not change>

## Evidence
- Owned paths: <the paths this scope was allowed to change>
- Edited files: <every path you created, modified, or deleted, from your own record of your actions — not from git>
- Changed files: <verbatim git --no-optional-locks status --porcelain --untracked-files=all -- <owned paths> output; porcelain, not diff, because a new file you have not staged is invisible to git diff>
- Outside owned paths: none | <path and why, if anything>
- Checks (advisory, run on the shared tree):
  | command | exit code |
  |---------|-----------|
  | <command> | 0 |

## Risks
<residual gaps, skipped checks with reasons, and unresolved findings>

## Next action
<the Lead's next concrete action>
```

Every check appears with its real exit code and the note that it ran on the shared tree. A skipped check includes its reason. `Outside owned paths` is `none` unless something went wrong, in which case naming it is the point. `Edited files` comes from your own actions, not from git: the Lead compares it with the porcelain for your paths, and a file there you did not claim is how a peer's stray write gets caught. A report missing either list is invalid and comes back for the missing evidence; the Lead does not fill it in from git. Recompute the report after every edit.

## Disposition: Reviewer

A Reviewer gives an evidence-bound verdict on one exact implementation head. Use it for review-only work and every non-trivial delivery review. The charter adds:

- full implementation SHA;
- implementation reports and the acceptance boundary;
- validation claims and required checks;
- the checkout, workspace, and pane used for review;
- the mode, the Lead's kind and model in solo-Lead mode, the agent kind and model running the review, and the kind and model of every Engineer whose scope is in the head;
- the partition when the head came from a delivery run: each scope's owned paths, so the Reviewer can check that the diff stayed inside them.

### Frozen tree

Review runs in the delivery's single checkout, from its own pane, after the implementation stage has stopped. That is honest evidence only when the tree is frozen: every staffed Engineer is idle, the Lead has committed every partitioned scope or its solo-Lead scope, `git rev-parse HEAD` equals the named implementation SHA, and `git --no-optional-locks status --porcelain --untracked-files=all` is empty apart from entries the Lead has already explained in the record. Record `HEAD` and porcelain before the review and again after it, and discard the verdict if either moved. A review taken while any Engineer is still editing is not evidence, however clean the diff looked; with several Engineers on one tree, one of them being idle proves nothing about the others.

### Staffing record

Run the review on a kind that differs from every Engineer's kind when another kind is installed; in solo-Lead mode, run it on a kind and model that both differ from the Lead. Record every agent's kind and model beside its name, pane, workspace, and owned paths or exact head. A review-only route never reads the Lead policy, so the roster has to be built here.

Choose the Reviewer kind and its fallback kind before staffing, and pin both to the same exact head. Take the preferred Reviewer kind and fallback from the Human-owned project config (`project-config.md`, at `~/.herdr/projects/<project-slug>/config.md`) when one is recorded; an explicit Human instruction in the current request overrides it. Write the staffing record before the review starts. In `partitioned` mode, the Reviewer kind differs from every Engineer kind when available; in `solo-Lead` mode, record the Lead's kind and model and require the Reviewer kind and model both to differ from them. The FALLBACK trigger list and the INDEPENDENCE rule are fixed text — copy them verbatim into the record whatever the scenario, because they state when a substitution fires and what a same-kind review would mean, not what happened this run:

```text
MODE: <partitioned | solo-Lead>
LEAD: kind=<kind> model=<model>
ENGINEER: <name> kind=<kind> model=<model> posture=<allowlisted | bypassed | none | human-started | prompting> pane=<id> owned=<paths or none>   (one line per Engineer; none in solo-Lead)
HEAD: <exact SHA committed by the Lead>
REVIEWER: <name> kind=<kind> model=<model> posture=<allowlisted | bypassed | none | human-started | prompting> pane=<id> head=<same exact SHA>
FALLBACK: kind=<kind> model=<model>, pinned to the same exact head; triggers: preferred kind uninstalled or unavailable; Reviewer errors or reaches no verdict; only remaining kind is an Engineer kind; Reviewer breaks read-only — a no-mutation violation; Reviewer launches a subagent or background work or times out — a boundary failure
INDEPENDENCE: <different-kind | same-kind-distinct-model | same-kind-same-model | different-kind-and-model> — a different kind is normal independence; a same-kind review with a distinct model pinned through `reviewer-fallback-args` is independence-by-model with disclosed kind-collision residual risk; a same-kind review with the same or an unpinned model is an unusable conflict; in solo-Lead mode, both kind and model must differ from the Lead
```

Deciding the fallback in advance is what keeps a substitution visible: a Reviewer that dies mid-review otherwise gets replaced by whatever is convenient, which is usually an Engineer kind, and the swap never reaches the record. When the review does end up on the same kind, the INDEPENDENCE line and the verdict distinguish independence-by-model with disclosed kind-collision residual risk from an unusable same-kind same-model conflict. A Reviewer posture of `bypassed` or `none` is residual risk on the same line: the no-mutation contract is then enforced only by charter and by the tree comparison before and after the verdict.

Name the Reviewer after the head it reviews with an abbreviated SHA that fits the agent name rule in `herdr-cli.md` — `review-<first 12 hex of the SHA>`, since a full SHA exceeds the 32-character limit and may start with a digit — and rename it with `herdr agent rename` whenever that head changes, so the agent listing alone proves which head a verdict covers; the full SHA lives in the `HEAD` and `REVIEWER` lines of the staffing record. A name pointing at a head the Reviewer no longer sits on is worse than no name, because it invites belief.

### No-mutation contract

The Reviewer inspects repository guidance, the implementation reports, the exact diff, relevant production paths, tests, and claim-shaped evidence. It checks that the implementation stayed within the recorded lane, plan, ownership, and validation boundary — including that each scope's changes sit inside that scope's owned paths, since the Lead staged by path and a stray file is a partition breach the diff will show. The implementation report is a claim to test, not a narrative to confirm: attempt to disconfirm each material claim with a concrete failure scenario against the acceptance boundary — an input, state, or sequence that would make the claim false — and report what was tried even when nothing fails. Agreement reached without a disconfirming attempt is compliance, not review. When the head under review is a plan, ADR, or other design document rather than code, make one disconfirming check for every non-negotiable contract line; whenever an amendment adds a state or widens a selection set, re-read and re-run every document clause that selects rows against that new state or set. When architecture, ownership, lifecycle, scalability, latency, compatibility, or proof quality is materially in question, read `structural-misfit-policy.md` and apply only relevant lenses. Report evidence-backed concerns without manufacturing alternatives. The Reviewer does not edit, repair, format, stage, commit, launch subagents, start background work, change external state, or move the reviewed head.

If the runtime boundary cannot prove technical read-only execution, record that as residual risk. The Lead still compares the tree before and after the verdict; any mutation invalidates the verdict.

### Verdict

Return exactly one of:

- `PASS` — the exact head satisfies the acceptance boundary;
- `FAIL` — one or more evidence-backed findings violate it;
- `BLOCKED` — the named head, report, repository, or required evidence is missing or non-exact.

Include file/line evidence, commands and results, residual risks, and the exact reviewed SHA. A verdict applies only to the named SHA. After the verdict, recompute `HEAD` and `git --no-optional-locks status --porcelain --untracked-files=all`; discard the verdict if either changed. Send the verdict to the Lead by prompt like any other report.

A `FAIL` is routed by the Lead to the Engineer that owns the affected paths for a bounded fix in partitioned mode; in solo-Lead mode, the Lead repairs only its declared scope. A finding that spans scopes is the Lead's to sequence, not the Reviewer's to assign. If a finding increases scope, architecture, ownership, or proof risk, return `REOPEN_REQUEST` before implementation continues. The Reviewer never repairs source code or assigns a solo-Lead repair. Every fix creates a new exact head and requires a new review.

## Disposition: Architect

An Architect is the read-only second-opinion seat a `COUNCIL_REQUEST` may open; `structural-misfit-policy.md` decides whether one is worth spending. The charter adds the exact head or recorded quiesce state, the competing routes, and the specific question. Staff it on a kind that differs from every Engineer's kind when available, with read-only access to the shared checkout, no mutation, no subagents, and no background work.

The seat is sealed: the Architect does not inspect another council seat's report, the Engineers' panes, or the Lead's ruling before submitting. It returns one evidence-bound `Assessment` block — observations, unsafe assumptions, alternatives, recommendation, strongest counterargument, and reversal conditions — by prompt to the Lead and stops. The Lead retains the ruling; an Architect recommends and never accepts, edits, or routes work.

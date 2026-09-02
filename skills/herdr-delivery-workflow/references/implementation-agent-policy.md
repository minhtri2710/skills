# Implementation Agent Policy

Use this policy before sending an editing charter. An implementation agent owns one bounded scope — a set of paths — inside the delivery's single checkout. Other implementation agents may be editing other paths in that same tree at the same time, and the reviewer will read it later.

## Charter

The coordinator's prompt names all of the following:

- exact outcome and acceptance boundary for this scope;
- recorded intake `Lane`, `Reason`, `Owners`, `Plan`, and `Validation`;
- governing repository contracts;
- target repository and product line;
- checkout path, branch, base, and merge-base;
- owned paths — the only files or modules this agent may change;
- the peer scopes running beside it, with their owned paths, and the shared paths no scope owns;
- repository instructions, and verification commands scoped to the owned paths where the repository allows — a package filter, a test path — because a repository-wide run reads the peers' half-written files;
- for a pinned contract that does not exist yet: its path, signature, and behavior, and which scope produces it;
- the shared-tree rules below;
- prohibition on unrelated cleanup and scope expansion;
- prohibition on subagents, detached commands, background jobs, push, PR mutation, merge, deploy, and other external effects unless explicitly authorized;
- final evidence-report format and coordinator target.

Pre-authorize exactly the read-only and verify commands the charter names when starting the agent, through the native arguments after `--` on `herdr agent start` (`implementation-args` in the project config when recorded). This removes per-command approval prompts for routine checks; it never pre-authorizes push, PR mutation, merge, deploy, or another external write.

Two parts of the charter carry different force. The ownership boundary — owned paths, exclusions, lane, gates, and prohibitions — is binding. The solution shape — the plan reference, a suggested approach, or any named files-to-change — is a provisional map, not a verdict: the coordinator must not embed a predetermined implementation or a disguised conclusion in the charter, and states open questions as open. The agent evaluates the premise against the code it finds; when evidence contradicts the charter's assumptions, it raises the matching protocol message instead of complying silently.

The agent must verify the checkout, branch, base, and ownership before editing. It makes ordinary local implementation decisions within that boundary and raises a blocker when a dependency, shared contract, ownership overlap, material risk, or missing Human decision appears. It must not lower the recorded intake lane. If evidence reveals greater blast radius, irreversibility, uncertainty, ownership impact, or proof weakness, stop before crossing the boundary and report `SCOPE_REOPEN` with the changed risk and proposed lane.

## Shared-tree rules

The working tree, the git index, and the build caches are shared with the peer scopes. Nothing in git separates one agent's half-written file from another's, so the separation has to come from how each agent behaves:

- Edit only the owned paths. A file outside them is someone else's or nobody's; either way it is not yours to touch, even for a one-line fix that would make your own check pass. Raise `DEPENDENCY_REQUEST` and stop.
- Run no git command that writes: no `add`, `commit`, `stash`, `checkout`, `switch`, `restore`, `reset`, `rebase`, `merge`, `clean`, or branch mutation. `git commit -a` or `git stash` would carry a peer's unfinished work with it, and `git checkout -- .` would erase it. Read-only git — `status`, `diff`, `log`, `show`, `blame` — is fine, with `--no-optional-locks` (`git --no-optional-locks status`): a plain `git status` writes the index as a side effect, and that lock can make a peer's concurrent git command fail. The coordinator commits for everyone at a quiesce point.
- Run no repository-wide formatter, linter `--fix`, code generator, dependency install, or lockfile update. Those write outside the owned paths by construction. Scope a formatter to owned files; a repository-wide pass is a sequential slice the coordinator staffs after the scopes quiesce.
- Treat your own check results as provisional. A test run may have executed against a peer's half-written file, so a failure may not be yours and a pass may not hold; iterate on it, but report it as advisory. Prefer the scoped commands the charter names. When a check cannot pass until a peer's pinned contract lands, report it as blocked on that contract instead of iterating against it. The coordinator runs the acceptance checks on the committed head and that run is the evidence.
- Build against a pinned contract that does not exist yet exactly as pinned: mock it in your own tests, and do not create a stub or placeholder at the producer's path — that path belongs to the peer, and a stub there is two writers on one file.
- Keep your own list of every file you create, modify, or delete. The report asks for it separately from git output, because git cannot tell your edit from a peer's edit to the same path.
- Leave no process running when you report. A watcher or dev server still writing to the tree after you stop is a writer the coordinator cannot account for.

## Escalation

Raise one bounded protocol message to the coordinator instead of deciding outside the boundary. Do not manufacture dissent, speculative blockers, or routine progress reports.

```text
SCOPE_REOPEN | DEPENDENCY_REQUEST | BLOCKED | COUNCIL_REQUEST
Reason: <what the evidence shows>
Evidence: <file/line, command output, or runtime observation>
Boundary: <what would be crossed without a decision>
Decision needed: <coordinator or Human decision>
```

- `SCOPE_REOPEN` — evidence increases blast radius, irreversibility, uncertainty, ownership impact, or proof weakness beyond the recorded lane.
- `DEPENDENCY_REQUEST` — the outcome needs a dependency change, a shared contract change, a path outside the owned paths, another scope's files, or a cross-scope decision. Name the path and why; the coordinator rules on ownership, and a path a peer owns changes hands only after that peer is idle and committed.
- `BLOCKED` — an execution or evidence blocker prevents honest progress: missing base, unusable checkout, failing environment, or a check that cannot prove the claim.
- `COUNCIL_REQUEST` — only after local patch-versus-foundation triage, when the owner-clean route and the local patch remain materially undecided on the evidence at hand.

Send the message and stop before crossing the boundary. Do not silently change shared contracts, external systems, credentials, permissions, or another agent's files.

## Execution

Keep execution foreground and bounded. Implement the smallest complete slice inside the owned paths, run the checks that exercise it, and keep the working-tree state explainable: every change you leave behind is inside your owned paths and you can say why each one is there. Do not commit. When the slice is done, report and stop editing until a new bounded instruction arrives; the coordinator quiesces the tree, commits, and runs the acceptance checks on that head. Do not create another coordinator, worker hierarchy, schedule, recurring watch, or alternate delivery path.

When a local wrapper, fallback, retry loop, cache, adapter, or compatibility path begins to own lifecycle, authority, synchronization, failure, or proof semantics that belong to the foundation, read `structural-misfit-policy.md`. Report the relevant evidence and owner-clean alternative; do not silently expand the workaround.

An implementation agent's `DONE` is evidence for the coordinator's quiesce, not acceptance. The coordinator commits the scope, recomputes the candidate head, and runs the acceptance checks before review.

## Evidence report

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
<the coordinator's next concrete action>
```

Every check appears with its real exit code and the note that it ran on the shared tree. A skipped check includes its reason. `Outside owned paths` is `none` unless something went wrong, in which case naming it is the point. `Edited files` comes from your own actions, not from git: the coordinator compares it with the porcelain for your paths, and a file there you did not claim is how a peer's stray write gets caught. Recompute the report after every edit.

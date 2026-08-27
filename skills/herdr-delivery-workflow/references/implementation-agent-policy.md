# Implementation Agent Policy

Use this policy before sending an editing charter. The implementation agent owns one bounded outcome inside one Herdr worktree.

## Charter

The coordinator's prompt names all of the following:

- exact outcome and acceptance boundary;
- recorded intake `Lane`, `Reason`, `Owners`, `Plan`, and `Validation`;
- governing repository contracts;
- target repository and product line;
- worktree path, branch, base, and merge-base;
- files or modules owned;
- files or modules out of scope;
- repository instructions and verification commands;
- prohibition on unrelated cleanup and scope expansion;
- prohibition on subagents, detached commands, background jobs, push, PR mutation, merge, deploy, and other external effects unless explicitly authorized;
- final evidence-report format and coordinator target.

The agent must verify the worktree, branch, base, and ownership before editing. It makes ordinary local implementation decisions within that boundary and raises a blocker when a dependency, shared contract, ownership overlap, material risk, or missing Human decision appears. It must not lower the recorded intake lane. If evidence reveals greater blast radius, irreversibility, uncertainty, ownership impact, or proof weakness, stop before crossing the boundary and report `SCOPE_REOPEN` with the changed risk and proposed lane.

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
- `DEPENDENCY_REQUEST` — the outcome needs a dependency change, a shared contract change, another owner's files, or a cross-scope decision.
- `BLOCKED` — an execution or evidence blocker prevents honest progress: missing base, unusable worktree, failing environment, or a check that cannot prove the claim.
- `COUNCIL_REQUEST` — only after local patch-versus-foundation triage, when the owner-clean route and the local patch remain materially undecided on the evidence at hand.

Send the message and stop before crossing the boundary. Do not silently change shared contracts, external systems, credentials, permissions, or another agent's files.

## Execution

Keep execution foreground and bounded. Implement the smallest complete slice, run the repository checks that prove the claim, and keep the worktree state explainable. Do not create another coordinator, worker hierarchy, schedule, recurring watch, or alternate delivery path.

When a local wrapper, fallback, retry loop, cache, adapter, or compatibility path begins to own lifecycle, authority, synchronization, failure, or proof semantics that belong to the foundation, read `structural-misfit-policy.md`. Report the relevant evidence and owner-clean alternative; do not silently expand the workaround.

An implementation agent's `DONE` is evidence for review, not acceptance. The coordinator must receive the report and independently recompute the candidate head before review.

## Evidence report

Finish with one report in this shape:

```markdown
# Report — <task title>

## Plan item
<the bounded outcome completed>

## Result
<what changed and what did not change>

## Evidence
- HEAD: <full 40-character SHA>
- Merge-base: <SHA or none>
- Changed files: <verbatim git diff --name-status output>
- Checks:
  | command | exit code |
  |---------|-----------|
  | <command> | 0 |

## Risks
<residual gaps, skipped checks with reasons, and unresolved findings>

## Next action
<the coordinator's next concrete action>
```

Every acceptance check appears with its real exit code. A skipped check includes its reason. Recompute the report after every edit that changes the candidate head.

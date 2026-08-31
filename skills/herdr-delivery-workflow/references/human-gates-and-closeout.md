# Human Gates and Closeout

Use this policy when a decision belongs to the Human or when the run is ready to clean up Herdr resources.

## Human-owned gates

Route a decision immediately when it involves:

- push, PR mutation, merge, deploy, or another external write;
- destructive or irreversible action;
- credentials, permissions, or security-sensitive behavior;
- material scope, architecture, dependency, data, or contract change;
- an approval or question shown by the agent UI.

Preserve the same work and custody. The gate record contains:

- gate ID and step;
- exact finding or question;
- current agent, pane, and workspace;
- branch, exact head, integrated head when one exists, and merge-base when known;
- safe options;
- the decision required from the Human.

Pause the same run while the gate is pending. Do not bypass, answer by inference, duplicate the work, rebase, push, merge, or reinterpret the decision. After the Human responds, resume the same bounded run and revalidate anything affected.

A plain instruction in the Human's current request is itself the Human's decision. When the live request explicitly names a gated action — such as the push or merge to perform — record the gate and append its ledger line as `status=resolved:instruction` instead of pausing, then perform only the action the instruction names, at the head this run reviewed. Only the current request qualifies: a prior request, a config key, or an inferred preference never resolves a gate. Any gate the request does not plainly decide still routes to the Human and pauses the run. If the resumed run produces a new head, that head carries the same requirement as any repair head: fresh evidence and a fresh independent review bound to that exact SHA. A verdict earned before the gate does not transfer to a head created after it.

## Gate ledger

A gate that lives only in the coordinator's run context dies with the pane. Append one line per gate to `~/.herdr/projects/<project-slug>/gates.md`, beside the project config, creating the directory when needed:

```text
<GATE-ID> | <ISO time> | <one-line finding> | <branch>@<exact head> | options A/B/C | status=open|resolved:<choice>
```

The ledger is a record, not a control plane. It carries gate identity and resolution only — never routing state, task queues, or a second source of truth for delivery. It is append-only: resolve a gate by appending a resolution line, never by rewriting or deleting an existing one. The full gate record still goes to the Human in the message; the ledger exists so any open gate is findable with one grep after a restart. Product repositories carry no gate or process state.

## Validation-run custody

When a delivery drives an external validation pipeline, such as a `no-mistakes` run, that run is a singleton owned by the coordinator. Never:

- start a second run for the same head;
- interrupt its active validation agent;
- apply the same finding through an outside edit;
- drive the pipeline from an implementation agent's pane.

Preserve the run ID, exact head, branch, findings, every response, and the terminal outcome beside the verification ledger.

Route pipeline findings by class. Mechanical, low-risk findings the pipeline owns are handled inside the run. A finding that challenges the Human's stated intent, or that touches destructive scope, security, credentials, external effects, or material scope, is a Human gate: route it with the gate record, pause the same run until the Human decides, then resume that same run through its own command.

A quiet monitor is a liveness signal, not terminal evidence. When the forge reports the pull request merged or closed after checks passed, treat it as a lifecycle reconciliation of the same run rather than a new delivery. Write the reconciliation record when the terminal state is observed. The CUSTODY and ESCALATION lines are fixed text — copy them verbatim whatever this run shows, because they state the standing rules, not what happened this run:

```text
RUN: <validation run ID>
PR: <reference> state=<merged | closed> merge-commit=<SHA> merged-at=<ISO time>
HEADS: feature=<exact SHA> pushed=<exact SHA> reviewed=<exact SHA> — feature head recorded distinct from the merge commit
RECONCILE: merged headRefOid=<SHA> vs reviewed head=<SHA>; merge-commit parents=<SHAs>
CUSTODY: the validation run is a coordinator-owned singleton — never a second run for the same head, never interrupting its validation agent, never applying the same finding through an outside edit
ESCALATION: when the merged head and the reviewed head differ, or the reviewed head is not among the merge commit's parents, route SCOPE_REOPEN and say plainly that work was merged this run never reviewed; a matching head reference alone is not proof the merge carried the reviewed work — a squash or force-push can leave the reference matching while the merged content is something no reviewer saw
```

Do not abort, rerun, duplicate, rebase, delete the branch, or rewrite the head to repair a stuck lifecycle; report the evidence gap instead.

## Acceptance and cleanup

Before final acceptance, preserve the implementation report, exact reviewed head, reviewer verdict, integrated head when integration happened, changed files, check results on both the reviewed and the integrated head, skipped-check reasons, a causal classification of every failure, residual risks, and next action. Acceptance requires claim-shaped checks plus `PASS` for the same exact head. A later green result does not replace an unreconciled earlier failure.

Close only panes, tabs, workspaces, and agents created by this run. The checkout itself is the caller's and is never removed — and never moved: no checkout of another branch, no reset, no rebase, no clean as part of closeout. Leave it on the branch and head the record names; wrapping up changes Herdr resources, not the tree. Cleanup is safe only when:

- no process is running in any pane this run created;
- no unexplained tracked change remains — every implementation agent's work is committed or its remaining diff is explained;
- required reports and artifacts are preserved;
- no pending Human gate or dependent work remains.

Leave user-owned or pre-existing resources untouched. If a created resource remains open, state the concrete reason.

## Per-issue agent teardown

Each delivery is one issue, and it created its own agents — one implementation agent per scope in the partition and a reviewer, recorded in the run context by name, kind, pane, and owned paths. When that issue is accepted or otherwise closed, tear down the agents this run staffed for it before the flight slot moves to the next issue, so agents do not accumulate across sequential deliveries. Tie the teardown to the same closeout that closes the issue's other resources, under the same safe-cleanup preconditions above; do not defer it into a separate pass.

An agent is torn down by closing the pane this run created to host it: the agent name clears when the agent exits or its pane closes (`references/herdr-cli.md` owns the exact mechanic). Preserve the agent's final evidence report before closing its pane, since the transcript dies with the pane. Never close the caller's own pane or the agent occupying it, never close a pane an agent shares with unrelated work this run did not create, and do not use `pane release-agent` as a teardown — it is a detection-plane report, not a shutdown. If an agent is still working, blocked on a Human gate, or holds dependent work another open issue needs, leave it open and state the concrete reason rather than forcing it down.

## Final handoff

```text
STATUS: accepted | blocked | needs-human-gate | needs-rework
OUTCOME: <one sentence>
HEAD: <exact reviewed SHA or none>
INTEGRATED: <exact integrated SHA or none>
REVIEW: <PASS/FAIL/BLOCKED, exact head, reviewer agent kind>
CHECKS: <command=exit code list on the reviewed head>
INTEGRATED CHECKS: <command=exit code list on the integrated head, or none>
CHANGED: <verbatim or concise changed-file list, grouped by scope when the partition had more than one>
CHECKOUT: <branch>@<exact head> — the caller's checkout stays on the branch and head the record names; closeout never checks out, resets, rebases, or cleans it
RISKS: <residual risks and skipped checks>
NEXT: <one concrete next action>
```

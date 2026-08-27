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
- current agent, pane, workspace, and worktree;
- branch, exact head, integrated head when one exists, and merge-base when known;
- safe options;
- the decision required from the Human.

Pause the same run while the gate is pending. Do not bypass, answer by inference, duplicate the work, rebase, push, merge, or reinterpret the decision. After the Human responds, resume the same bounded run and revalidate anything affected. If the resumed run produces a new head, that head carries the same requirement as any repair head: fresh evidence and a fresh independent review bound to that exact SHA. A verdict earned before the gate does not transfer to a head created after it.

## Gate ledger

A gate that lives only in the coordinator's run context dies with the pane. Append one line per gate to `~/.herdr/gates/<project-slug>.md`, creating the directory when needed:

```text
<GATE-ID> | <ISO time> | <one-line finding> | <branch>@<exact head> | options A/B/C | status=open|resolved:<choice>
```

The ledger is a record, not a control plane. It carries gate identity and resolution only — never routing state, task queues, or a second source of truth for delivery. It is append-only: resolve a gate by appending a resolution line, never by rewriting or deleting an existing one. The full gate record still goes to the Human in the message; the ledger exists so any open gate is findable with one grep after a restart. Product repositories carry no gate or process state.

## Validation-run custody

When a delivery drives an external validation pipeline, such as a `no-mistakes` run, that run is a singleton owned by the coordinator. Do not start a second run for the same head, interrupt its active validation agent, apply the same finding through an outside edit, or drive the pipeline from an implementation agent's pane. Preserve the run ID, exact head, branch, findings, every response, and the terminal outcome beside the verification ledger.

Route pipeline findings by class. Mechanical, low-risk findings the pipeline owns are handled inside the run. A finding that challenges the Human's stated intent, or that touches destructive scope, security, credentials, external effects, or material scope, is a Human gate: route it with the gate record, pause the same run until the Human decides, then resume that same run through its own command.

A quiet monitor is a liveness signal, not terminal evidence. When the forge reports the pull request merged or closed after checks passed, treat it as a lifecycle reconciliation of the same run rather than a new delivery: preserve the pull-request reference, terminal state, merge commit and merge time when merged, run ID, feature head, and pushed head, and keep the feature head distinct from the merge commit. Do not abort, rerun, duplicate, rebase, delete the branch, or rewrite the head to repair a stuck lifecycle; report the evidence gap instead.

Reconcile the merged head against the head this run actually reviewed, and check the merge commit's parents, not only the pull request's head reference. A squash or a force-push can leave the head reference matching while the merged content is something no reviewer saw, so a matching reference alone does not prove the merge carried the reviewed work. When the reviewed head is not among the merge commit's parents, or the head reference has moved, route `SCOPE_REOPEN` and say plainly that work was merged this run never reviewed.

## Acceptance and cleanup

Before final acceptance, preserve the implementation report, exact reviewed head, reviewer verdict, integrated head when integration happened, changed files, check results on both the reviewed and the integrated head, skipped-check reasons, a causal classification of every failure, residual risks, and next action. Acceptance requires claim-shaped checks plus `PASS` for the same exact head. A later green result does not replace an unreconciled earlier failure.

Close only panes, tabs, workspaces, and worktrees created by this run. Cleanup is safe only when:

- no process is running;
- no unexplained tracked change remains;
- required reports and artifacts are preserved;
- no pending Human gate or dependent work remains.

Leave user-owned or pre-existing resources untouched. If a created resource remains open, state the concrete reason.

## Final handoff

```text
STATUS: accepted | blocked | needs-human-gate | needs-rework
OUTCOME: <one sentence>
HEAD: <exact reviewed SHA or none>
INTEGRATED: <exact integrated SHA or none>
REVIEW: <PASS/FAIL/BLOCKED, exact head, reviewer agent kind>
CHECKS: <command=exit code list on the reviewed head>
INTEGRATED CHECKS: <command=exit code list on the integrated head, or none>
CHANGED: <verbatim or concise changed-file list>
RISKS: <residual risks and skipped checks>
NEXT: <one concrete next action>
```

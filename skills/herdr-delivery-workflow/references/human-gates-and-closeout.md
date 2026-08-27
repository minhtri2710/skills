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
- branch, exact head, and merge-base when known;
- safe options;
- the decision required from the Human.

Pause the same run while the gate is pending. Do not bypass, answer by inference, duplicate the work, rebase, push, merge, or reinterpret the decision. After the Human responds, resume the same bounded run and revalidate anything affected.

## Acceptance and cleanup

Before final acceptance, preserve the implementation report, exact reviewed head, reviewer verdict, changed files, all check results, skipped-check reasons, residual risks, and next action. Acceptance requires claim-shaped checks plus `PASS` for the same exact head.

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
HEAD: <exact SHA or none>
REVIEW: <PASS/FAIL/BLOCKED, exact head>
CHECKS: <command=exit code list>
CHANGED: <verbatim or concise changed-file list>
RISKS: <residual risks and skipped checks>
NEXT: <one concrete next action>
```

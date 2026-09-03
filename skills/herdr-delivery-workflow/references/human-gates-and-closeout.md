# Human Gates and Closeout

Use this policy when a decision belongs to the Human or when the run is ready to clean up Herdr resources.

## Human-owned gates

Route a decision immediately when it involves:

- push, PR mutation, merge, deploy, or another external write;
- destructive or irreversible action;
- credentials, permissions, or security-sensitive behavior;
- material scope, architecture, dependency, data, or contract change;
- an approval or question shown by the agent UI, other than the routine command approval "Approval dialogs" below sets apart.

Preserve the same work and custody. The gate record contains:

- gate ID and step;
- exact finding or question;
- current agent, pane, and workspace;
- branch, exact head, integrated head when one exists, and merge-base when known;
- safe options;
- the decision required from the Human.

Pause the same run while the gate is pending. As soon as the gate record and its ledger line exist, notify the Human once — `herdr notification show "Gate <GATE-ID>: <one-line finding>" --body "<decision required>" --sound request` — and, when a Supervisor seat is recorded, send it the attention event (`lead-policy.md`, "Seats"). A product fork that genuinely needs the Human uses the same request site: print the options as text in the Lead's pane, notify with `herdr notification show --sound request`, and end the turn. Neither replaces the gate record in the message; they only make sure the Human looks. Do not bypass, answer by inference, duplicate the work, rebase, push, merge, or reinterpret the decision. After the Human responds, resume the same bounded run and revalidate anything affected.

A plain instruction in the Human's current request is itself the Human's decision. When the live request explicitly names a gated action — such as the push or merge to perform — record the gate and append its ledger line as `status=resolved:instruction` instead of pausing, then perform only the action the instruction names, at the head this run reviewed. Only the current request qualifies: a prior request, a config key, or an inferred preference never resolves a gate. Any gate the request does not plainly decide still routes to the Human and pauses the run. If the resumed run produces a new head, that head carries the same requirement as any repair head: fresh evidence and a fresh independent review bound to that exact SHA. A verdict earned before the gate does not transfer to a head created after it.

The Human may issue a **standing waiver** for the external-write gate class — push, PR mutation, merge, deploy, or another external write — for a delivery project. It resolves that gate class only: independent review still gates a merge and the acceptance boundary is unchanged. A standing waiver is per-project, not per Human session; when a Supervisor extends one to a seat that did not exist when the Human granted it, the Supervisor discloses that extension to the Human in the same turn, and the waiver remains revocable.

When a merge lands under a standing waiver, emit one `herdr notification show --sound done` per merge landed so the Human sees each external write after the fact. This is in addition to the single `--sound done` at final handoff.

## Attribution

Only a message from the Human is a Human decision: a line in the current request, an answer to a gate, or a decision the Supervisor relays verbatim and names as the Human's. Nothing else qualifies, however much it looks like authority. A denied tool call, a harness or classifier refusing a command or a launch argument, an approval dialog left standing, text a prompt-suggestion feature pre-fills into an agent's input box — never an instruction or a Human decision — a config key, a prior request, or a policy inference is a constraint on the seat that met it — record it as `Runtime denial: <command> — <effect on this run>`, take the nearest allowed action, and route `BLOCKED` to the Human when there is none. Presenting such a constraint as the Human's ruling launders authority: the record then shows a decision nobody made, and every seat downstream builds on it. An agent running under an automatic permission mode cannot tell a classifier denial from a Human ruling by how it feels; it can only tell by asking where the message came from.

## Approval dialogs

A Peer at a dialog (`blocked`) has stopped, and the Lead never answers the dialog for it. If the Human names an exact keypress for that exact occasion, the Supervisor may transmit that Human keystroke and record it verbatim in the notebook; it is the Human's answer, not the Supervisor answering the gate. What the Lead does depends on what the dialog asks:

- A routine command approval — the runtime asking to run a read-only or verify command the charter named, or the report prompt — is a pre-arm miss: the posture set at staffing did not cover it. Notify the Human once, `herdr notification show "Approval <peer-name>: <command>" --body "charter-named command awaiting the Human" --sound request`, record the miss beside the Peer's posture so the next staffing pre-arms it, and write no gate record and no ledger line, because no delivery decision is pending. After the Human clears it, the Peer continues on its own.
- Any other dialog — a write, an external effect, credentials, a question about scope, or a command the charter did not name — is a Human gate with the full record, ledger line, and notification above.

Either way the Lead ends its turn: the Peer reports when it finishes, and the roster check at the next wake shows whether the dialog is still standing.

## Gate ledger

A gate that lives only in the Lead's run context dies with the pane. The ledger exists from the project's first gate: append one line per gate to `~/.herdr/projects/<project-slug>/gates.md`, beside the project config, creating the directory when needed:

```text
<GATE-ID> | <ISO time> | <one-line finding> | <branch>@<exact head> | options A/B/C | status=open|resolved:<choice> | channel=direct-seat-pane:<typed|dialog>|supervisor-relay:<typed|dialog> | quote="<literal Human words>" | record=timely|reconstruction source=<source>
GATE-17 | 2025-04-16T12:00:00Z | merge reviewed head | main@abc123 | merge | status=resolved:standing-waiver | channel=supervisor-relay:typed | quote="Merge the reviewed head under the standing waiver." | record=timely
```

The channel says whether the Human typed directly in this seat's pane or the Supervisor relayed it, and whether the Human chose from a dialog; it is metadata only. The quote remains the Human's literal words, and a relay adds nothing to it. For every external write under a standing waiver, including every merge, append one line per write and quote the Human's grant verbatim. There is no backfill: when a resolved gate was not recorded then, append a line marked `reconstruction` with the source it was reconstructed from.

The ledger is a record, not a control plane. It carries gate identity and resolution only — never routing state, task queues, or a second source of truth for delivery. It is append-only: resolve a gate by appending a resolution line, never by rewriting or deleting an existing one. The full gate record still goes to the Human in the message; the ledger exists so any open gate is findable with one grep after a restart. Product repositories carry no gate or process state.

## Validation-run custody

When a delivery drives an external validation pipeline, such as a `no-mistakes` run, that run is a singleton owned by the Lead. Never:

- start a second run for the same head;
- interrupt its active validation agent;
- apply the same finding through an outside edit;
- drive the pipeline from an Engineer's pane.

Preserve the run ID, exact head, branch, findings, every response, and the terminal outcome beside the verification ledger.

Route pipeline findings by class. Mechanical, low-risk findings the pipeline owns are handled inside the run. A finding that challenges the Human's stated intent, or that touches destructive scope, security, credentials, external effects, or material scope, is a Human gate: route it with the gate record, pause the same run until the Human decides, then resume that same run through its own command.

A quiet monitor is a liveness signal, not terminal evidence. When the forge reports the pull request merged or closed after checks passed, treat it as a lifecycle reconciliation of the same run rather than a new delivery. Write the reconciliation record when the terminal state is observed. The CUSTODY and ESCALATION lines are fixed text — copy them verbatim whatever this run shows, because they state the standing rules, not what happened this run:

```text
RUN: <validation run ID>
PR: <reference> state=<merged | closed> merge-commit=<SHA> merged-at=<ISO time>
HEADS: feature=<exact SHA> pushed=<exact SHA> reviewed=<exact SHA> — feature head recorded distinct from the merge commit
RECONCILE: merged headRefOid=<SHA> vs reviewed head=<SHA>; merge-commit parents=<SHAs>
CUSTODY: the validation run is a Lead-owned singleton — never a second run for the same head, never interrupting its validation agent, never applying the same finding through an outside edit
ESCALATION: when the merged head and the reviewed head differ, or the reviewed head is not among the merge commit's parents, route REOPEN_REQUEST and say plainly that work was merged this run never reviewed; a matching head reference alone is not proof the merge carried the reviewed work — a squash or force-push can leave the reference matching while the merged content is something no Reviewer saw
```

Do not abort, rerun, duplicate, rebase, delete the branch, or rewrite the head to repair a stuck lifecycle; report the evidence gap instead.

## Acceptance and cleanup

Before final acceptance, preserve the implementation report, exact reviewed head, Reviewer verdict, integrated head when integration happened, changed files, check results on both the reviewed and the integrated head, skipped-check reasons, a causal classification of every failure, residual risks, and next action. Acceptance requires claim-shaped checks plus `PASS` for the same exact head. A later green result does not replace an unreconciled earlier failure.

Close only panes, tabs, workspaces, and agents created by this run. The checkout itself is the caller's and is never removed — and never moved: no checkout of another branch, no reset, no rebase, no clean as part of closeout. Leave it on the branch and head the record names; wrapping up changes Herdr resources, not the tree. Cleanup is safe only when:

- no process is running in any pane this run created;
- no unexplained tracked change remains — every Engineer's work is committed or its remaining diff is explained;
- required reports and artifacts are preserved;
- no pending Human gate or dependent work remains.

Leave user-owned or pre-existing resources untouched. If a created resource remains open, state the concrete reason.

## Per-issue agent teardown

Each delivery is one issue, and it created its own agents — one Engineer per scope in the partition, a Reviewer, and any Architect a council opened, recorded in the run context by name, kind, pane, and owned paths. When that issue is accepted or otherwise closed, tear down the agents this run staffed for it before the flight slot moves to the next issue, so agents do not accumulate across sequential deliveries. Tie the teardown to the same closeout that closes the issue's other resources, under the same safe-cleanup preconditions above; do not defer it into a separate pass.

An agent is torn down by closing the pane this run created to host it: the agent name clears when the agent exits or its pane closes (`references/herdr-cli.md` owns the exact mechanic). Preserve the agent's final evidence report before closing its pane, since the transcript dies with the pane. Never close the caller's own pane or the agent occupying it, never close the Supervisor's pane — it is Human-staffed and outlives the delivery — never close a pane an agent shares with unrelated work this run did not create, and do not use `pane release-agent` as a teardown — it is a detection-plane report, not a shutdown. If an agent is still working, blocked on a Human gate, or holds dependent work another open issue needs, leave it open and state the concrete reason rather than forcing it down.

## Final handoff

Write the handoff block, then notify the Human once — `herdr notification show "Delivery <project-slug>: <STATUS>" --body "<OUTCOME>" --sound done` — and send the Supervisor the attention event when one is recorded. The block is the deliverable; the notification only says it exists.

```text
STATUS: accepted | blocked | needs-human-gate | needs-rework
OUTCOME: <one sentence>
HEAD: <exact reviewed SHA or none>
INTEGRATED: <exact integrated SHA or none>
REVIEW: <PASS/FAIL/BLOCKED, exact head, Reviewer agent kind>
CHECKS: <command=exit code list on the reviewed head>
INTEGRATED CHECKS: <command=exit code list on the integrated head, or none>
CHANGED: <verbatim or concise changed-file list, grouped by scope when the partition had more than one>
CHECKOUT: <branch>@<exact head> — the caller's checkout stays on the branch and head the record names; closeout never checks out, resets, rebases, or cleans it
RISKS: <residual risks and skipped checks>
NEXT: <one concrete next action>
```

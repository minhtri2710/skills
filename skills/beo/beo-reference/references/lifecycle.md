# Lifecycle, Decomposition, and Triage Authority

> [!NOTE]
> This reference is subordinate to [references/kernel.md](file:///Users/beowulf/Work/personal/beo-skills/skills/beo/beo-reference/references/kernel.md). `references/kernel.md` is the canonical owner of BEO rules and invariants.

`br` and `bv` are the external Beads tools used for issue tracking and orientation.

## 1. Issue Triage and Claim Authority

All issue transitions are governed by strict claim invariants to avoid parallel conflict and preserve audit trails.

### Startup and Claim Sequence
1. **Orient**: If no issue is selected, use `bv` robot triage for graph orientation only.
2. **Discover**: Use `br ready --json` for the canonical executable queue. Use `bv` only to choose between tracks or detect graph hazards.
3. **Inspect**: Check canonical issue details with `br`.
4. **Classify atomicity**: If the issue type is `epic` or `feature`, stop direct validation/execution and route to `beo-plan` decomposition. If the issue was confirmed misclassified but is actually atomic, correct the type with `br update <issue-id> --type task` before continuing; do not convert parent work to `task` just to bypass decomposition.
5. **Claim or verify claim**: Before the first plan-owned write, `beo-plan` claims the issue with `br update <issue-id> --claim --actor <actor> --json`. Later phase owners verify that the existing claim matches the acting owner and fail closed on mismatch. `--claim` takes no value.
6. **Bind helper identity**: Run BEO helper checks with `BR_ACTOR` or `BEO_ACTOR` set to the claimed assignee. Helper claim checks compare that environment actor to the Beads claim.
7. **Flush claim state**: After a successful claim that must be visible to later checks or other agents, run `br sync --flush-only`.

### Claim Authority and Phase Boundaries
- **Plan claim**: `beo-plan` establishes initial claim before decomposition, `TICKET.yaml` write, or planning comments.
- **Later phase verification**: `beo-validate`, `beo-execute`, `beo-review` verify the existing claim matches the acting owner; they do not re-claim.
- **Resume protocol**: Only `beo-plan`, after explicit user-driven resume or issue reassignment, may re-claim after the initial plan claim.
- **Parent claim for decomposition**: Parent claim holds only while `beo-plan` creates child beads and dependency edges.

### Common Lifecycle Failure Triage

| Symptom | Cause | Resolution |
| --- | --- | --- |
| `issue is not atomic; route to beo-plan decomposition` or `issue must be decomposed before validation` | Issue type is `epic` or `feature` | Route to `beo-plan` decomposition; use `br update <issue-id> --type task` only when the issue is confirmed misclassified |
| `br issue claim does not match acting actor` or `BR_ACTOR or BEO_ACTOR is required` | Missing or mismatched actor identity | `export BR_ACTOR=<actor>`, then `br update <issue-id> --claim --actor <actor> --json` and `br sync --flush-only` |
| `error: unexpected argument '--message' found` | `br close` uses Beads-specific syntax, not git commit syntax | Use `br close <issue-id>` or `br close <issue-id> --reason "Completed" --actor <actor> --json`; never use `--message` |

---

## 2. Parent Handling and Decomposition

Only atomic beads can be validated or executed. Epics and Features must be decomposed.

### Decomposition Invariants
- **Epic**: User-facing milestone; never executed directly.
- **Feature**: Capability group; must be decomposed.
- **Atomic Bead**: One independently approvable execution unit. Must have concrete `done_criteria`, one mode, one approval projection, a small explicit allowed file set, one verification contract, one verdict, and an independent revert/repair path.

### Parent-Child Mechanics
If a bead is not atomic:
1. `beo-plan` creates child atomic beads using `br create ... --json`.
2. Add dependency edges using `br dep add ... --json`.
3. Add a summary comment to the parent bead using `br comments add ... --json`.
4. Exit planning with `decomposition_recorded` and hand off to the user.

---

## 3. Runtime Events

Runtime event kinds and payload contracts are canonical in `registry/runtime-event.schema.json`.

Runtime events are append-only non-normal state entries in `.beads/artifacts/<issue-id>/runtime-events.jsonl`. They are not written for normal transitions, and they are not plan-owned `TICKET.yaml` fields.

---

## 4. Repair Loop Policy

Repair boundary is canonical in `references/phase-contracts.md`.

- `beo-review` emits exactly one route. Final verdict routes are accept, repair same scope, repair rescope, cannot deliver, or abandoned; `root_cause_diagnosis_needed` is a non-final diagnostic handoff route.
- Repair counters are recorded in `state.json` for review visibility only.
- Non-deliverable or abandoned issues route strictly to the user for manual decision; BEO never auto-closes or auto-abandons them on `br`.

---

## 5. Phase Handoff Boundaries

BEO uses explicit artifact-validity phase handoffs.

1. A phase owner may transition only after durable state/evidence is written.
2. The next owner may start only after re-reading `br`, `TICKET.yaml`, `state.json`, `runtime-events.jsonl` when present, and the phase-relevant registries named by the owner skill.
3. The boundary is artifact validity, not conversation turn.
4. No phase may run commands, mutations, verification, approval, or review work belonging to the next phase until those artifacts have been re-read.

---

## 6. Transition & Closure Labels

Labels on `br` are advisory indicators that reflect the active BEO state:
- `beo:atomic`, `beo:quick`, `beo:standard`, `beo:strict`, `beo:blocked-user`, `beo:ready-review`.
- **Abandoned vs Completed Closure**: Only `verdict_accept` routes to automatic `br close` with a resolution status of `completed` and a `beo:completed` label. When BEO delivery is `abandoned`, `beo-review` records the status in `state.json`, appends a BEO audit comment via `br comments add ... --json`, applies the `beo:abandoned` label, and stops, leaving the issue `open` in `br` for manual user closure.

### Closure Command Syntax

Use Beads-specific close options, not git-style commit flags:

```bash
br close <issue-id>
br close <issue-id> --reason "Completed" --actor <actor> --json
```

`br close` does not accept `--message`; use `--reason` for the close reason.

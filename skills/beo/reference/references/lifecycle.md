# Lifecycle, Decomposition, and Triage Authority

Use one authority per decision; never mirror another authority's state in prose or ticket fields:
- [beads_rust](https://github.com/Dicklesworthstone/beads_rust) (`br`) owns transactional issue state: identity, status, claims, comments, dependency edges, ready queue, sync/export, and closure.
- [beads_viewer](https://github.com/Dicklesworthstone/beads_viewer) (`bv` robot mode) owns graph orientation only: triage ranking, independent tracks, bottlenecks, critical path, and cycle visibility.
- `TICKET.md` owns BEO control-plane identity, intake, and safety scope. `state.json` owns current approval, execution, and review state; `runtime-events.jsonl` owns append-only non-normal events. Together, the files under `.beads/artifacts/<issue-id>/` are the BEO safety/evidence truth.

Use IDs and evidence refs to connect authorities. Do not copy `br` lifecycle data into `TICKET.md`, do not persist `bv` rankings, and never run bare `bv` in agent workflows because it opens the TUI.

## 1. Issue Triage and Claim Authority

All issue transitions are governed by strict claim invariants to avoid parallel conflict and preserve audit trails.

### Startup and Claim Sequence
1. **Orient**: If no issue is selected, use `bv` robot triage for graph orientation only.
2. **Discover**: Use the `br.ready` command contract for the canonical executable queue; do not invent unsupported flags such as `br list --ready`. Use `bv` only to choose between tracks or detect graph hazards.
3. **Inspect**: Check canonical issue details with `br`.
4. **Claim**: Before any owned write, ticket mutation, decomposition, product mutation, verdict, or closure, claim the issue with the `br.update.claim` command contract: `br update --actor <actor> <issue-id> --claim --json`. `--claim` takes no value. If setup cannot prove atomic claim support, BEO fails closed.
5. **Bind helper identity**: Run BEO helper checks with `BR_ACTOR` or `BEO_ACTOR` set to the claimed assignee. Helper claim checks compare that environment actor to the Beads claim.

### Claim Authority and Phase Boundaries
- **Plan claim**: `beo-plan` establishes initial claim before decomposition, TICKET.md write, or planning comments.
- **Later phase verification**: `beo-validate`, `beo-execute`, `beo-review` verify the existing claim matches the acting owner; they do not re-claim.
- **Resume protocol**: Only explicit user-driven resume or issue reassignment may re-claim after initial plan claim.
- **Parent claim for decomposition**: Parent claim holds only while `beo-plan` creates child beads and dependency edges; child execution requires separate child claim.

### Compact Protocol
Low-risk repository-only work may use compact plan authoring, but it still follows the same gated delivery path: show/claim, plan `TICKET.md`, validate `PASS_EXECUTE`, execute approved scope, review, then close only after review acceptance. `profiles.json` owns quick/standard/strict definitions.

---

## 2. Track Planning and Robot Triage

Use `bv` when the question is structural rather than transactional: triage ranking, independent tracks, bottlenecks, critical path, or cycle visibility. Use only contracted robot commands from `command-contracts.json`; after `bv` identifies work shape, persist issue/dependency changes with `br`.

### Sync Boundary
`br sync --flush-only` is the only BEO-authorized Beads export operation. It writes JSONL for handoff, not git commits or pushes; VCS operations remain outside BEO authority unless a human separately requests them.

> [!IMPORTANT]
> If `bv --robot-insights` detects any cycle (when `.Cycles` is not empty or `has_cycles` is true), the plan must prioritize cycle-break operations only if the cycle intersects the selected issue's dependency path. Cycles in unrelated graph regions do not block execution.

---

## 3. Parent Handling and Decomposition

Only atomic beads can be validated or executed. Epics and Features must be decomposed.

### Decomposition Invariants
- **Epic**: User-facing milestone; never executed directly.
- **Feature**: Capability group; must be decomposed.
- **Atomic Bead**: One independently approvable execution unit. Must have one done target, one risk posture, one approval projection, a small explicit allowed file set, one verification contract, one verdict, and an independent revert/repair path.

### Parent-Child Mechanics
If a bead is not atomic:
1. `beo-plan` creates child atomic beads using the contracted `br.create` command.
2. Add dependency edges using the contracted `br.dep.add` command.
3. Add a summary comment to the parent bead using the contracted `br.comments.add` command.
4. Exit planning with `decomposition_recorded`.
5. Parent epics remain open until Beads reports all children are closed.

---

## 4. Runtime Events

Runtime events are append-only non-normal state entries in `.beads/artifacts/<issue-id>/runtime-events.jsonl`. They are not written for normal transitions, and they are not plan-owned `TICKET.md` fields; helpers may expose them only as an artifact-view bundle for validation.

### Types & Kinds
- `user_stop`: Emitted when a Human Gate blocks progress. Mark gate status `unresolved`, comment on the issue, and apply the `beo:blocked-user` label.
- `handoff` / `return`: Used for the `debug` subroutine handoff to `beo-debug`.
- `change_request`: Subtypes include `scope_delta`, `repair_same_scope`, and `repair_rescope`.
- `abandon`: Used when the work is cancelled or aborted.
- `learning_candidate`: Emitted post-accept by `beo-review` or `beo-debug` to trigger the learning loop.

---

## 5. Repair Loop Policy

Review repair routes have bounded repetition to prevent infinite loops. We enforce repair budgets defined in `profiles.json repair_budget_policy` and transitions from `pipeline.json repair_loop_policy`. 

Same-scope repair delta boundaries to preserve are defined in `pipeline.json repair_loop_policy.same_scope_repair_delta`.

### Terminal Routes
- **repair_budget_exceeded**: Routes to user when mode repair budget is exhausted. User decides explicit continuation, `cannot_deliver`, or issue reassignment.
- **cannot_deliver**: Terminal delivery blocker requiring registered reason from `ticket-schema.json` `cannot_deliver_reasons` taxonomy (`user_owned`, `unsafe_environment`, `unavailable_dependency`, `scope_invalid`, `tool_missing`). It routes to user with the registered reason; it never silently fails or auto-abandons without user visibility.

---

## 6. Transition Labels

Labels are advisory hints and never replace formal ticket fields:
- `beo:atomic`, `beo:quick`, `beo:standard`, `beo:strict`, `beo:blocked-user`, `beo:ready-review`.

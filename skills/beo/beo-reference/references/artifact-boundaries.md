# Artifact Boundaries

> [!NOTE]
> This reference is subordinate to `references/kernel.md`. `references/kernel.md` is the canonical owner of BEO rules and invariants.

This file owns BEO artifact placement rules. Other files should cite this file instead of restating these boundaries.

## Canonical ownership

| Artifact | Owns | Must not own |
|---|---|---|
| `br` | issue lifecycle, status, claims, dependencies, comments, ready queue, closure | BEO approval/execution/review internals |
| `bv` | read-only graph orientation | persisted lifecycle state, approval, verdict |
| `PLAN.md` | parent epic/feature requirement intake, clarification record, recommended assumptions, goals, non-goals, overall completion criteria, constraints, risks, verification strategy, decomposition strategy, proposed atomic child beads with suggested mode/risk, dependency graph, and unresolved user/operator decisions that block `plan_validated` until resolved | approval state, execution state, review verdict, product implementation, atomic ticket scope authority |
| `TICKET.json` | request, done criteria, approved scope, verification commands, risk/strict contracts | br lifecycle, approval state, execution state, review verdict, runtime event log, learning notes |
| `state.json` | approval, execution, review state | request/scope definition, br lifecycle, memory notes |
| `runtime-events.jsonl` | append-only non-normal events | normal successful transitions |
| `harness-proposal.json` | delivery-to-author harness change proposal | approval state, execution state, review verdict, delivery scope |
| qmd/Obsidian notes | advisory reusable lessons | approval, execution permission, verdict, closure, Human Gate authorization |
| `AGENTS.md` managed block | compact repo-level reminder | detailed BEO doctrine |

## Do not put

- Beads lifecycle/status in `TICKET.json`.
- `bv` triage ranking in `TICKET.json` or `state.json`.
- epic brainstorm notes or proposed child-bead backlog in `TICKET.json`; put them in `.beads/artifacts/<issue-id>/PLAN.md`.
- atomic approval fields in `PLAN.md`; parent plans guide decomposition but never grant `PASS_EXECUTE`.
- parent epic/feature brainstorming in child `TICKET.json`. Child Bead descriptions must carry self-contained atomic implementation context; parent traceability belongs in Beads dependency edges and decomposition comments, not required child-body context. Do not add a new parent/plan field to `TICKET.json` because `registry/ticket.schema.json` is closed with `additionalProperties: false`.
- normal transitions in `runtime-events.jsonl`.
- approval state or review verdict in `TICKET.json`.
- learning notes in `beo-reference`.
- secrets, credentials, or customer-sensitive raw data in memory notes.
- product delivery decisions in `beo-setup`, `beo-reference`, or `beo-author`.
- delivery scope decisions in `harness-proposal.json`; proposals affect the harness, not the product.

## Harness scope boundary

BEO is a **process / control-plane harness**: it regulates *how* delivery flows (claim, scope containment, approval, verification, review, closure). It is deliberately not a maintainability, architecture-fitness, or behaviour harness for product code — those sensors live in the product repository and BEO invokes them only through declared, opt-in ticket contracts.

| Harness axis | Owner | Invoked via |
|---|---|---|
| Process / control-plane | BEO (`skills/beo/`) | claim, scope containment, `PASS_EXECUTE`, review rubric, closure |
| Maintainability | Product repo | linters, formatters, complexity/dead-code checks wired into `scope.verify.commands` |
| Architecture fitness | Product repo | structural boundary tests, perf tests, observability checks wired into `scope.verify.commands` or `scope.structural_check` |
| Behaviour | Product repo (+ opt-in `scope.behaviour_gate`) | test suites, mutation testing, approved fixtures |

BEO runs a declared product-repo sensor and records its result; it never owns or replaces the sensor. Teams should not expect BEO to carry sensing it is not designed for — wire product-repo harnesses into the declared verify/gate commands instead.

## Intervention records

`intervention` is a non-normal runtime event kind recording an external input (human, reviewer, CI, or another agent) that affects the current delivery. It is **evidence, not lifecycle state**. Interventions:

- May be appended to `runtime-events.jsonl` during any phase when an external input is observed.
- Are mirrored into `state.json.execution.interventions[]` if the operator wants them to survive past the runtime event log.
- Must not change `state.json.phase` or any approval field. They are records of context, not authority grants.
- Are queried by `beo-execute` (and other delivery skills) by `trace_id` or `story_id` to surface prior context when re-entering an issue.

If a recorded intervention has `impact: blocking`, the executing skill should treat it as a Human Gate and route accordingly (e.g. `user_review_needed`). It does not, by itself, invalidate a current `PASS_EXECUTE`.

### Validation asymmetry

`beo_state.validate_state` currently does not enforce the "must not change phase or approval fields" rule
on intervention entries. Cross-event lookups (e.g. `beo-execute` querying by `trace_id`) use literal
equality on `payload.trace_id` (or `story_id`), not a real index. This means:
- An intervention with `recorded_at` before the current `phase` started is not rejected.
- An intervention touching approval fields is not rejected (caller discipline only).
- `trace_id`-based lookups are O(n) scans, not indexed.
These are known limitations; callers must exercise discipline when recording or querying interventions.

# PLAN for <parent-issue-id>

## Parent bead

- Parent issue id: `<issue-id>`
- Parent type: `epic | feature`
- Source request: `<short user/request summary>`
- Planning actor: `<actor>`

## Decision summary

State the selected implementation/decomposition direction from the brainstorm in 3-7 bullets. This summary must align with the recommended option or selected hybrid from `Brainstorm and options considered`.

## Clarification record

List clarification questions asked during planning, or write `None — safe defaults and assumptions captured below` when no question is needed.
Each question asked must include:

- Question
- Why it matters
- Recommended default
- User answer, or fallback assumption if unanswered

## Brainstorm and options considered

For non-trivial epic or feature planning, explore plausible implementation or decomposition directions before converging. Include agent-resolvable uncertainty as assumptions, not blockers. Exactly one option must be marked recommended unless a blocking user/operator-owned decision prevents safe convergence; if using a hybrid, mark the hybrid as the recommended selected direction.

| Option | Summary | Pros | Cons/Risks | Decision |
|---|---|---|---|---|
| `Option 1` | `<implementation or decomposition direction>` | `<benefits>` | `<tradeoffs or risks>` | `recommended — <why>`, `rejected — <why>`, or `deferred — <why>` |

For trivial planning, write `Not needed — trivial atomic direction is clear`.

## Requirements

### Goals

- `<goal>`

### Non-goals

- `<explicit non-goal>`

### Assumptions

- `<assumption>`

### Constraints

- `<technical, safety, product, repo, or workflow constraint>`

## Overall completion criteria

List the parent-level outcomes that make the full decomposed epic/feature complete. Include parent-epic closure as an explicit final step: after every child reaches `verdict_accept`, close the parent with `br close <parent-issue-id> --reason "Completed" --actor <actor> --json` — child closure does not cascade.

- `<parent-level completion criterion>`

## Scope

### In scope

- `<in-scope area>`

### Out of scope

- `<out-of-scope area>`

### Expected touched areas

- `<expected file/path/module area, if known>`

## Risks

| Risk | Impact | Mitigation | Affects decomposition? |
|---|---|---|---|
| `<risk>` | `<impact>` | `<mitigation>` | `yes/no` |

## Verification strategy

Describe how completion will be verified across the decomposed atomic beads.

Include expected command categories, manual review expectations, and any evidence that child beads should produce.

## Decomposition strategy

Explain the boundary rule used to split atomic child beads.

A valid atomic child bead must have:

- one independently approvable task,
- clear done criteria,
- expected file/scope boundary,
- verification command or review method,
- independent repair path,
- explicit dependency/blocker links when needed.

## Proposed atomic beads

Each proposed atomic bead is the source text for a future child Bead description. Write each item in markdown, with enough detail that `beo-plan` can copy or lightly normalize it into `br create --description` without reinterpreting the parent plan. A child agent should be able to claim, validate, and implement the child from its Bead description without rereading this parent `PLAN.md`.

Preserve parent traceability through Beads dependency edges and the parent decomposition comment, not by requiring child descriptions to send agents back to the parent plan for implementation context.

### A1 — `<title>`

#### Task

<Full implementation request/context for this atomic task. Include relevant parent intent, domain terms, constraints, and any important assumptions needed by the child agent.>

#### Done criteria

- <specific acceptance criterion>
- <specific acceptance criterion>

#### Expected scope

- <files/areas allowed or expected>
- <explicit out-of-scope areas if useful>

#### Verification

- <commands/checks/manual review expected>
- <evidence the child should produce>

#### Dependencies and blockers

- Depends on: <none | A-id/title>
- Blocks: <none | A-id/title>
- Blocking user/operator decision: <none | decision>

#### Mode and risk notes

- Suggested mode: <quick | standard | strict>
- Rationale: <why this mode fits>
- Risk/rollback/human-gate/side-effect/reservation notes: <none or details sufficient to author child TICKET.json>

#### Atomicity rationale

<Why this task is independently approvable, has a separate repair path, and should not be split or merged further.>

Repeat the same markdown block for each proposed atomic bead (`A2`, `A3`, ...). When creating child Beads, `beo-plan` should normalize heading depth for rich markdown rendering in `br --description`/`bv`, not wrap the description in a code fence. Avoid parent-plan task checkboxes; once decomposition is recorded, Beads child issues and dependencies own task tracking.

## Dependency graph

Describe parent-child and child-child dependencies before creating Beads edges.

```text
<parent-issue-id>
  -> A1
  -> A2 depends on A1
```

## Open decisions

Only list decisions that genuinely block safe decomposition and require user/operator authority. Agent-resolvable uncertainty should become an explicit assumption or recommended default instead of an open decision. `plan_validated` requires no actual blocking decision rows; non-blocking follow-up notes belong in assumptions, risks, or a separate follow-up note, not this blocking-decision table. Any blocking open decision routes `user_review_needed`.

If no blocking decisions remain, write `None — no blocking user/operator decisions remain` and do not leave placeholder rows.

| Decision | Why blocked | Recommended option | Required owner |
|---|---|---|---|
| `<actual blocking decision only>` | `<reason>` | `<recommendation>` | `user/operator` |

## Plan validation summary

Write a short prose summary confirming whether the plan is ready for validation. Do not add task-completion checkboxes for the parent plan; after decomposition, child Beads and dependency edges are the task tracker.

The summary must state whether:

- parent bead id is present,
- goals and non-goals are explicit,
- brainstorm/options considered are recorded for non-trivial epic/feature planning, including one recommended direction with rationale and rejected or deferred alternatives with reasons,
- overall completion criteria are explicit,
- assumptions are explicit,
- scope and out-of-scope areas are explicit,
- verification strategy exists,
- proposed atomic beads are written as detailed markdown descriptions that include implementation context, done criteria, expected scope, verification guidance, dependencies/blockers, mode/risk notes, and atomicity rationale without requiring reread of the parent `PLAN.md`,
- decomposition traceability will be preserved through child Bead dependency edges when needed and the parent decomposition comment after `plan_validated`, without requiring per-child link fields before child Beads exist or a non-schema `TICKET.json` field,
- each proposed atomic bead has suggested mode/risk detail sufficient to author quick, standard, or strict child tickets without re-interpreting risk,
- no blocking open decisions remain; user/operator-owned blockers route `user_review_needed` instead of `plan_validated`.

`beo-validate` must validate the actual PLAN content, not trust this summary alone. The summary is planning evidence, not validation authority.

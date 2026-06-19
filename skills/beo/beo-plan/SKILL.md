---
name: beo-plan
description: "Plan BEO work from Beads issues. Use for epic requirement intake, recommended clarification, PLAN.md creation, validated atomic decomposition, and atomic TICKET.json/state authoring. Never mutate product files."
---
# beo-plan

## Read

- `br show <issue-id> --json`
- `.beads/artifacts/<issue-id>/PLAN.md` when it already exists
- `.beads/artifacts/<issue-id>/TICKET.json` when it already exists
- `.beads/artifacts/<issue-id>/state.json` when it already exists
- `.beads/artifacts/<issue-id>/runtime-events.jsonl` when present
- `beo-reference -> registry/ticket.schema.json` when writing or changing `TICKET.json`
- `beo-reference -> registry/profiles.json` when checking scope or protected paths
- `beo-reference -> registry/runtime-event.schema.json` before appending runtime events
- `beo-reference -> registry/pipeline.json` when choosing the emitted route
- `beo-reference -> templates/PLAN.template.md` when writing or decomposing a parent `PLAN.md`

## Do

1. Fresh-read the issue with `br`.
2. Claim the issue before any plan, ticket, or lifecycle write.
3. For an epic or feature, combine the user request with bead context and produce one clarification batch when needed. Each question must include why it matters, a recommended default, and the fallback assumption BEO will use if unanswered. Do not ask endless questions. If safe defaults exist, write `PLAN.md` with explicit assumptions. Use `user_review_needed` only when a missing decision affects risk mode, broad scope, human authorization, external side effects, irreversible behavior, or safe decomposition.
4. For non-trivial epic or feature planning, perform a short brainstorm pass before converging. Record 2-4 plausible implementation or decomposition options, their tradeoffs, exactly one recommended option with rationale unless the selected direction is an explicit hybrid, and rejected or deferred options with concise reasons. Brainstorming is not neutral option listing: recommend a safe direction whenever BEO has enough authority. If a safe recommendation is blocked by user/operator authority, route `user_review_needed` with the recommended option or fallback under the rule above; otherwise choose a safe default and record assumptions. Use this brainstorm to derive clarification questions, assumptions, risks, and proposed atomic beads. Do not route to the user just to brainstorm; ask only blocking authority questions under the rule above.
5. Write `.beads/artifacts/<issue-id>/PLAN.md` using `beo-reference/templates/PLAN.template.md`. The plan must include parent-level completion criteria, explicit assumptions, scope boundaries, verification strategy, brainstorm/options considered when non-trivial, and proposed atomic beads as detailed markdown blocks that are directly usable as child Bead descriptions without re-interpreting the parent requirement or risk/mode needs. Do not use table-row summaries or parent task checkboxes for proposed atomic beads.
   - Before finalizing proposed atomic beads, cross-reference their Expected scope. If 2+ beads share a file, note the merge or dependency in the decomposition strategy. Document the rationale to guide parallel dispatch later.
6. Emit `planned -> beo-validate` for `PLAN.md` validation.
7. Planning stop rule: after `PLAN.md` is written, emit `planned -> beo-validate` and stop. Do not create child beads until re-entering after `plan_validated`.
8. On re-entry after `plan_validated`, create child atomic beads directly from the validated `PLAN.md` proposed atomic bead blocks, dependency edges, and a parent summary comment referencing `PLAN.md`. Each child bead description must follow the self-contained description format in `beo-reference -> references/lifecycle.md`. Make child descriptions as detailed as the validated task text; do not collapse into one-line summaries or reinterpret parent requirements outside the validated plan.
   - When multiple child beads share an expected file, add dependency edges or document the merge decision in the parent summary comment.
   - Pre-write `TICKET.json` for **every** proposed atomic bead before emitting `decomposition_recorded`, using the validated `PLAN.md` "Proposed atomic beads" blocks as the source text. Create the child beads first to obtain each child `issue_id`, then write each child's `TICKET.json` in the same decomposition step. Pre-written tickets let each child enter validation directly instead of requiring a separate planning pass to author its ticket; the marginal cost of an unused TICKET is small. Each child TICKET is a self-contained `version: 1` ticket that conforms to the binding schema in `beo-reference -> registry/ticket.schema.json` (mode-conditional `risk` for standard/strict; `human_gates` and `strict` for strict).
9. For an atomic bead, record a compact atomicity rationale in the child Bead description or as a Beads comment/plan evidence ref, not as a `TICKET.json` field.
10. Write the smallest current `version: 1` `TICKET.json` for quick, standard, or strict mode. A child bead whose ticket was pre-written under step 8 keeps that ticket; correct it in place if a `validation_failed` finding requires it, rather than authoring a new one.
11. Initialize `state.json` in planned state.
12. When emitting `user_review_needed`, follow the `user_review_needed` handoff format in `beo-reference -> references/user-handoff.md`.

## Write

- `.beads/artifacts/<issue-id>/PLAN.md` for epic/feature planning only
- `.beads/artifacts/<issue-id>/TICKET.json` when the claimed issue is atomic, and `.beads/artifacts/<child-issue-id>/TICKET.json` for every pre-written child atomic bead at `decomposition_recorded`
- `.beads/artifacts/<issue-id>/state.json` initialization only
- Beads lifecycle/decomposition comments, child beads, dependency edges, compact `user_review_needed` route comments, and labels when needed, including `beo:blocked-user` only when an existing BEO label represents the state
- `runtime-events.jsonl` for `user_stop` only when a Human Gate blocks progress

## Emit

- `planned` -> `beo-validate`
- `decomposition_recorded` -> user
- `user_review_needed` -> user

## Never

- Do not mutate product files.
- Do not grant `PASS_EXECUTE`.
- Do not review or close work.
- Do not create fields outside the current canonical ticket or plan contracts.

# manual-pressure-scenarios

Role: ASSET
Allowed content only: prose pressure scenarios for authoring, audit, and hardening review. No executable checker, fixture, release, routing, or topology rules.

## Purpose

Use this file when reviewing or hardening beo contracts by prose pressure only.

For each scenario, inspect:
- scenario
- pressure
- expected wrong behavior
- likely rationalization
- required wording change

## Baseline scenarios

### 1. Tiny typo, one file, one verification
- Pressure: tiny work should not trigger expanded ceremony.
- Expected route: `beo-explore -> beo-plan(compact current-phase plan) -> beo-validate(PASS_SERIAL) -> beo-execute -> beo-review -> done(no-learning)`
- Expected wrong behavior: forcing a durable-learning hop for an obviously isolated accepted fix.
- Likely rationalization: “all accepts must go through compound for consistency.”
- Required wording change: let review close obvious `no-learning` inline without weakening durable-learning capture.

### 2. Stale approval before mutation, plan still current
- Pressure: execution must not continue on stale approval.
- Expected route: `beo-validate`
- Expected wrong behavior: execute keeps going because only freshness changed.
- Likely rationalization: “nothing in the files changed yet, so it is safe enough.”
- Required wording change: validate owns stale approval refresh before mutation.

### 3. Stale approval after mutation, changed files remain
- Pressure: execution must not resume as if nothing happened.
- Expected route: deterministically split to `beo-review` when scope impact needs assessment, or `beo-plan` when plan/file-scope/verification repair is already proven; never straight back to `beo-execute`
- Expected wrong behavior: execute continues implementing to finish the change.
- Likely rationalization: “we are almost done, so finishing first is cheaper.”
- Required wording change: approval/scope drift after mutation must exit execution immediately and must not emit `A or B` routing.

### 4. Requirement contradiction after plan exists
- Pressure: contradictory requirements must beat planning completeness.
- Expected route: `beo-explore`
- Expected wrong behavior: plan gets repaired on top of contradictory requirements.
- Likely rationalization: “the plan is the nearest editable artifact.”
- Required wording change: requirement failure outranks planning repair.

### 5. Plan file scope missing a required file
- Pressure: validation must not invent missing plan scope.
- Expected route: `beo-plan`
- Expected wrong behavior: validate passes or execute widens scope implicitly.
- Likely rationalization: “the missing file is obviously part of the same change.”
- Required wording change: plan owns bead/file-scope repair.

### 6. Execute needs file outside approved scope
- Pressure: execution must not widen scope in place.
- Expected route: `beo-plan`
- Expected wrong behavior: execute edits the file and explains it later.
- Likely rationalization: “the extra file is small and mechanically related.”
- Required wording change: approved scope is a hard stop, not a suggestion.

### 7. Root cause unproven blocker
- Pressure: mutation must not substitute for diagnosis.
- Expected route: `beo-debug`
- Expected wrong behavior: execute or review guesses a fix path.
- Likely rationalization: “the probable fix is obvious enough.”
- Required wording change: unproven blocker routes to debug first.

### 8. Debug proves plan invalid
- Pressure: debug should return to the real owner, not back to execution by habit.
- Expected route: `beo-plan`
- Expected wrong behavior: debug returns to execute even though scope or bead structure is wrong.
- Likely rationalization: “debug started from execute, so it should always return there.”
- Required wording change: proven plan invalidity beats origin-owner reflex.

### 9. Swarm channel unavailable before dispatch
- Pressure: swarm must not self-downgrade without reclassification.
- Expected route: `beo-validate`
- Expected wrong behavior: swarm silently converts to serial coordination.
- Likely rationalization: “the same work can still be done one-by-one.”
- Required wording change: swarm fallback must route through validate for mode reclassification.

### 10. Swarm overlap detected
- Pressure: coordinator must not normalize lost isolation.
- Expected route: `beo-plan`
- Expected wrong behavior: swarm keeps both workers active or serializes them ad hoc.
- Likely rationalization: “the overlap is small enough to manage operationally.”
- Required wording change: overlap means plan repair, not coordinator judgment.

### 11. Accept with durable repeated lesson
- Pressure: compact closure must not erase real reusable learning.
- Expected route: `beo-compound`
- Expected wrong behavior: review closes to done with `no-learning` too aggressively.
- Likely rationalization: “fewer hops is always better.”
- Required wording change: only obvious isolated accepts may skip compound.

### 12. Two accepted features share the same durable pattern
- Pressure: cross-feature learning must not stay trapped in feature-local closure.
- Expected route: `beo-dream`
- Expected wrong behavior: each feature records isolated learning but no consolidation occurs.
- Likely rationalization: “feature-level records are already enough.”
- Required wording change: dream owns cross-feature consolidation only after at least two accepted features support it.

### 13. Multiple active feature candidates
- Pressure: route must stop for feature selection instead of guessing.
- Expected route: `user`
- Expected wrong behavior: route picks one candidate from stale state or nearest artifact.
- Likely rationalization: “one candidate looks more recently touched.”
- Required wording change: ambiguous active feature selection belongs to user.

### 14. Fresh valid current owner, no contradiction
- Pressure: route churn should be suppressed.
- Expected route: preserve current owner
- Expected wrong behavior: route rewrites state and reselects the same owner on every re-entry.
- Likely rationalization: “recomputing route is safer every time.”
- Required wording change: preserve the current valid owner unless fresher contradictory evidence appears.

### 15. Review fix fully bounded in scope
- Pressure: review should only send work back to execute when the fix record is fully bounded.
- Expected route: `beo-review -> beo-execute`
- Expected wrong behavior: review routes to execute with a vague “small fix” and no bounded record.
- Likely rationalization: “the implementation detail is obvious from the finding.”
- Required wording change: reactive-fix records need explicit bounded fields before `fix_in_scope` is legal.

### 16. Agent Mail unavailable but one safe serial bead remains
- Pressure: serial fallback must be reclassified by validate, not improvised by swarm.
- Expected route: `beo-validate`, then `PASS_SERIAL` only if the serial envelope is explicitly still valid.
- Expected wrong behavior: swarm self-converts into serial coordination.
- Likely rationalization: “only the transport changed, not the work.”
- Required wording change: mode selection and serial fallback classification belong to validate.

### 17. Critical patterns exists but is not startup-critical
- Pressure: status scout lists `.beads/critical-patterns.md`, but startup policy says targeted consultation by default.
- Expected route: do not read `.beads/critical-patterns.md` as mandatory unless `beo-references -> learning.md` records repo-policy startup-critical designation or applicability matches the active feature.
- Expected wrong behavior: agent reads all critical patterns on every plan/execute/swarm because the file exists or appears in `next_reads`.
- Likely rationalization: “status output listed it, so it must be required.”
- Required wording change: status output must distinguish required reads from conditional/applicable reads.

### 18. Human-readable state drift temptation
- Pressure: `operator_view` must never outrank canonical owner fields.
- Expected route: canonical `current_owner` wins; stale `operator_view` is repaired or ignored.
- Expected wrong behavior: route or operator follows `operator_view.current_owner` when it disagrees with live state.
- Likely rationalization: “the human-readable mirror is easier to trust.”
- Required wording change: canonical fields win and stale `operator_view` must be cleaned up.

### 19. Scout overreach
- Pressure: read-only scout must not become a hidden gate owner.
- Expected route: final owner still comes from live artifacts and canonical routing.
- Expected wrong behavior: scout recommendation to execute is followed even though approval or plan is stale.
- Likely rationalization: “the status helper already summarized everything.”
- Required wording change: scout hints are advisory only and cannot authorize execution.

### 20. Go mode bypass temptation
- Pressure: go mode must not cover missing plan/readiness gates.
- Expected route: `beo-validate` emits `FAIL_PLAN` when required plan content is missing.
- Expected wrong behavior: execute starts because go mode is active.
- Likely rationalization: “go mode means just keep moving.”
- Required wording change: go mode suppresses only unnecessary questions, not owners or gates.

### 21. Worker successor-owner temptation
- Pressure: workers must not choose the next owner.
- Expected route: coordinator records the worker report; successor ownership remains with canonical swarm/pipeline logic.
- Expected wrong behavior: worker reports “next owner should be review” and the system accepts it as routing authority.
- Likely rationalization: “the worker already knows it is done.”
- Required wording change: workers report terminal shapes only; they do not own routing.

### 22. Review lenses split-verdict temptation
- Pressure: multiple lenses must not create multiple verdict authorities.
- Expected route: one `beo-review` verdict reflecting all lens evidence.
- Expected wrong behavior: acceptance lens passes so the review accepts despite an approval/scope lens failure.
- Likely rationalization: “most lenses passed.”
- Required wording change: lens findings are evidence only; any open P0/P1 still blocks accept.

### 23. Missing Agent Mail but PASS_SWARM temptation
- Pressure: dependency posture must constrain readiness.
- Expected route: `beo-validate` cannot emit `PASS_SWARM`; it may emit fresh `PASS_SERIAL` only when one safe serial bead remains.
- Expected wrong behavior: swarm starts or validate still emits `PASS_SWARM` because beads are isolated.
- Likely rationalization: “parallelism is conceptually still possible.”
- Required wording change: missing coordination dependency blocks swarm readiness.

### 24. Single-feature auto-promotion temptation
- Pressure: durable one-feature learning must not mutate shared guidance.
- Expected route: `beo-compound` may record a promotion candidate only.
- Expected wrong behavior: shared guidance is updated from one accepted feature without threshold evidence.
- Likely rationalization: “the lesson is obviously strong.”
- Required wording change: cross-feature promotion remains threshold-gated under `beo-dream`.

## Usage note

Use these scenarios to pressure-test wording and owner boundaries only. Canonical routing, approval, state, and schema doctrine remain in their shared references and owner skill contracts.

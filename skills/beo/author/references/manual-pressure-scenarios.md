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
- Expected route: `beo-explore -> beo-plan(micro-compact) -> beo-validate(PASS_SERIAL) -> beo-execute -> beo-review -> done(no-learning)`
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

## Usage note

Use these scenarios to pressure-test wording and owner boundaries only. Canonical routing, approval, state, and schema doctrine remain in their shared references and owner skill contracts.

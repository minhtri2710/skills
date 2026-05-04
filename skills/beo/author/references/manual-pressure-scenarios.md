## Contents

- Purpose
- Baseline must-read scenarios
- Extended corpus
- Usage note

# manual-pressure-scenarios

Role: ASSET
Allowed content only: prose pressure scenarios for authoring, review, and hardening review. No executable checker, fixture, release, routing, or topology rules.

## Purpose

Use this file when reviewing or hardening beo contracts by prose pressure only.

For each scenario, inspect:
- scenario
- pressure
- ambiguity to avoid
- likely rationalization
- possible wording hardening

## Baseline must-read scenarios

Start routine authoring or hardening review with these scenarios, then use the extended corpus when the changed surface needs broader pressure:

1. Tiny typo, one file, one verification
2. Stale approval before mutation
3. Stale approval after mutation
4. Requirement contradiction after plan exists
5. Execute needs file outside approved scope
6. Root cause unproven blocker
7. Review fix fully bounded in scope
8. Execution-set missing before execute
9. Partial-progress authority from display card only
10. PASS_EXECUTE without approval_ref on unchanged approval

These are prose-only scenarios. They are not checker scripts, fixtures, automated evals, benchmarks, or release gates.

## Extended corpus

### 1. Tiny typo, one file, one verification
- Pressure: tiny work should not trigger expanded ceremony.
- Contract reading should indicate: `beo-explore -> beo-plan(compact current-phase plan) -> beo-validate(PASS_EXECUTE) -> beo-execute -> beo-review -> done(no-learning)`
- Ambiguity to avoid: forcing a durable-learning hop for an obviously isolated accepted fix.
- Likely rationalization: “all accepts must go through compound for consistency.”
- Possible wording hardening: let review close obvious `no-learning` inline without weakening durable-learning capture.

### 2. Stale approval before mutation, plan still current
- Pressure: execution must not continue on stale approval.
- Contract reading should indicate: `beo-validate`
- Ambiguity to avoid: execute keeps going because only freshness changed.
- Likely rationalization: “nothing in the files changed yet, so it is safe enough.”
- Possible wording hardening: validate owns stale approval refresh before mutation.

### 3. Stale approval after mutation, changed files remain
- Pressure: execution must not resume as if nothing happened.
- Contract reading should indicate: deterministically split to `beo-review` when scope impact needs assessment, or `beo-plan` when plan/file-scope/verification repair is already proven; never straight back to `beo-execute`
- Ambiguity to avoid: execute continues implementing to finish the change.
- Likely rationalization: “we are almost done, so finishing first is cheaper.”
- Possible wording hardening: approval/scope drift after mutation must exit execution immediately and must not emit `A or B` routing.

### 4. Requirement contradiction after plan exists
- Pressure: contradictory requirements must beat planning completeness.
- Contract reading should indicate: `beo-explore`
- Ambiguity to avoid: plan gets repaired on top of contradictory requirements.
- Likely rationalization: “the plan is the nearest editable artifact.”
- Possible wording hardening: requirement failure outranks planning repair.

### 5. Plan file scope missing a required file
- Pressure: validation must not invent missing plan scope.
- Contract reading should indicate: `beo-plan`
- Ambiguity to avoid: validate passes or execute widens scope implicitly.
- Likely rationalization: “the missing file is obviously part of the same change.”
- Possible wording hardening: plan owns bead/file-scope repair.

### 6. Execute needs file outside approved scope
- Pressure: execution must not widen scope in place.
- Contract reading should indicate: `beo-plan`
- Ambiguity to avoid: execute edits the file and explains it later.
- Likely rationalization: “the extra file is small and mechanically related.”
- Possible wording hardening: approved scope is a hard stop, not a suggestion.

### 7. Root cause unproven blocker
- Pressure: mutation must not substitute for diagnosis.
- Contract reading should indicate: `beo-debug`
- Ambiguity to avoid: execute or review guesses a fix path.
- Likely rationalization: “the probable fix is obvious enough.”
- Possible wording hardening: unproven blocker routes to debug first.

### 8. Debug proves plan invalid
- Pressure: debug should return to the real owner, not back to execution by habit.
- Contract reading should indicate: `beo-plan`
- Ambiguity to avoid: debug returns to execute even though scope or bead structure is wrong.
- Likely rationalization: “debug started from execute, so it should always return there.”
- Possible wording hardening: proven plan invalidity beats origin-owner reflex.

### 9. Accept with durable repeated lesson
- Pressure: compact closure must not erase real reusable learning.
- Contract reading should indicate: `beo-compound`
- Ambiguity to avoid: review closes to done with `no-learning` too aggressively.
- Likely rationalization: “fewer hops is always better.”
- Possible wording hardening: only obvious isolated accepts may skip compound.

### 10. Two accepted features share the same durable pattern
- Pressure: cross-feature learning must not stay trapped in feature-local closure.
- Contract reading should indicate: `beo-dream`
- Ambiguity to avoid: each feature records isolated learning but no consolidation occurs.
- Likely rationalization: “feature-level records are already enough.”
- Possible wording hardening: dream owns cross-feature consolidation only after at least two accepted features support it.

### 11. Multiple active feature candidates
- Pressure: route must stop for feature selection instead of guessing.
- Contract reading should indicate: `user`
- Ambiguity to avoid: route picks one candidate from stale state or nearest artifact.
- Likely rationalization: “one candidate looks more recently touched.”
- Possible wording hardening: ambiguous active feature selection belongs to user.

### 12. Fresh valid current owner, no contradiction
- Pressure: route churn should be suppressed.
- Contract reading should indicate: preserve current owner
- Ambiguity to avoid: route rewrites state and reselects the same owner on every re-entry.
- Likely rationalization: “recomputing route is safer every time.”
- Possible wording hardening: preserve the current valid owner unless fresher contradictory evidence appears.

### 13. Review fix fully bounded in scope
- Pressure: review should only send work back to execute when the fix record is fully bounded.
- Contract reading should indicate: `beo-review -> beo-validate -> beo-execute`
- Ambiguity to avoid: review routes directly to execute with a bounded record, bypassing the validate gate for a fresh `PASS_EXECUTE`.
- Likely rationalization: "the fix is bounded and small enough to skip validation."
- Possible wording hardening: all reactive-fix routes require a fresh `PASS_EXECUTE` from `beo-validate`; `beo-review` routes to `beo-validate`, not directly to `beo-execute`.

### 13a. Review-created bounded reactive fix with stale approval temptation
- Pressure: a bounded reactive fix must not self-authorize or reuse stale approval by convenience.
- Starting state: `beo-review` has completed review for one executed bead; verdict is `fix`; the defect is bounded and does not require requirements repair; the prior execution approval covered only the original execution set.
- Contract reading should preserve:
  1. `beo-review` records the bounded reactive-fix evidence.
  2. The workflow routes to `beo-validate`, not directly to `beo-execute`.
  3. `beo-validate` checks whether the fix remains inside the approval envelope.
  4. If approval is stale or scope changed, validation refuses `PASS_EXECUTE`.
  5. `beo-execute` runs only after a fresh `PASS_EXECUTE` with exactly one selected execution set.
- Ambiguity to avoid:
  - `beo-review` must not approve readiness.
  - `beo-execute` must not reuse stale approval by convenience.
  - The reactive fix must not widen scope without `beo-plan`.
- Possible wording hardening: the reactive-fix loop is `beo-review -> beo-validate -> beo-execute -> beo-review`; bounded fixes remain validation-gated and cannot self-authorize.

### 14. Critical patterns exists but is not startup-critical
- Pressure: status scout lists `.beads/critical-patterns.md`, but startup policy says targeted consultation by default.
- Contract reading should indicate: do not read `.beads/critical-patterns.md` as mandatory; consult it only when applicability matches the active feature.
- Ambiguity to avoid: agent reads all critical patterns on every plan/execute step because the file exists or appears in `next_reads`.
- Likely rationalization: “status output listed it, so it must be required.”
- Possible wording hardening: status output must distinguish required reads from conditional/applicable reads.

### 15. Human-readable state drift temptation
- Pressure: `operator_view` must never outrank canonical owner fields.
- Contract reading should indicate: canonical `current_owner` wins; stale `operator_view` is repaired or ignored.
- Ambiguity to avoid: route or operator follows `operator_view.current_owner` when it disagrees with live state.
- Likely rationalization: “the human-readable mirror is easier to trust.”
- Possible wording hardening: canonical fields win and stale `operator_view` must be cleaned up.

### 16. Scout overreach
- Pressure: read-only scout must not become a hidden gate owner.
- Contract reading should indicate: final owner still comes from live artifacts and canonical routing.
- Ambiguity to avoid: scout recommendation to execute is followed even though approval or plan is stale.
- Likely rationalization: “the status helper already summarized everything.”
- Possible wording hardening: scout hints are advisory only and cannot authorize execution.

### 17. Go mode bypass temptation
- Pressure: go mode must not cover missing plan/readiness gates.
- Contract reading should indicate: `beo-validate` emits `FAIL_PLAN` when required plan content is missing.
- Ambiguity to avoid: execute starts because go mode is active.
- Likely rationalization: “go mode means just keep moving.”
- Possible wording hardening: go mode suppresses only unnecessary questions, not owners or gates.

### 18. Review lenses split-verdict temptation
- Pressure: multiple lenses must not create multiple verdict authorities.
- Contract reading should indicate: one `beo-review` verdict reflecting all lens evidence.
- Ambiguity to avoid: acceptance lens passes so the review accepts despite an approval/scope lens failure.
- Likely rationalization: “most lenses passed.”
- Possible wording hardening: lens findings are evidence only; any open P0/P1 still blocks accept.

### 19. Single-feature auto-promotion temptation
- Pressure: durable one-feature learning must not mutate shared guidance.
- Contract reading should indicate: `beo-compound` may record a promotion candidate only.
- Ambiguity to avoid: shared guidance is updated from one accepted feature without threshold evidence.
- Likely rationalization: “the lesson is obviously strong.”
- Possible wording hardening: cross-feature promotion remains threshold-gated under `beo-dream`.

### 20. MED risk has format but no proof
- Pressure: a standard feature risk is listed, but no real proof or mitigation exists before execution.
- Contract reading should indicate: `beo-validate(FAIL_PLAN)`.
- Ambiguity to avoid: validate passes because the risk map section exists.
- Likely rationalization: “MED is not HIGH, so a named risk is enough.”
- Possible wording hardening: MED risks that affect acceptance, scope, verification, rollback, security, privacy, migration behavior, or compatibility require proof or accepted mitigation.

### 21. Acceptance-critical decision lacks UAT evidence
- Pressure: tests pass, but a locked user-visible decision requires visual/manual/runtime confirmation.
- Contract reading should indicate: `beo-review(fix or user/blocking route by evidence)`, never `accept`.
- Ambiguity to avoid: review accepts based only on command success.
- Likely rationalization: “automated verification passed, so manual evidence is optional.”
- Possible wording hardening: acceptance-critical decisions require decision verification or explicit `N/A`; skipped UAT is not a pass.

### 22. Post-compaction stale memory
- Pressure: agent resumes after compaction and remembers stale approval/readiness.
- Contract reading should indicate: re-open STATE/HANDOFF/CONTEXT/PLAN/approval before mutation.
- Ambiguity to avoid: execution continues from memory.
- Likely rationalization: “I already checked this before compaction.”
- Possible wording hardening: post-compaction mutation requires fresh canonical reads.

### 23. Bare review lens label
- Pressure: review says `security lens: pass` without evidence.
- Contract reading should indicate: review remains incomplete until evidence is cited.
- Ambiguity to avoid: accept based on labels.
- Likely rationalization: “the lens passed, so details are unnecessary.”
- Possible wording hardening: lens labels are not evidence.

### 24. Stale or conflicting owner in status
- Pressure: status output shows owner conflict or stale owner evidence.
- Contract reading should indicate: use `beo-route`; status does not select the owner.
- Ambiguity to avoid: agent follows status as a selected owner.
- Likely rationalization: “status already summarized the route.”
- Possible wording hardening: status owner fields are observed/advisory only.

### 25. User says go with missing requirements
- Pressure: user asks to proceed while acceptance, non-goals, compatibility, or constraints are missing.
- Contract reading should indicate: stop at the requirements owner path.
- Ambiguity to avoid: go mode executes from intent alone.
- Likely rationalization: “go means infer the missing details.”
- Possible wording hardening: go mode suppresses unnecessary questions only after requirements are locked.

### 26. User says go with stale approval
- Pressure: user asks to proceed after approval became stale.
- Contract reading should indicate: stop at validation/approval path.
- Ambiguity to avoid: user go revives stale execution approval.
- Likely rationalization: “fresh user intent is equivalent to approval refresh.”
- Possible wording hardening: only canonical approval doctrine refreshes execution approval.

### 27. Tiny UI copy change
- Pressure: one low-risk copy edit looks too small for workflow.
- Contract reading should indicate: micro-compact can reduce prose only; gates remain.
- Ambiguity to avoid: skip plan, validation, approval, verification, or review.
- Likely rationalization: “it is just copy.”
- Possible wording hardening: compactness changes presentation only.

### 28. One-line auth, permission, or security change
- Pressure: a sensitive one-line edit appears mechanically small.
- Contract reading should indicate: not shortcut-eligible; use the appropriate risk/planning depth.
- Ambiguity to avoid: treat it as tiny safe work.
- Likely rationalization: “the diff is one line.”
- Possible wording hardening: sensitive surfaces are excluded from shortcut treatment.

### 29. Gate card claims approval or selected owner
- Pressure: a display card says work is approved or names a selected owner.
- Contract reading should indicate: reject wording; card is display only.
- Ambiguity to avoid: card fields become binding.
- Likely rationalization: “the card is clearer with explicit decisions.”
- Possible wording hardening: remove binding fields from advisory cards.

### 30. Advisory guide copies approval schema
- Pressure: a convenience guide duplicates canonical approval fields.
- Contract reading should indicate: reject duplication and point to canonical approval reference.
- Ambiguity to avoid: guide becomes a second approval source.
- Likely rationalization: “copying saves a click.”
- Possible wording hardening: advisory surfaces point; they do not mirror doctrine.

### 31. Writer-map required for unrelated future edit
- Pressure: an upgrade preflight row is reused as mandatory future ceremony.
- Contract reading should indicate: reject as runtime ceremony.
- Ambiguity to avoid: every edit requires writer-map evidence.
- Likely rationalization: “it helped during hardening.”
- Possible wording hardening: preflight evidence is upgrade-local only.

### 32. Manual pressure added to CI
- Pressure: prose pressure scenarios are converted into an executable gate.
- Contract reading should indicate: reject automation.
- Ambiguity to avoid: manual review becomes CI, fixture, golden trace, or release gate.
- Likely rationalization: “automation enforces consistency.”
- Possible wording hardening: scenarios remain prose-only.

### 33. Too many owner/card templates
- Pressure: startup grows with many convenience cards.
- Contract reading should indicate: compress or delete; startup must not grow.
- Ambiguity to avoid: operators must scan a large advisory guide before routing.
- Likely rationalization: “more cards reduce ambiguity.”
- Possible wording hardening: keep startup compact and pointer-based.

### 34. Rollback ambiguity in advisory wording
- Pressure: wording could be read as approval, routing, readiness, review, dispatch, or learning promotion.
- Contract reading should indicate: delete advisory/card wording first.
- Ambiguity to avoid: preserve convenient but ambiguous text.
- Likely rationalization: “users liked the shortcut.”
- Possible wording hardening: keep only correct canonical owner/reference wording.

### 35. Specialist says pass but verification is missing
- Pressure: specialist evidence is positive but required verification is absent.
- Contract reading should indicate: no accept verdict.
- Ambiguity to avoid: review accepts from specialist confidence.
- Likely rationalization: “the specialist found no issues.”
- Possible wording hardening: only `beo-review` emits verdicts and required verification evidence must be present.

### 36. Debug likely but unproven cause
- Pressure: diagnosis identifies a plausible cause without proof.
- Contract reading should indicate: mark inconclusive; no mutation.
- Ambiguity to avoid: implement the likely fix.
- Likely rationalization: “the cause is obvious enough.”
- Possible wording hardening: debug separates proven evidence from hypotheses.

### 37. Debug card includes patch wording
- Pressure: debug output starts describing code changes to make.
- Contract reading should indicate: remove patch wording; return to the legal owner.
- Ambiguity to avoid: debug effectively implements or prescribes a fix.
- Likely rationalization: “the unblock path should be actionable.”
- Possible wording hardening: safe unblock names owner/action, not patch content.

### 38. Learning card promotes one feature
- Pressure: one accepted feature has a reusable idea.
- Contract reading should indicate: feature-level disposition only; promotion remains threshold/explicit-request gated.
- Ambiguity to avoid: shared guidance changes from one feature.
- Likely rationalization: “the idea is clearly reusable.”
- Possible wording hardening: one feature can be a candidate, not shared doctrine.

### 39. Exactly one owner predicate is true
- Pressure: routing machinery is invoked even though one valid owner predicate is already true.
- Contract reading should indicate: do not detour through `beo-route`.
- Ambiguity to avoid: route churn rewrites state without need.
- Likely rationalization: “routing is always safer.”
- Possible wording hardening: route only for missing, stale, contradictory, or colliding owner state.

### 40. Wrong owner attempts artifact write
- Pressure: a skill tries to update a surface it does not own.
- Contract reading should indicate: stop and use the canonical owner/writer map.
- Ambiguity to avoid: write proceeds because the content is correct.
- Likely rationalization: “this is only a small wording fix.”
- Possible wording hardening: writer boundaries apply even for correct content.

### 41. Multiple ready beads after external-parallel removal
- Pressure: multiple approved ready beads exist, but no external-parallel owner exists.
- Contract reading should indicate: `beo-validate(PASS_EXECUTE)` only after writing an explicit `execution_set`.
- Ambiguity to avoid: route tries to select a removed parallel owner, blocks on external coordination, or lets execute mutate without a selected set.
- Likely rationalization: "multiple beads used to imply external parallel orchestration."
- Possible wording hardening: multiple safe beads are now execution-set evidence owned by validate/execute, not a separate route.

### 42. Local parallel overlap
- Pressure: execute sees two beads that look independent but share write paths or generated outputs.
- Contract reading should indicate: `beo-plan` if ordering/scope is missing, or `ordered_batch` if sequencing is already explicit.
- Ambiguity to avoid: execute runs them in parallel and reconciles conflicts ad hoc.
- Likely rationalization: "parallel is now inside execute."
- Possible wording hardening: local parallel is allowed only with disjoint write/generated scopes and no dependency edge.

### 43. Ordered batch with dependency edge
- Pressure: two approved beads are both ready, but bead B depends on bead A.
- Contract reading should indicate: `beo-validate(PASS_EXECUTE)` with `execution_set_mode=ordered_batch` and explicit order A then B.
- Ambiguity to avoid: validate blocks because multiple beads used to require swarm, or execute runs them concurrently.
- Likely rationalization: "batch means parallel."
- Possible wording hardening: execution-set mode separates ordered batch from local parallel.

### 44. Execution-set missing before execute
- Pressure: state says `beo-execute`, but no selected execution set is present.
- Contract reading should indicate: `beo-validate` or `beo-route` according to canonical state freshness.
- Ambiguity to avoid: execute picks a convenient ready bead from live graph.
- Likely rationalization: "execute can choose what to run."
- Possible wording hardening: validate selects the execution set; execute mutates only selected work.

### 45. Partial batch blocker
- Pressure: one bead in an execution set hits an unproven blocker while other beads are unaffected.
- Contract reading should indicate: stop the affected bead and record blocker evidence; continue unaffected beads only when `partial_progress_allowed=true`, otherwise stop the set and route through `beo-debug`.
- Ambiguity to avoid: execute guesses a fix for the blocked bead or silently skips it.
- Likely rationalization: "the rest of the batch can continue."
- Possible wording hardening: partial progress must be explicit in execution-set evidence.

### 46. Partial-progress authority from display card only
- Pressure: `beo-validate` emits `PASS_EXECUTE` for an `ordered_batch` execution set and writes `partial_progress_allowed=true` in the Execution Set Card display, but does not write the field to `STATE.json` or `readiness-record.json`. A bead blocks during execute. Execute reads the card value and continues the unaffected beads.
- Contract reading should indicate: `beo-execute` checks canonical `readiness-record.json` and `STATE.json` for `partial_progress_allowed`; finding neither, it treats the default as `false` and stops the set; routes to `beo-debug`.
- Ambiguity to avoid: execute uses the card value as authoritative and continues unaffected beads.
- Likely rationalization: "the card clearly shows partial_progress_allowed=true."
- Possible wording hardening: the Execution Set Card is display-only; canonical partial-progress authority requires both `STATE.json` and `readiness-record.json` to carry the field.

### 47. PASS_EXECUTE without approval_ref on unchanged approval
- Pressure: `beo-validate` emits `PASS_EXECUTE` with `approval_action=unchanged` but does not populate `approval_ref` (reasoning that the approval was not newly created). `beo-execute` proceeds without an auditable approval reference.
- Contract reading should indicate: `beo-validate` must write `approval_ref` for every `PASS_EXECUTE` verdict regardless of `approval_action` value; `beo-execute` must confirm `approval_ref` is present before beginning mutation.
- Ambiguity to avoid: execute treats an unchanged approval as needing no explicit reference.
- Likely rationalization: "`approval_action=unchanged` means nothing needs to be written."
- Possible wording hardening: `approval_ref` is required when `verdict=PASS_EXECUTE`, including when `approval_action=unchanged`; the existing approval must remain auditable.

### 48. Route used as default hop
- Pressure: exactly one non-route owner predicate is live, but the operator invokes `beo-route` anyway.
- Contract reading should indicate: preserve the current valid owner.
- Ambiguity to avoid: route churn as a safety ritual.
- Likely rationalization: "routing again is always safer."
- Possible wording hardening: route is exception-resolution, not normal pipeline.

### 49. Partial-progress mirror mismatch
- Pressure: `STATE.json` says `partial_progress_allowed=true`, but `readiness-record.json` is missing or false.
- Contract reading should indicate: execute treats partial progress as false and stops the set.
- Ambiguity to avoid: use the permissive value.
- Likely rationalization: "one canonical-looking surface allowed it."
- Possible wording hardening: disagreement uses the safer interpretation and routes to validate/debug.

### 50. Bounded reactive fix skips validation
- Pressure: review emits a bounded fix and the operator routes directly to execute.
- Contract reading should indicate: `beo-review -> beo-validate -> beo-execute -> beo-review`.
- Ambiguity to avoid: bounded means approved.
- Likely rationalization: "the fix is small and in scope."
- Possible wording hardening: bounded reactive fixes still require fresh `PASS_EXECUTE`.

## Usage note

Use these scenarios for manual prose pressure review of wording and owner boundaries only. Canonical routing, approval, state, and schema doctrine remain in their shared references and owner skill contracts.


# Manual Pressure Scenarios

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

| ID | Scenario | Purpose |
| --- | --- | --- |
| 1 | Stale approval before mutation | approval freshness |
| 2 | Root cause unproven blocker | debug routing |
| 3 | Review fix fully bounded | fix routing |
| 4 | Tiny lane grows beyond one bead | triage drift |
| 5 | Execution set missing before execute | validate/execute handoff |
| 6 | Display card tries to grant authority | display-card authority |

These are prose-only scenarios. They are not checker scripts, fixtures, automated evals, benchmarks, or release gates.

## Surface-targeted additions

| Surface edited | Add scenarios covering |
| --- | --- |
| Approval / validate | stale approval, unchanged approval ref, missing readiness fields |
| Execute | selected-set missing, stale after mutation, ordered batch blocked, unrelated live-file ambiguity |
| Review | live diff mismatch, bounded fix, post-execution modification, Decision Verification |
| Route / pipeline | route suppression, stale handoff, owner collision, feature collision |
| Tiny / compact | compact pressure, triage drift, short-prose accept gate boundary |
| Human Gates | chat-only gate, fallback limits, UAT/approval never fallback |
| Learning | no-learning, unclear signal, one-feature promotion, two-feature consolidation |
| Startup | missing state, stale handoff, multi-feature candidates |
| Authoring / governance | duplicate law, protected surfaces, self-modifying skill edits |
| Debug | unproven cause, patch-wording temptation, debug round-trip reverify |

## Scenarios

### 1. Stale approval before mutation

- Pressure: execution must not continue on stale approval.
- Contract reading should indicate: `beo-validate` or `beo-plan` by stale cause.
- Ambiguity to avoid: execute keeps going because no file changed yet.
- Likely rationalization: nothing changed locally, so it is safe.
- Possible wording hardening: approval freshness is required before mutation and is not inferred from intent.

### 2. Root cause unproven blocker

- Pressure: mutation must not substitute for diagnosis.
- Contract reading should indicate: `beo-debug`.
- Ambiguity to avoid: execute or review guesses a fix path.
- Likely rationalization: the probable fix is obvious.
- Possible wording hardening: unproven blocker routes to debug first.

### 3. Review fix fully bounded

- Pressure: review should not route directly to execute.
- Contract reading should indicate: `beo-review -> beo-plan -> beo-validate -> beo-execute` when root cause is proven, or `beo-review -> beo-debug` when unproven.
- Ambiguity to avoid: review creates executable fix scope or routes directly to validate/execute.
- Likely rationalization: the fix is small enough to skip planning.
- Possible wording hardening: review records findings only; every fix goes through plan after root cause is known.

### 4. Tiny lane grows beyond one bead

- Pressure: compact output should not hide larger scope.
- Contract reading should indicate: reclassify to `standard` before `PASS_EXECUTE` and suspend inherited go-mode.
- Ambiguity to avoid: tiny continues because it started tiny.
- Likely rationalization: preserving the short path is cheaper.
- Possible wording hardening: live scope growth beats initial triage.

### 5. Execution set missing before execute

- Pressure: execute must not infer selected beads from the plan.
- Contract reading should indicate: return to `beo-validate` for readiness and execution-set selection.
- Ambiguity to avoid: execute chooses the obvious bead itself.
- Likely rationalization: the plan has only one bead.
- Possible wording hardening: only validate emits selected execution-set mirrors.

### 6. Display card tries to grant authority

- Pressure: a display packet claims approval or readiness without canonical artifacts.
- Contract reading should indicate: display-only text has no authority; use canonical state/artifact references.
- Ambiguity to avoid: operator acts on a summary field.
- Likely rationalization: the card is clear enough.
- Possible wording hardening: authority note must point back to canonical surfaces.

### 7. Requirement contradiction after plan exists

- Pressure: contradictory requirements must beat planning completeness.
- Contract reading should indicate: `beo-explore`.
- Ambiguity to avoid: plan gets repaired on top of contradicted requirements.
- Likely rationalization: the plan is nearest editable artifact.
- Possible wording hardening: requirement failure outranks planning repair.

### 8. Plan file scope missing a required file

- Pressure: validation must not invent missing plan scope.
- Contract reading should indicate: `beo-plan`.
- Ambiguity to avoid: validate passes or execute widens scope implicitly.
- Likely rationalization: the missing file is mechanically related.
- Possible wording hardening: plan owns bead/file-scope repair.

### 9. Execute needs file outside approved scope

- Pressure: execution must not widen scope in place.
- Contract reading should indicate: `beo-plan`.
- Ambiguity to avoid: execute edits and explains later.
- Likely rationalization: the extra file is small.
- Possible wording hardening: approved scope is a hard stop.

### 10. Ordered batch bead blocks

- Pressure: selected sequential work cannot continue after a blocked bead.
- Contract reading should indicate: stop the batch and route by the proven condition.
- Ambiguity to avoid: continuing later beads because they look independent.
- Likely rationalization: unaffected beads can still finish.
- Possible wording hardening: ordered batch is stop-on-blocker.

### 11. Multiple active feature candidates

- Pressure: route must stop for feature selection instead of guessing.
- Contract reading should indicate: `user`.
- Ambiguity to avoid: route picks one from recent files.
- Likely rationalization: one candidate looks more recent.
- Possible wording hardening: ambiguous active feature selection belongs to user.

### 12. Fresh valid current owner

- Pressure: route churn should be suppressed.
- Contract reading should indicate: preserve current owner.
- Ambiguity to avoid: route reselects the same owner on every entry.
- Likely rationalization: recomputing route is safer.
- Possible wording hardening: preserve valid owner unless contradictory evidence appears.

### 13. Accept with no reusable learning

- Pressure: accepted isolated work should close without ceremony.
- Contract reading should indicate: `done` with `no-learning`.
- Ambiguity to avoid: every accept routes to compound.
- Likely rationalization: consistency requires a learning hop.
- Possible wording hardening: compound requires durable-candidate or unclear evidence.

### 14. One feature tries to promote shared guidance

- Pressure: feature-local learning should not become corpus guidance alone.
- Contract reading should indicate: `beo-compound` records local learning only.
- Ambiguity to avoid: single accepted feature mutates shared guidance.
- Likely rationalization: the pattern seems generally useful.
- Possible wording hardening: dream requires two outcomes or explicit user request.

### 15. Two accepted features share a pattern

- Pressure: cross-feature learning should consolidate when threshold evidence exists.
- Contract reading should indicate: `beo-dream`, with user-confirmed target path before shared mutation.
- Ambiguity to avoid: mutating an assumed shared file without confirmation.
- Likely rationalization: the target path is obvious.
- Possible wording hardening: shared guidance target must be current and user-confirmed.

### 16. Post-execution modification

- Pressure: finalized bundle hash differs from live file hash.
- Contract reading should indicate: review treats the file as post-execution modified or inconclusive and blocks accept if in scope.
- Ambiguity to avoid: attributing the later change to execution.
- Likely rationalization: the file is still part of the same feature.
- Possible wording hardening: hash mismatch blocks accept unless resolved by a legal repair path.

### 17. Approval or UAT gate under go-mode

- Pressure: go-mode fallback is active but approval or UAT is required.
- Contract reading should indicate: route to `user`.
- Ambiguity to avoid: go-mode assumes approval.
- Likely rationalization: the user asked to move fast.
- Possible wording hardening: approval and UAT gates never fallback.

### 18. Debug patch temptation

- Pressure: debug knows the fix and wants to include exact edits.
- Contract reading should indicate: report proof and unblock class only.
- Ambiguity to avoid: debug writes or describes the patch.
- Likely rationalization: saving execute time.
- Possible wording hardening: debug output excludes patch text and mutation commands.

### Setup 1. Setup helper tries to become runtime owner

- Pressure: user asks "check BEO setup and continue the feature."
- Contract reading should indicate: `beo-setup` may report setup status, then hand off to the valid runtime owner or `beo-route` if owner identity is unsafe.
- Ambiguity to avoid: setup skill repairs or continues runtime artifacts.
- Likely rationalization: setup already read state, so it can continue.
- Possible wording hardening: setup output is advisory and never overrides runtime owner contracts.

### Setup 2. Missing AGENTS.md in apply mode

- Pressure: user asks "set up BEO in this repo."
- Contract reading should indicate: `beo-setup` may create `AGENTS.md` from `AGENTS.template.md`.
- Ambiguity to avoid: setup creates `.beads` or initial feature artifacts.
- Likely rationalization: a setup should fully initialize the project.
- Possible wording hardening: setup creates only AGENTS.md; runtime artifacts are owner-owned.

### Setup 3. Missing managed block in check-only mode

- Pressure: user asks "is BEO installed?"
- Contract reading should indicate: report missing managed block, recommend apply, but do not write.
- Ambiguity to avoid: check-only silently appends the block.
- Likely rationalization: fixing is obvious and harmless.
- Possible wording hardening: writes require explicit apply/setup request.

### Setup 4. Malformed managed markers

- Pressure: AGENTS.md has duplicated or broken BEO managed markers.
- Contract reading should indicate: stop and ask user before editing.
- Ambiguity to avoid: setup guesses which block to keep.
- Likely rationalization: the newest block is probably right.
- Possible wording hardening: marker ambiguity blocks automatic edit.

### Setup 5. Usage guidance grants authority

- Pressure: user asks "how do I use BEO quickly?"
- Contract reading should indicate: explain normal path and authority boundaries.
- Ambiguity to avoid: usage guide implies user instruction can skip validate/approval/review.
- Likely rationalization: the user only wanted speed.
- Possible wording hardening: speed does not bypass owner selection, validation, approval freshness, execution scope, or review.

### Setup 6. Existing valid owner

- Pressure: STATE.json names a valid current owner.
- Contract reading should indicate: `beo-setup` reports current owner and recommends continuing there.
- Ambiguity to avoid: route churn or setup-driven owner reselection.
- Likely rationalization: setup should recompute route.
- Possible wording hardening: setup does not override a valid current runtime owner.

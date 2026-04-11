# REVIEW-PLAN.md

## Scope

Deep review of all 13 beo skills under `skills/beo/`:

`router` · `exploring` · `planning` · `validating` · `swarming` · `executing` · `reviewing` · `compounding` · `debugging` · `dream` · `writing-skills` · `using-beo` · `reference`

Review rubric:
- `SKILL.md` quality and hard-gate clarity
- shared-protocol correctness (`STATE.json`, `HANDOFF.json`, approval, status mapping)
- reference file alignment and cross-reference integrity
- `agents/openai.yaml` prompt fit
- eval realism, fixture grounding, and gate coverage
- current-phase semantics, CLI correctness, and context-budget behavior

---

## Executive Summary

The beo skill set is architecturally strong. All 13 skills have the expected structure, the current-phase model is mostly consistent end-to-end, and the shared reference layer is doing real work. Cross-references resolve correctly across all skills -- no broken pointers were found.

The main problems are **protocol drift**, **stale examples**, **critical stop behaviors living in prose instead of `<HARD-GATE>` blocks**, and **thin eval suites with no fixture grounding**.

### Highest-priority issues

1. **`STATE.md` vs `STATE.json` three-way split.** `beo-using-beo` script creates `.beads/STATE.md`, reference docs say `STATE.json`, canonical protocol says `STATE.json`. `beo_status.mjs` regex-parses Markdown. `checkRepo` schema docs disagree with implementation (`state_json_exists` vs `state_md_exists`). `onboarding.json` field names also mismatch (`state_json` vs `state_md`). Router eval fixtures use `STATE.md`.
2. **Swarming and executing drift from canonical state/task model.** Swarm HANDOFF example is malformed, worker flow bypasses parts of `dispatch_prepared -> in_progress`, approval-invalidated routing contradicts between SKILL.md and operations.
3. **18+ blocking behaviors are not hard-gated.** Onboarding gates use blockquotes not `<HARD-GATE>`. Swarming has no gate for `approved` label. Multiple skills bury stop conditions in operations prose.
4. **Eval suites are uniformly thin.** 10 of 13 skills have 2-3 evals. Zero skills have fixture-grounded evals (all `"files": []`). No skill tests all its hard gates.
5. **Stale internal numbering.** "Phase 6" in validating guardrails, "Phase 1"/"Phase 2" in blocker-handling and review-specialist-prompts reference an old SKILL.md structure that no longer exists.

---

## Risk Heatmap

| Tier | Skills | Why |
|---|---|---|
| **Critical** | `using-beo`, `swarming`, `executing` | STATE.md/JSON split breaks onboarding-to-pipeline handoff; swarming/executing have protocol drift that can misroute or corrupt task state |
| **High** | `router`, `validating`, `debugging`, `writing-skills` | Router depends on reference co-loading with no gate; validating has stale refs; debugging assumes Agent Mail; writing-skills references nonexistent tool |
| **Medium** | `exploring`, `planning`, `reviewing`, `compounding`, `dream`, `reference` | Mostly hard-gate gaps, alignment issues, eval-grounding, or stale numbering |

---

## Confirmed P1 Findings

| # | Finding | Representative locations | Action |
|---|---|---|---|
| 1 | **`STATE.md` vs `STATE.json` three-way split.** Script creates MD, refs say JSON, canonical says JSON. Scout regex-parses MD. `checkRepo` field names disagree with docs. `onboarding.json` has `state_md` vs documented `state_json`. | `using-beo/scripts/onboard_beo.mjs:120,130,197,212,292,324`, `using-beo/references/onboarding-flow.md:23,38,69,85`, `using-beo/assets/AGENTS.template.md:26,27,35`, router eval fixture | Migrate all to canonical `.beads/STATE.json` with 12-field schema; align script, docs, scout, and eval fixtures |
| 2 | **Router eval fixture contradicts canonical protocol.** `STATE.md` not `STATE.json`; HANDOFF.json says resume validating while STATE.md says next is executing. Evals 2-5 have no fixture files. | `router/evals/files/router-fixture/.beads/STATE.md`, `router/evals/files/router-fixture/.beads/HANDOFF.json`, `router/evals/evals.json` | Fix fixture to STATE.json; resolve contradictory state; add fixtures for evals 2-5 |
| 3 | **State routing table lives outside router with no co-loading gate.** Router's core job depends entirely on `pipeline-contracts.md` in beo-reference. Loading beo-router alone is insufficient. | `router/references/state-routing.md` (12-line pointer), `reference/references/pipeline-contracts.md` | Add `<HARD-GATE>` requiring beo-reference co-loading, or inline the routing table |
| 4 | **`plan.md` missing from router artifact inspection order.** Can misclassify `planning-current-phase` vs `planning-needs-approach` boundary. | `router/references/router-operations.md:186-196` | Add `plan.md` between `approach.md` and `phase-plan.md` in inspection order |
| 5 | **Exploring handoff missing STATE.json 12-field example.** Agent has no guidance on mandatory field values at exploring completion. | `exploring/SKILL.md:100-103` | Add concrete STATE.json example block with all 12 fields |
| 6 | **Exploring onboarding gate is blockquote not `<HARD-GATE>`.** Same issue in planning. LLMs trained on `<HARD-GATE>` markers may treat blockquotes as advisory. | `exploring/SKILL.md:11`, `planning/SKILL.md` | Wrap onboarding gates in `<HARD-GATE>` blocks |
| 7 | **Exploring default loop has no explicit "wait for user response" step.** Steps 5-7 flow without pause, contradicting the one-question-at-a-time hard gate. | `exploring/SKILL.md:35-43` | Restructure as repeat sub-loop with explicit wait step |
| 8 | **Swarming SKILL.md has no hard gate for `approved` label.** An agent loading beo-swarming directly can execute unapproved work. | `swarming/SKILL.md:23-30` | Add `<HARD-GATE>` requiring `approved` label |
| 9 | **Swarming completion STATE.json status field unspecified.** Operations say "update STATE.json with phase complete" but don't specify the canonical status value (`phase-complete-needs-replan`). | `swarming/references/swarming-operations.md:161-166` | Specify exact status value per pipeline-contracts row 13 |
| 10 | **Validating guardrails reference stale "Phase 6".** No numbered phases exist in current skill structure. | `validating/references/validating-guardrails.md:8` | Replace with reference to the approval gate directly |
| 11 | **Executing approval-invalidated routing contradicts between SKILL.md and operations.** SKILL.md says route to planning when tasks advanced; operations always routes to validating. | `executing/SKILL.md:41-46`, `executing/references/execution-operations.md:16` | Update operations to match SKILL.md's two-case branching |
| 12 | **Executing stale-label cleanup missing `in_progress`.** Previously stuck beads won't be cleaned before re-dispatch. | `executing/references/execution-operations.md:86-91` | Add `br label remove <TASK_ID> -l in_progress` to cleanup block |
| 13 | **Reviewing reactive fix bead uses `blocks:<closed-bead>` -- semantically meaningless.** Creating a fix bead that `blocks` an already-closed bead is a no-op. Consistent across 3 locations. | `reviewing/references/review-specialist-prompts.md:81-82`, `reviewing/references/reviewing-operations.md:67`, `reference/references/pipeline-contracts.md` | Clarify intended dep semantics; remove `blocks:` to closed beads or use `--parent` only |
| 14 | **Reviewing P2/P3 follow-up description inline contradicts template reference.** Inline `\n` escape sequences are fragile; immediately followed by "must use shared template." | `reviewing/references/review-specialist-prompts.md:92-97` | Remove inline block; direct to canonical template |
| 15 | **Compounding STATE.json uses `"status": "complete"` not `"completed"`.** `"complete"` is not in the routing table. | `compounding/references/compounding-operations.md:167` | Change to `"completed"` per routing table row 11 |
| 16 | **Compounding STATE.json uses `"next": "done"` -- not a valid `beo-<skill>` name.** | `compounding/references/compounding-operations.md:170` | Use `"beo-router"` or document `"done"` as canonical terminal value |
| 17 | **Debugging `fetch_inbox()` called without availability guard.** Solo-mode fallback exists in message-templates but diagnostic checklist doesn't branch to it. | `debugging/references/diagnostic-checklist.md:48` | Add availability check with solo-mode fallback |
| 18 | **Compounding graph verification doesn't account for multi-phase.** `br dep list` returns ALL children including future-phase beads that don't exist yet. | `compounding/references/compounding-operations.md:148-154` | Add note: verification applies to all beads; compounding runs only after entire feature completes |
| 19 | **`agentskills validate` is nonexistent, stderr suppressed.** Creates false-success validation step. | `writing-skills/references/writing-skills-operations.md:55`, `writing-skills/references/creation-log-template.md:194` | Remove or gate behind explicit availability check |

---

## Confirmed P2 Findings

### Router / Reference

- Evals 2-5 prompt-only with no fixture grounding
- `br doctor` referenced in guardrails but not operationalized in bootstrap
- `openai.yaml` for both skills is minimal -- no behavioral constraints for agent frameworks
- Reference SKILL.md surfaces only 1 `<HARD-GATE>` while underlying 15 files contain many critical rules
- `feature_name` vs `feature_slug` naming inconsistency (documented but cognitive trap)
- STATE.json write not mentioned in router SKILL.md main loop (only in operations ref)
- `dispatch_prepared` skip on instant path may violate status-mapping
- Reference evals have zero fixture files
- `beo_status.mjs` output schema undocumented
- `file-conventions.md` omits router as STATE.json writer
- `communication-standard.md` is only 9 lines / 4 bullets
- `agent-mail-coordination.md` uses pseudo-API syntax without specifying execution mechanism

### Exploring / Planning

- No mandatory learnings step in exploring (planning has it, exploring only has pointer)
- `CONTEXT.md` template missing scope classification field (Quick/Standard/Deep)
- Planning references use stale "Phase N" numbering (`discovery-guide.md:1` says "Phase 1", `bead-creation-guide.md:1` says "Phase 6/7")
- Quick mode bead-creation-guide tension with "no beads before phase-contract" hard gate
- `br dep cycles --json` may not exist (needs CLI verification)
- Both skills have 3 evals each with no fixtures
- No HIGH-stakes trigger heuristic defined concretely
- Minimal `openai.yaml` files
- CONTEXT.md routing loop potential between exploring and planning on wrong-slug edge case
- Planning context ~10k tokens (heavy but manageable with progressive disclosure)
- `plan-template.md` wrapped in code fence (agents may copy fence markers)
- Exploring "codebase scout" terminology used once without definition
- Exploring guardrails use wall-clock time (">15 min") which LLMs can't track

### Validating / Swarming

- `--graph-root` applicability unclear for `bv --robot-insights`
- Swarming `||` bash chaining syntax broken (at start of lines, not end)
- Validating has no HANDOFF.json template for checkpoint
- Swarming skill loading semantics unclear for subagent runtimes
- Swarming has only 3 evals, missing: unapproved-epic, worker-cap, phase-completion, checkpoint
- Idle tending section has no operational teeth (no cycle frequency, no escalation)
- `plan.md` listed as required in validating but not in route-back condition
- Missing CONTEXT.md not in `<HARD-GATE>` block in validating
- Worker-template "fully filled" example still has `<MODEL>` and `<RUNTIME_PROGRAM>` placeholders
- Validating `bead-reviewer-prompt.md` uses `BR-<id>` notation instead of real beo ID format

### Executing / Reviewing

- Executing has 3 evals no fixtures; reviewing has 2 evals missing critical paths
- `br audit record` command may not exist (needs CLI verification)
- `approach.md` missing from reviewing specialist inputs
- `partial` worker status undefined (no guidance on when to use vs `blocked`/`failed`)
- `blocker-handling.md` uses stale "Phase 1" reference; `review-specialist-prompts.md` uses "Phase 2"
- No hard gate preventing review entry when later phases remain (checks only after entry)
- P1 fix-bead create command inconsistent across reviewing files (`-p 1`, `--json` presence varies)
- Communication standard too thin to serve as formatting reference for review output
- Executing completion STATE.json example hardcodes `has_phase_plan: false` (misleading for multi-phase)
- Reviewing "Quick Mode" underspecified -- no explicit check against Quick-scope criteria
- Reviewing Learnings Synthesis specialist uses P1/P2/P3 severity framework despite being informational

### Compounding / Debugging / Dream

- Dream `codex-source-policy.md` referenced hardcoded `~/.codex/` paths with no platform guard
- `dream-run-provenance.md` format undefined (no template, no field list)
- All three skills' `openai.yaml` files are metadata-only (no behavioral constraints)
- Debugging SKILL.md missing learnings-read as explicit Phase 0 step
- All three skills have only 2 evals each, no fixtures
- Debugging message-templates uses `send_message()`/`fetch_inbox()`/`br comments add` without unified availability-detection guidance
- Compounding has no staging file cleanup after synthesis
- Compounding SKILL.md References section missing `compounding-operations.md`
- Debugging SKILL.md has no dedicated References section
- Dream SKILL.md step numbering doesn't align with operations sections

### Writing-Skills / Using-Beo

- Writing-skills onboarding gate questionable for meta-skill (blocks legitimate skill editing in non-beo repos)
- Writing-skills has only 2 evals -- no coverage for description trap, REFACTOR phase, context budget
- Using-beo has no adversarial evals testing hard gates under pressure
- `AGENTS.template.md` bloated at ~3.1k tokens (duplicates content from reference skills)
- `beo_status.mjs` regex-parses STATE.md -- fragile even if kept as Markdown
- Inconsistent indentation in `onboard_beo.mjs` (mixed 2/4-space, dedented closing brace)
- Using-beo says 30% context budget but template alone is ~3.1k tokens
- `AGENTS.template.md` contradicts itself (bans bare `bv` then shows bare `bv` example)
- `dream/references/pressure-scenarios.md` has 7 excellent RED scenarios not converted to evals
- Writing-skills `creation-log-template.md` has arbitrary "SKILL.md < 400 lines" criterion with no rationale

---

## Findings Downgraded or Removed

These were in the older review plan but should no longer drive active work:

- **Swarming top-level `format` field in HANDOFF**: undocumented but not a proven schema blocker. Treat as doc cleanup.
- **Reviewing "SKILL.md only mentions HANDOFF.json"**: outdated. `reviewing/SKILL.md` routes through shared protocol.
- **Dream "QMD guidance absent"**: too strong. Guidance exists; real gap is missing concrete query examples.
- **Dream "no structured anti-patterns"**: outdated. `dream/SKILL.md` has red-flags section.
- **Router `state-routing.md` being short**: intentional pointer file. Focus on co-loading gate instead.
- **Reference `communication-standard.md` being short**: functional as-is. Low priority.

---

## Execution Passes

### Pass 1 -- Canonical State Surface Migration _(M, 1-3h)_
- [x] Update `using-beo/scripts/onboard_beo.mjs` to create/read `.beads/STATE.json` with 12-field schema
- [x] Regenerate `beo_status.mjs` to read JSON state instead of regex-parsing Markdown
- [x] Align `beo_status.mjs` "current" logic with `checkRepo` managed-block freshness
- [x] Fix `checkRepo` field names to match reference docs (`state_json_exists`)
- [x] Fix `onboarding.json` field name to `state_json` per reference
- [x] Update `using-beo/scripts/test_onboard_beo.mjs` for JSON schema + scout/check parity
- [x] Fix router eval fixture: rename `STATE.md` to `STATE.json`, resolve HANDOFF contradiction, add fixtures for evals 2-5
- [x] Add `plan.md` to router-operations artifact inspection order
- [x] Reconfirm `using-beo/references/onboarding-flow.md`, `reference/references/file-conventions.md`, and `reference/references/state-and-handoff-protocol.md` all agree
- [x] Add router to `file-conventions.md` as STATE.json writer

### Pass 2 -- Swarming / Executing Protocol Alignment _(M, 2-4h)_
- [x] Add `<HARD-GATE>` for `approved` label in swarming SKILL.md
- [x] Specify exact `phase-complete-needs-replan` status value in swarming completion
- [x] Fix `||` bash chaining in swarming-operations (move to end of lines)
- [x] Fill placeholders in worker-template "fully filled" example
- [x] Add HANDOFF.json template to validating operations
- [x] Fix executing approval-invalidated routing (planning not validating when tasks advanced)
- [x] Add `in_progress` to executing stale-label cleanup
- [x] Add canonical cleanup to blocker resume flow
- [x] Replace hardcoded single-phase completion examples with planning-aware variants
- [x] Add `br sync --flush-only` after swarm-side mutation batches
- [x] Clarify `partial` worker status semantics

### Pass 3 -- Stale References and Protocol Drift _(M, 1-3h)_
- [x] Replace "Phase 6" in validating guardrails with direct approval-gate reference
- [x] Replace "Phase 1"/"Phase 2" in blocker-handling.md and review-specialist-prompts.md with current step references
- [x] Replace "Phase N" numbering in planning discovery-guide.md and bead-creation-guide.md
- [x] Fix reactive fix-bead `blocks:<closed-bead>` semantics across reviewing/reference
- [x] Remove inline P2/P3 description block; direct to canonical template
- [x] Fix compounding STATE.json: `"completed"` not `"complete"`, decide on `"done"` vs `"beo-router"`
- [x] Add multi-phase note to compounding graph verification
- [x] Remove or availability-gate `agentskills validate` in writing-skills
- [x] Add Agent Mail availability guard to debugging diagnostic-checklist
- [x] Normalize P1 fix-bead create command across reviewing files

### Pass 4 -- Hard-Gate Hardening _(M, 2-4h)_
- [x] Router: add co-loading gate for beo-reference, approved-lifecycle, graph-health gates
- [x] Exploring: wrap onboarding gate in `<HARD-GATE>`; add explicit wait-for-user step in loop
- [x] Exploring: add STATE.json 12-field example to handoff section
- [x] Planning: wrap onboarding gate in `<HARD-GATE>`; add discovery-before-approach gate
- [x] Validating: add CONTEXT.md to second hard gate's artifact list; add 3-iteration ceiling gate
- [x] Swarming: add approved-only, min-3 independent tasks, worker-cap gates
- [x] Executing: add required-artifact and D-ID mismatch stop gates
- [x] Reviewing: add multi-phase check to prerequisites (stop before starting, not just route out after)
- [x] Compounding: hard-gate no fabrication and no final-state write before graph/epic completion
- [x] Debugging: hard-gate 3-cycle escalation, exact failing-command verification, `needs_human` stop
- [x] Dream: hard-gate bootstrap/recurring ambiguity and `no durable signal -> no write`
- [x] Writing-skills: remove or scope onboarding gate for meta-skill context
- [x] Using-beo: hard-gate Node >=18 and approval-before-apply

### Pass 5 -- Shared Reference / Support-Skill Alignment _(M, 2-4h)_
- [x] Reconcile go-mode Gate 1 with `reference/references/approval-gates.md`
- [x] Make `--no-daemon` and `br sync --flush-only` explicit shared rules
- [x] Align exploring Quick wording with canonical Quick definition in `pipeline-contracts.md`
- [x] Add CONTEXT.md scope classification field (Quick/Standard/Deep) to context-template.md
- [x] Surface planning refactor sequencing + Quick-mode handling in main SKILL.md
- [x] Clarify Quick-mode bead-creation-guide compatibility with "no beads before phase-contract" hard gate
- [x] Update shared learnings-read guidance: **Obsidian + QMD first, flat-file fallback only when unavailable**
- [x] Apply same read-order to dream and compounding skills
- [x] Add concrete Obsidian/QMD examples or shared-reference pointer for dream and compounding
- [x] Generalize `dream/references/codex-source-policy.md`: platform-aware path resolution, no hardcoded paths
- [x] Fix `AGENTS.template.md` bare `bv` contradiction
- [x] Reduce `AGENTS.template.md` bloat (move reference content to on-demand loading)
- [x] Add staging file cleanup step to compounding after synthesis
- [x] Add debugging Phase 0 (learnings check) to SKILL.md main loop
- [x] Add provenance file template for dream-run-provenance.md

### Pass 6 -- Eval Grounding and Coverage _(L, 1-2d)_
- [x] Replace stale `STATE.md` fixtures and expectations across all evals
- [x] Add real artifact-backed fixtures for router, swarming, executing, using-beo, validating
- [x] Router: fix eval 1 fixture, add grounded fixtures for evals 2-5
- [x] Exploring: add resume, self-review loop, domain-classification scenarios
- [x] Planning: add single-vs-multi-phase, Quick mode, promotion flow scenarios
- [x] Validating: add boundary test (2 vs 3 thin beads), missing CONTEXT.md scenario
- [x] Swarming: add unapproved-epic, worker-cap, phase-completion, checkpoint scenarios
- [x] Executing: add missing-artifact, blocked-resume, approval-invalidated, multi-phase scenarios
- [x] Reviewing: add open-bead, missing-artifact, repeated-P1, later-phases-remain, Quick-review scenarios
- [x] Compounding: add epic-not-closed, no-learnings-no-fabrication, withheld-promotion scenarios
- [x] Debugging: add Agent-Mail-unavailable, decision-violation, `needs_human` scenarios
- [x] Dream: add no-durable-signal, approval-required-for-promotion, non-default-runtime scenarios; convert pressure-scenarios.md RED scenarios to evals
- [x] Writing-skills: add description-trap, REFACTOR phase, missing-validation-tool scenarios
- [x] Using-beo: add stale-managed-block, scout/check parity, Node <18, approval-before-apply scenarios
- [x] Ensure each blocking hard gate has at least one eval
- [x] Ensure every skill has at least one fixture-backed scenario

---

## Done Criteria

This review pass is complete when:

- [x] All canonical state surfaces use `.beads/STATE.json` with 12-field schema
- [x] `beo_status.mjs`, `checkRepo`, onboarding docs, router ops, and shared references agree on state semantics
- [x] Swarming/executing follow the canonical task transition model and flush rules
- [x] All stale "Phase N" references are replaced with current structure references
- [x] Reactive fix-bead creation is consistent across shared and per-skill docs
- [x] `agentskills validate` no longer creates false-green behavior
- [x] High-severity stop conditions are elevated into visible `<HARD-GATE>` blocks
- [x] Compounding STATUS.json and terminal-value fields match canonical protocol
- [x] Every skill has at least one fixture-backed eval and coverage for its blocking gates
- [x] Remaining medium-severity issues are either fixed or explicitly accepted as risk

---

## Notes

The old plan was directionally right about the repo's strengths and biggest weak spots (`using-beo`, `swarming`, eval depth). Changes in this update:
- **19 P1 findings** (up from 9) -- expanded from deep file-level review across all 13 skills
- Sharper prioritization: less doc-polish, more protocol correctness and hard-gate enforcement
- Eval pass now skill-specific with concrete scenario lists per skill
- Cross-reference integrity confirmed clean across all 13 skills (no broken pointers)
- Context budget analysis: exploring ~2.8k tokens (lean), planning ~10k (heavy but progressive disclosure works), validating ~9.4k, swarming ~7.3k, router ~7.1k minimum for functional routing

Additional user direction for follow-up fixes:
- Prefer **Obsidian + QMD first** for learnings lookup
- Apply to both **dream** and **compounding**
- Fall back to flat-file reads/search only when those are unavailable

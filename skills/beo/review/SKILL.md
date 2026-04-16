---
name: beo-review
description: |
  Use when all current-phase beads are terminal and post-implementation quality assessment is needed. Runs 5-specialist review (Code Quality, Architecture, Testing, UX/Performance, Security) with P1/P2/P3 severity grading, producing accept, fix, or reject. Do not use before implementation (use beo-validate), during active execution (use beo-execute/beo-swarm), for plan redesign (use beo-plan), for failure diagnosis (use beo-debug), or for learning extraction (use beo-compound).
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References**: Protocol rules reference the `beo-reference` skill via `→ references/<file>` for canonical documents.

# beo-review

## Overview
**Atomic purpose: assess post-execution quality across 5 specialist dimensions and emit a severity-classified verdict.** Make the post-execution quality decision for the completed current phase. **Core principle: pure assessment — produce findings and a decision, never implementation changes or follow-up bead creation.**

## Boundary Rules
- **MUST NOT** perform independent state detection or free-form routing — owned by `beo-route`. May emit canonical handoff to the next allowed pipeline skill when exit conditions are met.
- **MUST NOT** gather requirements — owned by `beo-explore`.
- **MUST NOT** decompose work — owned by `beo-plan`.
- **MUST NOT** verify plan structure — owned by `beo-validate`.
- **MUST NOT** write implementation code — owned by `beo-execute`.
- **MUST NOT** orchestrate workers — owned by `beo-swarm`.
- **MUST NOT** capture learnings — owned by `beo-compound`.
- **MUST NOT** diagnose root causes — owned by `beo-debug`.

## Hard Gates
> **HARD-GATE: ALL-BEADS-COMPLETE** — Review only starts when all current-phase beads are in terminal state per `the bead lifecycle states` (`beo-reference` → `references/status-mapping.md`) and pipeline readiness per the pipeline transition rules (`beo-reference` → `references/pipeline-contracts.md`). If any bead is in_progress or pending, route back.

> **HARD-GATE: NO-CODE-CHANGES** — Review never modifies implementation code. It only produces findings and decisions. If implementation changes are needed, hand back via the pipeline transition rules (`beo-reference` → `references/pipeline-contracts.md`).

> **HARD-GATE: APPROVAL-REMOVAL** — If review decides fix or reject, review MUST remove the `approved` label per `the beo approval gates` (`beo-reference` → `references/approval-gates.md`).

> **HARD-GATE: P1-BLOCKS-ACCEPT** — Any P1 finding blocks the accept decision. No exceptions.

## Communication Standard
> Follow the communication standard (`beo-reference` → `references/communication-standard.md`).

## Default Review Loop
1. **Setup**: Enumerate completed beads. Read implementation code, test results, bead comments, `CONTEXT.md`, and the current `phase-contract.md`. Resolve artifact locations from `artifact conventions (`beo-reference` → `references/artifact-conventions.md`)` under `.beads/artifacts/<feature_slug>/`.
2. **5-Specialist Review**: Run each specialist sequentially using `references/review-specialist-prompts.md`: Code Quality, Architecture, Testing, UX/Performance, and Security. Record findings with explicit P1/P2/P3 severity.
3. **Synthesis & Decision**: Aggregate findings and apply the decision rubric. Write `review-findings.md` to `.beads/artifacts/<feature_slug>/review-findings.md` using paths and ownership rules from `artifact conventions (`beo-reference` → `references/artifact-conventions.md`)`.
4. **Handoff**: Accept → hand off to `beo-compound`. Fix → remove `approved`, hand off to `beo-execute` with exact remediation scope. Reject → remove `approved`, hand off to `beo-plan` with structural issues. All transitions must follow the pipeline transition rules (`beo-reference` → `references/pipeline-contracts.md`) and `the STATE.json/HANDOFF.json protocol` (`beo-reference` → `references/state-and-handoff-protocol.md`).

### Reference Files
| File | Purpose |
|------|---------|
| `references/reviewing-operations.md` | Operational review sequence, review execution details, and failure handling hooks. |
| `references/review-specialist-prompts.md` | Canonical prompts and coverage expectations for the 5 review specialists. |

## Review Specialists
1. **Code Quality** — style, patterns, readability, maintainability.
2. **Architecture** — structural alignment with the plan, dependency correctness, integration points, regression risk.
3. **Testing** — test coverage, test quality, edge cases, verification completeness.
4. **UX/Performance** — user experience, performance characteristics, resource usage.
5. **Security** — vulnerabilities, data handling, auth/authz.

## Severity Model
- **P1 (Critical)** — Must fix before shipping. Blocks accept.
- **P2 (Important)** — Should fix. Recorded in findings for downstream tracking. Does not block accept.
- **P3 (Minor)** — Nice to fix. Never blocks accept.

## Inputs and Outputs
- **Inputs** — Completed current-phase implementation, test/verification results, bead comments/history, `CONTEXT.md`, `phase-contract.md`, optional `plan.md` as accepted-scope baseline.
- **Outputs** — `.beads/artifacts/<feature_slug>/review-findings.md`, severity-graded findings, decision (`accept | fix | reject`), exact remediation targets for fix/reject.

## Decision Rubrics
- **Accept vs Fix vs Reject** — Any P1 finding → fix. P2 findings are recorded in review-findings.md for downstream tracking and do not block acceptance. Structural mismatch with `CONTEXT.md`, `plan.md`, or `phase-contract.md` → reject and route to `beo-plan`. Only P2/P3 findings → accept.
- **Fix Scope** — Every fix directive must name the exact bead(s), exact finding(s), and exact acceptance condition. Never issue vague directives like “improve quality.”
- **UAT Gate** — If user approval is required at this point, follow `the beo approval gates` (`beo-reference` → `references/approval-gates.md`) before finalizing the decision.
- **Failure Recovery** — If review execution is interrupted, incomplete, or inconsistent, recover using `standard failure recovery (`beo-reference` → `references/failure-recovery.md`)`.

## Special Rules
- Review is a pure gate: no code edits, no plan edits, no hidden implementation suggestions outside recorded findings.
- State transitions must align with `the bead lifecycle states` (`beo-reference` → `references/status-mapping.md`).
- All handoff payloads must follow `the STATE.json/HANDOFF.json protocol` (`beo-reference` → `references/state-and-handoff-protocol.md`).
- If a shared concern appears, reference the canonical doc rather than restating it.

## Handoff
> Write `STATE.json` for normal transitions to adjacent skills with review findings, severity summary, required fixes, and compounding inputs. Use `HANDOFF.json` only for emergency checkpoint or low-context resume scenarios.

## Context Budget
> If context exceeds 65% capacity, compress non-essential history before continuing (`beo-reference` → `references/shared-hard-gates.md`).

## Red Flags & Anti-Patterns
- Review modifies code or artifacts outside review outputs.
- Review accepts with any P1 finding.
- Review starts while current-phase beads are still active or not terminal.
- Review fails to remove `approved` on fix or reject.
- Review emits vague findings without severity, owner, or remediation target.
- Review duplicates shared-reference content instead of linking canonical sources.
- Review creating follow-up beads or tracked work items (plan owns bead creation).

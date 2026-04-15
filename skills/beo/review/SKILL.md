---
name: beo-review
description: |
  Use after the final approved execution scope is complete, or when the user asks whether a feature is done, ready to ship, safe to merge, or needs a quality check. Triggers: "review this feature", "is this done?", "can we ship this?", "double-check the implementation", "run UAT". Runs 5-specialist review with P1/P2/P3 severity grading and accept/fix/reject decision. MUST NOT modify implementation code, approve with P1 issues, or validate plans. Do not use for plan review (use beo-validate) or mid-execution quality checks.
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References**: Protocol rules reference the `beo-reference` skill via `→ references/<file>` for canonical documents.

# beo-review

## Overview
Assess completed execution scope through 5-specialist review with severity grading and accept/fix/reject decision. **Core principle: pure assessment — produce findings and a decision, never implementation changes.**

## Boundary Rules
- **MUST NOT** route to skills — owned by `beo-route`.
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

> **HARD-GATE: APPROVAL-REMOVAL** — If review decides fix or reject, review MUST remove the `Approved` label per `the beo approval gates` (`beo-reference` → `references/approval-gates.md`).

> **HARD-GATE: P1-BLOCKS-ACCEPT** — Any P1 finding blocks the accept decision. No exceptions.

## Communication Standard
> Follow the communication standard (`beo-reference` → `references/communication-standard.md`).

## Default Review Loop
1. **Setup**: Enumerate completed beads. Read implementation code, test results, bead comments, `CONTEXT.md`, and the current `phase-contract.md`. Resolve artifact locations from `artifact conventions (`beo-reference` → `references/artifact-conventions.md`)` under `.beads/artifacts/<feature_slug>/`.
2. **5-Specialist Review**: Run each specialist sequentially using `references/review-specialist-prompts.md`: Code Quality, Testing, Integration, UX/Performance, and Security. Record findings with explicit P1/P2/P3 severity.
3. **Synthesis & Decision**: Aggregate findings and apply the decision rubric. Write `review-findings.md` at the feature artifact root using paths and ownership rules from `artifact conventions (`beo-reference` → `references/artifact-conventions.md`)`.
4. **Handoff**: Accept → hand off to `beo-compound`. Fix → remove `Approved`, hand off to `beo-execute` with exact remediation scope. Reject → remove `Approved`, hand off to `beo-plan` with structural issues. All transitions must follow the pipeline transition rules (`beo-reference` → `references/pipeline-contracts.md`) and `the STATE.json/HANDOFF.json protocol` (`beo-reference` → `references/state-and-handoff-protocol.md`).

### Reference Files
| File | Purpose |
|------|---------|
| `references/reviewing-operations.md` | Operational review sequence, review execution details, and failure handling hooks. |
| `references/review-specialist-prompts.md` | Canonical prompts and coverage expectations for the 5 review specialists. |

## Review Specialists
1. **Code Quality** — style, patterns, readability, maintainability.
2. **Testing** — coverage, edge cases, test quality.
3. **Integration** — cross-component compatibility, API contracts, data flow.
4. **UX/Performance** — user experience, performance characteristics, resource usage.
5. **Security** — vulnerabilities, data handling, auth/authz.

## Severity Model
- **P1 (Critical)** — Must fix before shipping. Blocks accept.
- **P2 (Important)** — Should fix. Blocks accept if there are 3 or more P2 findings.
- **P3 (Minor)** — Nice to fix. Never blocks accept.

## Inputs and Outputs
- **Inputs** — Completed execution scope for the current phase, implementation code, test results, bead comments/history, and current feature artifacts under `.beads/artifacts/<feature_slug>/` per `artifact conventions (`beo-reference` → `references/artifact-conventions.md`)`.
- **Outputs** — `review-findings.md`, severity-graded findings, accept/fix/reject decision, label updates per `the beo approval gates` (`beo-reference` → `references/approval-gates.md`), and handoff artifacts per `the STATE.json/HANDOFF.json protocol` (`beo-reference` → `references/state-and-handoff-protocol.md`).

## Decision Rubrics
- **Accept vs Fix vs Reject** — Any P1 finding → fix. Three or more P2 findings → fix. Structural mismatch with `CONTEXT.md`, `plan.md`, or `phase-contract.md` → reject and route to `beo-plan`. Only P3 findings → accept.
- **Fix Scope** — Every fix directive must name the exact bead(s), exact finding(s), and exact acceptance condition. Never issue vague directives like “improve quality.”
- **UAT Gate** — If user approval is required at this point, follow `the beo approval gates` (`beo-reference` → `references/approval-gates.md`) before finalizing the decision.
- **Failure Recovery** — If review execution is interrupted, incomplete, or inconsistent, recover using `standard failure recovery (`beo-reference` → `references/failure-recovery.md`)`.

## Special Rules
- Review is a pure gate: no code edits, no plan edits, no hidden implementation suggestions outside recorded findings.
- State transitions must align with `the bead lifecycle states` (`beo-reference` → `references/status-mapping.md`).
- All handoff payloads must follow `the STATE.json/HANDOFF.json protocol` (`beo-reference` → `references/state-and-handoff-protocol.md`).
- If a shared concern appears, reference the canonical doc rather than restating it.

## Handoff
> Write `HANDOFF.json` for every skill transition (`beo-reference` → `references/pipeline-contracts.md`). Transitions follow the pipeline: route → explore → plan → validate → (execute | swarm → execute) → review → compound.

## Context Budget
> If context exceeds 65% capacity, compress non-essential history before continuing (`beo-reference` → `references/shared-hard-gates.md`).

## Red Flags & Anti-Patterns
- Review modifies code or artifacts outside review outputs.
- Review accepts with any P1 finding.
- Review starts while current-phase beads are still active or not terminal.
- Review fails to remove `Approved` on fix or reject.
- Review emits vague findings without severity, owner, or remediation target.
- Review duplicates shared-reference content instead of linking canonical sources.

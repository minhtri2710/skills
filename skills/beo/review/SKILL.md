---
name: beo-review
description: |
  Use when all current-phase beads are terminal and the completed implementation needs a post-execution quality decision. Review runs the specialist review pass, writes `review-findings.md`, and emits exactly one verdict: `accept`, `fix`, or `reject`. Do not use before implementation completes, during active execution, for requirements or planning work, or to apply fixes directly.
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-review

## Atomic purpose
Assess completed current-phase work and issue one post-implementation verdict.

## When to use
- all current-phase beads are in canonical terminal states
- execution has finished and quality must be assessed before compounding or rework
- a reactive fix returned to review and the phase needs another review decision

## Inputs
**Required**
- completed current-phase implementation
- verification evidence and bead comments
- locked `.beads/artifacts/<feature_slug>/CONTEXT.md`
- current-phase `.beads/artifacts/<feature_slug>/phase-contract.md`

**Optional**
- `.beads/artifacts/<feature_slug>/plan.md`
- prior `review-findings.md` for resumed review work

## Outputs
**Allowed writes**
- `.beads/artifacts/<feature_slug>/review-findings.md`
- approval-label removal when verdict is `fix` or `reject`
- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- implementation code
- planning artifacts
- learnings artifacts

## Boundary rules
- Review is a pure post-implementation gate.
- Review does not edit code, debug root causes, redesign plans, or write learnings.
- Review may specify remediation targets, but remediation work is performed elsewhere.

## Minimum hard gates
- **ALL-BEADS-TERMINAL** — Start only when current-phase execution is complete enough to review.
- **NO-CODE-CHANGES** — Review does not implement fixes.
- **P1-BLOCKS-ACCEPT** — Any P1 finding blocks acceptance.
- **APPROVAL-REMOVAL-ON-FIX-OR-REJECT** — Remove `approved` when the verdict sends work backward.
- **STRUCTURED-UAT-ONLY** — If user-facing UAT approval is required, request it via the structured question tool.
- **TERMINATE-ON-HANDOFF** and **FRESH-LOAD-REQUIRED** — Follow the shared session-boundary rules.

## Default loop
1. Read the completed implementation, verification evidence, bead history, locked context, and current-phase contract.
2. Run the 5-specialist review using `references/review-specialist-prompts.md`.
3. Aggregate the findings, assign P1/P2/P3 severities, and write `review-findings.md`.
4. Emit exactly one verdict:
   - `accept` → hand off to `beo-compound`
   - `fix` → hand off to `beo-execute` when the canonical reactive-fix contract allows it
   - `reject` → hand off to `beo-plan`
5. Write `.beads/STATE.json` and stop.

## References
| File | Use when |
|------|----------|
| `references/reviewing-operations.md` | Running the review flow and verdict logic |
| `references/review-specialist-prompts.md` | Applying the 5 specialist lenses |
| `beo-reference` → `references/pipeline-contracts.md` | Reactive-fix eligibility and allowed transitions |
| `beo-reference` → `references/approval-gates.md` | UAT and approval-label ownership |
| `beo-reference` → `references/failure-recovery.md` | Recovering interrupted or inconsistent review work |

## Handoff and exit
- `accept` → `beo-compound`
- `fix` → `beo-execute` only when the reactive-fix contract permits it
- `reject` → `beo-plan`
- `ReturnToUser(...)` when explicit UAT confirmation is required
- Review stops after writing handoff state.

## Context budget
If context exceeds 65%, checkpoint via the shared protocol in `beo-reference` → `references/shared-hard-gates.md`.

## Red flags
- editing code during review
- accepting with a P1 finding
- starting while current-phase beads are still active
- issuing vague remediation instead of exact findings and targets
- continuing after writing inter-skill handoff state

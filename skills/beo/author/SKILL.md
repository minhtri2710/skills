---
name: beo-author
description: |
  Create, revise, or pressure-test beo skill definitions and their supporting references when the skill system itself must be changed, clarified, or evaluated. Use only for skill-system authoring, not for live feature delivery, operational pipeline execution, bootstrap repair, or product-code implementation.

---

> **HARD-GATE: SKILL-REPO-CONTEXT** — Author operates on beo skill definitions and their supporting references, not on feature-delivery artifacts.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-author

## Atomic purpose
Modify and pressure-test the beo skill system itself.

## When to use
- a beo skill must be created or rewritten
- an existing beo skill shows overlap, ambiguity, or hidden dependency drift
- a beo skill definition needs structured pressure-testing before release

## Inputs
**Required**
- target skill change request
- existing `SKILL.md` files and relevant supporting references
- pressure-test scenarios

**Optional**
- prior findings or optimization notes about the target skill definitions

## Outputs
**Allowed writes**
- new or revised `SKILL.md` files
- updated supporting author or reference artifacts required for the skill definition
- pressure-test logs or creation logs
- `.beads/STATE.json` only if this meta-work is being routed back through beo state
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- feature-delivery artifacts
- implementation code for product features
- onboarding bootstrap state except through `beo-onboard`

## Boundary rules
- Author owns skill creation and modification only.
- Author must not perform product feature work, execute operational pipeline phases on behalf of delivery skills, or do onboarding except by routing to `beo-onboard`.
- Author must not substitute for route, explore, plan, validate, execute, review, debug, compound, dream, or onboard in live delivery.
- Author must not change canonical skill order, topology, or control flow accidentally; any such change must be explicit in the request and propagated consistently through the canonical pipeline references.
- Author must remove overlap through explicit contract clarity rather than vague instructions.
- Author must not leave hidden dependencies or undefined contracts in authored skills.

## Minimum hard gates
- **CANONICAL-CONTRACT-COMPLETE** — Every authored skill must define purpose, inputs, outputs, boundaries, minimum hard gates, references, and handoff behavior.
- **PRESSURE-TEST-REQUIRED** — New or substantially changed skills must be pressure-tested before release.
- **NO-FEATURE-WORK** — If the task becomes product feature delivery, hand off to the appropriate beo pipeline skill.
- **TERMINATE-ON-HANDOFF** and **FRESH-LOAD-REQUIRED** — Follow the shared session-boundary rules when author work participates in beo routing.

## Default loop
1. Read the target skill definition and adjacent skills to understand the current boundary surface.
2. Rewrite or refine the skill contract so responsibility, inputs, outputs, and non-goals are explicit.
3. Run the pressure-test scenarios and record failures.
4. Refine until the skill no longer overlaps adjacent skills and every failure mode has a recovery path.
5. If beo state is being used for this meta-work, write handoff state and stop.

## References
| File | Use when |
|------|----------|
| `references/writing-skills-operations.md` | Running the authoring workflow |
| `references/creation-log-template.md` | Recording decisions and revision history |
| `references/pressure-test-template.md` | Testing boundary clarity and failure handling |
| `beo-reference` → `references/pipeline-contracts.md` | Checking that authored skills do not change the canonical pipeline accidentally |
| `beo-reference` → `references/failure-recovery.md` | Ensuring authored skills have explicit recovery paths |

## Handoff and exit
- Normal completion handoff: `beo-route` when this meta-work is being managed through beo state
- Otherwise author simply finishes after updating the skill definitions.

## Context budget
If context exceeds 65%, checkpoint via the shared protocol in `beo-reference` → `references/shared-hard-gates.md`.

## Red flags
- letting author drift into product feature work
- shipping a skill contract without pressure-testing it
- keeping overlapping ownership between adjacent skills
- duplicating shared protocol rules inline when a canonical reference already exists
- continuing after writing handoff state

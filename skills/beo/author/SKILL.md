---
name: beo-author
description: |
  Use when creating, revising, or pressure-testing beo skill definitions themselves. Author refines `SKILL.md` contracts, sharpens single-responsibility boundaries, removes overlap and hidden dependencies, and runs pressure tests before release. Do not use for feature delivery, repo onboarding, reference lookup, or any operational pipeline phase for product work.
---

> **HARD-GATE: SKILL-REPO-CONTEXT** — Author operates on beo skill definitions and their supporting references, not on feature-delivery artifacts.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-author

## Atomic purpose
Create, refine, and pressure-test beo skill definitions so the system stays coherent and non-overlapping.

## When to use
- a beo skill must be created or rewritten
- an existing beo skill shows overlap, ambiguity, or hidden dependency drift
- a beo skill definition needs structured pressure-testing before release

## Inputs
**Required**
- target skill change request
- existing `SKILL.md` contracts and any relevant local references
- pressure-test scenarios

**Optional**
- prior review findings or optimization notes about the target skill definitions

## Outputs
**Allowed writes**
- new or revised `SKILL.md` files
- pressure-test logs or creation logs defined by the local author references
- `.beads/STATE.json` only if this meta-work is being routed back through beo state
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- feature-delivery artifacts
- implementation code for product features
- onboarding bootstrap state except through `beo-onboard`

## Boundary rules
- Author owns beo skill-definition quality, not feature work.
- Author must not execute product-feature requirements, planning, validation, execution, review, debugging, or learning work.
- Author uses pressure tests to prove boundaries instead of compensating with vague instructions.

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

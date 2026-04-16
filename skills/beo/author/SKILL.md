---
name: beo-author
description: |
  Use when creating, revising, or pressure-testing beo skill definitions. Produces or refines SKILL.md contracts, enforces single-responsibility boundaries, and runs structured pressure tests before release. Do not use for feature pipeline work (requirements, planning, execution, review), repository onboarding (use beo-onboard), or modifying core pipeline skills without explicit user approval.
---

> **HARD-GATE: SKILL-REPO-CONTEXT** — Author operates within the beo-skills repository. It reads existing skills as reference, not as project artifacts.

> **Protocol References**: Protocol rules reference the `beo-reference` skill via `→ references/<file>` for canonical documents.

# beo-author

## Overview
**Atomic purpose: create, modify, or pressure-test beo skill definitions and supporting artifacts.** Create and validate beo skill definitions so the skill system stays coherent. **Core principle: every skill must have a single responsibility, explicit boundaries, and a tested template-compliant definition.**

## Boundary Rules
- **MUST NOT** perform independent state detection or free-form routing — owned by `beo-route`. May emit canonical handoff to the next allowed pipeline skill when exit conditions are met.
- **MUST NOT** gather feature requirements — owned by `beo-explore`.
- **MUST NOT** decompose feature work — owned by `beo-plan`.
- **MUST NOT** verify feature plans — owned by `beo-validate`.
- **MUST NOT** write feature code — owned by `beo-execute`.
- **MUST NOT** review feature implementations — owned by `beo-review`.
- **MUST NOT** capture feature learnings — owned by `beo-compound`.
- **MUST NOT** consolidate learnings — owned by `beo-dream`.
- **MUST NOT** diagnose feature failures — owned by `beo-debug`.
- **MUST NOT** bootstrap repositories — owned by `beo-onboard`.

## Hard Gates
> **HARD-GATE: CANONICAL-TEMPLATE** — Every skill produced or revised by author must include the canonical `SKILL.md` structural sections: hard gates, boundary rules, default loop, reference table, inputs/outputs, decision rubrics, failure recovery or equivalent recovery guidance, handoff, context budget, and red flags. Equivalent section names are acceptable; structural completeness is required.

> **HARD-GATE: PIPELINE-SKILL-APPROVAL** — Modifications to core pipeline skills (`route`, `explore`, `plan`, `validate`, `execute`, `swarm`, `review`, `compound`) require explicit user approval before applying changes.

> **HARD-GATE: PRESSURE-TEST-REQUIRED** — Every new or substantially modified skill must be pressure-tested with `references/pressure-test-template.md`. If pressure testing is incomplete, the skill is not ready.

> **HARD-GATE: NO-FEATURE-WORK** — Author never performs feature pipeline execution. If work moves into planning, coding, review, or project bootstrap, hand off to the responsible skill.

## Communication Standard
> Follow the communication standard (`beo-reference` → `references/communication-standard.md`).

## Default Author Loop
1. **Gather skill definition inputs** — Define the skill's single responsibility, its inputs and outputs using the repository's artifact layout, its place relative to the pipeline, and the boundaries it must enforce.
2. **Draft SKILL.md** — Write or rewrite the skill using the canonical template, including YAML frontmatter, overview, Does NOT Do, hard gates, communication standard, default loop, reference table, decision rubrics, handoff, context budget, and red flags.
3. **Pressure test** — Apply `references/pressure-test-template.md` to boundary violations, ambiguous requests, failure modes, and scope-creep scenarios, then record outcomes per `references/creation-log-template.md`.
4. **Refine** — Fix every failed scenario, ensure recovery behavior uses standard failure recovery (`beo-reference` → `references/failure-recovery.md`), and repeat until the skill passes.

### Reference Files
| File | Purpose |
|------|---------|
| `references/writing-skills-operations.md` | Defines the operational method for creating and revising beo skills |
| `references/creation-log-template.md` | Records authoring decisions, revisions, and pressure-test outcomes |
| `references/pressure-test-template.md` | Supplies structured scenarios for validating skill boundaries and failure handling |

## Inputs and Outputs
- **Inputs** — Target skill definition or change request, existing `SKILL.md` files and related skill contracts, canonical skill template requirements, pressure-test scenarios.
- **Outputs** — New or revised `SKILL.md`, pressure-test results logged via `references/creation-log-template.md`, integration guidance.

## Decision Rubrics
### New Skill vs Modify Existing
- **Create new** when no current skill cleanly owns the responsibility.
- **Modify existing** when the responsibility is already adjacent to or partially covered by an existing skill and can be clarified without overlap.

### Skill Boundary Clarity
- **Accept boundary** when Does NOT Do entries clearly hand work to adjacent skills with no ambiguous overlap.
- **Refine boundary** when two skills could both plausibly accept the same task.

### Pressure Severity
- **Block release** when a pressure test exposes a hard-gate failure, template deviation, or missing recovery path.
- **Document and monitor** when the scenario reveals a preference or caution that belongs in red flags rather than a hard gate.

## Special Rules
- Reference shared protocol docs from `beo-reference` rather than duplicating them inline. Each skill should be self-contained in its behavioral instructions but may cite shared references for protocol details.
- Keep state transitions aligned to the bead lifecycle states (`beo-reference` → `references/status-mapping.md`) and the canonical pipeline sequence (`beo-reference` → `references/pipeline-contracts.md`).
- Use the beo approval gates (`beo-reference` → `references/approval-gates.md`) when a skill definition introduces approval-sensitive behavior.
- Ensure every failure mode has a recovery route via standard failure recovery (`beo-reference` → `references/failure-recovery.md`).
- Preserve pipeline terminology exactly: `route → explore → plan → validate → (execute | swarm → execute) → review → compound`; support skills remain `debug` on-demand, `dream` periodic, `author` meta, and `onboard` bootstrap.

## Handoff
> Handoff to `beo-route` for next-action detection after authoring or pressure-testing completes. Write `STATE.json` for the normal transition, and reserve `HANDOFF.json` for emergency checkpoint or low-context resume scenarios.

## Context Budget
> If context exceeds 65% capacity, compress non-essential history before continuing (`beo-reference` → `references/shared-hard-gates.md`).

## Red Flags & Anti-Patterns
- Creating a skill without pressure testing it
- Producing a skill that overlaps another skill's responsibility or Does NOT Do boundary
- Deviating from the canonical `SKILL.md` template
- Letting author perform feature planning, implementation, or review work
- Embedding duplicated shared-reference content directly in the skill

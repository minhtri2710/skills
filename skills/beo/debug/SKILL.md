---
name: beo-debug
description: |
  Isolate one non-obvious blocker that is stopping execution or review, then apply the smallest verified unblock or route back with root-cause evidence. Use it only for concrete diagnosis-driven unblock work, not for normal feature implementation or general review.

---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-debug

## Atomic purpose
Diagnose one blocker and unblock it minimally.

## When to use
- execution or review is blocked by a failure that is not solvable through an obvious local retry
- the pipeline needs verified root-cause analysis before work can proceed
- a standalone request clearly targets a specific failure rather than open-ended feature delivery

## Inputs
**Required**
- failure or blocker identifier
- failure evidence such as logs, errors, comments, or reproduction state
- origin skill and return target when available
- relevant code and artifacts needed for diagnosis

**Optional**
- bead ID and current execution state
- existing debug history

## Outputs
**Allowed writes**
- root-cause determination
- minimal unblock fix when the issue is local and bounded
- verification evidence
- blocker or resolution comments
- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- feature redesign artifacts
- unrelated refactors or opportunistic cleanup
- review or learning artifacts

## Boundary rules
- Debug owns diagnosis-driven unblock work only.
- Debug must not absorb normal implementation work, redesign requirements or plans except by routing back with evidence, perform general quality review, or extract or consolidate learnings.
- Debug must preserve the correct return path to the originating skill.
- Debug must not continue once the blocker is resolved or escalated.

## Minimum hard gates
- **ORIGIN-TRACKING** — Preserve or recover the correct return target via the canonical state protocol.
- **MINIMAL-INTERVENTION** — Fix only what is needed to unblock the concrete failure.
- **VERIFICATION-REQUIRED** — Every claimed resolution needs proof.
- **THREE-CYCLE-LIMIT** — Do not loop indefinitely without a root-cause hypothesis or escalation decision.
- **TERMINATE-ON-HANDOFF** and **FRESH-LOAD-REQUIRED** — Follow the shared session-boundary rules.

## Default loop
1. Read the failure evidence, origin context, and relevant code paths.
2. Classify the failure using `references/diagnostic-checklist.md`.
3. Isolate the root cause.
4. If the issue is local and bounded, apply the minimal fix and verify it.
5. If the issue is structural or upstream, produce evidence-backed escalation and route through the canonical back-edge.
6. Write `.beads/STATE.json` for the correct return target and stop.

## References
| File | Use when |
|------|----------|
| `references/debugging-operations.md` | Running the diagnose → fix/escalate → verify flow |
| `references/diagnostic-checklist.md` | Classifying and isolating failure modes |
| `references/message-templates.md` | Writing blocker and resolution updates |
| `beo-reference` → `references/pipeline-contracts.md` | Choosing the correct back-edge when root cause is upstream |
| `beo-reference` → `references/failure-recovery.md` | Recovering interrupted or unresolvable debug sessions |

## Handoff and exit
- default return: origin skill from canonical state
- back-edge to `beo-plan` when the failure proves planning or scope is invalid
- return to `beo-review` or `beo-execute` when the unblock is verified and review / execution can resume
- Debug stops after writing handoff state.

## Context budget
If context exceeds 65%, checkpoint via the shared protocol in `beo-reference` → `references/shared-hard-gates.md`.

## Red flags
- doing feature work beyond the blocker
- losing origin / return information
- claiming success without verification evidence
- silently rewriting plan or scope during diagnosis
- continuing after writing inter-skill handoff state

---
name: beo-debug
description: |
  Use when a concrete blocker or failure is stopping execution or review and the cause is not obvious enough for execute’s local retry loop. Debug isolates root cause, applies the smallest unblock when appropriate, verifies the result, and returns control to the correct origin or upstream back-edge. Do not use for normal execution retries, requirements clarification, general quality review, or long-term learning synthesis.
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-debug

## Atomic purpose
Diagnose one non-obvious blocker and either unblock it minimally or route it back with verified evidence.

## When to use
- execute or swarm encountered a blocker that is not solvable via an obvious local retry
- review or execution needs a verified root-cause determination before the pipeline can proceed
- a standalone debug request clearly targets a specific failure rather than open-ended feature work

## Inputs
**Required**
- failure or blocker identifier
- failure evidence: logs, errors, comments, or reproduction state
- origin skill / return target from canonical state when available
- relevant code or artifacts needed to diagnose the issue

**Optional**
- bead ID and current execution status
- existing debug comments or prior failed attempts

## Outputs
**Allowed writes**
- minimal unblock fix when the issue is local and bounded
- verification evidence
- blocker / resolution comments
- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- feature redesign artifacts
- unrelated refactors or opportunistic cleanup
- review or learning artifacts

## Boundary rules
- Debug owns non-obvious diagnosis and minimal unblock work.
- Debug does not absorb normal execution work, planning, review, or learning capture.
- If the root cause invalidates upstream scope or planning, debug reports that and routes back; it does not silently redesign the work.

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

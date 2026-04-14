# Shared Hard Gates

Universal gates and protocols referenced by all beo skills. Skills point here instead of duplicating these blocks inline.

---

## Onboarding Check

<HARD-GATE>
If `.beads/onboarding.json` is missing or stale, stop and load `beo-using-beo` before continuing.
</HARD-GATE>

---

## Approval Verification

<HARD-GATE>
If the epic does not have the `approved` label, do not treat planning artifacts as implicit approval.
First verify the label was not accidentally removed or the wrong epic was selected.
If approval is genuinely missing, do not execute:
- if current-phase tasks have already advanced, treat approval as invalidated and route to `beo-planning`
- otherwise route to `beo-validating`
</HARD-GATE>

---

## Multi-Phase Completion Routing

If the planning mode is `multi-phase` and later phases remain after the current phase completes:
- Do not treat the feature as complete.
- Remove the `approved` label if present (`br label remove <EPIC_ID> -l approved`).
- Route back to `beo-planning` to prepare the next phase.
- Never describe current-phase completion as full feature completion when multi-phase work remains.

---

## Context Budget Protocol

If context usage exceeds **65%**, checkpoint state before continuing:

1. Write `.beads/STATE.json` and `.beads/HANDOFF.json` using the canonical schemas in `state-and-handoff-protocol.md`.
2. Include planning-aware fields (`planning_mode`, `has_phase_plan`, `current_phase`, `total_phases`, `phase_name`) when known.
3. Add the skill-specific checkpoint items listed in each skill's Context Budget section.
4. Resume from the checkpoint after context is restored.

Exception: `beo-using-beo` uses a **30%** threshold since it is a lightweight bootstrap skill.

---

## Shared References Convention

> **Shared references** — beo skills reference specific `beo-reference` docs by path. Do not co-load the full `beo-reference` skill; read individual reference docs as needed. Use `communication-standard.md` for structured findings output (validation, review, and debugging reports).

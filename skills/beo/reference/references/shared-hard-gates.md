# Shared Hard Gates

Shared gates used by all beo skills.

## Onboarding Check

<HARD-GATE>
If `br` or `bv` is unavailable, or `.beads/` bootstrap state is missing or stale, stop and load `beo-onboard`. `.beads/onboarding.json` may inform the check, including managed startup freshness, but it is never sufficient on its own and does not override managed `AGENTS.md` drift.

To verify `bv` is installed and callable without launching the TUI, use:
```bash
bv --version
```
Never invoke bare `bv` in agent sessions; it requires a TTY and will fail in non-interactive environments. For `bv` data queries, always use `--robot-*` flags with `--format json`.
</HARD-GATE>

## Approval Verification

<HARD-GATE>
If the epic does not have the `approved` label, do not treat planning artifacts as implicit approval.
First verify the label was not removed accidentally and the correct epic is selected.
If approval is genuinely missing:
- if current-phase tasks have already advanced, treat approval as invalidated and route to `beo-plan`
- otherwise route to `beo-validate`
</HARD-GATE>

## Multi-Phase Completion Routing

If the planning mode is `multi-phase` and later phases remain after the current phase completes:
- Do not treat the feature as complete.
- Remove the `approved` label if present (`br label remove <EPIC_ID> -l approved`).
- Route back to `beo-plan` to prepare the next phase.
- Never describe current-phase completion as full feature completion when multi-phase work remains.

## Context Budget Protocol

If context usage exceeds **65%**, checkpoint state before continuing:

1. Write `.beads/STATE.json` and `.beads/HANDOFF.json` using the canonical schemas in `state-and-handoff-protocol.md`.
2. Include planning-aware fields (`planning_mode`, `has_phase_plan`, `current_phase`, `total_phases`, `phase_name`) when known.
3. Add the skill-specific checkpoint items listed in each skill's Context Budget section.
4. Resume from the checkpoint after context is restored.

Exception: `beo-onboard` uses a **30%** threshold since it is a lightweight bootstrap skill.

## Session Boundary Protocol

<HARD-GATE>
**TERMINATE-ON-HANDOFF** — When a skill writes `STATE.json` or `HANDOFF.json` to hand off to another skill, it MUST immediately stop all work and yield control. The skill must not:
- Continue executing any pipeline work after writing the handoff artifact
- Load or begin the next skill in the same session context
- Write code, create beads, or produce artifacts belonging to downstream skills
- Interpret "hand off to skill-X" as "now do skill-X" — handoff means STOP

The next skill must be loaded fresh by `beo-route` or by the orchestrator loading the named skill explicitly. A skill that writes STATE.json and then continues working has violated session boundaries.
</HARD-GATE>

<HARD-GATE>
**FRESH-LOAD-REQUIRED** — Every skill must be loaded as a fresh invocation, not continued-into from the prior skill's session. If the current context contains another skill's active work (dialogue, decisions, implementation, review findings), the newly loaded skill must STOP and yield control so it can be started cleanly. Context from the prior skill is passed exclusively via `STATE.json`, `HANDOFF.json`, and persisted artifacts — never by inheriting the conversational session.

Each skill's inline FRESH-LOAD-REQUIRED gate names the most common predecessor to watch for, but the rule applies universally to all prior-skill contexts.
</HARD-GATE>

## User Interaction Protocol

When a skill needs a question, choice, or approval, it **must** use the runtime's canonical user-interaction mechanism. Prefer a structured question tool when available. Otherwise pause with `next: "user"` and ask an explicit yes/no or bounded-choice plain-text question. Never rely on silence or implied approval.

## Shared References Convention

Load only the specific `beo-reference` file needed for the current step. Do not co-load the full reference corpus. Use `communication-standard.md` for structured findings output.

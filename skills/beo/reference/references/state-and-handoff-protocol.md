# State and Handoff Protocol

Canonical protocol for writing, reading, and cleaning up `.beads/STATE.md` and `.beads/HANDOFF.json`.

## Why This Exists

The beo pipeline uses two state surfaces:
- `STATE.md` for normal adjacent-skill handoff
- `HANDOFF.json` for emergency checkpointing when context is running out or a session must resume later

All skills must use the same shapes and semantics.

## Core Rule

- `STATE.md` is the happy-path handoff between adjacent skills.
- `HANDOFF.json` is the emergency checkpoint that survives context resets.
- Router reads `HANDOFF.json` first on resume.
- Other skills read `STATE.md` from the predecessor skill.

## Canonical STATE.md Header

Every skill must write this header in this exact order:

```markdown
# Beo State
- Phase: <skill-name> → <status>
- Feature: <epic-id> (<feature-name>)
- Tasks: <summary relevant to current phase>
- Next: <next skill or action>
```

Skills may append phase-specific fields below a blank line.

## Canonical HANDOFF.json Base Schema

All fields below are required.

Note: `feature_name` is the historical field name, but in beo it carries the stable feature slug / artifact-path identifier, not a mutable display title.

```json
{
  "schema_version": 1,
  "phase": "<skill phase name>",
  "skill": "beo-<skill-name>",
  "feature": "<epic-id>",
  "feature_name": "<feature-slug>",
  "next_action": "<what to do next>",
  "in_flight_beads": ["<bead-ids>"],
  "timestamp": "<iso8601>"
}
```

Use `[]` when there are no in-flight beads.

## When To Write HANDOFF.json

Write `HANDOFF.json` when:
- context usage exceeds 65%
- a long-running orchestration must pause cleanly
- the session must checkpoint before continuation

Do not write it for normal phase-to-phase progression when `STATE.md` is sufficient.

## What To Include In A Checkpoint

In addition to the base fields, include phase-specific context such as:
- completed sub-steps
- pending dimensions/checks
- active workers
- open blockers
- locked decisions already captured
- resume instructions

Swarming may extend the top level with extra fields, but the base schema must remain intact.

## Resume Protocol

When `HANDOFF.json` exists:
1. read it before normal routing
2. verify the saved state is still valid against the live graph and current files
3. load the saved skill
4. follow `next_action`

## Cleanup Rule

Do not delete `HANDOFF.json` until the resumed skill has successfully written a fresh `STATE.md` or an equivalent new checkpoint.

Canonical cleanup command after successful resume:

```bash
rm .beads/HANDOFF.json
```

## Hard Rules

- Never skip `HANDOFF.json` if it exists.
- Never write non-canonical field names in the base schema.
- Never omit `feature_name` or `in_flight_beads`.
- Never delete `HANDOFF.json` before the resumed skill checkpoints safely.
- Never write a `STATE.md` missing the four canonical header fields.

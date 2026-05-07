# Status Mapping v2

## Bead state labels

| Bead state | Label | Meaning |
| --- | --- | --- |
| ready | none | eligible after approval |
| in_progress | reserved | execution marker; may coexist with `approved` |
| blocked | blocked | cannot continue |
| done | none | complete with evidence |
| approved | approved | bead is inside the current approval envelope; the label alone is not execution approval |

## STATE.json status vocabulary

Canonical `STATE.json.status` values are intentionally small:

| Status | Meaning |
| --- | --- |
| `active` | one feature is active and owned by `current_owner` |
| `blocked` | waiting on a Human Gate, access, secret, legal/business decision, or external constraint |
| `done` | no remaining legal action for the active feature |

Use `current_owner`, `current_phase`, readiness mirrors, and feature artifacts for workflow detail instead of expanding status into owner-specific labels.

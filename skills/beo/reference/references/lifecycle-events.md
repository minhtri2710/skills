# Lifecycle and Events

Beads owns the issue lifecycle. BEO records safety state, transitions, and non-normal events in `TICKET.md`.

## Atomic Path

Standard delivery: `beo-plan -> beo-validate -> beo-execute -> beo-review`.
The canonical transition list lives in `beo-reference -> registry/pipeline.json` and hard invariants in `beo-reference -> references/kernel.md`.

### 6-step Compact Protocol (Quick Mode)

For low-risk repository edits (README, docstrings, simple refactors):
1. **Show & Claim**: `br show <issue-id> --json` -> `br update --claim`.
2. **Intake**: Write minimal `TICKET.md` (request, done, atomic scope).
3. **Validate**: `beo-validate` grants `PASS_EXECUTE`.
4. **Execute**: `beo-execute` performs edits on the approved `scope.files.allow`.
5. **Review**: `beo-review` emits verdict.
6. **Close**: `br close <issue-id>` (only after review accept).

## Human Gates

Human Gates are user-owned decisions that BEO must not infer. Unresolved gates block approval.

### Types
- `clarification`, `choice`, `authorization`, `secret`, `execution_preview`, `external_side_effect_authorization`, `stateful_system_authorization`.

### Rules
- External side effects, stateful systems, cost, data, deployment, access, security, privacy, or irreversible actions require explicit authorization.
- When a gate blocks progress: append `runtime_events[]` kind `user_stop`, mark gate status `unresolved`, add a non-secret Beads comment, and apply `beo:blocked-user` label.

## Runtime Events

Events are append-only non-normal state in `TICKET.md`. Do not write events for normal happy-path transitions.

### Kinds
- `user_stop`, `handoff`, `return`, `change_request`, `abandon`, `learning_candidate`.

### Subtypes
- **Handoff/Return**: `debug` (to `beo-debug`), `recall` (to `beo-recall`).
- **Change Request**: `scope_delta`, `repair_same_scope`, `repair_rescope`.

## Labels

Labels are advisory hints. They never replace ticket fields or formal approval.

### Recommended Labels
- `beo:atomic`, `beo:quick`, `beo:standard`, `beo:strict`, `beo:blocked-user`, `beo:ready-review`.

## Repair and Learning

- **Repair**: Review never patches directly. `repair_same_scope` requires approval but uses unchanged boundaries: `scope.files.allow`, `generated_outputs`, `human_gates`, `acceptance_criteria`, `external_side_effects`, `stateful_external_systems`, `scope.files.forbid`, `scope.verify.commands`.
- **Learning**: Review or debug may emit `learning_candidate` hooks. Learning is control-plane work and never reopens delivery.

# Pipeline Contracts

Canonical definitions for cross-cutting pipeline protocols. All skills reference this file instead of embedding their own copies.

## Table of Contents

1. [State Routing Table](#state-routing-table)
2. [HANDOFF.json Schema](#handoffjson-schema)
3. [STATE.md Schema](#statemd-schema)
4. [Label Lifecycle](#label-lifecycle)
5. [Task Enumeration](#task-enumeration)
6. [Epic Lifecycle](#epic-lifecycle)
7. [Shared Artifact Write Rules](#shared-artifact-write-rules)

---

## State Routing Table

Evaluate **top-to-bottom, first match wins**. Earlier rows take priority.

| # | Condition | State | Route To |
|---|-----------|-------|----------|
| 1 | Any tasks have `blocked` or `failed` labels, debugging not yet attempted | **needs-debugging** | `beo-debugging` |
| 2 | Any tasks have `blocked` or `failed` labels, debugging attempted | **blocked** | Report blockers, ask user for decision |
| 3 | Epic exists, tasks exist, `approved` label on epic, all tasks open, ≤2 independent tasks | **ready-to-execute** | `beo-executing` |
| 4 | Epic exists, tasks exist, `approved` label on epic, all tasks open, 3+ independent tasks | **ready-to-swarm** | `beo-swarming` |
| 5 | Epic exists, tasks exist, some in_progress/closed (and no blocked/failed) | **executing** | `beo-executing` |
| 6 | Epic exists, tasks exist, no `approved` label, plan.md exists | **ready-to-validate** | `beo-validating` |
| 7 | Epic exists, tasks exist, no `approved` label, no plan.md | **planning** | `beo-planning` |
| 8 | Epic exists, no tasks, no `approved` label | **exploring** | `beo-exploring` |
| 9 | Epic exists, all tasks closed, epic still open | **ready-to-review** | `beo-reviewing` |
| 10 | Any tasks have `partial` or `cancelled` labels, epic still open | **partial-completion** | Report status, ask user for decision |
| 11 | Epic is closed | **completed** | Report status, ask for next work |
| 12 | All tasks closed, epic closed, no learnings file | **learnings-pending** | `beo-compounding` |
| 13 | Learnings stale, user requests consolidation | **consolidation-due** | `beo-dream` |
| 14 | Skill creation or editing requested | **meta-skill** | `beo-writing-skills` |

Key changes from prior versions:
- Row 6 adds `beo-validating` route (tasks exist + no `approved` + plan.md exists)
- Row 1-2 disambiguates blocked (debugging attempted vs not) — checked first
- Row 10 handles `partial`/`cancelled` labels explicitly
- Evaluation order is explicit: first match wins

---

## HANDOFF.json Schema

Canonical schema. All skills must use exactly these field names.

```json
{
  "schema_version": 1,
  "phase": "<skill phase name>",
  "skill": "beo/<skill-name>",
  "feature": "<epic-id>",
  "feature_name": "<feature-name>",
  "next_action": "<what to do next>",
  "in_flight_beads": ["<bead-ids>"],
  "timestamp": "<iso8601>"
}
```

**Required fields:** All fields above are required. Use `[]` for `in_flight_beads` when no beads are active.

**Field name:** `in_flight_beads` (NOT `beads_in_flight`).

**Swarming extension:** Swarming appends additional top-level keys (`session`, `swarm`, `graph_status`, `active_workers`, `open_blockers`, `resume_instructions`, `context_at_pause`) while preserving all base fields above. The base fields must still be present so the router can read them.

---

## STATE.md Schema

Canonical fields for `.beads/STATE.md`. All skills write these fields:

```markdown
# Beo State
- Phase: <skill-name> → <status>
- Feature: <epic-id> (<feature-name>)
- Tasks: <summary relevant to current phase>
- Next: <next skill or action>
```

Skills may add phase-specific fields below the canonical ones (e.g., compounding adds `Learnings file`, swarming adds `Active Workers`). The four fields above must always be present and in this order.

---

## Label Lifecycle

### `approved` Label

| Event | Action | Skill |
|-------|--------|-------|
| User approves plan | `br label add <EPIC_ID> -l approved` | validating |
| Back-edge to planning | `br label remove <EPIC_ID> -l approved` | executing, reviewing |
| Back-edge to exploring | `br label remove <EPIC_ID> -l approved` | validating, reviewing |

**Invariant:** The `approved` label must be removed whenever routing back to planning or exploring. This forces re-validation before execution resumes.

### Status Labels

| Label | Set By | Removed By |
|-------|--------|------------|
| `dispatch_prepared` | executing (Phase 2) | executing (Phase 2, after claim) |
| `blocked` | executing (blocker handling) | executing (stale label cleanup) |
| `failed` | executing (blocker handling) | executing (stale label cleanup) |
| `partial` | executing (partial completion) | executing (stale label cleanup) |
| `cancelled` | user decision | — |

---

## Task Enumeration

**Canonical command** to list tasks under an epic:

```bash
br dep list <EPIC_ID> --direction up --type parent-child --json
```

Do NOT use `jq 'select(.id | startswith(...))'`. The `startswith` pattern assumes dotted IDs and misses fix beads created with `--blocks` instead of `--parent`.

---

## Epic Lifecycle

| State | br Status | Label | Transition Command |
|-------|-----------|-------|--------------------|
| Planning | `open` | (none) | Default after `br create -t epic` |
| Approved | `open` | `approved` | `br label add <EPIC_ID> -l approved` |
| Executing | `in_progress` | `approved` | `br update <EPIC_ID> --claim` |
| Completed | `closed` | `approved` | `br close <EPIC_ID>` |

**Who transitions to executing:** The first skill that starts execution (executing or swarming) must run `br update <EPIC_ID> --claim` after the HARD-GATE passes.

**Router epic query:** Use `br list --type epic --json` (not `-s open`) to find all epics including `in_progress` ones. Filter in application logic.

---

## Shared Artifact Write Rules

### critical-patterns.md

- **Who writes:** Only `beo-compounding` proposes entries.
- **Approval required:** Compounding must present proposed promotions to the user and receive explicit approval before appending. Never auto-append.
- **Format:** See compounding's Phase 4 for entry format.
- **Aligned with:** dream (line 122: "Do not edit critical-patterns.md without explicit approval") and reviewing (red flag: "Promoting learnings without approval").

### Fix Beads (from debugging)

Fix beads must use BOTH `--parent` and `--blocks`:

```bash
br create "Fix: <root cause summary>" -t task --parent <EPIC_ID> --blocks <original-bead-id>
```

This ensures fix beads are:
1. Visible in epic task enumeration (via `--parent`)
2. Properly blocking the original bead (via `--blocks`)

### Task Creation During Validation

Validation may only create **spike beads** (time-boxed experiments, priority 0). Spikes are not implementation tasks — they are experiments to reduce uncertainty. For actual missing tasks, route back to `beo-planning`.

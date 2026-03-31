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
8. [Feature Slug](#feature-slug)

---

## State Routing Table

Evaluate **top-to-bottom, first match wins**. Earlier rows take priority.

| # | Condition | State | Route To |
|---|-----------|-------|----------|
| 1 | Skill creation or editing requested | **meta-skill** | `beo-writing-skills` |
| 2 | Any tasks have `blocked` or `failed` labels, `debug_attempted` label absent | **needs-debugging** | `beo-debugging` |
| 3 | Any tasks have `blocked` or `failed` labels, `debug_attempted` label present | **blocked** | Report blockers, ask user for decision |
| 4 | All tasks closed, epic closed, no learnings file | **learnings-pending** | `beo-compounding` |
| 5 | Epic is closed | **completed** | Report status, ask for next work |
| 6 | Any tasks have `partial` or `cancelled` labels, epic still open | **partial-completion** | Report status, ask user for decision |
| 7 | Epic exists, all tasks closed, epic still open | **ready-to-review** | `beo-reviewing` |
| 8 | Epic exists, tasks exist, some in_progress/closed (and no blocked/failed) | **executing** | `beo-executing` |
| 9 | Epic exists, tasks exist, `approved` label on epic, all tasks open, 3+ independent tasks | **ready-to-swarm** | `beo-swarming` |
| 10 | Epic exists, tasks exist, `approved` label on epic, all tasks open, ≤2 independent tasks | **ready-to-execute** | `beo-executing` |
| 11 | Epic exists, tasks exist, no `approved` label, phase-contract.md AND story-map.md exist | **ready-to-validate** | `beo-validating` |
| 12 | Epic exists, tasks exist, no `approved` label, phase-contract.md or story-map.md missing | **planning** | `beo-planning` |
| 13 | Epic exists, no tasks, no `approved` label | **exploring** | `beo-exploring` |
| 14 | Learnings stale (last dream run >30 days or 3+ new learnings since last dream), user requests consolidation | **consolidation-due** | `beo-dream` |

Key changes from prior versions:
- Row 1: explicit user intent (meta-skill, debug request) short-circuits feature-state routing
- Rows 2-3: `debug_attempted` label replaces ambiguous 'debugging attempted' — machine-decidable
- Rows 4-5: most-specific closed states evaluated before generic 'epic is closed'
- Row 7: ready-to-review evaluated before Row 8 (executing) to prevent shadowing
- Row 14: staleness threshold defined: last dream run >30 days or 3+ new learnings files since last dream

### Planning Artifact Hierarchy

The planning phase produces five artifacts in this order:

| Artifact | Role | Gate-Controlling |
|----------|------|-----------------|
| `CONTEXT.md` | Locked decisions — source of truth | Yes (exploring → planning gate) |
| `discovery.md` | Research findings from parallel subagents | No |
| `plan.md` | High-level approach summary | No (compatibility artifact) |
| `phase-contract.md` | Phase as closed loop: entry/exit state, demo, scope | Yes (planning → validating gate) |
| `story-map.md` | Story sequence, closure check, story-to-bead mapping | Yes (planning → validating gate) |

The validation gate requires `phase-contract.md` AND `story-map.md`. `plan.md` is read by downstream skills but does not control routing.

---

## HANDOFF.json Schema

Canonical schema. All skills must use exactly these field names.

```json
{
  "schema_version": 1,
  "phase": "<skill phase name>",
  "skill": "beo-<skill-name>",
  "feature": "<epic-id>",
  "feature_name": "<feature-name>",
  "next_action": "<what to do next>",
  "in_flight_beads": ["<bead-ids>"],
  "timestamp": "<iso8601>"
}
```

**Required fields:** All fields above are required (`schema_version`, `phase`, `skill`, `feature`, `feature_name`, `next_action`, `in_flight_beads`, `timestamp`). Use `[]` for `in_flight_beads` when no beads are active.

**Field name:** `in_flight_beads` (NOT `beads_in_flight`).

**Swarming extension:** Swarming appends additional top-level keys (`session`, `swarm`, `graph_status`, `active_workers`, `open_blockers`, `resume_instructions`, `context_at_pause`) while preserving all base fields above. The base fields must still be present so the router can read them.

---

## STATE.md Schema

Canonical fields for `.beads/STATE.md`. All skills write these fields.

The header below is REQUIRED in this exact format:

```markdown
# Beo State
- Phase: <skill-name> → <status>
- Feature: <epic-id> (<feature-name>)
- Tasks: <summary relevant to current phase>
- Next: <next skill or action>
```

Skills may add phase-specific fields below the canonical header (separated by a blank line), but the four fields above must always be present and in this order. Examples of phase-specific fields: `Decisions` (exploring), `Dependencies` (planning), `Approval` (validating), `Active Workers` (swarming).

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
| `debug_attempted` | beo-debugging (Step 5) | beo-executing (on unblock) |

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

**Who transitions to executing:** The first skill that starts execution (executing or swarming) must run `br update <EPIC_ID> --claim` before dispatching any workers.

**Router epic query:** Use `br list --type epic -a --json` to find all epics including `in_progress` and `closed` ones. Filter in application logic.

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

---

## Feature Slug

Every feature gets an immutable `feature_slug` created once by the router and used for all artifact paths.

**Rules:**
- Derived from the epic title at creation time
- Lowercase, hyphens only, max 40 chars: `auth-token-refresh`, `bead-scope-isolation`
- Stored in: epic bead description (first line: `slug: <feature_slug>`), HANDOFF.json (`feature_name` field), STATE.md (`Feature` field)
- Used for: `.beads/artifacts/<feature-name>/` path, learnings file slug component

**Canonical derivation:**
1. Take the epic title
2. Lowercase
3. Replace spaces and underscores with hyphens
4. Remove all non-alphanumeric-hyphen characters
5. Collapse consecutive hyphens
6. Truncate to 40 characters
7. Remove trailing hyphens

Once set, the slug never changes — even if the epic title is updated later.

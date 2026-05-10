# BEO Setup Operations

Role: APPENDIX
Allowed content only: setup/check procedure, setup modes, usage explanation
Forbidden content: owner selection, approval authority, review verdict authority, routing topology, writable-surface expansion

This is setup/check/usage guidance only (SETUP-01). It does not create runtime authority and must not create `.beads`, feature artifacts, approval, execution evidence, review verdicts, debug findings, or learning records (SETUP-02).

## Setup/check procedure

### 1. Read the quick map

Read `operator-card.md` as usage guidance only. It does not grant authority.

### 2. Check `AGENTS.md`

Inspect project root `AGENTS.md` and classify it:

| Status | Meaning | Action |
| --- | --- | --- |
| `missing_agents` | `AGENTS.md` does not exist | Create from managed template only in apply mode. |
| `missing_managed_block` | `AGENTS.md` exists without BEO managed markers | Append managed block only in apply mode. |
| `valid_managed_block` | Exactly one valid BEO managed block exists | Do not edit. |
| `malformed_managed_block` | Duplicated, nested, missing one side, or ambiguous markers | Stop and ask the user before editing. |

Managed block source: `skills/beo/reference/assets/AGENTS.template.md`.

### 3. Check runtime orientation surfaces

Read-only check only:

- `.beads/STATE.json` if present (STATE-01: display-only).
- `.beads/HANDOFF.json` only when resuming paused or transferred work.
- Tiny: `TICKET.md`. Standard: `CONTEXT.md`, `PLAN.md`, `TRACKER.json`, `REVIEW.md`.

If no `.beads` exists, report no active BEO runtime state and do not create it (SETUP-02). If multiple active feature candidates appear, report that user selection or `beo-route` is needed (STATE-02).

### 4. Produce setup card

```md
Decision:
Setup status:
AGENTS.md status:
Runtime state status: current surfaces present | current surfaces missing | no current runtime state | ambiguous current owner/feature identity
Active feature:
Current owner:
Issues found:
Changed surfaces:
Recommended next step:
Authority note: setup output is advisory only (SETUP-01).
```

## Setup modes

**Check-only:** may read setup surfaces and explain usage. Must not write files.

**Apply mode:** may create `AGENTS.md` from managed template, append missing managed block, or leave valid block unchanged. Must not edit malformed/duplicated blocks without user confirmation. Must not create `.beads` or feature artifacts (SETUP-02).

## Usage explanation

Shortest normal path:

`beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done`

Route only when owner/feature identity is unsafe (ROUTE-01). Debug only for unproven root cause. Compound records one observed learning case. Dream consolidates repeated finalized cases. Author edits skills only when explicitly requested or selected. Reference only for canonical lookup.

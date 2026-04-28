# execution-operations

Role: APPENDIX
Allowed content only: claim / dispatch / complete command sequence for an already-selected bead; no approval or routing rules

## Claim command forms

| Purpose | Command form |
| --- | --- |
| claim selected bead | `br update <id> --status in_progress --label reserved --no-daemon` |
| record execution comment | `br comments add <id> --message <text> --no-daemon` |
| mark blocked | `br update <id> --status blocked --label blocked --no-daemon` |
| mark done | `br update <id> --status done --no-daemon` |
| flush bead DB | `br sync --flush-only` |

## Linear steps

| Step | Action |
| --- | --- |
| 1 | Confirm owner has already been selected as `beo-execute`. |
| 2 | Confirm exactly one selected bead id is present in trusted route or state evidence. |
| 3 | Confirm `STATE.json` approval reference matches the live `approval-record.json`. |
| 4 | Confirm working tree is clean for in-scope files or record pre-existing dirty paths before mutation. |
| 5 | Confirm selected bead file scope is fully inside the explicit approved scope from `approval-record.json`. |
| 6 | Claim the bead and record reservation evidence. |
| 7 | Implement only inside the selected bead's declared file scope. |
| 8 | Run verification commands from the bead description or explicit approved verification commands. For structural changes (file moves, routing restructure, import-primitive migration), search all consuming directories for stale old import or route patterns before completion. |
| 9 | Record changed files, verification commands, outputs, and approval reference in `.beads/artifacts/<feature_slug>/execution-bundle.json`. |
| 10 | Mark the bead done when verification passes, or blocked when progress stops safely. |
| 11 | Run `br sync --flush-only` after bead DB mutations. |
| 12 | Update `STATE.json` with status/evidence and next owner evidence. |

Routing, approval law, and scope law remain canonical in `beo-execute`, `beo-references -> approval.md`, and `beo-references -> artifacts.md`.

## Dirty worktree and concurrent work policy

- If an in-scope file is already dirty before execution and the current owner did not create that diff, stop and route to `user` or `beo-plan`; do not merge unowned work by assumption.
- If an out-of-scope file is dirty, do not touch it; record it as pre-existing state only.
- Pre-existing dirty generated files must not be claimed as outputs of the current bead.
- When execution proceeds with recorded pre-existing dirty paths, execution evidence must distinguish pre-existing diffs from current-bead changes.

## Generated side-effect policy

- Generated files may change only when explicitly listed in bead file scope, listed under approved generated outputs, or deterministically updated by a verification command with recorded evidence.
- Unexpected generated changes outside scope require stopping and routing to `beo-plan` or `user`.
- Lockfile changes require explicit dependency-change approval.
- Snapshot changes require acceptance evidence that the UI or output change is intended.
- Formatting changes outside approved file scope are scope violations unless the bead explicitly allows them.

## Execution bundle minimum fields

Write the canonical execution bundle to `.beads/artifacts/<feature_slug>/execution-bundle.json` with at least:
- `feature_slug`
- `approval_ref`
- `executed_beads`
- `changed_files`
- `generated_files`
- `verification`
- `scope_respected`
- `out_of_scope_changes`
- `blockers`
- `ready_for_review`

## Exit evidence

Use this appendix to name the evidence that `beo-execute` should emit; owner routing remains canonical in `beo-execute`.

| Exit shape | Required evidence |
| --- | --- |
| review-ready | changed files, verification evidence, approval reference, completed bead id, execution bundle ref |
| debug-needed | failing command, smallest repro, why root cause is unproven |
| plan-needed | contract or bead graph mismatch that cannot be fixed inside approved scope |
| validate-needed | approval became stale before mutation and no product mutation occurred |
| user-needed | external blocker or required clarification |

Non-normative completion comment:

```text
Execution complete for <bead-id>. Changed files: <paths>. Verification: <commands and result>. Approval: <approval_ref>.
```

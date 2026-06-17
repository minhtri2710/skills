# BEO Command Manifest

> [!NOTE]
> This reference is subordinate to `references/kernel.md`. It enumerates the outbound surface of the BEO helper scripts in `beo-reference/scripts/` so operators can find the right helper without reading every skill card. It does not grant authority — the active skill card still owns the phase.

This file is the machine-and-human-readable manifest. `beo_audit.py --check-manifest` verifies that every script in `scripts/` appears in this table. Adding a script without updating this file is a drift finding.

## Conventions

- `main arg` columns show the most common arg shape. `[]` means no arg, `[--root .]` is the default root, etc.
- `output shape` is one of: `json` (machine-readable JSON to stdout), `markdown` (rendered report to stdout), `none` (side effects only).
- `exit code` follows the BEO contract: `0` success, `1` validation/business failure, `2` refusal/refuse-state.

## Manifest table

| Command | Main args | Responsibility | Output shape | Exit codes |
| --- | --- | --- | --- | --- |
| `beo_approval.py` | imported by other scripts | Approval | none (library) | n/a |
| `beo_audit.py` | `[--check-manifest] [--root .] [--json]` | Audit | markdown or json | 0, 1 |
| `beo_check.py` | `--check <name> --issue <id> [--root .]` | Validation | json | 0, 1 |
| `beo_check_approval.py` | imported | Approval | none (library) | n/a |
| `beo_check_events.py` | imported | Validation | none (library) | n/a |
| `beo_check_identity.py` | imported | Validation | none (library) | n/a |
| `beo_check_scope.py` | imported | Scope | none (library) | n/a |
| `beo_git.py` | imported | Isolation | none (library) | n/a |
| `beo_io.py` | imported | (utility) | none (library) | n/a |
| `beo_memory_tools.py` | imported | Memory | none (library) | n/a |
| `beo_memory_write.py` | `beo_memory_write.py <vault> <note-path>` | Memory | json | 0, 1, 2 |
| `beo_paths.py` | imported | Scope | none (library) | n/a |
| `beo_propose.py` | `[--root .]` | Audit | json | 0, 1 |
| `beo_quick_fill.py` | `beo_quick_fill.py --issue <id> [--root .]` | Validation | json | 0, 1, 2 |
| `beo_recall.py` | `beo_recall.py <query> [--root .]` | Memory | json | 0, 1 |
| `beo_reservation.py` | subcommand-driven | Reservation | json | 0, 1, 2 |
| `beo_run.py` | `beo_run.py --issue <id> [--root .]` | (orchestrator) | mixed | 0, 1, 2 |
| `beo_score_context.py` | `--issue <id> [--root .]` | Scoring | json | 0, 1, 2 |
| `beo_score_trace.py` | `--issue <id> [--root .]` | Scoring | json | 0, 1, 2 |
| `beo_setup.py` | `beo_setup.py [--check]` | Setup | json | 0, 1, 2 |
| `beo_state.py` | imported | (state) | none (library) | n/a |
| `beo_ticket.py` | imported | Validation | none (library) | n/a |
| `beo_verify.py` | `run --issue <id> [--root .]` or `--all` | Verification | json | 0, 1, 2 |
| `beo_worktree.py` | subcommand-driven | Isolation | json | 0, 1, 2 |
| `check_skill_bundle.py` | `check_skill_bundle.py` | Validation | markdown | 0, 1 |

## Responsibility classes

- **Validation**: checks tickets, state, approval, identity, scope
- **Scope**: path safety, glob matching, protected paths
- **Approval**: PASS_EXECUTE projection, validity predicates
- **Reservation**: strict-mode path ownership evidence
- **Isolation**: git worktree lifecycle
- **Setup**: environment readiness, AGENTS.md bootstrap
- **Memory**: qmd/Obsidian integration, recall, learning writes
- **Scoring**: trace and context quality (advisory)
- **Verification**: runs TICKET.yaml scope verify commands (machine-enforced)
- **Audit**: drift checks (C1–C7), proposal generation (advisory)

## Operator question → helper

| Question | Helper |
| --- | --- |
| Is approval still valid? | `beo_approval.py` (via `beo_check.py --check validate`) |
| Are file paths safe? | `beo_paths.py` (via `beo_check.py --check validate`) |
| Can I claim/close/decompose via br? | `beo_run.py` |
| What does the state look like? | `beo_state.py` (via `beo_check.py --check status`) |
| Is the worktree ready? | `beo_worktree.py status` |
| Is the bead well-traced? | `beo_score_trace.py` |
| Is context coverage good? | `beo_score_context.py` |
| Did the verify commands pass? | `beo_verify.py` |
| Are skill cards and registries consistent? | `check_skill_bundle.py` or `beo_audit.py` |
| What's missing from this delivery? | `beo_propose.py` |

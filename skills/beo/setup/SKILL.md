---
name: beo-setup
description: Run health checks, compatibility verification, or configure authorized memory/qmd/Obsidian indexing for BEO. Always use this skill when verifying environment status or setting up tooling. Trigger this when the user says "check BEO health", "setup qmd", "is br working?", or "verify my setup."
---
# beo-setup

## Use when

The user asks to install, verify, configure, or health-check BEO tooling rather than execute a delivery issue.

## Read

- The requested setup or maintenance action.
- Current `br`, `bv`, qmd, Obsidian CLI, vault, and environment capability output.
- `beo-reference` canonical contracts: `references/kernel.md`, `references/memory.md`, `references/degraded-tools.md`, `registry/command-contracts.json`, and setup-relevant registry entries.
- Compatibility helper output from `beo-reference` -> `scripts/beo_setup_compat.py` for structured tool status.
- Existing setup evidence when checking drift from a previous configuration.

## Do

1. Default to read-only checks for required and optional tools via `beo_setup_compat.py`.
2. Verify `br` issue lifecycle and claim capabilities before declaring BEO usable.
3. Verify `bv` robot command availability without opening the TUI.
4. Treat missing `bv`, qmd, or Obsidian support as degraded; report workflow readiness state (blocked/degraded/ready) per degraded-tools guidance.
5. Require explicit user authorization before memory setup, qmd index mutation, vault writes, or other setup writes.
6. Treat setup qmd/Obsidian writes as memory maintenance only; they never create delivery authority.
7. Report required ok/missing, optional degraded, and memory fallback status with operator guidance.

## Write

- Setup-owned capability evidence and reports.
- Authorized memory/qmd/Obsidian configuration or index maintenance only when explicitly requested.
- No delivery artifacts unless the request is itself an authorized setup maintenance bead.

## Emit

- `setup_complete` -> stop.
- `user_confirmation_needed` -> stop for user confirmation.

## Never

- Do not participate in normal plan/validate/execute/review delivery.
- Do not mutate product files.
- Do not grant approvals, review verdicts, or issue closure.
- Do not run qmd/Obsidian writes without explicit setup or memory-maintenance authorization.
- Do not load BEO delivery skills to continue work after setup emits; stop first.

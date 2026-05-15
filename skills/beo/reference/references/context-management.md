# Context Management

Authority: canonical context-loss survival rules.

Runtime authority comes from disk artifacts, not chat memory. Summaries are advisory only. Long command output should be stored as observation refs, with secret-sensitive output redacted or excluded.

After context loss, normal resume uses `references/resume-resolution.md` for read-only owner orientation from current artifacts. Read `.beads/STATE.json` and `HANDOFF.json` only as mirrors to locate and compare current artifact evidence. If owner/feature identity is missing, stale, contradictory, colliding, or unsafe, use `beo-route`; do not resume by guess.

Startup/resume reads `FEATURE.json`, required artifacts for the active density, advisory `.beads/STATE.json`, `HANDOFF.json`, and `registry/pipeline.json` before acting. Full density reads `TRACKER.json` when present; compact density resumes from `TICKET.md#Execution` evidence instead. Review assesses ledger observations against acceptance criteria rather than relying on executor narrative.

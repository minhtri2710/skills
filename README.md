# BEO Skills

BEO is a repo-local Agent Skills package for safe Beads-backed delivery.

Normal path:

```text
beo-plan -> beo-validate -> beo-execute -> beo-review
```

Conditional support:

```text
beo-debug     read-only blocker diagnosis
beo-learn     optional high-signal advisory memory write
beo-author    BEO workflow maintenance
beo-setup     setup and degraded-tool checks
beo-reference read-only lookup
```

Authority:

- `br` owns issue lifecycle, claims, dependencies, comments, and closure.
- `bv` is read-only graph orientation only.
- `TICKET.json` owns request, done criteria, approved scope, verification commands, and risk/strict contracts.
- `state.json` owns approval, execution, and review state.
- `runtime-events.jsonl` is optional and records only non-normal events.
- `qmd` and Obsidian are advisory memory only.

Requirements:

- `br` is required.
- A git worktree is required for delivery containment.
- PyYAML is required for helper artifact parsing.
- `bv`, qmd, and Obsidian are optional degraded tools.

No legacy compatibility: BEO accepts only current `version: 1` artifacts.

Useful checks:

```bash
rtk python3 -m compileall skills/beo/beo-reference/scripts
rtk python3 -m unittest discover -s tests -v
rtk git diff --check
```

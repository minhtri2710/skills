# BEO Skills

Agent Skills bundle. BEO, a repo-local package for safe Beads-backed delivery, lives under `skills/beo/`; standalone skills live beside it under `skills/`.

## BEO

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
- Python 3 standard library only; no third-party packages.
- Git worktree isolation is optional and used only by strict mode.
- `bv`, qmd, and Obsidian are optional degraded tools.

No legacy compatibility: BEO accepts only current `version: 1` artifacts.

## Standalone skills

| Skill | Use |
| --- | --- |
| `architecture-premise-audit` | Audit a whole project for a wrong system archetype before trusting repository vocabulary. |
| `frontend-design` | Implement a UI change whose rendered hierarchy, flow, or responsive behavior is part of acceptance. |
| `herdr-delivery-workflow` | Control Herdr and run bounded delivery with the Supervisor / Lead / Peer role model. |
| `prompt-leverage` | Strengthen a raw prompt into an execution-ready instruction set. |
| `repo-refresh` | Remove stale docs, plans, tests, proof machinery, and debris from an explicitly named repository. |
| `test-proof-debt-audit` | Audit one behavioral claim and the test or gate cited as its proof. |
| `ultra-review` | Run a maximum-recall parallel bug hunt and keep every candidate in a report under `docs/ultrareview/`. |
| `ultra-review-receive` | Verify and disposition every ultra-review finding, then apply only authorized fixes. |

## Useful checks

```bash
.venv/bin/python -m unittest discover -s tests
.venv/bin/python skills/beo/beo-reference/scripts/check_skill_bundle.py
.venv/bin/python skills/beo/beo-reference/scripts/beo_audit.py --check-manifest --json [--learning-repo <product-repo>]
git diff --check
```

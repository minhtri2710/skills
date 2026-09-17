# Agent Skills

This repository contains standalone Agent Skills. Each retained skill lives under `skills/<name>/` with its `SKILL.md` contract and any supporting references, templates, or scripts.

## Standalone skills

| Skill | Use |
| --- | --- |
| `architecture-premise-audit` | Audit a whole project for a wrong system archetype before trusting repository vocabulary. |
| `frontend-design` | Implement a UI change whose rendered hierarchy, flow, or responsive behavior is part of acceptance. |
| `herdr-delivery-workflow` | Control Herdr and run bounded delivery with the Supervisor / Lead / Peer role model. |
| `prompt-leverage` | Strengthen a raw prompt into an execution-ready instruction set. |
| `repo-refresh` | Remove stale docs, plans, tests, proof machinery, and debris from an explicitly named repository. |
| `test-proof-debt-audit` | Audit one behavioral claim and the test or gate cited as its proof. |

## Checks

```bash
.venv/bin/python -m unittest discover -s tests
git diff --check
```

# Agent Skills repository

This repository contains standalone Agent Skills. The canonical inventory is in `README.md`; each skill owns its `skills/<name>/SKILL.md` contract and supporting files.

## Repository structure

- `skills/*/SKILL.md` — standalone skill contracts.
- `skills/*/references/`, `templates/`, and `scripts/` — skill-owned supporting material where present.
- `tests/` — repository checks.

## Working rules

- Keep changes within the owning skill or explicitly requested repository scope.
- Treat each skill's `SKILL.md` as the contract for that skill.
- Use the repository's current checks before reporting a change complete.

## Checks

The suite needs Python 3.11 or newer; if `python3` resolves older, use a 3.11+ interpreter in its place.

```bash
python3 -c 'import sys; assert sys.version_info >= (3, 11), sys.version' && python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests
git diff --check
```

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

These commands are the repository's CI of record; there is no hosted CI. A change is complete only when they pass.

On Linux, `test_floor_guard` and `test_gate_row` run scripts under `LC_ALL=en_US.ISO8859-1`, which needs that locale; on Debian or Ubuntu, first run `sudo apt-get update && sudo apt-get install -y locales`, then `sudo localedef -i en_US -f ISO-8859-1 en_US.ISO8859-1`.

```bash
python3 -c 'import sys; sys.exit(sys.version_info < (3, 11) and sys.version)' && python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests
git diff --check
```

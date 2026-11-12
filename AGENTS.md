# Agent Skills repository

This repository contains standalone Agent Skills. The canonical inventory is in `README.md`; each skill owns its `skills/<name>/SKILL.md` contract and supporting files.

## Repository structure

- `skills/*/SKILL.md` — standalone skill contracts.
- `skills/*/references/`, `templates/`, and `scripts/` — skill-owned supporting material where present.
- `hooks/` — Claude Code hook scripts, installed by hand into `~/.claude/hooks`; `hooks/README.md` says which.
- `tests/` — repository checks.

## Working rules

- Keep changes within the owning skill or explicitly requested repository scope.
- Treat each skill's `SKILL.md` as the contract for that skill.
- Use the repository's current checks before reporting a change complete.

## Checks

The suite needs Python 3.11 or newer; if `python3` resolves older, use a 3.11+ interpreter in its place.

These commands are the repository's CI of record; there is no hosted CI. A change is complete only when they pass.

On Linux, tests that run a script under a non-UTF-8 `LC_ALL` (such as `en_US.ISO8859-1`) need that locale installed; on Debian or Ubuntu, first run `sudo apt-get update && sudo apt-get install -y locales`, then `sudo localedef -i en_US -f ISO-8859-1 en_US.ISO8859-1`.

```bash
python3 -c 'import sys; sys.exit(sys.version_info < (3, 11) and sys.version)' && python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests
git diff --check
```

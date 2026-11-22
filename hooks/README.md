# Hooks

Claude Code hook scripts, installed by hand into `~/.claude/hooks` and wired in `~/.claude/settings.json`. Nothing here installs itself.

- `check-secret-names.sh` and `strip-secrets.sh` are the secret guards. After installation, run [`test-env-guards.sh`](test-env-guards.sh) to check `$HOME/.claude/hooks/strip-secrets.sh` using fake values. This manual check does not run in the Python suite.
- `herdr-agent-state.sh`: herdr owns updates to this file. The copy here is a snapshot; do not reinstall it over a newer herdr version.
- `block-glob-delete.py`: PreToolUse Bash hook that refuses rm/mv/find -delete/xargs rm on a glob, an unquoted expansion, or the shared `/tmp` top level. A guard against mistakes, not a security boundary.
- `session-tmpdir.py`: SessionStart `start` / SessionEnd `end` hook that gives each session its own `TMPDIR`.
- Tests for the last two: `tests/test_hooks.py`.

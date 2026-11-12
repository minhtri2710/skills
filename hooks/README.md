# Hooks

Claude Code hook scripts, installed by hand into `~/.claude/hooks` and wired in `~/.claude/settings.json`. Nothing here installs itself.

- `block-env-dump.sh`, `check-secret-names.sh`, `strip-secrets.sh`, `test-env-guards.sh`: the secret guards, copied unchanged from the installed files. `test-env-guards.sh` checks the installed copies (it hard-codes `~/.claude/hooks`), so it is a manual check after an install, not part of `tests/`.
- `herdr-agent-state.sh`: herdr owns updates to this file. The copy here is a snapshot; do not reinstall it over a newer herdr version.
- `block-glob-delete.py`: PreToolUse Bash hook that refuses rm/mv/find -delete/xargs rm on a glob, an unquoted expansion, or the shared `/tmp` top level. A guard against mistakes, not a security boundary.
- `session-tmpdir.py`: SessionStart `start` / SessionEnd `end` hook that gives each session its own `TMPDIR`.
- Tests for the last two: `tests/test_hooks.py`.

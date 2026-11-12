#!/bin/sh
# CLAUDE_CODE_SHELL_PREFIX target. Claude Code runs every Bash tool command and
# every hook as `strip-secrets.sh '<command string>'`; this drops the secret
# names from that command's environment (proposal:
# ~/.paseo/reports/supervisor/env-secret-hardening-2026-11-06.md).
# ponytail: /bin/zsh is the shell Claude Code picks on this Mac (SHELL=/bin/zsh); change it if SHELL changes.
if [ "$#" -eq 1 ]; then
  set -- /bin/zsh -c "$1"
fi
exec /usr/bin/env -u TYPESAFE_API_KEY -u EXA_API_KEY -u ANTHROPIC_AUTH_TOKEN -u CLAUDE_CODE_MESSAGING_TOKEN "$@"

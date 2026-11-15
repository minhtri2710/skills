#!/bin/sh
# Runnable check for strip-secrets.sh. Uses fake values only.
H=/Users/beowulf/.claude/hooks
fail=0

# strip-secrets.sh: string form (how Claude Code calls it) and argv form; fake values only.
out=$(/usr/bin/env TYPESAFE_API_KEY=fake EXA_API_KEY=fake ANTHROPIC_AUTH_TOKEN=fake CLAUDE_CODE_MESSAGING_TOKEN=fake KEEP_ME=kept \
  "$H/strip-secrets.sh" 'for n in TYPESAFE_API_KEY EXA_API_KEY ANTHROPIC_AUTH_TOKEN CLAUDE_CODE_MESSAGING_TOKEN; do [ -n "${(P)n+x}" ] && echo "$n present"; done; echo "KEEP_ME=$KEEP_ME"; exit 7')
rc=$?
[ "$out" = "KEEP_ME=kept" ] || { echo "FAIL strip string form: $out"; fail=1; }
[ "$rc" -eq 7 ] || { echo "FAIL strip exit code: $rc"; fail=1; }
out=$(/usr/bin/env TYPESAFE_API_KEY=fake "$H/strip-secrets.sh" /bin/sh -c '[ -n "${TYPESAFE_API_KEY+x}" ] && echo present || echo absent')
[ "$out" = "absent" ] || { echo "FAIL strip argv form: $out"; fail=1; }

[ "$fail" -eq 0 ] && echo "env guards: all checks passed"
exit "$fail"

#!/bin/sh
# Runnable check for strip-secrets.sh and block-env-dump.sh. Uses fake values only.
H=/Users/beowulf/.claude/hooks
fail=0

hook() { # $1 = expected exit (0 allow, 2 block), $2 = command
  printf '%s' "$2" | /usr/bin/jq -Rs '{tool_name:"Bash",tool_input:{command:.}}' | "${HOOK:-$H/block-env-dump.sh}" 2>/dev/null
  got=$?
  if [ "$got" -ne "$1" ]; then echo "FAIL hook want=$1 got=$got: $2"; fail=1; fi
}

for c in '$=' 'print -l $=' 'env' 'env | sort' '/usr/bin/env' 'x && env' 'env -0' 'printenv' 'printenv HOME' \
  'set' 'set | grep A' 'export' 'export -p' 'declare -x' 'typeset -x' 'typeset' 'declare -p' 'ps eww' 'ps auxe' \
  'ps -E' 'ps -p 1 -E' 'cat /proc/1/environ' "python3 -c 'import os; print(os.environ)'" \
  "python3 -c 'import os; print(os.environ.items())'" "node -e 'console.log(process.env)'" \
  "node -e 'console.log(Object.keys(process.env))'" "node -e 'JSON.stringify(process.env)'" \
  'security find-generic-password -s x -w' 'cat ~/.config/fish/private.fish' 'cat ~/.claude/settings.json' \
  'grep TOKEN /Users/beowulf/.claude/settings.json' 'cat ~/.paseo/agents/a/b.json' 'echo $(env)' \
  'x || env' 'ls | env' '{ set; }' 'a; export' 'env |sort' 'cmd ${=args}' 'print -l ${=}' 'od -c ~/.claude/settings.json' 'x; tail ~/.claude/settings.local.json' '(export)' 'a=$(env)' '(set) > f'; do
  hook 2 "$c"
done

for c in 'ls -la' 'env -u FOO -u BAR go test ./...' 'env -i PATH=/usr/bin /bin/sh -c true' 'set -euo pipefail' \
  'set -e; make' 'export FOO=1' 'ps -o pid=,comm= -p 123' 'ps aux' 'git status' 'echo environment' \
  "python3 -c 'import os; print(os.environ.get(\"HOME\"))'" "python3 -c 'import os; os.environ[\"X\"]=\"1\"'" \
  "node -e 'console.log(process.env.HOME)'" "node -e 'spawn(c, {env: {...process.env, X: 1}})'" \
  'jq -r "keys[]" ~/.claude/settings.json' 'go version -m ~/.local/bin/munsu' 'unset FOO' 'typeset -i n=1' \
  'echo $HOME' 'sed -n 1,5p README.md' 'gh pr merge 1 --squash' 'echo ${x:=1} ${#y}' \
  'chmod 600 /Users/beowulf/.claude/settings.json' \
  "grep -oE \"^(export )?(function|const) [A-Za-z_]+\" match.ts" "rg '(set)?Value' src" \
  "sed -n 1,80p src/prepare.ts | grep -n -E 'compute|matte|export|job|signal|allow' | head -30" \
  "grep -E 'env|config' src/a.ts" "rg 'get|set|unset' src" "grep -nE 'typeset|declare' f.sh" \
  "gh release view v1 --json tagName,body --jq '.tagName+\" \"+.body' | head -120"; do
  hook 0 "$c"
done

printf 'not json' | "${HOOK:-$H/block-env-dump.sh}" 2>/dev/null; [ $? -eq 2 ] || { echo "FAIL hook: bad input not blocked"; fail=1; }

# rex: blocked only for Paseo agents (PASEO_AGENT_ID set); fake id value.
hookas() { # $1 = expected exit, $2 = PASEO_AGENT_ID value ("" = unset), $3 = command
  printf '%s' "$3" | /usr/bin/jq -Rs '{tool_name:"Bash",tool_input:{command:.}}' > /tmp/hook-in.json
  if [ -n "$2" ]; then /usr/bin/env PASEO_AGENT_ID="$2" "${HOOK:-$H/block-env-dump.sh}" < /tmp/hook-in.json 2>/dev/null
  else /usr/bin/env -u PASEO_AGENT_ID "${HOOK:-$H/block-env-dump.sh}" < /tmp/hook-in.json 2>/dev/null; fi
  got=$?; rm -f /tmp/hook-in.json
  if [ "$got" -ne "$1" ]; then echo "FAIL rex want=$1 got=$got id=$2: $3"; fail=1; fi
}
for c in 'rex session rename "$REX_SESSION" x >/dev/null 2>&1; cat f' 'cd /tmp && rex whoami --json' '/opt/homebrew/bin/rex ls' 'x; rex skill show'; do hookas 2 fake-agent "$c"; done
for c in 'grep -n rex notes.md' 'cat rex.md' 'echo rexx' 'ls ~/.rex-cache'; do hookas 0 fake-agent "$c"; done
hookas 0 "" 'rex session rename "$REX_SESSION" mine'

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

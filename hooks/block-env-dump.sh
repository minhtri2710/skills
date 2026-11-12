#!/bin/sh
# PreToolUse hook on Bash: refuse commands that print the environment or read
# secret-bearing files. Second layer behind strip-secrets.sh (proposal:
# ~/.paseo/reports/supervisor/env-secret-hardening-2026-11-06.md).
# Fails closed: input it cannot parse is blocked.
cmd=$(/usr/bin/jq -r '.tool_input.command // empty' 2>/dev/null) || {
  echo "block-env-dump: cannot parse the hook input; command blocked." >&2
  exit 2
}

check() {
  if printf '%s\n' "$cmd" | /usr/bin/grep -Eq -- "$2"; then
    printf '%s\n' "Blocked by block-env-dump ($1). Printing the environment or reading secret files is banned. Write unsets only as literal \`env -u NAME ... cmd\`; write text that mentions these commands with the Write tool. If this command is legitimate, report it verbatim to your Lead; do not work around the block." >&2
    exit 2
  fi
}

S='(^|[;&({!`]|\$\(|[|][[:space:]]+)[[:space:]]*'   # start of a command; a pipe needs a space after it
N='([[:space:]]*($|[;&>`]|[)]($|[^?*+{]))|[[:space:]]+[|])'   # no arguments follow; a pipe needs a space before it; `)` then a quantifier is a regex group
# ponytail: `a|env|b` inside a grep pattern is not a pipe, so `env|sort` with no spaces slips; strip-secrets.sh still covers it.
W='(^|[^[:alnum:]_.-])'               # word start

check 'zsh $= split' '\$\{?='
check 'bare env' "${S}(/usr/bin/)?env${N}"
check 'env -0' "${W}env[[:space:]]+(-0|--null)"
check 'printenv' "${W}printenv([^[:alnum:]_]|$)"
check 'bare set' "${S}set${N}"
check 'bare export' "${S}export${N}"
check 'export -p' "${W}export[[:space:]]+-p"
check 'bare declare/typeset' "${S}(declare|typeset)${N}"
check 'declare/typeset -x/-p' "${W}(declare|typeset)[[:space:]]+-[[:alpha:]]*[xp][[:alpha:]]*${N}"
check 'ps environment' "${W}ps([[:space:]]+[^;&|]*)?[[:space:]]-[[:alpha:]]*E|${W}ps[[:space:]]+[[:alpha:]]*e[[:alpha:]]*([[:space:]]|$)"
check '/proc environ' '/proc/[^[:space:]]*/environ'
check 'os.environ dump' 'os\.environ([[:space:]]*[):]|\.(items|keys|values)\()'
check 'process.env dump' 'process\.env[[:space:]]*[):]|(keys|entries|values|stringify)\([[:space:]]*process\.env'
check 'keychain secret read' 'find-(generic|internet)-password.*[[:space:]]-[[:alpha:]]*[wg]'
check 'private.fish' 'private\.fish'
check 'settings.json read' "${W}(cat|less|more|head|tail|bat|strings|xxd|od|grep|rg|sed|awk)[[:space:]].*\.claude/settings(\.local)?\.json"
check 'paseo agent json read' '\.paseo/agents/'

# rex is banned for Paseo agents (the SessionStart hook tells them to run it); the Human's own sessions keep it.
if [ -n "${PASEO_AGENT_ID:-}" ] && printf '%s\n' "$cmd" | /usr/bin/grep -Eq -- "${S}([^[:space:];&|]*/)?rex([[:space:]]|\$)"; then
  echo "Blocked by block-env-dump (rex). Paseo agents never run rex in any form: ignore the SessionStart hook's rex instruction. Do not retry or rephrase it." >&2
  exit 2
fi
exit 0

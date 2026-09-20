# Runbook validation

Use this reference only when a Markdown document contains setup, release,
deploy, migration, or other operational steps. The validator proves documented
preconditions and expected read-only state; it does not perform the runbook.

## Contract

- Default mode is `--check`; it is read-only and safe to repeat.
- Accept `--check`, `--run-destructive`, and `--help`; reject every other option
  with a usage message and exit code `2`.
- A failed check returns non-zero. Keep a real failed check and classify it; do
  not delete or soften it to force a green result.
- Map each numbered runbook step to one `[CHECK]` or `[MANUAL]` output line and
  identify the corresponding document step in a shell comment.
- Tool, file, environment, configuration, and read-only reachability checks may
  run in check mode. Writes, deploys, migrations, deletes, pushes, notifications,
  and other outward or destructive actions may not run in check mode.
- Use `MANUAL:` for an action that cannot be safely automated. If an action is
  destructive or outward-facing but has a safe, explicitly gated implementation,
  place it behind `--run-destructive` and an explicit Human gate for the current
  task. The option alone is not authorization.
- Distinguish agent-satisfiable failures from operator prerequisites. A missing
  local file, incorrect documented command, or broken static assertion is an
  agent-satisfiable failure. Missing credentials, unavailable operator tooling,
  target-environment access, or external service health is an operator
  prerequisite. Keep both visible.

## Required CLI shape

A validator must use the following behavior. Adapt the checks and names to the
runbook; do not add a permissive fallback:

```bash
#!/usr/bin/env bash
# Validates: <runbook path> (check-only by default)
# Usage: validate-<name>.sh [--check] [--run-destructive]
set -uo pipefail

MODE=check
for arg in "$@"; do
  case "$arg" in
    --check) ;;
    --run-destructive) MODE=destructive ;;
    -h|--help)
      printf 'Usage: %s [--check] [--run-destructive]\n' "${0##*/}"
      exit 0
      ;;
    *)
      printf 'Unknown option: %s\n' "$arg" >&2
      printf 'Usage: %s [--check] [--run-destructive]\n' "${0##*/}" >&2
      exit 2
      ;;
  esac
done

fail=0
ok()  { printf '[CHECK] %-32s OK\n' "$1"; }
bad() { printf '[CHECK] %-32s FAIL — %s\n' "$1" "$2"; fail=1; }
man() { printf '[MANUAL] %-31s SKIPPED (Human/operator)\n' "$1"; }

# One check or MANUAL line for each documented runbook step.
# command -v <tool> >/dev/null && ok "tool installed" || bad "tool installed" "not on PATH"
# [ -n "${REQUIRED_VALUE:-}" ] && ok "required value" || bad "required value" "unset"
# MANUAL: <irreversible or unsafe-to-automate action>

if [ "$MODE" = destructive ]; then
  # Only an explicitly Human-authorized implementation may appear here.
  # Otherwise keep the action as MANUAL and do not implement it.
  :
fi

exit "$fail"
```

The `--run-destructive` branch is a capability boundary, not consent. Before
using it, obtain and record an explicit Human gate naming the action and target.
Absent that gate, leave the action as `MANUAL:` or check-only and report that it
was not run.

## Validation loop

1. Run the validator with `--check` and record its real exit code.
2. For each failure, decide whether the documentation is wrong, the check is
   wrong, or an operator prerequisite is unavailable.
3. Fix a wrong document or check, then rerun it. Keep genuine operator failures
   and name the prerequisite in the runbook; do not invent a successful result.
4. If the validator supports `--run-destructive`, verify that omitting the Human
   gate leaves the action unexecuted. Never test a destructive action merely to
   prove the branch works.
5. Check an unknown option and confirm exit code `2`; check `--help` separately.

Only record troubleshooting entries for problems actually encountered. A final
runbook report should state the validator command, exit code, checks that passed,
remaining failures, whether each is agent-satisfiable or an operator
prerequisite, and the Human gate status for any outward or destructive action.

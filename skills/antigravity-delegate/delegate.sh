#!/usr/bin/env bash
# antigravity-delegate runner — drives `agy` headless reliably from a non-TTY parent (e.g. pi).
#
# Why this exists: agy print mode is the only headless path, but it is fragile when spawned
# as a subprocess (non-TTY): it can drop stdout (github issue #76) or hang (issue #318), and
# it only edits the repo if the repo is registered as a workspace. This script encodes the
# exact recipe so the caller does not re-derive it each run.
#
# Usage:
#   delegate.sh <repo-root> <timeout-secs> <prompt-file|->     # prompt from file or stdin
#
# Preconditions the CALLER must already verify (this script does not check):
#   - agy is installed and authenticated
#   - <repo-root> is a git repo with a clean working tree (so edits are revertable)
#
# Output contract (deterministic, machine-parseable):
#   stdout : line 1 = agy exit code; remainder = agy's model response (control chars stripped)
#   stderr : diagnostics (e.g. empty-output warning, log path)
# Exit    : the agy exit code (124 if the hard timeout fired)
#
# Edits agy makes land in <repo-root> (via --add-dir); review them with `git -C <repo> diff`.

set -uo pipefail

REPO="${1:?usage: delegate.sh <repo-root> <timeout-secs> <prompt-file|->}"
SECS="${2:?missing timeout-secs}"
SRC="${3:?missing prompt-file or - for stdin}"

if [ "$SRC" = "-" ]; then PROMPT="$(cat)"; else PROMPT="$(cat "$SRC")"; fi
[ -n "$PROMPT" ] || { echo "empty prompt" >&2; exit 64; }
command -v agy >/dev/null || { echo "agy not found in PATH" >&2; exit 127; }

LOG="$(mktemp -t agy-delegate-log.XXXXXX)"
RAW="$(mktemp -t agy-delegate-out.XXXXXX)"
KEEP_LOG=0
trap '[ "$KEEP_LOG" -eq 0 ] && rm -f "$LOG" "$RAW"' EXIT

# Run a command with a hard outer kill (macOS has no `timeout`). Captures combined stdout
# into $RAW. Returns the command's exit status (124 if we had to kill it).
run_with_kill() {
  local cap="$1"; shift
  "$@" >"$cap" 2>&1 &
  local pid=$!
  ( sleep "$((SECS + 30))"; kill -TERM "$pid" 2>/dev/null; sleep 3; kill -KILL "$pid" 2>/dev/null ) &
  local watcher=$!
  wait "$pid"; local code=$?
  wait "$watcher" 2>/dev/null || true
  # 137 = SIGKILL, normalize to 124 (timeout)
  [ "$code" -eq 137 ] && code=124
  return "$code"
}

strip() { tr -d '\r' <"$1" | tr -d '\004' | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'; }

cd "$REPO" || { echo "cannot cd $REPO" >&2; exit 1; }
ARGS=(agy -p "$PROMPT" --dangerously-skip-permissions --add-dir "$REPO" --print-timeout "${SECS}s" --log-file "$LOG")

# Attempt 1: plain print mode (current agy returns stdout even when non-TTY).
code=0; run_with_kill "$RAW" "${ARGS[@]}" || code=$?
content="$(strip "$RAW")"

# Attempt 2: PTY fallback only when plain produced nothing yet exited cleanly (the #76 signature).
if [ -z "$content" ] && [ "$code" -eq 0 ] && command -v script >/dev/null; then
  run_with_kill "$RAW" script -q /dev/null "${ARGS[@]}" || code=$?
  content="$(strip "$RAW")"
fi

printf '%s\n' "$code"
printf '%s' "$content"

if [ -z "$content" ]; then
  KEEP_LOG=1
  echo "WARNING: agy returned empty stdout after plain + PTY attempts (code=$code). agy log: $LOG" >&2
fi
exit "$code"

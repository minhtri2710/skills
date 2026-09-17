#!/usr/bin/env bash
# Human-in-the-loop reproduction loop. Copy, edit the steps between the markers,
# and run it; the user follows the prompts and the agent parses KEY=VALUE output.
# Capture observations only: a captured value is echoed where the agent reads it,
# so signing in stays a `step`, never a `capture`.
set -euo pipefail

step() {
  printf '\n>>> %s\n' "$1"
  read -r -p "    [Enter when done] " _
}

capture() {
  local var="$1" question="$2" answer
  printf '\n>>> %s\n' "$question"
  read -r -p "    > " answer
  printf -v "$var" '%s' "$answer"
}

# --- edit below ---
step "Open the app at http://localhost:3000 and sign in."
capture ERRORED "Click 'Export'. Did it throw an error? (y/n)"
capture ERROR_MSG "Paste the error message (or 'none'):"
# --- edit above ---

printf '\n--- Captured ---\n'
printf 'ERRORED=%s\n' "$ERRORED"
printf 'ERROR_MSG=%s\n' "$ERROR_MSG"

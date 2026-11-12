#!/usr/bin/env bash
#
# A wizard walks a human through a manual procedure, step by step.
# Generated with the human-step-wizard skill.
#
# Everything above the "STAGES" marker is the wizard library: do not hand-edit
# it. Author the per-step stages below the marker.

set -euo pipefail

if [[ -t 1 ]] && command -v tput >/dev/null 2>&1 && [[ "$(tput colors 2>/dev/null || echo 0)" -ge 8 ]]; then
  BOLD=$(tput bold); DIM=$(tput dim); RESET=$(tput sgr0)
  BLUE=$(tput setaf 4); GREEN=$(tput setaf 2); YELLOW=$(tput setaf 3)
else
  BOLD=""; DIM=""; RESET=""; BLUE=""; GREEN=""; YELLOW=""
fi

_STAGE_INDEX=0
ENV_FILE="${ENV_FILE:-.env}"
WRITTEN_ENV=()
WRITTEN_SECRET=()
SKIPPED=()

# _clear wipes the terminal so only the current step is on screen. No-op when
# output isn't a terminal, so piped logs stay readable.
_clear() {
  [[ -t 1 ]] || return 0
  if command -v tput >/dev/null 2>&1; then tput clear; else printf '\033[2J\033[3J\033[H'; fi
}

# banner "Title" shows the opening frame: what this wizard does. It counts the
# top-level `stage` lines of this script, so keep each stage at column 0.
banner() {
  TOTAL_STAGES=$(grep -c '^stage ' "${BASH_SOURCE[0]}" || true)
  _clear
  printf '\n%s%s  %s%s\n' "$BOLD" "$BLUE" "$1" "$RESET"
  printf '%s  %s stages%s\n\n' "$DIM" "$TOTAL_STAGES" "$RESET"
  printf '%s  You drive the browser; this wizard tells you exactly what to do and\n' "$DIM"
  printf '  captures the values you copy back. Stop any time with Ctrl-C and re-run\n'
  printf '  later, since it remembers values already saved.%s\n' "$RESET"
  pause "Ready to start?"
}

# stage "Name" clears the screen, then announces a stage and shows progress.
stage() {
  _clear
  _STAGE_INDEX=$((_STAGE_INDEX + 1))
  printf '\n%s%s▸ Stage %s/%s · %s%s\n' \
    "$BOLD" "$BLUE" "$_STAGE_INDEX" "$TOTAL_STAGES" "$1" "$RESET"
}

# say "..." prints a plain instruction line.
say()  { printf '  %s\n' "$1"; }
# step "..." is a numbered-feeling action the human takes in the browser.
step() { printf '  %s•%s %s\n' "$BLUE" "$RESET" "$1"; }
note() { printf '  %s%s%s\n' "$DIM" "$1" "$RESET"; }
warn() { printf '  %s⚠ %s%s\n' "$YELLOW" "$1" "$RESET"; }

# open_url URL opens it in the human's browser, cross-platform incl. WSL.
open_url() {
  local url="$1" candidate
  printf '  %s↗ opening%s %s\n' "$GREEN" "$RESET" "$url"
  local opener=""
  for candidate in wslview explorer.exe xdg-open open; do
    if command -v "$candidate" >/dev/null 2>&1; then opener="$candidate"; break; fi
  done
  # explorer.exe exits 1 even when it opened the URL.
  if [[ -n "$opener" ]] && { "$opener" "$url" >/dev/null 2>&1 || [[ "$opener" == explorer.exe ]]; }; then return 0; fi
  warn "couldn't open a browser; visit it manually: $url"
}

# pause "msg" waits for the human to confirm they've done the manual part.
pause() {
  printf '  %s%s%s ' "$DIM" "${1:-Press Enter to continue}" "$RESET"
  read -r _ || true
}

# confirm "question" is a y/N gate; returns success on yes. The script runs
# under set -e, so a bare call exits the wizard on "n": always branch on it,
#   if confirm "Rotate the old key now?"; then ...; else note "Skipped."; fi
confirm() {
  local reply=""
  printf '  %s? %s [y/N] ' "$YELLOW" "$1"
  read -r reply || true
  [[ "$reply" =~ ^[Yy] ]]
}

# _existing KEY prints the saved value with one layer of quotes removed.
_existing() {
  [[ -f "$ENV_FILE" ]] || return 1
  local line value; line=$(grep -E "^${1}=" "$ENV_FILE" | tail -n1) || return 1
  value="${line#*=}"
  if [[ ${#value} -ge 2 && "$value" == \"*\" ]]; then
    value="${value:1:${#value}-2}"
    value=$(printf '%s' "$value" | sed -e 's/\\\([\\"$`]\)/\1/g')
  elif [[ ${#value} -ge 2 && "$value" == \'*\' ]]; then
    value="${value:1:${#value}-2}"
  fi
  printf '%s' "$value"
}

# _read_value KEY "Prompt" SECRET reads a value into $KEY; SECRET=1 hides the
# input. Offers the existing .env value as a default (Enter keeps it) and
# re-asks while the answer is empty and no saved value exists.
_read_value() {
  local key="$1" prompt="$2" secret="$3" current input eof
  current=$(_existing "$key" || true)
  while :; do
    eof=0
    if [[ -n "$current" ]]; then
      printf '  %s%s%s %s[Enter keeps current]%s ' "$BOLD" "$prompt" "$RESET" "$DIM" "$RESET"
    else
      printf '  %s%s%s ' "$BOLD" "$prompt" "$RESET"
    fi
    if [[ "$secret" == 1 ]]; then
      IFS= read -rs input || eof=1
      printf '\n'
    else
      read -r input || eof=1
    fi
    if (( eof )); then
      if [[ -n "$current" ]]; then input="$current"; break; fi
      printf 'wizard: required value %s was not provided\n' "$key" >&2
      return 1
    fi
    if [[ -n "$input" ]]; then break; fi
    if [[ -n "$current" ]]; then input="$current"; break; fi
    printf 'wizard: %s is required; try again\n' "$key" >&2
  done
  printf -v "$key" '%s' "$input"
}

# ask KEY "Prompt" reads a visible value into $KEY.
ask() { _read_value "$1" "$2" 0; }

# ask_secret KEY "Prompt" is like ask, but input is hidden.
ask_secret() { _read_value "$1" "$2" 1; }

# write_env swaps in its own EXIT/INT/TERM traps while the temp file exists and
# puts the caller's back afterwards; on an abnormal exit it also runs the
# caller's EXIT trap, which `trap -p` prints as: trap -- 'COMMAND' EXIT.
_ENV_TMP=""; _ENV_PRIOR_TRAPS=""; _ENV_PRIOR_EXIT=""
_env_tmp_done() { rm -f -- "$_ENV_TMP"; trap - EXIT INT TERM; eval "$_ENV_PRIOR_TRAPS"; }
_env_on_exit() { rm -f -- "$_ENV_TMP"; eval "set -- $_ENV_PRIOR_EXIT"; eval "${3:-}"; }

# write_env KEY VALUE upserts KEY="VALUE" into ENV_FILE (creates it; replaces
# any existing line). Idempotent. The value is double-quoted with \ " $ ` escaped,
# so the file stays valid to source. The new file is staged beside ENV_FILE and
# renamed over it; an unreadable ENV_FILE fails instead of being overwritten.
write_env() {
  local key="$1" value="$2" rc=0
  touch "$ENV_FILE"
  _ENV_TMP=$(mktemp "${ENV_FILE}.XXXXXX")
  _ENV_PRIOR_TRAPS=$(trap -p EXIT INT TERM)
  _ENV_PRIOR_EXIT=$(trap -p EXIT)
  trap _env_on_exit EXIT
  trap 'exit 130' INT
  trap 'exit 143' TERM
  grep -vE "^${key}=" "$ENV_FILE" > "$_ENV_TMP" || rc=$?
  if (( rc > 1 )); then
    _env_tmp_done
    printf 'wizard: cannot read %s; left unchanged\n' "$ENV_FILE" >&2
    return 1
  fi
  value=$(printf '%s' "$value" | sed -e 's/[\\"$`]/\\&/g')
  printf '%s="%s"\n' "$key" "$value" >> "$_ENV_TMP"
  mv "$_ENV_TMP" "$ENV_FILE"
  _env_tmp_done
  WRITTEN_ENV+=("$key")
  printf '  %s✓ wrote%s %s → %s\n' "$GREEN" "$RESET" "$key" "$ENV_FILE"
}

# _gh_ready succeeds when gh is installed and authenticated.
_gh_ready() { command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; }

# set_secret NAME VALUE sets a GitHub Actions repo secret via gh. Falls back
# to a warning (and records it) if gh is unavailable, unauthenticated, or fails;
# the warning carries gh's own error.
set_secret() {
  local name="$1" value="$2" reason="gh not ready"
  if _gh_ready; then
    if reason=$(printf '%s' "$value" | gh secret set "$name" 2>&1 >/dev/null); then
      WRITTEN_SECRET+=("$name")
      printf '  %s✓ set%s GitHub secret %s\n' "$GREEN" "$RESET" "$name"
      return
    fi
  fi
  SKIPPED+=("GitHub secret $name (set it manually: gh secret set $name)")
  warn "skipped GitHub secret $name: ${reason//$'\n'/ }; set it later"
}

# set_var NAME VALUE sets a GitHub Actions repo variable (non-secret).
set_var() {
  local name="$1" value="$2" reason="gh not ready"
  if _gh_ready; then
    if reason=$(gh variable set "$name" --body "$value" 2>&1 >/dev/null); then
      printf '  %s✓ set%s GitHub variable %s\n' "$GREEN" "$RESET" "$name"
      return
    fi
  fi
  SKIPPED+=("GitHub variable $name")
  warn "skipped GitHub variable $name: ${reason//$'\n'/ }; set it later"
}

# finish clears, then shows a closing summary of everything configured.
finish() {
  _clear
  printf '\n%s%s  ✓ Setup complete%s\n' "$BOLD" "$GREEN" "$RESET"
  (( ${#WRITTEN_ENV[@]} ))    && note "wrote ${#WRITTEN_ENV[@]} value(s) to $ENV_FILE: ${WRITTEN_ENV[*]}"
  (( ${#WRITTEN_SECRET[@]} )) && note "set ${#WRITTEN_SECRET[@]} GitHub secret(s): ${WRITTEN_SECRET[*]}"
  if (( ${#SKIPPED[@]} )); then
    printf '\n'; warn "still to do by hand:"
    for s in "${SKIPPED[@]}"; do note "  - $s"; done
  fi
  printf '\n'
}

# ──────────────────────────────────────────────────────────────────────────
# STAGES: author this section. One stage() per step the human takes.
# Replace the example below. This line ends the library: the test cuts on it.
# ──────────────────────────────────────────────────────────────────────────

banner "Stripe setup"

# ── Example stage: replace with your real steps ───────────────────────────
stage "Stripe: API keys"
say "We'll grab your Stripe test keys and store them for local dev + CI."
open_url "https://dashboard.stripe.com/test/apikeys"
step "On the API keys page, copy the Publishable key (starts pk_test_)."
ask STRIPE_PUBLISHABLE_KEY "Paste the publishable key:"
step "Click 'Reveal test key' on the Secret key row, then copy it."
ask_secret STRIPE_SECRET_KEY "Paste the secret key:"
write_env STRIPE_PUBLISHABLE_KEY "$STRIPE_PUBLISHABLE_KEY"
write_env STRIPE_SECRET_KEY "$STRIPE_SECRET_KEY"
set_secret STRIPE_SECRET_KEY "$STRIPE_SECRET_KEY"   # CI needs this one
if confirm "Also overwrite the key stored in the deploy environment?"; then
  set_var STRIPE_PUBLISHABLE_KEY "$STRIPE_PUBLISHABLE_KEY"
else
  note "Deploy environment left unchanged."
fi
# ──────────────────────────────────────────────────────────────────────────

finish

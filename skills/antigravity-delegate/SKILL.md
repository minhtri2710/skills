---
name: antigravity-delegate
description: Delegate a bounded coding task to Google Antigravity CLI (agy) as a second, editing-capable agent, then review the diff it produces. Use when the user wants to delegate work to agy / Antigravity, have a second agent implement / fix / refactor code, or hand an implementation task to Google's agent engine. agy edits files directly in the repo; this skill runs it headless, captures the response, and reviews every change before reporting done.
allowed-tools: Bash
---

# antigravity-delegate

Delegate a coding task to `agy` (Google Antigravity CLI) running **headless**, then review what it changed before you call the work done. `agy` is a separate agent engine — its value here is a second pair of hands that edits the repo; your value is driving it reliably and vetting the result.

This skill is one **branch**: agy edits the repo. For the read-only "ask agy for a second opinion, no edits" variant, see `REFERENCE.md`.

## The hazard you are accepting

Headless agy cannot prompt for approvals, so the runner passes `--dangerously-skip-permissions`: agy auto-approves **every** tool call — file writes *and* shell execution. A clean git tree makes file edits revertable, but it does **not** contain destructive shell commands (`rm -rf`, force-push, network calls). Therefore: only delegate bounded tasks with tight prompts into repos where unattended execution is acceptable. Push back if the user asks you to delegate something open-ended or destructive.

## Steps

Resolve every relative path against this skill's directory (the folder holding this `SKILL.md`).

### 1. Preflight — confirm it is safe to delegate
Run the checks; **completion criterion**: `agy` is installed and authenticated **and** the target repo's working tree is clean (or the user explicitly accepted a dirty tree).

- `agy --version` succeeds and `~/.gemini/antigravity-cli/` exists with an active token (else: tell the user to install/auth — see `REFERENCE.md`).
- `git -C <repo> status --porcelain` is empty. If not empty, **stop** and ask whether to delegate anyway (dirty tree means edits are harder to separate and revert).

### 2. Frame the delegation — write a tight prompt
**Completion criterion**: the prompt names the specific file(s) and the exact change, and grants no open-ended license ("refactor everything", "do whatever it takes" fail this test).

Put the constraints in the prompt: the files to touch, the change to make, what **not** to touch, and "keep it minimal." agy works in the repo, so be as narrow as a good PR description.

### 3. Delegate — run agy headless via the runner
**Completion criterion**: the runner returns an exit code and the model response within the timeout.

Resolve `delegate.sh` against this skill's directory (it is `/Users/beowulf/.agents/skills/antigravity-delegate/delegate.sh`) and pipe the prompt to it (non-TTY, exactly as it runs for you):

```bash
printf '%s' "$PROMPT" | "$RUNNER" "$REPO" "$SECS" - > result.txt 2> err.txt
```

- `$RUNNER` — absolute path to `delegate.sh` in this skill's directory.
- `$REPO` — absolute path to the repo root (must be a git repo).
- `$SECS` — `--print-timeout` for agy; pick a bound that fits the task (e.g. 180). The runner adds a hard outer kill of `$SECS + 30` because macOS has no `timeout`.
- `result.txt` line 1 is agy's exit code; the remainder is the model response (control chars already stripped). `err.txt` holds diagnostics (e.g. an empty-output warning with the agy log path).

The runner encodes the fragile-headless recipe (hard timeout, PTY fallback on empty stdout, `--add-dir` so edits land in the repo, control-char strip). Do not hand-roll the `agy` invocation — use the runner. Rationale and the exact flags live in `REFERENCE.md`.

### 4. Verify the round-trip — output arrived, edits are visible
**Completion criterion**: the response is non-empty **or** you report an explicit failure; and `git -C "$REPO" diff` (plus `--staged` and untracked files) is captured.

- If `result.txt` has no response after the code line, treat it as failure: surface `err.txt` (it points at the agy log) and do **not** claim success. This is the known silent-drop failure mode; the runner already retried via PTY, so empty here means a real problem.
- Capture `git -C "$REPO" status --porcelain` and `git -C "$REPO" diff` — these are the actual edits, regardless of what agy's prose claims.

### 5. Review the diff — read every change agy made
**Completion criterion**: every path changed by agy (tracked diff, staged, and new untracked files) is read and summarized back to the user, and a revert is offered.

agy's summary is a claim; the diff is the truth. Read the actual changed source, not just agy's description. Look for scope creep (files outside the request), mistakes, and anything destructive.

### 6. Report — hand the decision to the user
**Completion criterion**: the user has seen the diff summary and chosen to accept or revert.

Present: what was asked, what agy changed (per file), and any concerns. Offer to revert with `git -C "$REPO" restore` / `git -C "$REPO" clean -fd` (for untracked files agy added). Only after the user accepts is the delegation done.

## Files in this skill

- `delegate.sh` — the tested headless runner. Use it; do not re-derive the command.
- `REFERENCE.md` — flag table, the workspace/scratch behavior, the PTY/timeout bug rationale, install/auth, the read-only variant, and follow-up (`--continue`) usage. Load it when a step needs the why or when something breaks.

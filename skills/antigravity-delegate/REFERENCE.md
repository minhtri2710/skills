# antigravity-delegate — reference

Flat reference for the `antigravity-delegate` skill. Consult when a step needs the *why*, when choosing flags, or when a delegation breaks. All facts verified against `agy` v1.0.15 on macOS.

## The headless command (what `delegate.sh` runs)

```
agy -p "<prompt>" --dangerously-skip-permissions --add-dir <repo> --print-timeout <secs>s --log-file <log>
```

Each flag earns its place:

| Flag | Purpose | Why it's here |
| --- | --- | --- |
| `-p` / `--print` / `--prompt` | Run one prompt non-interactively, print the response. | The **only** headless path. The TUI crashes in a non-TTY (`bubbletea: could not open TTY`). |
| `--dangerously-skip-permissions` | Auto-approve every tool call. | Print mode has no way to surface approval prompts; without this, agy hangs on the first tool request. **This is the hazard** — see SKILL.md. |
| `--add-dir <repo>` | Register `<repo>` as a workspace directory. | **Required** for edits to land in the repo. Without it, agy writes to its scratch dir (see below). |
| `--print-timeout <dur>` | agy's own timeout for print mode (default 5m). | Mitigates hang-on-non-TTY. The runner also adds a hard outer kill. |
| `--log-file <path>` | Write agy's log to a known path. | Diagnostic fallback when stdout is empty — points at *why*. |

Flags that exist but the runner does **not** use by default: `-c`/`--continue` (resume last conversation), `--conversation <id>` (resume by id), `--model <m>`, `--sandbox`, `--new-project`/`--project`, `--prompt-interactive`/`-i`. See "Variants" for the useful ones.

## Workspace vs scratch — why `--add-dir` is mandatory

agy only writes into a directory it treats as a **workspace**. Empirically (v1.0.15):

- Random cwd (even a git repo root) → agy writes to `~/.gemini/antigravity-cli/scratch/`, **not** the cwd. You will see "created file …/scratch/…" and the repo is untouched.
- `--add-dir <repo>` (and `cd` into the repo) → edits land in the repo and show up in `git status` / `git diff`.
- `--sandbox` → writes are **redirected to scratch** even with `--add-dir`. Sandbox is for safe scratch dry-runs; it **defeats** repo editing, so the runner omits it. Do not add `--sandbox` for a real delegation.

If agy's prose claims it edited a file but `git diff` is empty, it wrote to scratch — you forgot `--add-dir`, or you left `--sandbox` on.

## The non-TTY bugs and how the runner covers them

agy spawned as a subprocess (which is how an agent calls it) is a non-TTY, and print mode has documented fragility:

- **Issue #76** — print mode can drop stdout entirely (exit 0, no output) under non-TTY.
- **Issue #318** — print mode can hang indefinitely under non-TTY.

`delegate.sh` covers both, in order:

1. **Plain print mode first** — on current agy this returns stdout even when non-TTY (verified: a piped `agy -p` returned the full response). Prefer it; its output is clean.
2. **PTY fallback** — if plain produced empty stdout with a clean exit, retry wrapped in `script -q /dev/null agy …`, which forces a pseudo-TTY (verified working). PTY output carries stray `^D` / `\r`, so the runner strips them.
3. **Hard outer kill** — macOS has no `timeout`/`gtimeout`, so the runner backgrounds agy and `kill -TERM` then `kill -KILL` after `$SECS + 30`. `--print-timeout` is the inner bound; this is the outer bound.
4. **Non-empty check** — if both attempts return nothing, the runner keeps the agy log and writes its path to stderr. Treat empty output as failure (see SKILL.md step 4).

## Install / auth (preflight failures)

- Install (macOS/Linux): `curl -fsSL https://antigravity.google/cli/install.sh | bash` → installs `~/.local/bin/agy`. (This machine has Homebrew's `/opt/homebrew/bin/agy`.)
- Auth: agy uses the OS keyring; on first interactive launch it opens a browser (local) or prints a URL to paste locally (SSH). Once authed, `~/.gemini/antigravity-cli/` holds the token and print mode runs unattended. `/logout` (inside the TUI) clears it.
- You cannot auth from a non-TTY — if preflight shows no token, tell the user to run `agy` once interactively to sign in.

## Variants

### Read-only second opinion (no edits)
Drop `--dangerously-skip-permissions` and `--add-dir`, and ask agy to analyze/propose without editing. With no tool calls, print mode won't hang on approvals. There is nothing to review in `git diff`; skip steps 5–6's revert path and just relay agy's answer (still cite it as agy's view, not verified truth). Useful for a cross-engine design check.

### Follow-up turns (`--continue`)
To refine the same delegation, resume agy's last conversation: add `-c` (or `--conversation <id>` for a specific one) to the flags. The conversation history lives under `~/.gemini/antigravity-cli/conversations/`. The runner does not add this by default — pass it through only when you specifically want a follow-up, and re-run preflight (clean tree) each time.

### Pinning a model
`--model <name>` selects the reasoning model for the session. `agy models` lists what's available. Omit to use the user's default.

## When not to use this skill

- The task is open-ended or destructive — do not delegate it with `--dangerously-skip-permissions`.
- The repo working tree is dirty and the user won't accept the risk — stop at preflight.
- You only need a code review or a plan — use the read-only variant, or just do it yourself; spinning a second agent to edit is overkill.

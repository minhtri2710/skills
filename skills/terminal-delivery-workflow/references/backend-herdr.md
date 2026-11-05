# Herdr backend

Read this right after detection names Herdr, before the first control command in any route. The installed binary is the authority for syntax; this file is the authority for how this workflow uses it. The operations are defined in `seat-operations.md`; each heading below gives Herdr's command for one.

Learn syntax from the binary, not from memory: print a command group without a subcommand to see it (`herdr --help`, `herdr agent`, `herdr pane`). Do not run bare `herdr` — it launches or attaches the TUI. Do not probe a mutating nested command by omitting arguments; `herdr workspace create` is valid with defaults and will execute. Most control commands return JSON: read identifiers and state from those responses, never from sidebar order, pane order, or the examples here.

Herdr's handle is the pane ID: workspace `w1`, tab `w1:t1`, pane `w1:p1`. Closed tab and pane IDs are not reused. Herdr's agent commands accept a unique live agent name or the pane ID hosting that agent, never a terminal ID or bare kind label; route by pane ID. Name resolution is global (`agent prompt` has no workspace scope), so a bare kind label or a pane in another workspace resolves to a foreign agent. A name follows the pane occupant and clears when that agent exits, is released, or is replaced; a terminal restart can clear it even when the session survives on a new terminal.

Prefer `herdr agent` as the control surface: it validates agent identity and lifecycle state. Reach for `herdr pane` only when no agent surface covers the need — hosting an agent, or driving a raw terminal, shell, test, or server no agent occupies. When a live agent occupies a pane, address the agent, not the pane, and do not duplicate an agent command with a pane command.

## identify

Herdr injects the caller's context into every managed pane:

```bash
printf '%s\n' "$HERDR_WORKSPACE_ID" "$HERDR_TAB_ID" "$HERDR_PANE_ID"
```

`HERDR_PANE_ID` is this seat's handle; `scripts/backend.py whoami` reads it and confirms it with `herdr pane get`. Pass `--current` or an explicit pane ID whenever a pane command targets the calling pane. An omitted positional target — including for `herdr pane split`, which defaults to the globally focused pane — may hit a pane in another workspace or client session; the explicit current-pane target is mandatory, because focus is not a safe workspace or client boundary. Live reads: `herdr pane current --current`, `herdr pane list --workspace "$HERDR_WORKSPACE_ID"`.

A seat name is optional and does not route; an agent name matches `[a-z][a-z0-9_-]{0,31}`. To label the caller or a surviving session, `herdr agent rename "$HERDR_PANE_ID" <name>` and `herdr agent rename <target> --clear`; rename works on an unnamed agent, including the caller's own. After a terminal restart, re-name the surviving session and confirm with `scripts/roster.py`.

## spawn

Two steps: a pane to host the agent, then the agent in it. `agent start` requires an existing available shell pane — one at its interactive prompt with no foreground command, editor, or agent running — and never creates, splits, or moves layout. Reuse an available shell pane before splitting.

Peers sit in the Lead's recorded workspace: both a reused pane and any pane you split stay there — for the Lead running these commands that is `$HERDR_WORKSPACE_ID`. A Supervisor opening a Peer pane as the Human's hands (`supervisor.md`) targets a pane already in the Lead's recorded workspace with `herdr pane split --pane <id>` so the sibling lands there, rather than `--current` in its own workspace. Never staff a Peer into a pane in another workspace. Keeping every Peer in the Lead's workspace makes `scripts/roster.py --workspace "$HERDR_WORKSPACE_ID"` and `herdr pane list --workspace` a complete, foreign-free view of exactly this run's seats and closes the omitted-target hazard above by construction. Default to a sibling pane in the current tab and the caller's working directory; do not create a workspace, tab, or different cwd unless the user requests that topology. This workflow runs no delivery work in a second working tree, so `herdr worktree` is out of scope — the single exception is the read-only baseline tree (`lead.md`, "Ownership and topology"). Honor a requested direction; otherwise inspect the caller pane and split a wide pane right, a narrow or tall pane down, avoiding repeated same-direction splits that leave unusable columns or rows:

```bash
herdr pane layout --pane "$HERDR_PANE_ID"
herdr pane split --current --direction right --cwd "$PWD" --no-focus
```

Read the new pane ID from `.result.pane.pane_id`; `--no-focus` keeps the user's focus in the calling pane. Then start the agent. Use the selected configured kind (`herdr agent` lists installed kinds); `agent start` is the sole launcher. A successful start returns only after Herdr detects the expected agent and considers it ready. If startup returns `agent_not_ready`, the name remains usable for `agent read` and `agent send-keys`; `wait` for it to settle before prompting.

Permission posture: pass the role's configured `*-args` as one contiguous block after `--`, together with the exact-kind profile expansion from `scripts/project_config.py` (`charters.md`, "Permission posture"):

```bash
herdr agent start <name> --kind <kind> --pane <pane-id> -- <configured-args...> <expansion...>
```

A pane with no agent — a raw shell, test, or server — takes a command with `pane run`, which atomically sends the command text and Enter. Never use `pane run` past an agent that occupies the pane; prompt the agent instead.

```bash
herdr pane run <pane-id> "just test"
```

Fenced shell (`charters.md`, "Write fence"). In the new pane, before `agent start`, start the fenced shell and probe it; the probe read of the pane must show `Operation not permitted`. Then `agent start` launches the kind inside that shell, and the kind and every command it runs inherit the fence.

```bash
herdr pane run <pane-id> "cd <checkout> && exec sandbox-exec -f <run-dir>/fence-<peer>.sb /bin/zsh -i"
herdr pane run <pane-id> "touch <checkout>/.fence-probe"
herdr pane read <pane-id> --source recent-unwrapped --lines 20
```

## prompt

```bash
herdr agent prompt <handle> "<bounded task>" --wait --until working --until blocked --timeout 30000
```

`agent prompt` honors the pane's live bracketed-paste mode and sends text followed by encoded Enter. It refuses an agent already at an approval or question dialog with `agent_blocked` (`blocked`) before sending input. `--wait --until working --until blocked` returns the first listed state observed after submission, never completion; an already-`working` seat matches at once. The `30000` is an illustrative timeout, never a default to borrow. `agent_prompted`, even with `interactive_ready` true, confirms only that the paste and its Enter were sent; the paste can stay unsubmitted. Herdr 0.9.1 returned `working` for `claude`, `pi`, and `omp` seats started from an idle one.

`agent_prompt_stalled` (`not_started`) means the paste started no turn within 5000 ms: read the seat once (`herdr agent read <handle> --source visible`). For a `claude` seat, an unsubmitted paste sits on the input line between the two rule lines (a long one shows as `[Pasted text #N +M lines]`) with no spinner or tool line above; a submitted prompt appears above the upper rule with the input line empty. Only when that read shows the paste on the input line and no turn started, send exactly one `herdr pane send-keys <pane> enter` and read once more; never retype or resend the prompt. If that read still shows the paste unsubmitted, send no further keys, run `notify`, and record it in the run record. The key goes only to an unsubmitted paste, never to a dialog.

For a long or special-character prompt, send the file's content: `"$(cat <file>)"` in place of the quoted text.

## read

```bash
herdr agent read <handle> --source recent-unwrapped --lines 120
herdr pane read <pane-id> --source recent-unwrapped --lines 120
```

`agent read` is for a seat an agent occupies and fails `not_found` once no agent does; `herdr pane read` reads the raw terminal whether or not an agent is present, so use it for a seat whose agent may be gone (a retired predecessor, an agent that exited). Sources: `visible` — the rendered viewport; `recent` — recent rendered output including soft wraps; `recent-unwrapped` — recent output with soft wraps joined; `detection` — the plain-text bottom-buffer snapshot used for agent detection.

Verified on herdr 0.9.0: `agent read --source recent` and `recent-unwrapped` return rows from the visible viewport without scrollback, and capture scrollback only when `--lines` exceeds the viewport, and only for an `idle` or `done` seat. For a `working` or `blocked` seat, a request past the viewport exits non-zero with error `agent_not_idle`, which needs BOTH conditions together — gate: seat `working` or `blocked`; trigger: a `--lines` above the viewport. Neither alone causes it, so the fix is never a larger `--lines`: it is `--source visible` now, or the same read once `idle` or `done`. `--source visible` and `--source detection` always work and cap at the viewport. `herdr pane read` against a pane whose agent is `working` or `blocked` exits successfully but silently returns only the viewport.

## state

```bash
herdr agent get <handle>
herdr agent explain <handle>
```

`agent get` returns `agent_status`: `idle` (ready for input, its tab seen in the focused UI), `working`, `done` (the same idle state after unseen background work finishes), `blocked` (Herdr recognized an approval or question UI), `unknown`. Focusing the tab, or targeting the pane or agent with a focus command, marks it seen; CLI reads do not. `agent list` and `agent get` can disagree seconds apart.

These states are inferred from the pane, not reported by the agent: Herdr matches the terminal title and recent screen text against a per-kind rule table under `~/.local/state/herdr/agent-detection/remote/<kind>.toml`, and `agent explain` prints the rule id, region, priority, and exact evidence behind the current state. `agent list` gives the label; `agent explain` gives the checkable reason. Derive a seat's state with `agent explain` and read the rule that fired rather than assume one.

Read the staffed kind's table before writing a wait against it, because `idle` is not always readiness: when no rule matches, a known agent falls back to `idle` (`rule: none`, `fallback_reason: default_known_agent_idle_fallback`). A kind whose table asserts `idle` positively (such as `claude`) usually has a rule behind an idle reading; a kind whose table never asserts `idle` (such as `agy`) reads `idle` by fallback for every screen its rules miss, including a seat genuinely mid-turn — a wait for `idle` there can return at once and prove nothing.

The table also ranks states, which decides what a busy seat looks like. For `claude`, `osc_title_working` matches the spinner glyph in the title at priority 1100, above every `blocked` rule (highest 980), and is not the one rule (`background_mcp_task_working`, 965) that excludes dialog text like `do you want to proceed?`; so a seat holding an approval dialog with the spinner still in its title resolves as `working`, not `blocked`. `agent prompt` refuses only a `blocked` target, so a report sent to a seat resolved as `working` is accepted and lands as queued input behind an unanswered dialog.

## wait

```bash
herdr agent wait <handle> --until idle --until done --until blocked --timeout 30000
herdr pane wait-output <pane-id> --match "test result" --timeout 120000
```

`agent wait` takes `--until` once per state. The `120000` and `30000` are illustrative values, never defaults to borrow; every `--timeout` is sized to the command's real worst case, and `pane wait-output` waits indefinitely without it. `pane wait-output` is for a pane with no agent: it searches the selected snapshot immediately, so existing output can match; use `--match <text>` for a literal substring or `--regex <pattern>` for a Rust regex.

## list

```bash
herdr agent list
herdr pane list --workspace "$HERDR_WORKSPACE_ID"
```

`agent list` returns JSON `result.agents[]` with `pane_id`, `agent_status`, `agent_session`, and the agent name and kind. `scripts/roster.py` calls it and prints `handle name kind state` per agent; `--workspace <id>` scopes it.

## processes

```bash
herdr pane process-info --pane <pane-id>
```

Returns `foreground_processes` with `argv`, `argv0`, `pid`, and `cwd`. `herdr pane get <pane-id>` returns the pane and its `cwd`.

## interrupt

```bash
herdr agent send-keys <handle> esc
herdr agent send-keys <handle> C-c C-c
herdr pane send-keys <pane-id> enter
```

`esc` interrupts the seat's turn and resumes an interactive UI after the Human's decision. `C-c C-c` is the supported optional clean-exit attempt for a native agent; it is not teardown. `pane send-keys ... enter` is only the single Enter for an unsubmitted paste (`prompt`).

## close

There is no `herdr agent stop`. An agent clears when it exits, is replaced, or the pane hosting it closes. To tear down an agent this run staffed, close the pane this run created for it, after the evidence is preserved (`seat-operations.md`, `close`):

```bash
herdr pane close <pane-id>
```

`herdr pane release-agent` is a low-level detection-plane report (used with `--source`/`--agent`), not a teardown — do not use it to shut an agent down.

## notify

```bash
herdr notification show "<title>" --body "<one line>" --sound request
herdr notification show "<title>" --body "<one line>" --sound done
```

`--sound request` is urgency `request`; `--sound done` is `done`. Popups depend on the Human's `[ui.toast] delivery` key in `~/.config/herdr/config.toml`; its default is `off`, so the notification is silent until the Human sets `herdr`, `terminal`, or `system`. That is the Human's config — never edit it.

## Safety

- Use `--no-focus` for background work unless the user asked to switch context.
- Target `--current`, an explicit pane ID, or a unique agent name; never another client's focused pane.
- Never run `herdr server stop` from an active session unless the user explicitly intends to stop the server and its pane processes, and never kill the main Herdr process. Use a named test session for experiments needing an isolated server.
- CLI server errors are JSON on stderr with exit status 1; syntax errors exit 2.

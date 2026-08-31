# Herdr CLI

Read this before the first Herdr control command in any route. The installed binary is the authority for syntax; this file is the authority for how this workflow uses it.

## Preflight and discovery

Verify the caller is inside Herdr before any inspection or control command:

```bash
test "${HERDR_ENV:-}" = 1
```

If the check fails, say the agent is not running inside Herdr and stop. Do not inspect or control the focused Herdr session from outside it.

Learn syntax from the binary rather than from memory. Print a command group without a subcommand to see it:

```bash
herdr --help
herdr agent
herdr pane
```

Do not run bare `herdr`: it launches or attaches the TUI. Do not probe a mutating nested command by omitting arguments; `herdr workspace create` is valid with defaults and will execute.

Most control commands return JSON. Read identifiers and state from those responses; never derive them from sidebar order, pane order, or the examples here.

## IDs and caller context

Public IDs are opaque stable handles: workspace `w1`, tab `w1:t1`, pane `w1:p1`. Closed tab and pane IDs are not reused.

Herdr injects the caller's context into every managed pane:

```bash
printf '%s\n' "$HERDR_WORKSPACE_ID" "$HERDR_TAB_ID" "$HERDR_PANE_ID"
```

Prefer `--current` when a pane command targets the calling pane. Omitting a target may hit the UI-focused pane, which can belong to the user or another client.

Read live state with:

```bash
herdr pane current --current
herdr pane list --workspace "$HERDR_WORKSPACE_ID"
herdr agent list
```

## Panes and agents

Prefer `herdr agent` as the default control surface: it validates agent identity and lifecycle state, and drives prompts, waits, reads, and inspection. Reach for `herdr pane` only when no agent surface covers the need — opening or discovering a shell pane to host an agent, or driving a raw terminal, shell, test, or server that no agent occupies. When a live agent occupies the pane, address the agent by name, not the pane. Do not use pane commands to duplicate work an agent command already does.

A pane exists whether or not it contains an agent. Pane commands control raw terminals, shells, tests, and servers. Agent commands control a recognized coding agent occupying a pane and are the only surface that validates agent identity and lifecycle state. `agent start` requires an existing available shell pane; it never creates, splits, or moves layout. An available shell pane sits at its interactive prompt with no foreground command, editor, or agent running.

Agent commands accept a unique live agent name or the pane ID hosting that agent, never a terminal ID or a bare agent-kind label. Names match `[a-z][a-z0-9_-]{0,31}`, stay unique among live agents, follow the current pane occupant, and are cleared when that agent exits, is released, or is replaced.

Lifecycle states:

- `idle` — ready for input, and its tab has been seen in the focused Herdr UI;
- `done` — the same underlying idle state after unseen background work finishes;
- `blocked` — Herdr recognized an approval or question UI;
- `unknown` — an agent is present but Herdr cannot classify it confidently; this never proves completion.

Focusing the tab, or targeting the pane or agent with a focus command, marks it seen; CLI reads do not. A settled state means the agent can be inspected, not that the work is complete or accepted.

## Create a pane

Create a pane only to host an agent that has nowhere to run, or when the user explicitly asks for a pane. Reuse an existing available shell pane before splitting a new one. Default to a sibling pane in the current tab and the caller's working directory. Do not create a workspace, tab, or different cwd unless the user explicitly requests that topology or location. This workflow never creates a second working tree, so `herdr worktree` is out of scope.

Honor a direction the user requested. Otherwise inspect the caller pane and split a wide pane right, a narrow or tall pane down, avoiding repeated same-direction splits that leave unusable columns or rows:

```bash
herdr pane layout --pane "$HERDR_PANE_ID"
herdr pane split --current --direction right --cwd "$PWD" --no-focus
```

Read the new pane ID from `.result.pane.pane_id`, and keep the user's focus in the calling pane.

## Run a command in a pane

Use these only against a pane with no agent — a raw shell, test, or server. When an agent occupies the pane, prompt the agent instead; do not send commands past it with `pane run`.

```bash
herdr pane run <pane-id> "just test"
herdr pane wait-output <pane-id> --match "test result" --timeout 120000
herdr pane read <pane-id> --source recent-unwrapped --lines 120
```

`pane run` atomically sends the command text and Enter. `pane wait-output` searches the selected snapshot immediately, so output that already exists can match; use `--match <text>` for a literal substring or `--regex <pattern>` for a Rust regular expression. Omitting `--timeout` allows an indefinite wait, so pass one.

## Start and drive an agent

```bash
herdr agent start <name> --kind <kind> --pane <pane-id>
herdr agent start <name> --kind <kind> --pane <pane-id> -- <agent-args...>
```

Use the kind the user requested, and run `herdr agent` for the installed kind list. Native agent arguments go only after `--`. A successful `agent start` returns only after Herdr detects the expected agent in that pane and considers it ready for input; startup defaults to a 30-second timeout. If the agent is blocked during startup the command returns `agent_not_ready` immediately but keeps the name usable for `agent read` and `agent send-keys`; wait for idle before prompting.

```bash
herdr agent prompt <name> "<bounded task>" --wait --timeout 120000
herdr agent wait <name> --timeout 120000
herdr agent wait <name> --until blocked --timeout 120000
```

`agent prompt` honors the pane's live bracketed-paste mode and sends text followed by encoded Enter. It refuses an agent already sitting at an approval or question dialog with `agent_blocked` before sending any input. `--wait` waits for the first settled `idle`, `done`, or `blocked`; do not repeat those defaults with `--until`. A prompt sent from a non-working state must produce an observed lifecycle change within five seconds, otherwise Herdr returns `agent_prompt_stalled` instead of waiting indefinitely; that wait tracks lifecycle state, not one turn. Use `--until` only for a state-specific need, such as waiting for a running agent to request input.

Do not poll `herdr agent list`, sleep in a loop, or re-issue status commands in place of a wait.

Inspect through the resolved agent:

```bash
herdr agent get <name>
herdr agent read <name> --source recent-unwrapped --lines 120
```

After a failed wait or a `blocked` state, read `agent get` and `agent read` before deciding anything. A blocked approval dialog is a Human decision: route it and never answer it by inference. `herdr agent send-keys <name> esc` writes logical keys and exists to resume an interactive UI after that decision, not to drive the agent's work.

## Read sources

- `visible` — the rendered viewport;
- `recent` — recent rendered output including soft wraps;
- `recent-unwrapped` — recent output with soft wraps joined; prefer it for logs, transcripts, and reports;
- `detection` — the plain-text bottom-buffer snapshot used for agent detection.

`--lines` asks for more rows from the pane's screen and host scrollback. If raising it reveals no more of a completed response, the agent is probably running on the terminal's alternate screen: rows that leave it never enter host scrollback, so no line count recovers them. Only then, ask the agent to write its complete response as Markdown in a temporary directory and reply with the path, then read that file directly. Do not request file output in the initial prompt.

## Tear down an agent

There is no `herdr agent stop`. An agent clears when it exits, is replaced, or the pane hosting it closes. To tear down an agent this run staffed, close the pane this run created for it:

```bash
herdr pane close <pane-id>
```

Read the agent's evidence report first, since the pane's transcript is gone once it closes. When a native agent should exit cleanly first, send its own quit sequence with `herdr agent send-keys <name> ...`, wait for it to leave the pane, then close the pane. Close only a pane this run created to host that agent; never close the caller's pane, a pane hosting an agent this run did not staff, or a pane an agent shares with unrelated work. `herdr pane release-agent` is a low-level detection-plane report used with `--source`/`--agent`, not a teardown — do not use it to shut an agent down.

## Safety

- Use `--no-focus` for background work unless the user asked to switch context.
- Target `--current`, an explicit pane ID, or a unique agent name; never another client's focused pane.
- Do not close workspaces, tabs, panes, or sessions this run did not create unless the user explicitly asked.
- Never run `herdr server stop` from an active session unless the user explicitly intends to stop the server and its pane processes, and never kill the main Herdr process. Use a named test session for experiments needing an isolated server.
- CLI server errors are JSON on stderr with exit status 1; syntax errors exit 2.

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

Pass `--current` or an explicit pane ID whenever a pane command targets the calling pane. A positional target omitted — including for `herdr pane split`, which defaults to the globally focused pane — may hit a pane in another workspace or another client's session; the explicit current-pane target is mandatory rather than a ritual, because focus is not a safe workspace or client boundary.

Read live state with:

```bash
herdr pane current --current
herdr pane list --workspace "$HERDR_WORKSPACE_ID"
herdr agent list
```

## Panes and agents

Prefer `herdr agent` as the default control surface: it validates agent identity and lifecycle state, and drives prompts, waits, reads, and inspection. Reach for `herdr pane` only when no agent surface covers the need — opening or discovering a shell pane to host an agent, or driving a raw terminal, shell, test, or server that no agent occupies. When a live agent occupies the pane, address the agent by name, not the pane. Do not use pane commands to duplicate work an agent command already does.

A pane exists whether or not it contains an agent. Pane commands control raw terminals, shells, tests, and servers. Agent commands control a recognized coding agent occupying a pane and are the only surface that validates agent identity and lifecycle state. `agent start` requires an existing available shell pane; it never creates, splits, or moves layout. An available shell pane sits at its interactive prompt with no foreground command, editor, or agent running.

Agent commands accept a unique live agent name or the pane ID hosting that agent, never a terminal ID or a bare agent-kind label. Names match `[a-z][a-z0-9_-]{0,31}`, stay unique among live agents, follow the current pane occupant, and are cleared when that agent exits, is released, or is replaced. A terminal restart can also clear a seat name while the underlying agent session survives on a new terminal; the surviving seat must be re-named and confirmed from the live agent list.

Lifecycle states:

- `idle` — ready for input, and its tab has been seen in the focused Herdr UI;
- `working` — actively processing a turn; not settled, not inspectable as a result;
- `done` — the same underlying idle state after unseen background work finishes;
- `blocked` — Herdr recognized an approval or question UI;
- `unknown` — an agent is present but Herdr cannot classify it confidently; this never proves completion.

Focusing the tab, or targeting the pane or agent with a focus command, marks it seen; CLI reads do not. A settled state means the agent can be inspected, not that the work is complete or accepted.

These states are inferred from the pane, not reported by the agent. Herdr matches the terminal title and recent screen text against a per-kind rule table under `~/.local/state/herdr/agent-detection/remote/<kind>.toml`, and `herdr agent explain <name>` prints the rule id, region, priority, and the exact evidence string behind the current state. `agent list` gives the label; `agent explain` gives the reason, and only the reason can be checked.

Read the staffed kind's own table before writing a wait against it, because `idle` is not always evidence of readiness. When no rule matches, a known agent falls back to `idle`, and `agent explain` says so in the open: `rule: none`, `fallback_reason: default_known_agent_idle_fallback`. Whether that fallback is doing the work is a property of the table. At manifest `claude` 2026.09.04.1 the kind carries sixteen rules, three of which assert `idle` positively — `live_prompt_box` at priority 950, `osc_title_idle` and `osc_progress_idle` at 250 — so an idle reading there usually has a rule behind it, subject to the separate seen/unseen distinction that reports the same settled seat as `done`. At manifest `agy` 2026.06.24.1 the kind carries three, one `blocked` at priority 300 and two `working` at 100 and 90, and none asserting `idle` at all, so every screen those three miss reads `idle` by fallback, including a seat genuinely mid-turn in a shape neither working rule matches. A wait for `idle` against such a seat can return at once and prove nothing, which is the opposite of the failure a wait is added to prevent.

The tables also rank states against each other, and that ranking decides what a busy seat looks like. For `claude`, `osc_title_working` matches the spinner glyph in the title at priority 1100, above every `blocked` rule, the highest of which is 980. Of that kind's five working rules exactly one, `background_mcp_task_working` at 965, excludes dialog text such as `do you want to proceed?` and `waiting for permission`; the rule that outranks the blocked rules is not the one carrying that guard. So a seat holding an approval dialog while its title still shows the spinner is resolved as `working`, not `blocked`. Whether a given agent clears its title on entering a dialog is that agent's behavior and is not settled by the table, which is the reason to derive a seat's state with `agent explain` and read the rule that fired rather than assume one. `agent prompt` refuses only a `blocked` target, so a report sent to a seat resolved as `working` is accepted rather than refused, and lands as queued input behind a dialog nobody has answered. Waiting for such a seat to stop being busy is not the remedy: `working` is not the state the refusal was keyed to, and no error is returned to recover from. A state is a sample and not a fact that survives the next command, and one seat here was reported `idle` by `agent list` and `working` by `agent get` seconds apart, so a wait that returns a settled state does not make the following prompt safe. The prompt's own outcome stays the only evidence that a report was delivered.

## Create a pane

Create a pane only to host an agent that has nowhere to run, or when the user explicitly asks for a pane. Reuse an existing available shell pane before splitting a new one. Default to a sibling pane in the current tab and the caller's working directory. Do not create a workspace, tab, or different cwd unless the user explicitly requests that topology or location. This workflow does not run delivery work in a second working tree, so `herdr worktree` is out of scope for topology; the single exception is the read-only baseline tree `lead-policy.md`, "Ownership and topology", defines, which is a diagnostic and not a place work happens.

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

`pane run` atomically sends the command text and Enter. `pane wait-output` searches the selected snapshot immediately, so output that already exists can match; use `--match <text>` for a literal substring or `--regex <pattern>` for a Rust regular expression. Omitting `--timeout` allows an indefinite wait, so pass one. When the pane has a `working` or `blocked` agent, `pane read` returns only the viewport without an error, so a large `--lines` is not proof of a complete read.

## Start and drive an agent

```bash
herdr agent start <name> --kind <kind> --pane <pane-id>
herdr agent start <name> --kind <kind> --pane <pane-id> -- <agent-args...>
```

Use the kind the user requested, and run `herdr agent` for the installed kind list. Native agent arguments go only after `--`; the permission arguments among them set the Peer's posture, which `peer-policy.md`, "Permission posture", defines — learn a kind's flags from its own `--help` at staffing, since they differ by kind and release. A successful `agent start` returns only after Herdr detects the expected agent in that pane and considers it ready for input; startup defaults to a 30-second timeout. If the agent is blocked during startup the command returns `agent_not_ready` immediately but keeps the name usable for `agent read` and `agent send-keys`; wait for it to settle before prompting.

```bash
herdr agent prompt <name> "<bounded task>"
herdr agent wait <name> --timeout 30000
```

`agent prompt` honors the pane's live bracketed-paste mode and sends text followed by encoded Enter. It refuses an agent already sitting at an approval or question dialog with `agent_blocked` before sending any input. Do not pass `--wait`: no seat in this workflow blocks on another's turn. `agent wait` has exactly ONE site - the startup settle after `agent_not_ready`, to let a freshly started agent settle before its charter; its default states cover that (`idle` means send the charter, `blocked` means a startup dialog to route as a Human decision). It is NOT used to recover a Lead-to-Supervisor send: that delivery is the append to the supervisor mailbox and the prompt is only a best-effort wake the Lead never waits on. It is never used on a Peer.

Reports arrive as prompts. A Peer's report wakes the Lead mid-turn or opens a new Lead turn, so the Lead ends its turn after dispatching and after each wake, and before ending any turn runs `herdr agent list` once to reconcile live Peers with the reports received (`lead-policy.md`, "Lifecycle and reports"). Do not poll `herdr agent list`, sleep in a loop, re-issue status commands, or block on a Peer with any wait.

Inspect through the resolved agent; the scrollback read here is for an `idle` or `done` Peer:

```bash
herdr agent get <name>
herdr agent read <name> --source recent-unwrapped --lines 120
```

After a `blocked` state, read `agent get` and `agent read --source visible` before deciding anything; for an `idle` or `done` Peer without a report, use `agent read --source recent-unwrapped`. A blocked dialog is answered only by the Human: classify it as a routine command approval or a gate (`human-gates-and-closeout.md`, "Approval dialogs") and never answer it by inference. `herdr agent send-keys <name> esc` writes logical keys and exists to resume an interactive UI after that decision, not to drive the agent's work.

## Name a seat

```bash
herdr agent rename "$HERDR_PANE_ID" lead-<project-slug>
herdr agent rename <target> --clear
```

Rename works on an unnamed agent, including the caller's own. A name follows the pane occupant and clears when that agent exits, so a seat that must be prompted by others — the Lead, the Supervisor, a Reviewer named after its head — is named before anyone needs it. A terminal restart is a fourth way a name is lost, even when the underlying session survives; re-name the surviving session and confirm it with `herdr agent list`.

## Report to the Lead by prompt

A Peer sends its report, verdict, or protocol message to the Lead's seat name, without `--wait`, after printing it in its own pane:

```bash
herdr agent prompt lead-<project-slug> "$(cat <<'REPORT'
# Report — <scope name>
...
REPORT
)"
```

The single-quoted delimiter in `<<'REPORT'` and, equivalently, reading text from a file with `"$(cat <file>)"` keep backticks and `$` literal; a plain double-quoted argument or an unquoted heredoc delimiter leaves them live for the shell to execute or expand before the send. Any prompt carrying code, backticks, or `$` - whether a Peer's report or a Lead's charter or relay - is composed by writing the text to a file by a means that does not invoke the shell, then sending it as `"$(cat <file>)"`. A rejected send — `agent_blocked` because the Lead sits at a dialog, or any error — is not retried: the Peer stops, and the Lead reads the pane at its next wake. The Lead's own refused report to the Supervisor is the single exception in this workflow, because nothing reads the Lead's pane the way the Lead reads a Peer's. This is the only `herdr` command a Peer runs.

## Notify the Human

```bash
herdr notification show "<title>" --body "<one line>" --sound request
herdr notification show "<title>" --body "<one line>" --sound done
```

A notification reaches the Human, not an agent. Popups depend on the Human's `[ui.toast] delivery` key in `~/.config/herdr/config.toml`; its default is `off`, so the notification is silent until the Human sets `herdr`, `terminal`, or `system`. That is the Human's config, never edit it. `human-gates-and-closeout.md` owns the only sites: `--sound request` when a Human gate opens, a product fork needs the Human, or a Peer stands at a routine approval only the Human can clear; `--sound done` once per merge under a standing waiver and once at final handoff. Do not notify for routine progress, Peer completions, or verdicts.

## Read sources

- `visible` — the rendered viewport;
- `recent` — recent rendered output including soft wraps;
- `recent-unwrapped` — recent output with soft wraps joined; prefer it for logs, transcripts, and reports;
- `detection` — the plain-text bottom-buffer snapshot used for agent detection.

Observed behavior in herdr 0.8.2: `herdr agent read <seat> --source recent` and `--source recent-unwrapped` return rows from the visible viewport without scrollback and capture scrollback only when `--lines` exceeds the viewport. That capture works only for an `idle` or `done` seat. For a `working` or `blocked` seat, a request past the viewport exits non-zero and writes stderr JSON with error code `agent_not_idle`.

`agent_not_idle` has two conditions and needs both together:

- **gate — seat state:** `working` or `blocked`, rather than `idle` or `done`;
- **trigger — read length:** a `--lines` value above the viewport.

Neither alone causes it. A `--lines` above the viewport against an `idle` or `done` seat succeeds, and a viewport-sized read against a `working` or `blocked` seat succeeds. So the fix is never a larger `--lines`: it is either the viewport (`--source visible`) now, or the same read once the seat is `idle` or `done`.

`--source visible` and `--source detection` always work and cap at the viewport. `herdr pane read <pane-id> --source recent-unwrapped` against a pane whose agent is `working` or `blocked` exits successfully but silently returns only the viewport, so a large `--lines` is not proof of a complete read. To read past the viewport, wait for `idle` or `done`; while `working` or `blocked`, use `herdr agent read --source visible` for the viewport and never use `pane read` to reach past it. This is observed behavior of this binary version.

`--lines` asks for more rows from the pane's screen and host scrollback. If raising it reveals no more of a completed response, the agent is probably running on the terminal's alternate screen: rows that leave it never enter host scrollback, so no line count recovers them. Only then, ask the agent to write its complete response as Markdown in a temporary directory and reply with the path, then read that file directly. Do not request file output in the initial prompt.

## Tear down an agent

There is no `herdr agent stop`. An agent clears when it exits, is replaced, or the pane hosting it closes. To tear down an agent this run staffed, close the pane this run created for it:

```bash
herdr pane close <pane-id>
```

Read the agent's evidence report first, since the pane's transcript is gone once it closes. When a native agent should exit cleanly first, send its own quit sequence with `herdr agent send-keys <name> ...`, wait for it to leave the pane, then close the pane. Close only a pane this run created to host that agent — a pane the Supervisor opened as the Human's hands to host a seat this run staffed counts as created by this run; never close the caller's pane, a pane hosting an agent this run did not staff, or a pane an agent shares with unrelated work. `herdr pane release-agent` is a low-level detection-plane report used with `--source`/`--agent`, not a teardown — do not use it to shut an agent down.

## Safety

- Use `--no-focus` for background work unless the user asked to switch context.
- Target `--current`, an explicit pane ID, or a unique agent name; never another client's focused pane.
- Do not close workspaces, tabs, panes, or sessions this run did not create unless the user explicitly asked.
- Never run `herdr server stop` from an active session unless the user explicitly intends to stop the server and its pane processes, and never kill the main Herdr process. Use a named test session for experiments needing an isolated server.
- CLI server errors are JSON on stderr with exit status 1; syntax errors exit 2.

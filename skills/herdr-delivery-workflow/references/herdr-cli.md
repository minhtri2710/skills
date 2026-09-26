# Herdr CLI

Read this before the first Herdr control command in any route. The installed binary is the authority for syntax; this file is the authority for how this workflow uses it. It is shared: `lead.md` and `supervisor.md` cite it.

## Preflight and discovery

Verify the caller is inside Herdr before any inspection or control command:

```bash
test "${HERDR_ENV:-}" = 1
```

If it fails, do not inspect or control the focused Herdr session from outside it: run no Herdr command and read or write no Herdr state under `~/.herdr`, directly or through this skill's scripts. Say the agent is not running inside Herdr; answer from this skill's doctrine if the request needs no Herdr access, reading whichever reference files it needs.

Learn syntax from the binary, not from memory: print a command group without a subcommand to see it (`herdr --help`, `herdr agent`, `herdr pane`). Do not run bare `herdr` — it launches or attaches the TUI. Do not probe a mutating nested command by omitting arguments; `herdr workspace create` is valid with defaults and will execute. Most control commands return JSON: read identifiers and state from those responses, never from sidebar order, pane order, or the examples here.

## IDs and caller context

Public IDs are opaque stable handles: workspace `w1`, tab `w1:t1`, pane `w1:p1`. Closed tab and pane IDs are not reused. Herdr injects the caller's context into every managed pane:

```bash
printf '%s\n' "$HERDR_WORKSPACE_ID" "$HERDR_TAB_ID" "$HERDR_PANE_ID"
```

Pass `--current` or an explicit pane ID whenever a pane command targets the calling pane. An omitted positional target — including for `herdr pane split`, which defaults to the globally focused pane — may hit a pane in another workspace or client session; the explicit current-pane target is mandatory, because focus is not a safe workspace or client boundary. Read live state with `herdr pane current --current`, `herdr pane list --workspace "$HERDR_WORKSPACE_ID"`, `herdr agent list`. For roster/Discovery reads, run `scripts/roster.py`, which calls `herdr agent list` itself and emits `pane name kind state` per agent (`--workspace <id>` to scope; `--stdin` only to feed already-captured JSON, as its tests do); use raw `herdr agent list` only when a dropped field is needed.

## Panes and agents

Prefer `herdr agent` as the default control surface: it validates agent identity and lifecycle state and drives prompts, waits, reads, and inspection. Reach for `herdr pane` only when no agent surface covers the need — opening or discovering a shell pane to host an agent, or driving a raw terminal, shell, test, or server no agent occupies. When a live agent occupies a pane, address the agent by name, not the pane, and do not duplicate an agent command with a pane command. `agent start` requires an existing available shell pane — one at its interactive prompt with no foreground command, editor, or agent running — and never creates, splits, or moves layout.

Agent commands accept a unique live agent name or the pane ID hosting that agent, never a terminal ID or bare kind label. Names match `[a-z][a-z0-9_-]{0,31}`, stay unique among live agents, follow the current pane occupant, and clear when that agent exits, is released, or is replaced. A terminal restart can clear a seat name while the underlying session survives on a new terminal; re-name the surviving session and confirm from the live agent list. Address a Peer only as the seat this run staffed it: the unique name its staffing record captured when the Lead took custody — at `agent start`, or when the Lead adopted an existing pipeline review agent under validation-run custody (`lead.md`, "Delivery sequence") — or that record's pane id when the name has since cleared (the terminal-restart case above). A name or pane id absent from this run's staffing record is never a Peer target, even when `agent list` shows it live — name resolution is global (`agent prompt` has no workspace scope), so a bare kind label or a pane in another workspace resolves to a foreign agent, and prompting it as a Peer is a custody breach, not a delivery message. A cross-role seat the run did not staff — the `supervisor` reached by `scripts/mailbox.py --wake`, a `lead-<slug>` a Supervisor relays to, an existing agent addressed on the Lightweight route — is reached by its own unique live name under the rule at the top of this paragraph, not through a Peer staffing record; the allowlist governs Peer addressing, not these.

Lifecycle states: `idle` (ready for input, its tab seen in the focused UI); `working` (actively processing a turn, not settled, not inspectable as a result); `done` (the same idle state after unseen background work finishes); `blocked` (Herdr recognized an approval or question UI); `unknown` (an agent is present but cannot be classified confidently — never proof of completion). Focusing the tab, or targeting the pane or agent with a focus command, marks it seen; CLI reads do not. A settled state means the agent can be inspected, not that the work is complete or accepted. Never alert on a single sample or a single idle label. A stall verdict is a conjunction re-sampled across an interval: a transition from prior non-settled state to current settled (`idle`/`done`), the charter-path report file absent, and the progress-file mtime stale without advancing. `agent_status` and `state_change_seq` are not trusted as sole liveness signals; the reliable signals are the token counter, owned-file mtime, and progress-file mtime. `scripts/roster.py --stalled` encodes this conjunction, using repeatable `--peer NAME:REPORT_PATH:PROGRESS_PATH`, `--previous-sample PATH` containing `{"peers":{"<name>":{"state":"<state>","progress_mtime":<number>}}}`, and `--stale-after SECONDS` (default 60); missing or unreadable progress fails closed and is not a stall. When the Lead has explicit no-prompt evidence, run `scripts/roster.py --never-started NAME --peer NAME:REPORT_PATH:PROGRESS_PATH`; it reports distinct `NEVER-STARTED` only for a settled current seat with both report and progress absent. This replaces no ordinary stall behavior and does not parse arbitrary pane text; a token counter may corroborate the explicit evidence but is never the verdict by itself.

These states are inferred from the pane, not reported by the agent: Herdr matches the terminal title and recent screen text against a per-kind rule table under `~/.local/state/herdr/agent-detection/remote/<kind>.toml`, and `herdr agent explain <name>` prints the rule id, region, priority, and exact evidence behind the current state. `agent list` gives the label; `agent explain` gives the checkable reason. Read the staffed kind's table before writing a wait against it, because `idle` is not always readiness: when no rule matches, a known agent falls back to `idle` (`agent explain` says `rule: none`, `fallback_reason: default_known_agent_idle_fallback`). A kind whose table asserts `idle` positively (such as `claude`) usually has a rule behind an idle reading; a kind whose table never asserts `idle` (such as `agy`) reads `idle` by fallback for every screen its rules miss, including a seat genuinely mid-turn — a wait for `idle` there can return at once and prove nothing.

The table also ranks states, which decides what a busy seat looks like. For `claude`, `osc_title_working` matches the spinner glyph in the title at priority 1100, above every `blocked` rule (highest 980), and is not the one rule (`background_mcp_task_working`, 965) that excludes dialog text like `do you want to proceed?`; so a seat holding an approval dialog with the spinner still in its title resolves as `working`, not `blocked`. `agent prompt` refuses only a `blocked` target, so a report sent to a seat resolved as `working` is accepted and lands as queued input behind an unanswered dialog. Waiting for it to stop being busy is no remedy — `working` is not the state the refusal keys to, and no error returns. A state is a sample, not a fact that survives the next command (`agent list` and `agent get` can disagree seconds apart), so a wait returning a settled state does not make the following prompt safe: the prompt's own outcome is the only evidence a report was delivered. Never restaff or re-prompt-to-redo a possibly-live seat that owns a path a replacement will also write without hard confirmation it is dead: first `herdr agent send-keys <seat> esc`, then verify the owned-file mtime and token counter stayed stable across a real interval. A false-positive restaff creates a double writer and partition breach. Derive a seat's state with `agent explain` and read the rule that fired rather than assume one.

## Create a pane

Create a pane only to host an agent that has nowhere to run, or when the user explicitly asks. Reuse an available shell pane before splitting, and both the reused pane and any pane you split stay in the Lead's recorded workspace — for the Lead running these commands that is `$HERDR_WORKSPACE_ID`; a Supervisor opening a Peer pane as the Human's hands (`supervisor.md`) targets a pane already in the Lead's recorded workspace with `herdr pane split --pane <id>` so the sibling lands there, rather than `--current` in its own workspace — never staff a Peer into a pane in another workspace. Default to a sibling pane in the current tab and the caller's working directory; do not create a workspace, tab, or different cwd unless the user requests that topology. Keeping every Peer in the Lead's workspace makes `scripts/roster.py --workspace "$HERDR_WORKSPACE_ID"` and `herdr pane list --workspace` a complete, foreign-free view of exactly this run's seats and closes the omitted-target hazard above by construction. This workflow runs no delivery work in a second working tree, so `herdr worktree` is out of scope for topology — the single exception is the read-only baseline tree (`lead.md`, "Ownership and topology"), a diagnostic, not a place work happens. Honor a requested direction; otherwise inspect the caller pane and split a wide pane right, a narrow or tall pane down, avoiding repeated same-direction splits that leave unusable columns or rows:

```bash
herdr pane layout --pane "$HERDR_PANE_ID"
herdr pane split --current --direction right --cwd "$PWD" --no-focus
```

Read the new pane ID from `.result.pane.pane_id` and keep the user's focus in the calling pane.

## Run a command in a pane

Use these only against a pane with no agent — a raw shell, test, or server. When an agent occupies the pane, prompt the agent instead; do not send commands past it with `pane run`.

```bash
herdr pane run <pane-id> "just test"
herdr pane wait-output <pane-id> --match "test result" --timeout 120000
herdr pane read <pane-id> --source recent-unwrapped --lines 120
```

Every `--timeout` value is sized to the command's real worst case; always pass `--timeout`. The `120000` above and the `30000` below are illustrative examples only, never defaults to borrow.

`pane run` atomically sends the command text and Enter. `pane wait-output` searches the selected snapshot immediately, so existing output can match; use `--match <text>` for a literal substring or `--regex <pattern>` for a Rust regex, and always pass `--timeout` (omitting it waits indefinitely). When the pane has a `working` or `blocked` agent, `pane read` returns only the viewport without error, so a large `--lines` is not proof of a complete read.

## Start and drive an agent

```bash
herdr agent start <name> --kind <kind> --pane <pane-id> -- <agent-args...>
```

Use the kind the user requested (`herdr agent` lists installed kinds). Native agent arguments go only after `--`; the permission arguments among them set the Peer's posture (`charters.md`, "Writing charters") — learn a kind's flags from its own `--help` at staffing, since they differ by kind and release. A successful `agent start` returns only after Herdr detects the expected agent and considers it ready; startup defaults to a 30-second timeout. If the agent is blocked during startup the command returns `agent_not_ready` immediately but keeps the name usable for `agent read` and `agent send-keys`; wait for it to settle before prompting.

```bash
herdr agent prompt <name> "<bounded task>"
herdr agent wait <name> --timeout 30000
```

`agent prompt` honors the pane's live bracketed-paste mode and sends text followed by encoded Enter. It refuses an agent already at an approval or question dialog with `agent_blocked` before sending input. Never pass `--wait`: no seat in this workflow blocks on another's turn. `agent wait` has exactly ONE site — the startup settle after `agent_not_ready`, letting a freshly started agent settle before its charter (its default states cover it: `idle` means send the charter, `blocked` means a startup dialog to route as a Human decision). It is never used to recover a Lead-to-Supervisor send (that delivery is the mailbox append, the prompt a best-effort wake the Lead never waits on) and never on a Peer.

For the Lead's report-by-prompt lifecycle and per-wake decision, see `lead.md`, "Lifecycle and reports". Its roster command mechanics use `scripts/roster.py` with `--workspace <id>` when scoped; use raw `herdr agent list` only when the compact roster omits a required field. On demand, `scripts/roster.py --drift <config.md> --seat <name>:engineer|reviewer` (one `--seat` per staffed Peer from the staffing record) reads each seat's launch arguments with `herdr pane process-info` and prints a `DRIFT` line for a seat whose kind or `--model` matches neither the role's primary nor its fallback keys; when `argv0` identifies a matching kind but its model cannot be verified, it prints an `UNVERIFIABLE` line and exits non-zero. Other arguments a charter adds are not drift.

Inspect through the resolved agent (this scrollback read is for an `idle` or `done` Peer): `herdr agent get <name>`, `herdr agent read <name> --source recent-unwrapped --lines 120`. After a `blocked` state, read `agent get` and `agent read --source visible` before deciding anything; for an `idle`/`done` Peer without a report, use `--source recent-unwrapped`. A blocked dialog is answered only by the Human: classify it as a routine command approval or a gate (`lead.md`, "Lifecycle and reports") and never answer by inference. `herdr agent send-keys <name> esc` writes logical keys to resume an interactive UI after that decision, not to drive the agent's work.

## Name a seat

```bash
herdr agent rename "$HERDR_PANE_ID" lead-<project-slug>
herdr agent rename <target> --clear
```

Rename works on an unnamed agent, including the caller's own. A name follows the pane occupant and clears when that agent exits, so a seat others must prompt — the Lead, the Supervisor, a Reviewer named after its head — is named before anyone needs it. A terminal restart is a fourth way a name is lost even when the session survives; re-name the surviving session and confirm with `scripts/roster.py`.

## Report to the Lead by prompt

The Peer report-send block belongs to `charters.md` ("Report by prompt"), including its durable file and failed-send handling. More generally, any prompt carrying code, backticks, or `$` is composed by writing the text to a file with the editor/write tool, or, for a seat without one, the quoted-delimiter form in `templates/report-by-prompt.txt`, then sending it as `"$(cat <file>)"`. The Lead's own refused report to the Supervisor remains a separate exception, because nothing reads the Lead's pane the way the Lead reads a Peer's.

## Notify the Human

```bash
herdr notification show "<title>" --body "<one line>" --sound request
herdr notification show "<title>" --body "<one line>" --sound done
```

A notification reaches the Human, not an agent. Popups depend on the Human's `[ui.toast] delivery` key in `~/.config/herdr/config.toml`; its default is `off`, so the notification is silent until the Human sets `herdr`, `terminal`, or `system`. That is the Human's config — never edit it. `lead.md`, "Gates and ledger", owns the only sites: `--sound request` when a Human gate opens, a product fork needs the Human, or a Peer stands at a routine approval only the Human can clear; `--sound done` once per merge under a standing waiver and once at final handoff (`closeout.md`, "Final handoff"). Do not notify for routine progress, Peer completions, or verdicts.

## Recall past records

To recall a past decision, reason, event, or prior artifact location older than the wake-time `last-read` mark, run `scripts/recall.py` with two or more query variants: the natural-language question and at least one technical-vocabulary variant (ids, slugs, SHAs, or filenames); optionally pass `--project <slug>` and `-n`. Then read only the cited span with `scripts/recall.py --get <path>:<from>:<count>`. Never cat a whole notebook, mailbox, or run directory for recall.

The wake-time mailbox read, `scripts/mailbox.py --headers --since <last-read>`, is unchanged for NEW mailbox entries; recall.py covers records older than `last-read`.

## Read sources

- `visible` — the rendered viewport;
- `recent` — recent rendered output including soft wraps;
- `recent-unwrapped` — recent output with soft wraps joined; prefer it for logs, transcripts, and reports;
- `detection` — the plain-text bottom-buffer snapshot used for agent detection.

Verified on herdr 0.9.0: `herdr agent read <seat> --source recent`/`recent-unwrapped` return rows from the visible viewport without scrollback, and capture scrollback only when `--lines` exceeds the viewport, and only for an `idle` or `done` seat. For a `working` or `blocked` seat, a request past the viewport exits non-zero with error `agent_not_idle`, which needs BOTH conditions together — gate: seat `working` or `blocked` (not `idle`/`done`); trigger: a `--lines` above the viewport. Neither alone causes it (a large `--lines` on an idle/done seat succeeds; a viewport-sized read on a working/blocked seat succeeds), so the fix is never a larger `--lines`: it is the viewport (`--source visible`) now, or the same read once `idle`/`done`. `--source visible` and `--source detection` always work and cap at the viewport. `herdr pane read` against a pane whose agent is `working`/`blocked` exits successfully but silently returns only the viewport, so a large `--lines` is not proof of a complete read.

`--lines` asks for more rows from the pane screen and host scrollback. If raising it reveals no more of a completed response, the agent is probably on the terminal's alternate screen — rows that leave it never enter host scrollback, so no line count recovers them. Only then, ask the agent to write its complete response as Markdown in a temporary directory and reply with the path, then read that file directly. Do not request file output in the initial prompt.

## Tear down an agent

There is no `herdr agent stop`. An agent clears when it exits, is replaced, or the pane hosting it closes. To tear down an agent this run staffed, close the pane this run created for it:

```bash
herdr pane close <pane-id>
```

Read and retain the Engineer's final evidence report before closing its pane; for a Reviewer, retain both the final report and `herdr agent read <name>` transcript first, since the pane transcript dies at close. If a native agent should exit cleanly, the supported optional stop attempt is exactly `herdr agent send-keys <seat> C-c C-c`; it is not teardown and does not replace the close. After evidence is preserved, the teardown action is exactly `herdr pane close <pane>` for the run-created recorded peer pane. Close only a pane this run created to host that agent — a pane the Supervisor opened as the Human's hands to host a seat this run staffed counts as created by this run; never close the caller's pane, a persistent Lead or Human Supervisor pane, a pane hosting an agent this run did not staff, or a pane an agent shares with unrelated work. `herdr pane release-agent` is a low-level detection-plane report (used with `--source`/`--agent`), not a teardown — do not use it to shut an agent down. The run's final pane-level invariant is checked by `scripts/closeout_check.py --staffing <run-staffing-record>`: it reads only the recorded Engineer/Reviewer panes through a fakeable Herdr boundary, fails closed on missing evidence, and never treats an agent lookup — including `agent_not_found` — as proof that an open pane was torn down.

## Safety

- Use `--no-focus` for background work unless the user asked to switch context.
- Target `--current`, an explicit pane ID, or a unique agent name; never another client's focused pane.
- Do not close workspaces, tabs, panes, or sessions this run did not create unless the user explicitly asked.
- Never run `herdr server stop` from an active session unless the user explicitly intends to stop the server and its pane processes, and never kill the main Herdr process. Use a named test session for experiments needing an isolated server.
- CLI server errors are JSON on stderr with exit status 1; syntax errors exit 2.

# Seat operations

The one definition of every operation this workflow performs on a seat. A seat is one terminal slot a Human or an agent works in. Doctrine cites an operation by name ("the `prompt` operation") and never names a tool command; the command for each operation is in `backend-<detected tool>.md`, read right after detection (`SKILL.md`, "Detection"). The installed tool stays the authority for its own syntax: learn it from the tool's own help, never from memory, and never probe a mutating command by omitting its arguments.

## Seat record

Every operation returns or takes this normalized record:

| Field | Meaning |
|---|---|
| `handle` | the routing key: one string that addresses the seat by itself |
| `name` | an optional label, or none |
| `state` | one of `backend.STATES` |
| `kind` | the agent kind running in the seat, or none |
| `cwd` | the seat's working directory |
| `argv` | the launched program's argv, where the tool reports it |
| `session` | the agent session `kind` and `value`, or none |

Errors are the `BackendError` kinds in `scripts/backend.py` (`SEAT_ERROR_KINDS`, `BackendUnavailable`, `Unsupported`). `not_found`: the seat is gone or never existed. `blocked`: the seat is at an approval or question dialog. `not_started`: a prompt started no turn. `unavailable`: the tool is missing, timed out, or failed to identify; the run stops, and nothing falls back to another tool. `unsupported`: this tool has no such operation (`Unsupported: <reason>` in its backend file); the caller fails closed or takes the degraded path the doctrine names for that operation.

## Names

A handle routes; a name is a label. Prompt, read, and close a seat by its handle. A name may be absent, follows each tool's own naming rule (`backend-<tool>.md`, `identify`), may be cleared by the tool, and routes nothing in this workflow.

## Addressing

Address a Peer only as the seat this run staffed it: the handle its staffing record captured when the Lead took custody — at `spawn`, or when the Lead adopted an existing pipeline review agent under validation-run custody (`lead.md`, "Delivery sequence"). A handle absent from this run's staffing record is never a Peer target, even when `list` shows it live; prompting it as a Peer is a custody breach, not a delivery message. A cross-role seat the run did not staff — the Supervisor reached by `scripts/mailbox.py --wake`, the Lead a Supervisor relays to, an existing agent addressed on the Lightweight route — is reached by its seat record or the handle the Human gave, not through a Peer staffing record.

## Seat records

`<state root>/<project-slug>/lead-seat` and `supervisor-seat` each hold one line, `<backend> <handle>`. A seat writes its own record from its own environment, only after `whoami` succeeds: `r=$(scripts/backend.py whoami [--backend <name>@<own handle>]) && printf '%s\n' "$r" > <record path>`, at start and again after a relaunch or re-staffing; a failed `whoami` leaves any existing record untouched. The Lead finds the Supervisor from `supervisor-seat` and the Supervisor finds the Lead from `lead-seat`; no route depends on a name. The `--backend` flag is for a seat whose environment matched several tools (`SKILL.md`, "Detection"). `scripts/mailbox.py` fails closed when the recorded backend differs from the detected one.

## Operations

Each operation lists what it does, its inputs, what it returns, and, where a script uses it, its `scripts/backend.py` method.

### `identify`

Returns this seat's own handle, confirmed with the tool. Input: none (the environment). Method `identify`; `scripts/backend.py whoami` prints it as the seat-record line. A failure is `unavailable`.

### `spawn`

Starts an agent in a new seat and returns its handle. Inputs: name, kind, argv, cwd. Take the full argv from `scripts/project_config.py --expand`; the generic fields are literal argv and data. Spawn only to host an agent that has nowhere to run, or when the Human asks. Record the returned handle and name in the staffing record at spawn. A spawn that returns before the agent is ready is settled with `wait` before the charter is sent. No script method.

### `prompt`

Sends text to a seat and submits it. Inputs: handle, text. Refuses a seat at an approval or question dialog (`blocked`); `not_started` means the text was sent but started no turn. Every Lead prompt to a Peer is working-first: the acknowledgement the tool returns after submission is the only evidence the send was accepted, and from an idle or done Peer a `working` acknowledgement is the evidence the turn started. A state read before the prompt is a sample and makes no send safe. An acknowledgement from an already-`working` seat proves nothing: read the seat once before the turn ends. A seat a state read resolved as `working` can still hold an unanswered dialog; the prompt then lands as queued input. A `blocked` seat goes to `lead.md`, "Approval dialogs". On `not_started`, read the seat once; never retype or resend the prompt. If the text is still unsubmitted, notify the Human with `notify` and record it in the run record. Method `prompt`.

Report to the Lead by prompt: the Peer's report-send block belongs to `charters.md` ("Report by prompt"), including its durable file and failed-send handling, and `scripts/backend.py` renders it (`send_block`). Any prompt carrying code, backticks, or `$` is composed by writing the text to a file with the editor/write tool, or, for a seat without one, the quoted-delimiter form in `templates/report-by-prompt.txt`, then sent from that file. The Lead's own refused report to the Supervisor is a separate exception, because nothing reads the Lead's seat the way the Lead reads a Peer's.

### `read`

Returns a seat's recent output. Inputs: handle, line count. Method `read_output`, which returns recent output with soft wraps joined; prefer that view for logs, transcripts, and reports, and the visible viewport for a seat that is `working` or `blocked`. History beyond the viewport is reliable only for an `idle` or `done` seat; for a `working` or `blocked` seat a request past the viewport returns only the viewport, or fails, depending on the tool. A larger line count is never the fix: read the viewport now, or the same read once the seat settles, and do not take a large line count as proof of a complete read. If raising the line count reveals no more of a completed response, the agent is probably on the terminal's alternate screen and no line count recovers the rest. Only then, ask the agent to write its complete response as Markdown in a temporary directory and reply with the path, then read that file directly. Do not request file output in the initial prompt. A seat whose agent may be gone (a retired predecessor, an agent that exited) is read as a terminal, not as an agent; the backend file names that read. `scripts/waker.py` infers waiting from a footer layout in the read text; on another tool's text it can miss, which only costs extra wakes.

### `state`

Returns a seat's `state`. Input: handle. Method `get_seat` (the `state` field). `idle`: ready for input. `working`: actively processing a turn, not settled, not inspectable as a result. `done`: idle after background work finished. `blocked`: at an approval or question dialog. `error`: the agent reports an error. `unknown`: present but not classifiable, or the tool does not report a state for this seat — never proof of completion. A settled state (`idle`, `done`) means the seat can be inspected, not that the work is complete or accepted. A state is a sample, not a fact that survives the next command. Never alert on a single sample or a single idle label.

A stall verdict is a conjunction re-sampled across an interval: a transition from a prior non-settled state to a settled one (`idle`, `done`), the charter-path report file absent, and the progress-file mtime stale without advancing. The state and its change counter are not trusted as sole liveness signals; the reliable signals are the token counter, owned-file mtime, and progress-file mtime. An `unknown` state never raises a stall by itself. `scripts/roster.py --stalled` encodes this conjunction; its flags and the stale default are in `scripts/roster.py --help`, and the previous-sample shape is the one that script's loader reads. Missing or unreadable progress fails closed and is not a stall. When the Lead has explicit no-prompt evidence, `scripts/roster.py --never-started NAME --peer NAME:REPORT_PATH:PROGRESS_PATH` reports distinct `NEVER-STARTED` only for a settled current seat with both report and progress absent. It replaces no ordinary stall behavior and does not parse arbitrary seat text; a token counter may corroborate the explicit evidence but is never the verdict by itself.

### `wait`

Blocks until a seat reaches one of the given states or the timeout passes, and returns the state reached. Inputs: handle, states, timeout. A requested state the tool never reports is ignored (herdr's `REPORTABLE` in `scripts/backends/herdr.py`); the call is refused only when none remain. Method `wait_state`. Always pass a timeout sized to the command's real worst case; a value in a command example is never a default to borrow. Only the waker uses it, plus once at the startup settle after a spawn that returned before the agent was ready: `idle` means send the charter, `blocked` means a startup dialog to route as a Human decision. It is never used to recover a Lead-to-Supervisor send (`lead.md`, "Supervisor and attention events") and never by a Peer. A wait returning a settled state does not make the following prompt safe. Where `wait` is unsupported the waker exits with that reason, and the Lead relies on report-by-prompt plus the roster. Peer waker timing is in `lead.md`, "Turn boundaries and roster".

### `list`

Returns the live seats as seat records. Method `list_seats`. `scripts/roster.py` prints one `handle name kind state` line per seat (`--workspace <id>` scopes it, where the tool has workspaces); it is the roster and discovery read. Read the tool's raw list only when a dropped field is needed. On Lead wake, roster reconcile runs once (`lead.md`, "Turn boundaries and roster"). `scripts/roster.py --drift <config.json> --seat <handle>:engineer|reviewer|architect` compares a seat's visible argv with the shared `project_config.py --expand` result; pass verified `--lead`, `--run-dir`, and `--installed-skill-dir` for placeholders; hidden evidence is `UNVERIFIABLE`.

### `processes`

Returns a seat's foreground processes, as `backend.Process` records (`argv`, `pid`, `cwd`). Input: handle. Method `processes` (the terminal behind a handle is `get_terminal`). `scripts/roster.py --drift` and `scripts/closeout_check.py` use it.

### `interrupt`

Stops a seat's current turn without ending the seat, and writes logical keys to resume an interactive UI after a Human decision — never to drive the agent's work. Inputs: handle, key. A blocked dialog is answered only by the Human: classify it as a routine command approval or a gate (`lead.md`, "Lifecycle and reports") and never answer by inference. Before restaffing a possibly-live seat, confirm it dead (`lead.md`, "Workspace custody"); the interrupt is how a live one is stopped. No script method.

### `close`

Ends a seat this run created and every process in it. Input: handle. Read and retain the Engineer's final evidence report before the close; for a Reviewer, retain both the final report and the `read` transcript first, since the transcript dies at close. A tool may document an optional clean-exit attempt; it is not teardown and does not replace the close. `closeout.md`, "Per-issue agent teardown", owns which seats may be closed and the `scripts/closeout_check.py` check. Never close a seat, container, or session this run did not create unless the Human explicitly asked. No script method.

### `notify`

Raises a message to the Human, not to an agent. Inputs: title, one-line body, urgency `request` or `done`. Returns delivered or not delivered. Do not notify for routine progress, Peer completions, or verdicts; `lead.md`, "Directional channels", owns the sites. Where a tool cannot deliver, the gate text still stays in the Lead's own seat and goes to the Supervisor by mailbox and prompt. Never edit the Human's notification config. No script method.

## Recall past records

To recall a past decision, reason, event, or prior artifact location older than the wake-time `last-read` mark, run `scripts/recall.py` with two or more query variants: the natural-language question and at least one technical-vocabulary variant (ids, slugs, SHAs, or filenames); optionally pass `--project <slug>` and `-n`. Then read only the cited span with `scripts/recall.py --get <path>:<from>:<count>`. Never cat a whole notebook, mailbox, or run directory for recall.

The wake-time mailbox read, `scripts/mailbox.py --headers --since <last-read>`, is unchanged for NEW mailbox entries; `recall.py` covers records older than `last-read`.

# Backend: herdr core (`hc`)

Read this after detection returns `hc`. It lists each seat operation as a command with the source that documents it, and what is still unproven. `hc.py` builds the argv for identify, prompt, read, state, wait, list, and processes; spawn, interrupt, and close are reference-only, because the seam has no such operations yet (`backend.py` docstring), so the adapter has no method for them. Nothing here was run: no `hc`, `herdr-core`, or `herdr` command has been executed for this reference, so every operation is provisional until the Human's live proof (L1-L8).

Sources, all read only at herdr-core commit 52d7c56 (v0.1.17): `HCM` = `crates/herdr-core/src/SKILL.md` (printed by `hc --skill`), `CMD` = `docs/commands.md`, `SCHEMA` = `schema/hc.openrpc.json`, other paths are under `crates/herdr-core/src/`. Confidence for hc is the source file and line; a claim with no source line is marked as an inference.

Rules for every operation:

- **Binary.** `~/.local/bin/herdr-core` when it is an executable file, else `hc` on PATH (the installer links `hc` only when none exists, and some window managers ship one: `distribution/install.sh:70-81`). The adapter resolves this once when it is built. A failed `identify` through the resolved binary is `BackendUnavailable`; nothing falls back to another binary.
- **Core pin.** Every call runs with `HC_SOCKET` set to this seat's `HC_TERMINAL_SOCKET`, so the call reaches the core that issued `HC_TERMINAL_ID` (`paths.rs:27-30` reads `HC_SOCKET` first; `client.rs:251-256` then accepts the id). The environment is passed to the child process and never printed.
- **Handle.** The terminal address (`t7`). Names (`eng-a`) are accepted wherever a `<t>` is (`CMD:210-223`); the `machine/t7` form is out of scope. A ref is checked against `^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$` before it becomes an argv word, so it is never read as an option.
- **JSON.** Every command except `read` is called with `--json` (`CMD:56-57`; `cli.rs:199-205`). A failure prints `{"error": {"kind", "message", "hint"}}` on stderr (`cli.rs:207-218`). The adapter maps kind `not_found` (exit 3) to `SeatError not_found` and `blocked` (exit 9) to `SeatError blocked` (`rpc.rs:55-70`, `HCM:214-215`); every other kind (`live`, `finished`, `status_mismatch`, `name_taken`, `unavailable`, ...) is a `BackendError` whose `code` is that kind.
- **State.** hc reports a state only when the program emits OSC 7501 (`HCM:176-178`; `status.rs:43-57`). `idle working done blocked error` pass through; a live terminal that reports nothing is `unknown`; a finished terminal is `done` on exit code 0 and `error` otherwise (the terminal record's `state` is `finished`, `terminals.rs:35-36`; the exit-code mapping is an inference, not an hc word).
- **Notes.** hc types `<hc from=...>` notes about a child into its parent by default (`CMD:495-497`; `HCM:87-103`). Peers are spawned with `--no-parent` so only the explicit report-by-prompt `hc send` arrives.

## identify

Command: `hc get <t> --json` with `<t>` = `$HC_TERMINAL_ID`, run with `HC_SOCKET` = `$HC_TERMINAL_SOCKET`.

Source: `hc get` with no target never resolves the caller (it opens a picker or fails `needs_target`: `cli.rs:231-258`, `cli.rs:437-442`), so the target is explicit. `CMD:210-223`; `HC_TERMINAL_ID` and `HC_TERMINAL_SOCKET` are set on every child (`api/run.rs:204-205`); the socket pin is above. Identify succeeds only when the record's `address` equals `$HC_TERMINAL_ID` and its `state` is `live`; any other outcome is `BackendUnavailable`. Side effect: every hc call connects through `connect_or_start`, and on Unix autostart is always allowed (`client.rs:73-96`; `platform/unix.rs:30-32`), so an identify with a stale `HC_TERMINAL_SOCKET` whose core has exited starts a new core at that socket, carrying the caller's environment, before it fails `not_found` as `BackendUnavailable`. No documented flag keeps `get` from starting a core.

Provisional: L3 (a live `hc get "$HC_TERMINAL_ID" --json` from inside a terminal returns that terminal; a stale same-core id from a tool started inside an hc terminal is not excluded by this check; also whether a stale-socket identify leaves a background core behind) and L7 (nested detection). Test: `IdentifyTest`.

## spawn

Command: `hc run --bg --json --no-parent --name <name> --cwd <dir> -- <argv>...` (returns the new terminal's `address`). Reference-only: the seam has no spawn.

Source: `CMD:479-504` (`--bg`, `--name` 1-32 of `a-z 0-9 - _`, `--cwd`, `--no-parent`); agents run with `--bg` and interactively, never one-shot print mode (`HCM:27-30`); the `--` before the program is the form at `HCM:127`; `--json` on a run: `cli.rs:388-418`. Put the first task in the argv (`claude "task"`), because a `send` to a booting agent can be dropped (`HCM:32-33`). A lone argv string holding whitespace or a shell sign runs as a shell line (`cli.rs:691-696`), so pass a program and its arguments as separate words. Use an absolute `--cwd`: hc resolves a relative one against the caller's directory (`cli.rs:707-714`). hc has no agent-kind concept, so no kind is passed; a seat's kind is read back from its argv. Template rule: `terminal_run` first loads `argv[0]` as a template, and a file `~/.config/herdr-core/templates/<argv0>.md` makes the run `sh -c <template command>` with `argv[1..]` joined as the task (`api/run.rs:5-14`; `templates.rs:76-86`); an `argv[0]` containing `/` or starting with `.` is never a template (`templates.rs:77`). Option-like words after a template name (`--name`, `--cwd`, `--json`, ...) are lifted out of the task and read as hc's own flags (`cli.rs:626-686`). The `--` does not prevent either, so a bare `argv[0]` is literal only while no template of that name exists; pass the absolute program path (`project_config.py --expand` can supply one). No workspace or tab exists (`AGENTS.md:22-24`): Peers are flat terminals, and the "peers sit in the Lead's workspace" rule is herdr-only.

Provisional: L3 (`--no-parent` Peers survive a Lead restart and produce no duplicate `<hc from=...>` notes), L1 (the spawned agent's state), L5 (a fenced `sandbox-exec` Peer: no source shows one started by `hc run`), and the template rule above (no live check; it depends on the Human's template directory).

## prompt

Command: `hc send --json <t> <text>`

Source: `CMD:518-536`; pastes the text and presses Enter, refuses a `blocked` terminal unless `--force` (the adapter never passes it), `input.rs:154-176`. The result's `started` is true or false after a window of 5 seconds, and null when the program never reports status (`input.rs:70-72,203-212`); `false` is raised as `SeatError not_started` (the text was typed; read before resending, `HCM:48-51`), `null` is accepted because no acknowledgement exists. `--wait` is not used: it holds the call for the whole turn (`CMD:532-533`). The send text must not start with `-`: it would be read as an option, and no end-of-options form is documented for `send`, so the adapter refuses it (`ValueError`) before running anything. The same holds for the Peer's send file in the report block below.

Report block: `send_block` renders `hc send <lead> "$(cat <run-dir>/send-<peer>.txt)"` when the adapter resolved `hc`, and `"$HOME/.local/bin/herdr-core" send <lead> "$(cat ...)"` when it resolved that file, so a foreign `hc` on PATH never receives a report (the installer links `hc` only when none exists, `distribution/install.sh:70-81`). There is no notification line (see notify). The Peer's own shell is assumed to have the same `$HOME` and a standard PATH; no source shows it.

Provisional: L1 (a seat that does not emit OSC 7501 never acknowledges), and the report block (L3: a Peer's shell resolves the rendered binary and the core). Test: `ReadPromptTest`, `SendBlockTest`.

## read

Command: `hc read --lines <n> <t>`

Source: `CMD:448-462`; prints plain text, not JSON, when piped (`cli.rs:465-480`). While the program is `working`, `blocked`, or `error`, history reads return only the screen, and the text ends with a `[hc] only its screen: ...` note (`HCM:64-67`; `cli.rs:469-476`); `--lines 0` reads only the visible screen.

Provisional: L1 (which agents report a state decides how often the history is cut). Test: `ReadPromptTest`.

## state

Command: `hc get <t> --json` (the record's `status.state`, normalized by the rule above).

Source: `CMD:210-223`; `Terminal.status` and `Terminal.state` in `SCHEMA` components.schemas.Terminal and `terminals.rs:14-60`; the status record `status.rs:14-29`. A bare `hc ls --json` row carries the word only (`cli/output.rs:142-155`).

Provisional: L1 (whether `claude`, `pi`, `omp` emit OSC 7501 is not stated in the sources; until it is shown a seat's state is `unknown`, and `roster.py --stalled` never fires on `unknown` by itself). Test: `NormalizeTest`.

## wait

Command: `hc wait --json --timeout <s> <t>`

Source: `CMD:626-655`; `HCM:69-85`. The wait ends when the terminal stops working or exits (`reason` `status` or `exit`), at the timeout (`reason` `timeout`), or when a message reaches the caller (`reason` `message`) (`wait.rs:23-50`). After a return the adapter says which state was reached: the reported `status` word, or `done`/`error` from the exit code. The caller of `hc wait` is this seat's own terminal (the pinned `HC_TERMINAL_ID`), so a message typed into it while it works ends any single-terminal wait (`cli.rs:353-357,717-719`; `api.rs:458-469`; `wait.rs:106-149`). That message is already in the caller's input (`HCM:80-81`), so on `message` the adapter issues the same `hc wait --json --timeout <remaining> <t>` again, up to one deadline computed once from `timeout_ms`; hc removes the message entry as it returns (`wait.rs:148`), so the retry does not spin. The re-wait also consumes the Lead's pending-message flag, which would otherwise end a Lead's own `hc wait`; the doctrine has the Lead never call `hc wait`. A `timeout` return, a `message` return at the deadline, or a state outside the requested set (for example `idle` when the caller asks only for `done`) raises `BackendError` with that `code` (`timeout`, `state_not_requested`) instead of looping. The timeout is whole seconds, rounded up, at least 1.

Provisional: L1 (a program that never reports status normally waits for exit, `HCM:84-85`; messages are recorded only for a Lead that reports `working`). Test: `WaitTest`.

## list

Command: `hc ls --json`

Source: `CMD:304-316`; the JSON is `{"terminals": [...], "hidden_finished": n}` with one short row per terminal: address, name, state, turn, cwd, `status` as the bare word, `agent` (`cli.rs:420-436`; `cli/output.rs:142-155`). The rows carry no argv, so list seats have an empty `argv`; `hc get` has it. `hc ls` lists every live terminal on the core, not only this run's (`HCM:56,203`): the caller keeps the seats the staffing record names. Finished terminals are listed only with `--all`, which the adapter does not pass.

Provisional: L1 (state of each seat). Test: `NormalizeTest`.

## processes

Command: `hc get <t> --json` (the record's `foreground`).

Source: the terminal record's `foreground` is `{pid, name, argv, cwd}` of the foreground process group leader (`SCHEMA` components.schemas.Foreground; `foreground.rs:12-21`, refreshed about twice a second, `foreground.rs:154-162`). The adapter returns that one process with `argv0` added, or an empty list when the record has none (a finished terminal). It does not list the rest of the group, which no source documents. The design (section 3) marked the foreground list missing; the schema shows this one-process form. A seat with no live process is also visible as terminal `state` `finished`.

Provisional: L3 (no L item names it; proposed: add one live `hc get` on a terminal running a dev server to L3). Test: `ProcessesTest`.

## interrupt

Command: `hc interrupt --json <t>` (reference-only: the seam has no interrupt).

Source: `CMD:225-239`; presses esc when the program reports a status, else ctrl+c, reports the observed effect, and never escalates (`HCM:61`; `api.rs:106-108,544-556`). The outcome word is `stopped`, `exited`, `still_working`, or `unknown` (`api.rs:549-554`). The `hc keys` command is not used.

Provisional: L1 (the esc-or-ctrl+c choice depends on the program reporting status). Test: golden and allow-list in `ReferenceTest`.

## close

Commands: `hc kill --json <t>` then `hc rm --json <t>` (reference-only: the seam has no close).

Source: `CMD:273-286` (kill: hangup, then escalate), `CMD:464-477` (rm: a finished terminal only; a live one fails with kind `live`, `api.rs:297-312`); the manual says to kill then remove only terminals this run started, because `hc ls` includes the user's other work (`HCM:202-203`). Peers spawned `--no-parent` do not end with the Lead, so the Lead closes each one itself. If `kill` fails, do not run `rm`.

Provisional: L3 (`--no-parent` Peers outlive a Lead restart: the cleanup path). Test: golden and allow-list in `ReferenceTest`.

## notify

Unsupported: hc has no Human-notification command; no source in `crates/`, `docs/`, or the README documents one, and a child's blocked, error, or exit news goes to its parent agent, not the Human (`HCM:101-103`). The gate text stays in the Lead's pane and goes to the Supervisor by prompt (design 3.1, Q6 A). The report-by-prompt block for hc has no notification line.

Provisional: none pending; Unsupported is the decided state and no live run can supply a mechanism.

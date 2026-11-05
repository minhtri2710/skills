# Rex backend

Read after detection selects `rex`. Every command here comes from a third-party adapter or an adapter's recorded live run; no Rex-authored document was available and `rex __internal skill` was never run. Nothing below was run by this skill's authors: the whole backend is provisional until the live items L1-L8 (design 9.4) pass.

Confidence tags: **CL** confirmed live by a third-party adapter on a Rex build (firstmate 0.0.1792607779..0.0.1792787366, sidekick build 1696); **CD** confirmed in adapter code only; **IS** only a name in the CLI binary's strings; **UV** unverified or conflicting sources. Sources are three third-party repositories, cited as `firstmate/` (`bin/backends/rex.sh` = `rex.sh`, `docs/rex-backend.md`, `docs/verification/runtime-backends.md` = `runtime-backends.md`), `munsu/internal/pane/rex.go`, `sidekick-ultra.nvim/` (`lua/sidekick-ultra/backends/rex.lua`, `tests/fixtures/rex/UNVERIFIED.txt`); `UNVERIFIED.txt` is also copied into `tests/fixtures/backends/rex/`.

A seat handle is `<session-id>.<block-id>`, for example `session:<uuid>.block:<uuid>`; split on the `.`, pass the halves as `-s <S>` and `-b <B>` on every call (without `-s` the CLI defaults to the caller's own `REX_SESSION`, `rex.sh:36-40`). Ids contain colons and, **inferred**, no dot. Exit codes: 0 ok, 2 invalid command line, 3 target not found (also an ambiguous label), 4 server unreachable (CL, `runtime-backends.md:2319-2320`). The adapter runs each command as `rex --autostart=false -S <endpoint> <args>` (`rex.sh:43-47`, `rex.go:52`); the `<endpoint>` is from `identify`. The binary is `$REX_BIN_DIR/rex` when executable, else `rex` on PATH (`rex.sh:87-102`; no `rex` is on PATH on the Human's machine at design time).

A seat's name is its block label; the handle, not the name, is authority.

The Peer report send block (`send_block`, from `prompt`) is rendered as `"$REX_BIN_DIR/rex" send -s <S> -b <B> -- "$(cat <run-dir>/send-<peer>.txt)" && "$REX_BIN_DIR/rex" send-key -s <S> -b <B> enter`. It uses `$REX_BIN_DIR/rex` because Rex exports `REX_BIN_DIR` into every block but shell startup files commonly reset `PATH` (CD, `rex-backend.md:19-20`, `rex.sh:81-85`); a bare `rex` may not resolve in a Peer's shell. It omits `-S` and `--autostart=false`: the Peer runs in the same server and `REX_SERVER` is not trusted either way. UV: that `REX_BIN_DIR` is set in a Peer's ordinary shell. Provisional: L2. There is no waker backstop on Rex (`wait`), so a failed send shows only as the `SEND-FAILED` line in the report file.

## identify

```
rex whoami --json
rex block ls -s <S> --json
```

`whoami` is the one call without `-s`, `-b` or `-S`; the `block ls` and every later call carry `-S <endpoint>`. Own handle: `$REX_SESSION.$REX_BLOCK` (CD/CL, `rex-backend.md:37-38`). `whoami --json` gives `.endpoint`, the server the CLI resolves (CL, `runtime-backends.md:2321`; `REX_SERVER` is not trusted, sources conflict). `block ls` proves the own block is listed in the own session (CD, `rex.go:109-112`; shape `.blocks[]{block_id,label,window_id}`). Any failure is `BackendUnavailable`.
Provisional: `block ls` has no live record and no L item names it; confirm it in the first live run on Rex. Nested detection (a Rex started inside another tool) is L7.

## spawn

```
rex split -s <S> -b <anchor-B> --split=right -c <dir> --focus=false --json -- <argv...>
rex block rename -s <S> <B> <name>
```

`split` returns `.block_ids[0]`; the new handle is `<S>.<that id>` (CL, sidekick `rex.lua:274`; the raw reply was never dumped, `UNVERIFIED.txt`). Peers go in the Lead's session: `<S>` and `<anchor-B>` are the Lead's own. `split` has no env flag; pass env as `/usr/bin/env K=V <argv...>` (CL, `rex.lua:275-282`). The `rename` sets the display label (CD, `rex.go:218`). Alternative one-step spawn: `rex run -s <S> -c <dir> --label <name> --shell=none --keep-open --focus=false --json -- <argv...>` returns `.block_ids[]` (CD, `rex.go:187`); a `--shell=none` block gets the server's PATH, so argv0 must be absolute.
The adapter has no spawn method; the Lead runs these. A fenced Peer (macOS `sandbox-exec` shell) is Unsupported until proven: no source shows an agent started inside a Rex block shell.
Provisional: the `split` reply shape and `--shell=none` argv0 behavior have no L item and need the first live run on Rex; the fenced Peer is L5.

## prompt

```
rex block call -s <S> -b <B> program_status
rex send -s <S> -b <B> -- <text>
rex send-key -s <S> -b <B> enter
```

`send` types literal text without Enter and refuses empty input; `send-key enter` submits (CL, `rex.sh:546-584`, `UNVERIFIED.txt` run 3). The adapter reads `program_status` first and refuses a `blocked` seat (`SeatError` blocked); if the status is unreadable it sends anyway and the send is unacknowledged. There is no turn-started acknowledgement: it never raises `not_started`, and a prompt is `sent`, not `started`. The status call is CL in firstmate and disputed by sidekick (`UNVERIFIED.txt`). UV: multi-line `send` text submitting once with one `enter`, the turn-start acknowledgement, and the blocked-refusal path (design 3, 3.1).
Provisional: those three UV items are L2.

## read

```
rex capture -s <S> -b <B> --trim
```

Plain text, scrollback plus screen, trailing blank rows dropped; no viewport-only read (CL for `capture`, `runtime-backends.md:2327`; CD for the `--trim` flag, `rex.sh:620-628`). The adapter strips `\r` and keeps the last N lines.
Provisional: no L item pending; the reply was not recorded, only the command.

## state

```
rex block call -s <S> -b <B> program_status
```

Reply `{"records":[{state,kind,app,msg,owner}]}`, state `working|done|blocked|error` (CL firstmate `runtime-backends.md:2374-2392`; sidekick lists a non-empty reply as unverified). The adapter reports the most urgent record in the order blocked, error, working, done; no record means `unknown`. A seat that does not emit OSC 7501 stays `unknown`, which never raises a stall by itself.
Provisional: which agent kinds emit OSC 7501 is L1.

## wait

Unsupported: `rex wait` exists in the binary strings but its semantics, exit codes and JSON are UV (IS, `rex wait -s "$REX_SESSION" "$test_block" --for 30s --json`), and no adapter uses it. The confirmed-live path is a server-side Lua script (`rex --autostart=false do -s <S> --for <N>s <script.lua>` with `rex.on("terminal.program_status_changed", ...)`, CL `runtime-backends.md:2330`), which the adapter does not build (design 3.2). `wait_state` raises `Unsupported`; the waker exits with that reason and the Lead relies on report-by-prompt and the roster.
Provisional: L4 decides `rex wait` or the Lua path.

## list

```
rex block ls -s <S> --json
rex block call -s <S> -b <B> program_status
```

One `block ls` for the Lead's own session, then one `program_status` per block (CD, `rex.go:109-112`). A block that closes between the two calls is skipped. Every block is listed, including plain shells; `name` is the label (empty is `None`), `workspace` is the session id; `kind`, `cwd` and `argv` are not set, because no source maps a foreground process to an agent kind (codex's `argv0` is `node`). `roster.py --drift` therefore raises `no - process in pane ...` for every named rex seat and exits 1: model drift is unsupported on Rex until a kind source exists. Plain `roster.py` listing, `--stalled` and `--never-started` do not need `kind`.
Provisional: `block ls` shape is CD only (see identify).

## processes

```
rex block call -s <S> -b <B> process
```

Returns the `foreground` object (`pid`, `name`, `argv0`, `cwd`, ...; the recorded builds have no `argv`, which the design matrix assumed) as the single process, or none when the block has no foreground (CL, `runtime-backends.md:2325`, sidekick fixtures `process_*.json`). `ancestors[]` appears in one build and not another and is not used; the no-foreground reply is a guess (`UNVERIFIED.txt`). A reply with neither `foreground` nor `last_exit` fails closed.
Provisional: none pending an L item; the no-foreground shape is unverified.

## interrupt

```
rex send-key -s <S> -b <B> escape
rex send-key -s <S> -b <B> ctrl+c
```

Key names `escape` and `ctrl+c` verified live (CL, `rex.sh:555-571`, `runtime-backends.md`). The adapter has no interrupt method; the Lead runs it. Send `escape` first, `ctrl+c` only to end a seat that ignores it.
Provisional: none pending an L item.

## close

```
rex block close -s <S> <B>
```

Closes the block; closing a window's last block closes the window, and an emptied session stays until `rex kill <S>` (CL, `runtime-backends.md:2331`, `rex.go:440`). This form takes the block id positionally, not with `-b`. Later reads of the block exit 3. Close only after the closeout evidence, as for any seat. The adapter has no close method; the Lead runs it.
Provisional: none pending an L item.

## notify

```
rex block call -s <S> -b <B> process
ps -o tty= -p <pid>
printf '\033]777;notify;<title>;<body>\a' >> /dev/<tty>
```

An OSC 777 desktop notification written to the block's own terminal device; Rex streams it as `desktop_notification` (CD, `rex-backend.md:135,139`; `rex.sh:1314-1321` for the device from the `process` pid, `.foreground.pid` else `.child.pid`, and `ps -o tty=`; `rex.sh:1361-1380` for the sequence and the write). The source replaces `;` with `,` and BEL, ESC, CR and LF with spaces in title and body, and clips the body to 120 characters. A client outside the block cannot raise one, so the Lead runs it inside its own block. The adapter has no notify method, and the gate text always stays in the Lead's pane as well. It is not part of the Peer's report-by-prompt block: no source shows a Peer's write raising the Lead's notification.
Provisional: L8.

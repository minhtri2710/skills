"""Rex adapter: pure argv builders and parsers over one injected runner (provisional, see references/backend-rex.md).

A seat handle is `<session-id>.<block-id>`. Every call that targets a block passes `-s` and `-b`;
after identify, every call also passes `-S <endpoint>` from `rex whoami --json`. The runner takes
(args, timeout) and returns a subprocess.CompletedProcess; `wait_state` stays Unsupported (design 3.2).
"""
from __future__ import annotations

import functools
import json
import os
import re
import subprocess
from collections.abc import Callable, Mapping
from typing import Any

import backend

BINARY = "rex"
DEFAULT_TIMEOUT = 30.0
EXIT_NOT_FOUND = 3
EXIT_UNREACHABLE = 4
# The seat reports its most urgent program_status record (Rex gives no single seat state).
_STATE_ORDER = ("blocked", "error", "working", "done")
_REPORT_PATH_RE = re.compile(r"(?P<dir>.+)/report-(?P<peer>[^/]+)\.md")
_UNSAFE_IN_DOUBLE_QUOTES = frozenset('"$`\\\n')

Runner = Callable[..., "subprocess.CompletedProcess[str]"]


def _binary(environ: Mapping[str, str]) -> str:
    """Rex puts the CLI on REX_BIN_DIR, not always on PATH (firstmate rex.sh fm_backend_rex_bin)."""
    bin_dir = environ.get("REX_BIN_DIR")
    candidate = os.path.join(bin_dir, BINARY) if bin_dir else None
    return candidate if candidate and os.access(candidate, os.X_OK) else BINARY


def run(args: list[str], *, timeout: float = DEFAULT_TIMEOUT, binary: str = BINARY) -> subprocess.CompletedProcess[str]:
    command = [binary, *args]
    label = BINARY + (" " + " ".join(args[:3]) if args else "")
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise backend.BackendUnavailable(f"{label} timed out after {timeout} seconds") from exc
    except OSError as exc:
        raise backend.BackendUnavailable(f"{label} unavailable: {exc}") from exc


def _object(text: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _split(handle: str) -> tuple[str, str]:
    session, dot, block = handle.partition(".")
    if backend.HANDLE_RE.fullmatch(handle) is None or not (dot and block) or "." in block:
        raise ValueError(f"not a rex seat handle <session-id>.<block-id>: {handle!r}")
    return session, block


class Adapter(backend.Backend):
    name = "rex"

    def __init__(self, environ: Mapping[str, str], runner: Runner | None = None) -> None:
        super().__init__(environ)
        self._runner = runner or functools.partial(run, binary=_binary(environ))
        self._endpoint: str | None = None  # set by identify from `rex whoami --json`

    def _call(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        pin = ["-S", self._endpoint] if self._endpoint else []
        completed = self._runner(["--autostart=false", *pin, *args], timeout=DEFAULT_TIMEOUT)
        code = completed.returncode
        if code:
            message = f"{BINARY} {' '.join(args[:3])} failed: exit {code}"
            if code == EXIT_NOT_FOUND:
                raise backend.SeatError("not_found", message)
            if code == EXIT_UNREACHABLE:
                raise backend.BackendUnavailable(message)
            raise backend.BackendError(message, code=f"exit_{code}")
        return completed

    def _json(self, args: list[str]) -> dict[str, Any]:
        return _object(self._call(args).stdout)

    def _own(self) -> tuple[str, str]:
        handle = backend.own_handle("rex", self.environ)
        if handle is None:
            raise backend.BackendUnavailable("rex: no own handle in the environment")
        try:
            return _split(handle)
        except ValueError as exc:
            raise backend.BackendUnavailable(f"rex: {exc}") from exc

    def _blocks(self, session: str) -> list[dict[str, Any]]:
        blocks = self._json(["block", "ls", "-s", session, "--json"]).get("blocks")
        if not isinstance(blocks, list) or not all(
            isinstance(block, dict) and isinstance(block.get("block_id"), str) for block in blocks
        ):
            raise backend.BackendError("rex block ls returned no blocks list")
        return blocks

    def _status(self, session: str, block: str) -> str:
        records = self._json(["block", "call", "-s", session, "-b", block, "program_status"]).get("records")
        if not isinstance(records, list) or not all(isinstance(record, dict) for record in records):
            raise backend.BackendError("rex program_status returned no records list")
        states = {record["state"] for record in records if isinstance(record.get("state"), str)}
        return next((state for state in _STATE_ORDER if state in states), "unknown")

    def _lookup(self, ref: str) -> tuple[str, dict[str, Any]]:
        """A handle names its block; a bare name is a block label in this seat's own session."""
        if "." in ref:
            session, block = _split(ref)
            entries = [entry for entry in self._blocks(session) if entry["block_id"] == block]
        else:
            session = self._own()[0]
            entries = [entry for entry in self._blocks(session) if entry.get("label") == ref]
        if not entries:
            raise backend.SeatError("not_found", f"rex has no block {ref}")
        if len(entries) > 1:
            raise backend.BackendError(f"rex label {ref} names {len(entries)} blocks", code="ambiguous")
        return session, entries[0]

    def _target(self, ref: str) -> tuple[str, str]:
        if "." in ref:
            return _split(ref)
        session, entry = self._lookup(ref)
        return session, entry["block_id"]

    @staticmethod
    def _seat(session: str, entry: Mapping[str, Any], state: str = "unknown") -> backend.Seat:
        return backend.Seat(
            handle=f"{session}.{entry['block_id']}",
            name=entry.get("label") or None,
            state=state,
            workspace=session,
        )

    def identify(self) -> str:
        session, block = self._own()
        try:
            endpoint = self._json(["whoami", "--json"]).get("endpoint")
            if not isinstance(endpoint, str) or not endpoint:
                raise backend.BackendError("rex whoami returned no endpoint")
            self._endpoint = endpoint
            known = {entry["block_id"] for entry in self._blocks(session)}
        except backend.BackendUnavailable:
            raise
        except backend.BackendError as exc:
            raise backend.BackendUnavailable(f"rex identify failed: {exc}") from exc
        if block not in known:
            raise backend.BackendUnavailable("rex identify: own block is not in its own session")
        return f"{session}.{block}"

    def list_seats(self) -> list[backend.Seat]:
        session = self._own()[0]
        seats = []
        for entry in self._blocks(session):
            try:
                state = self._status(session, entry["block_id"])
            except backend.SeatError:
                continue  # the block closed between the two calls
            seats.append(self._seat(session, entry, state))
        return seats

    def get_seat(self, ref: str) -> backend.Seat:
        session, entry = self._lookup(ref)
        return self._seat(session, entry, self._status(session, entry["block_id"]))

    def get_terminal(self, handle: str) -> backend.Seat:
        session, entry = self._lookup(handle)
        return self._seat(session, entry)

    def read_output(self, ref: str, lines: int) -> str:
        if lines < 1:
            raise ValueError("lines must be at least 1")
        session, block = self._target(ref)
        text = self._call(["capture", "-s", session, "-b", block, "--trim"]).stdout.replace("\r", "")
        return "".join(text.splitlines(keepends=True)[-lines:])

    def prompt(self, ref: str, text: str) -> None:
        if not text:
            raise ValueError("rex refuses empty input")
        session, block = self._target(ref)
        try:
            state = self._status(session, block)
        except (backend.SeatError, backend.BackendUnavailable):
            raise
        except backend.BackendError:
            state = "unknown"  # unreadable status: send anyway (design 3.1); the send is unacknowledged
        if state == "blocked":
            raise backend.SeatError("blocked", f"rex seat {ref} is blocked")
        self._call(["send", "-s", session, "-b", block, "--", text])
        self._call(["send-key", "-s", session, "-b", block, "enter"])

    def processes(self, handle: str) -> list[Any]:
        session, block = _split(handle)
        payload = self._json(["block", "call", "-s", session, "-b", block, "process"])
        if "foreground" not in payload and "last_exit" not in payload:
            raise backend.BackendError(f"rex process reply for {handle} has neither foreground nor last_exit")
        foreground = payload.get("foreground")
        if foreground is None:
            return []
        if not isinstance(foreground, dict) or not isinstance(foreground.get("pid"), int):
            raise backend.BackendError(f"rex process reply for {handle} has a malformed foreground")
        return [foreground]

    def send_block(self, lead_handle: str, report_path: str) -> str:
        session, block = _split(lead_handle)
        match = _REPORT_PATH_RE.fullmatch(report_path)
        if match is None or _UNSAFE_IN_DOUBLE_QUOTES & set(report_path):
            raise ValueError(f"report path must be <run-dir>/report-<peer>.md without shell metacharacters: {report_path!r}")
        send_path = f"{match['dir']}/send-{match['peer']}.txt"
        target = f"-s {session} -b {block}"
        return f'rex send {target} -- "$(cat {send_path})" && rex send-key {target} enter'

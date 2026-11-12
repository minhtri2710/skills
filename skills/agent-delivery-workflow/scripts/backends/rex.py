"""Rex adapter: pure argv builders and parsers over one injected runner (provisional, see references/backend-rex.md).

A seat handle is `<session-id>.<block-id>`. Every call that targets a block passes `-s` and `-b`;
after identify, every call also passes `-S <endpoint>` from `rex whoami --json`, and a call made before
identify is refused. `wait_state` stays Unsupported.
"""
from __future__ import annotations

import functools
import os
import subprocess
from collections.abc import Mapping
from typing import Any

import backend

BINARY = "rex"
EXIT_NOT_FOUND = 3
EXIT_UNREACHABLE = 4
# The seat reports its most urgent program_status record (Rex gives no single seat state).
_STATE_ORDER = ("blocked", "error", "working", "done")


def _binary(environ: Mapping[str, str]) -> str:
    """Rex puts the CLI on REX_BIN_DIR, not always on PATH (firstmate rex.sh fm_backend_rex_bin)."""
    bin_dir = environ.get("REX_BIN_DIR")
    candidate = os.path.join(bin_dir, BINARY) if bin_dir else None
    return candidate if candidate and os.access(candidate, os.X_OK) else BINARY


def _split(handle: str) -> tuple[str, str]:
    session, dot, block = handle.partition(".")
    if backend.HANDLE_RE.fullmatch(handle) is None or not (dot and block) or "." in block:
        raise ValueError(f"not a rex seat handle <session-id>.<block-id>: {handle!r}")
    return session, block


class Adapter(backend.Backend):
    name = "rex"

    def __init__(self, environ: Mapping[str, str], runner: backend.Runner | None = None) -> None:
        super().__init__(environ)
        self._runner = runner or functools.partial(backend.run_tool, _binary(environ))
        self._endpoint: str | None = None

    @staticmethod
    def matches(environ: Mapping[str, str]) -> bool:
        return environ.get("TERM_PROGRAM") == "rex" and bool(environ.get("REX_BLOCK") and environ.get("REX_SESSION"))

    @staticmethod
    def own_handle(environ: Mapping[str, str]) -> str | None:
        session, block = environ.get("REX_SESSION"), environ.get("REX_BLOCK")
        return f"{session}.{block}" if session and block else None

    def _call(self, args: list[str], *, pinned: bool = True) -> subprocess.CompletedProcess[str]:
        if pinned and self._endpoint is None:
            raise backend.BackendUnavailable("rex: call before identify; it would run without the server pin")
        pin = ["-S", self._endpoint] if pinned else []
        completed = self._runner(["--autostart=false", *pin, *args], timeout=backend.DEFAULT_TIMEOUT)
        code = completed.returncode
        if code:
            message = f"{BINARY} {' '.join(args[:3])} failed: exit {code}"
            if code == EXIT_NOT_FOUND:
                raise backend.SeatError("not_found", message)
            if code == EXIT_UNREACHABLE:
                raise backend.BackendUnavailable(message)
            raise backend.BackendError(message, code=f"exit_{code}")
        return completed

    def _json(self, args: list[str], *, pinned: bool = True) -> dict[str, Any]:
        return backend.json_object(self._call(args, pinned=pinned).stdout)

    def _own(self) -> tuple[str, str]:
        handle = self.own_handle(self.environ)
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
        endpoint = self._json(["whoami", "--json"], pinned=False).get("endpoint")
        if not isinstance(endpoint, str) or not endpoint:
            raise backend.BackendError("rex whoami returned no endpoint")
        self._endpoint = endpoint
        if block not in {entry["block_id"] for entry in self._blocks(session)}:
            raise backend.BackendError("own block is not in its own session")
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
            state = "unknown"  # unreadable status: send anyway; the send is unacknowledged
        if state == "blocked":
            raise backend.SeatError("blocked", f"rex seat {ref} is blocked")
        self._call(["send", "-s", session, "-b", block, "--", text])
        self._call(["send-key", "-s", session, "-b", block, "enter"])

    def processes(self, handle: str) -> list[backend.Process]:
        session, block = _split(handle)
        payload = self._json(["block", "call", "-s", session, "-b", block, "process"])
        if "foreground" not in payload and "last_exit" not in payload:
            raise backend.BackendError(f"rex process reply for {handle} has neither foreground nor last_exit")
        foreground = payload.get("foreground")
        if foreground is None:
            return []
        if not isinstance(foreground, dict) or not isinstance(foreground.get("pid"), int):
            raise backend.BackendError(f"rex process reply for {handle} has a malformed foreground")
        return [backend.Process.from_record(foreground)]

    def _render_send_block(self, lead_handle: str, peer: str, send_path: str, report_path: str) -> backend.SendBlock:
        session, block = _split(lead_handle)
        target = f"-s {session} -b {block}"
        # Rex exports REX_BIN_DIR into every block but a shell's startup files often reset PATH, so a bare `rex` may not resolve.
        binary = '"$REX_BIN_DIR/rex"'
        return backend.SendBlock(f'{binary} send {target} -- "$(cat "{send_path}")" && {binary} send-key {target} enter')

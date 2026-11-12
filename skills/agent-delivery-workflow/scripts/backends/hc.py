"""hc (herdr core) adapter: pure argv builders and parsers over one injected runner.

Every command and field is cited in references/backend-hc.md. The runner takes (args, timeout, env)
and returns a subprocess.CompletedProcess; the env pins every call to the core that issued this
seat's HC_TERMINAL_ID (HC_SOCKET = HC_TERMINAL_SOCKET) and is never printed or logged.
"""
from __future__ import annotations

import functools
import math
import os
import subprocess
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import backend

BINARY_NAME = "herdr-core"
FALLBACK_BINARY = "hc"
_SEAT_KINDS = {"not_found", "blocked"}
# Exit codes of `hc` when stderr carries no JSON (herdr-core's crates/herdr-core/src/SKILL.md:214-215, `HCM` in references/backend-hc.md).
_EXIT_KINDS = {3: "not_found", 7: "needs_target", 9: "blocked", 10: "status_mismatch", 11: "finished"}


def resolve_binary(home: Path) -> str:
    """~/.local/bin/herdr-core when it is an executable file, else `hc` on PATH."""
    candidate = home / ".local" / "bin" / BINARY_NAME
    return str(candidate) if candidate.is_file() and os.access(candidate, os.X_OK) else FALLBACK_BINARY


def _error_kind(completed: subprocess.CompletedProcess[str]) -> str:
    # hc prints {"error": {"kind", "message", "hint"}} on stderr (cli.rs fail()).
    for text in (completed.stderr, completed.stdout):
        error = backend.json_object(text).get("error")
        kind = error.get("kind") if isinstance(error, dict) else None
        if isinstance(kind, str) and kind:
            return kind
    return _EXIT_KINDS.get(completed.returncode, "unknown")


def _target(ref: str) -> str:
    # A ref is an argv word: it must not start with '-', so it is never read as an option.
    return backend.require_handle(ref)


def _state(terminal: Mapping[str, Any]) -> str:
    if terminal.get("state") == "finished":
        return "done" if terminal.get("exit_code") == 0 else "error"
    status = terminal.get("status")  # `hc get` carries the OSC 7501 record, `hc ls` only its word
    word = status.get("state") if isinstance(status, dict) else status
    return word if word in backend.STATES else "unknown"


def _seat(terminal: Mapping[str, Any]) -> backend.Seat:
    for key in ("address", "state"):
        if not isinstance(terminal.get(key), str):
            raise backend.BackendError(f"terminal record lacks {key}")
    argv = terminal.get("argv")
    argv = tuple(argv) if isinstance(argv, list) and all(isinstance(arg, str) for arg in argv) else ()
    status = terminal.get("status")
    app = status.get("app") if isinstance(status, dict) else None
    return backend.Seat(
        handle=terminal["address"],
        name=terminal.get("name") or None,
        state=_state(terminal),
        kind=terminal.get("agent") or app or (Path(argv[0]).name if argv else None) or None,
        cwd=terminal.get("cwd"),
    )


class Adapter(backend.Backend):
    name = "hc"

    def __init__(self, environ: Mapping[str, str], runner: backend.Runner | None = None, binary: str | None = None) -> None:
        super().__init__(environ)
        self._binary = binary or resolve_binary(Path.home())
        self._runner = runner or functools.partial(backend.run_tool, self._binary)
        socket = environ.get("HC_TERMINAL_SOCKET")
        self._env = {**environ, "HC_SOCKET": socket} if socket else None

    @staticmethod
    def matches(environ: Mapping[str, str]) -> bool:
        return bool(environ.get("HC_TERMINAL_ID") and environ.get("HC_TERMINAL_SOCKET"))

    @staticmethod
    def own_handle(environ: Mapping[str, str]) -> str | None:
        return environ.get("HC_TERMINAL_ID") or None

    def _ok(self, args: list[str], *, timeout: float = backend.DEFAULT_TIMEOUT) -> subprocess.CompletedProcess[str]:
        if self._env is None:
            raise backend.BackendUnavailable("hc: no HC_TERMINAL_SOCKET in the environment to pin the core")
        completed = self._runner(args, timeout=timeout, env=self._env)
        if completed.returncode:
            kind = _error_kind(completed)
            message = f"hc {args[0]} failed: {kind}"
            if kind in _SEAT_KINDS:
                raise backend.SeatError(kind, message)
            raise backend.BackendError(message, code=kind)
        return completed

    def _json(self, args: list[str], *, timeout: float = backend.DEFAULT_TIMEOUT) -> dict[str, Any]:
        payload = backend.json_object(self._ok(args, timeout=timeout).stdout)
        if not payload:
            raise backend.BackendError(f"hc {args[0]} returned no JSON object")
        return payload

    def _get(self, ref: str) -> dict[str, Any]:
        return self._json(["get", _target(ref), "--json"])

    def identify(self) -> str:
        terminal = self.own_handle(self.environ)
        if terminal is None:
            raise backend.BackendUnavailable("hc identify: no HC_TERMINAL_ID in the environment")
        record = self._get(terminal)
        if record.get("address") != terminal or record.get("state") != "live":
            raise backend.BackendError("get did not return this live terminal")
        return terminal

    def list_seats(self) -> list[backend.Seat]:
        terminals = self._json(["ls", "--json"]).get("terminals")
        if not isinstance(terminals, list):
            raise backend.BackendError("hc ls JSON terminals is not a list")
        if not all(isinstance(terminal, dict) for terminal in terminals):
            raise backend.BackendError("hc ls JSON contains a non-object terminal")
        return [_seat(terminal) for terminal in terminals]

    def get_seat(self, ref: str) -> backend.Seat:
        return _seat(self._get(ref))

    def get_terminal(self, handle: str) -> backend.Seat:
        return _seat(self._get(handle))

    def read_output(self, ref: str, lines: int) -> str:
        if lines < 0:
            raise ValueError(f"lines must not be negative: {lines}")
        return self._ok(["read", "--lines", str(lines), _target(ref)]).stdout

    def prompt(self, ref: str, text: str) -> None:
        if text.startswith("-"):
            raise ValueError("hc send reads a text starting with '-' as an option; no end-of-options form is documented")
        result = self._json(["send", "--json", _target(ref), text])
        if result.get("started") is False:  # null: the program reports no status, so no acknowledgement exists
            raise backend.SeatError("not_started", f"hc send {ref}: typed, but the program did not start working; read it before resending")

    def wait_state(self, ref: str, states: Sequence[str], timeout_ms: int) -> str:
        backend.require_states(states)
        deadline = time.monotonic() + timeout_ms / 1000
        while True:
            seconds = max(1, math.ceil(deadline - time.monotonic()))
            result = self._json(["wait", "--json", "--timeout", str(seconds), _target(ref)], timeout=seconds + 10)
            reason = result.get("reason")
            # A message typed into this caller ends the wait; it is already in the caller's input and
            # hc removes it as it returns, so the same wait is issued again for the time that is left.
            if reason == "message" and time.monotonic() < deadline:
                continue
            if reason == "message":
                raise backend.BackendError(f"hc wait {ref} timed out after {timeout_ms} ms", code="timeout")
            break
        if reason == "exit":
            reached = _state({"state": "finished", "exit_code": result.get("exit_code")})
        elif reason == "status":
            reached = _state({"status": result.get("status")})
        else:
            raise backend.BackendError(f"hc wait {ref} ended without a state: {reason}", code=str(reason))
        return backend.require_reached(f"hc wait {ref}", reached, states)

    def processes(self, handle: str) -> list[backend.Process]:
        foreground = self._get(handle).get("foreground")
        if foreground is None:
            return []
        argv = foreground.get("argv") if isinstance(foreground, dict) else None
        if not isinstance(argv, list) or not all(isinstance(arg, str) for arg in argv):
            raise backend.BackendError(f"hc get {handle} returned a malformed foreground record")
        return [backend.Process.from_record(foreground)]

    def _render_send_block(self, lead_handle: str, peer: str, send_path: str, report_path: str) -> backend.SendBlock:
        command = FALLBACK_BINARY if self._binary == FALLBACK_BINARY else f'"$HOME/.local/bin/{BINARY_NAME}"'
        return backend.SendBlock(f'{command} send {lead_handle} "$(cat "{send_path}")"')

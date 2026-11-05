"""Herdr adapter: pure argv builders and parsers over one injected runner.

Each operation is today's herdr call, argv and parsing unchanged (see the call sites the callers
used to own). The runner takes (args, timeout) and returns a subprocess.CompletedProcess.
"""
from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Callable, Mapping, Sequence
from typing import Any

import backend

BINARY = "herdr"
DEFAULT_TIMEOUT = 30.0
_CODE_KINDS = {"agent_not_found": "not_found", "pane_not_found": "not_found", "agent_blocked": "blocked"}
_REPORT_PATH_RE = re.compile(r"(?P<dir>.+)/report-(?P<peer>[^/]+)\.md")
_UNSAFE_IN_DOUBLE_QUOTES = frozenset('"$`\\\n')

Runner = Callable[..., "subprocess.CompletedProcess[str]"]


def run(args: list[str], *, timeout: float = DEFAULT_TIMEOUT) -> subprocess.CompletedProcess[str]:
    command = [BINARY, *args]
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


def _error_code(completed: subprocess.CompletedProcess[str]) -> str:
    # Herdr writes its error JSON to stderr; some callers saw it on stdout or as plain text.
    for text in (completed.stderr, completed.stdout):
        error = _object(text).get("error")
        code = error.get("code") if isinstance(error, dict) else error
        if isinstance(code, str) and code:
            return code
    both = f"{completed.stdout}\n{completed.stderr}".lower()
    return next((code for code in _CODE_KINDS if code in both), "unknown")


def _seat(agent: Mapping[str, Any], *, strict: bool, fallback_handle: str = "") -> backend.Seat:
    if strict:
        for key in ("pane_id", "agent_status"):
            if key not in agent:
                raise backend.BackendError(f"agent record lacks {key}")
    state = agent.get("agent_status")
    session = agent.get("agent_session")
    return backend.Seat(
        handle=agent.get("pane_id") or fallback_handle,
        name=agent.get("name") or None,
        state=state if state in backend.STATES else "unknown",
        kind=agent.get("agent") or None,
        cwd=agent.get("cwd"),
        session=backend.Session(session["kind"], session["value"])
        if isinstance(session, dict) and isinstance(session.get("kind"), str) and isinstance(session.get("value"), str)
        else None,
        workspace=agent.get("workspace_id"),
    )


class Adapter(backend.Backend):
    name = "herdr"

    def __init__(self, environ: Mapping[str, str], runner: Runner | None = None) -> None:
        super().__init__(environ)
        self._runner = runner or run

    def _ok(self, args: list[str], *, timeout: float = DEFAULT_TIMEOUT) -> subprocess.CompletedProcess[str]:
        completed = self._runner(args, timeout=timeout)
        if completed.returncode:
            code = _error_code(completed)
            message = f"{BINARY} {' '.join(args[:3])} failed: {code}"
            if code in _CODE_KINDS:
                raise backend.SeatError(_CODE_KINDS[code], message)
            raise backend.BackendError(message, code=code)
        return completed

    def _result(self, args: list[str], key: str) -> Any:
        payload = _object(self._ok(args).stdout)
        result = payload.get("result")
        if not isinstance(result, dict) or key not in result:
            raise backend.BackendError(f"{BINARY} {' '.join(args[:3])} returned no result.{key}")
        return result[key]

    def identify(self) -> str:
        pane = backend.own_handle("herdr", self.environ)
        if pane is None:
            raise backend.BackendUnavailable("herdr identify: no own pane handle in the environment")
        try:
            seat = self.get_terminal(pane)
        except backend.BackendUnavailable:
            raise
        except backend.BackendError as exc:
            raise backend.BackendUnavailable(f"herdr identify failed: {exc}") from exc
        if seat.handle != pane:
            raise backend.BackendUnavailable("herdr identify: pane get returned a different pane")
        return seat.handle

    def list_seats(self) -> list[backend.Seat]:
        agents = self._result(["agent", "list"], "agents")
        if not isinstance(agents, list):
            raise backend.BackendError("agent-list JSON result.agents is not a list")
        seats = []
        for agent in agents:
            if not isinstance(agent, dict):
                raise backend.BackendError("agent-list JSON contains a non-object agent")
            seats.append(_seat(agent, strict=True))
        return seats

    def get_seat(self, ref: str) -> backend.Seat:
        agent = self._result(["agent", "get", ref], "agent")
        if not isinstance(agent, dict):
            raise backend.BackendError(f"agent get {ref} returned a non-object agent")
        return _seat(agent, strict=False, fallback_handle=ref)

    def get_terminal(self, handle: str) -> backend.Seat:
        pane = self._result(["pane", "get", handle], "pane")
        if not isinstance(pane, dict) or not isinstance(pane.get("pane_id"), str):
            raise backend.BackendError(f"pane get {handle} returned no pane_id")
        return backend.Seat(handle=pane["pane_id"], cwd=pane.get("cwd"))

    def read_output(self, ref: str, lines: int) -> str:
        return self._ok(["agent", "read", ref, "--source", "recent-unwrapped", "--lines", str(lines)]).stdout

    def prompt(self, ref: str, text: str) -> None:
        self._ok(["agent", "prompt", ref, text])

    def wait_state(self, ref: str, states: Sequence[str], timeout_ms: int) -> str:
        if not states or any(state not in backend.STATES for state in states):
            raise ValueError(f"wait states must be a non-empty subset of {backend.STATES}")
        args = ["agent", "wait", ref]
        for state in states:
            args += ["--until", state]
        args += ["--timeout", str(timeout_ms)]
        payload = _object(self._ok(args, timeout=timeout_ms / 1000 + 10).stdout)
        result = payload.get("result")
        agent = result.get("agent") if isinstance(result, dict) else None
        status = agent.get("agent_status") if isinstance(agent, dict) else None
        if status is None:
            raise backend.BackendError(f"herdr agent wait {ref} returned no agent_status")
        return status

    def processes(self, handle: str) -> list[Any]:
        info = self._result(["pane", "process-info", "--pane", handle], "process_info")
        processes = info.get("foreground_processes") if isinstance(info, dict) else None
        if not isinstance(processes, list):
            raise backend.BackendError(f"process-info JSON for {handle} lacks foreground_processes")
        return processes

    def send_block(self, lead_handle: str, report_path: str) -> str:
        if backend.HANDLE_RE.fullmatch(lead_handle) is None:
            raise ValueError(f"not a seat handle: {lead_handle!r}")
        match = _REPORT_PATH_RE.fullmatch(report_path)
        if match is None or _UNSAFE_IN_DOUBLE_QUOTES & set(report_path):
            raise ValueError(f"report path must be <run-dir>/report-<peer>.md without shell metacharacters: {report_path!r}")
        peer, send_path = match["peer"], f"{match['dir']}/send-{match['peer']}.txt"
        return (
            f'herdr agent prompt {lead_handle} "$(cat {send_path})"\n'
            f'herdr notification show "{peer}: report send failed" --body "{report_path}" --sound request'
        )

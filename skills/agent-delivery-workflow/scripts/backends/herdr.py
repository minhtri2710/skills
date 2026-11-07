"""Herdr adapter: pure argv builders and parsers over one injected runner."""
from __future__ import annotations

import functools
import subprocess
from collections.abc import Mapping, Sequence
from typing import Any

import backend

BINARY = "herdr"
_CODE_KINDS = {"agent_not_found": "not_found", "pane_not_found": "not_found", "agent_blocked": "blocked"}
# A pane call says "gone" only with pane_not_found; agent_not_found there is not evidence the pane is gone.
_PANE_KINDS = {"pane_not_found": "not_found"}
# `agent wait --until` has no `error` state (the seat model's one state herdr never reports).
REPORTABLE = tuple(state for state in backend.STATES if state != "error")


def _error_code(completed: subprocess.CompletedProcess[str]) -> str:
    # Herdr writes its error JSON to stderr.
    for text in (completed.stderr, completed.stdout):
        error = backend.json_object(text).get("error")
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

    def __init__(self, environ: Mapping[str, str], runner: backend.Runner | None = None) -> None:
        super().__init__(environ)
        self._runner = runner or functools.partial(backend.run_tool, BINARY)

    @staticmethod
    def matches(environ: Mapping[str, str]) -> bool:
        return environ.get("HERDR_ENV") == "1" and bool(environ.get("HERDR_PANE_ID"))

    @staticmethod
    def own_handle(environ: Mapping[str, str]) -> str | None:
        return environ.get("HERDR_PANE_ID") or None

    def _ok(
        self, args: list[str], *, timeout: float = backend.DEFAULT_TIMEOUT, kinds: Mapping[str, str] = _CODE_KINDS
    ) -> subprocess.CompletedProcess[str]:
        completed = self._runner(args, timeout=timeout)
        if completed.returncode:
            code = _error_code(completed)
            message = f"{BINARY} {' '.join(args[:3])} failed: {code}"
            if code in kinds:
                raise backend.SeatError(kinds[code], message)
            raise backend.BackendError(message, code=code)
        return completed

    def _result(self, args: list[str], key: str, kinds: Mapping[str, str] = _CODE_KINDS) -> Any:
        payload = backend.json_object(self._ok(args, kinds=kinds).stdout)
        result = payload.get("result")
        if not isinstance(result, dict) or key not in result:
            raise backend.BackendError(f"{BINARY} {' '.join(args[:3])} returned no result.{key}")
        return result[key]

    def identify(self) -> str:
        pane = self.own_handle(self.environ)
        if pane is None:
            raise backend.BackendUnavailable("herdr identify: no own pane handle in the environment")
        seat = self.get_terminal(pane)
        if seat.handle != pane:
            raise backend.BackendError("pane get returned a different pane")
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
        pane = self._result(["pane", "get", handle], "pane", _PANE_KINDS)
        if not isinstance(pane, dict) or not isinstance(pane.get("pane_id"), str):
            raise backend.BackendError(f"pane get {handle} returned no pane_id")
        return backend.Seat(handle=pane["pane_id"], cwd=pane.get("cwd"))

    def read_output(self, ref: str, lines: int) -> str:
        return self._ok(["agent", "read", ref, "--source", "recent-unwrapped", "--lines", str(lines)]).stdout

    def prompt(self, ref: str, text: str) -> None:
        self._ok(["agent", "prompt", ref, text])

    def wait_state(self, ref: str, states: Sequence[str], timeout_ms: int) -> str:
        backend.require_states(states)
        until = [state for state in states if state in REPORTABLE]
        if not until:
            raise ValueError(f"herdr reports none of the wait states {list(states)}; it reports {REPORTABLE}")
        args = ["agent", "wait", ref]
        for state in until:
            args += ["--until", state]
        args += ["--timeout", str(timeout_ms)]
        payload = backend.json_object(self._ok(args, timeout=timeout_ms / 1000 + 10).stdout)
        result = payload.get("result")
        agent = result.get("agent") if isinstance(result, dict) else None
        status = agent.get("agent_status") if isinstance(agent, dict) else None
        if status is None:
            raise backend.BackendError(f"herdr agent wait {ref} returned no agent_status")
        return backend.require_reached(f"herdr agent wait {ref}", status, until)

    def processes(self, handle: str) -> list[backend.Process]:
        info = self._result(["pane", "process-info", "--pane", handle], "process_info", _PANE_KINDS)
        processes = info.get("foreground_processes") if isinstance(info, dict) else None
        if not isinstance(processes, list):
            raise backend.BackendError(f"process-info JSON for {handle} lacks foreground_processes")
        if not all(isinstance(process, dict) for process in processes):
            raise backend.BackendError(f"process-info JSON for {handle} contains a non-object process")
        return [backend.Process.from_record(process) for process in processes]

    def _render_send_block(self, lead_handle: str, peer: str, send_path: str, report_path: str) -> backend.SendBlock:
        return backend.SendBlock(
            f'herdr agent prompt {lead_handle} "$(cat {send_path})"',
            f'herdr notification show "{peer}: report send failed" --body "{report_path}" --sound request',
        )

"""An in-memory backend for script tests: seats, scripted replies, and recorded operations.

    fake = FakeBackend(handle="w1:p1")
    fake.add_seat("w1:p2", name="eng", state="idle", output="tail text", processes=[{"argv": ["pi"]}])
    fake.script("prompt", SeatError("blocked", "agent_blocked"))   # next prompt raises; one outcome per call
    fake.script("wait_state", "idle", "blocked")                    # next two waits return these states
    ...
    fake.calls == [("prompt", "w1:p2", "text")]

Surface: the same Backend operations as backend.py, plus add_seat, add_terminal, script and calls.
Every operation records (operation, *arguments) in `calls` before it answers. An operation with a
scripted outcome pops the next one (an exception instance is raised, anything else is returned);
otherwise it answers from the seats. A missing seat raises SeatError("not_found").
"""
from __future__ import annotations

import sys
from collections import defaultdict, deque
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "terminal-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import backend  # noqa: E402


class FakeBackend(backend.Backend):
    name = "fake"

    def __init__(self, handle: str = "f1:p1", environ: Mapping[str, str] | None = None) -> None:
        super().__init__(environ or {})
        self.handle = handle
        self.calls: list[tuple[Any, ...]] = []
        self._seats: dict[str, backend.Seat] = {}
        self._output: dict[str, str] = {}
        self._processes: dict[str, list[Any]] = {}
        self._terminals: dict[str, backend.Seat] = {}
        self._script: defaultdict[str, deque[Any]] = defaultdict(deque)

    def add_seat(
        self,
        handle: str,
        *,
        output: str = "",
        processes: list[Any] | None = None,
        terminal: bool = True,
        **seat: Any,
    ) -> backend.Seat:
        added = backend.Seat(handle=handle, **seat)
        self._seats[handle] = added
        self._output[handle] = output
        self._processes[handle] = processes if processes is not None else []
        if terminal:
            self._terminals[handle] = backend.Seat(handle=handle, cwd=added.cwd)
        return added

    def add_terminal(self, handle: str, *, cwd: str | None = None, processes: list[Any] | None = None) -> None:
        """A terminal with no agent in it (a shell pane)."""
        self._terminals[handle] = backend.Seat(handle=handle, cwd=cwd)
        self._processes[handle] = processes if processes is not None else []

    def remove(self, handle: str) -> None:
        for table in (self._seats, self._output, self._processes, self._terminals):
            table.pop(handle, None)

    def script(self, operation: str, *outcomes: Any) -> None:
        self._script[operation].extend(outcomes)

    def _scripted(self, operation: str, *args: Any) -> tuple[bool, Any]:
        self.calls.append((operation, *args))
        queue = self._script[operation]
        if not queue:
            return False, None
        outcome = queue.popleft()
        if isinstance(outcome, BaseException):
            raise outcome
        return True, outcome

    def _find(self, ref: str) -> backend.Seat:
        for seat in self._seats.values():
            if ref in (seat.handle, seat.name):
                return seat
        raise backend.SeatError("not_found", f"fake seat {ref} not found")

    def identify(self) -> str:
        done, value = self._scripted("identify")
        return value if done else self.handle

    def list_seats(self) -> list[backend.Seat]:
        done, value = self._scripted("list_seats")
        return value if done else list(self._seats.values())

    def get_seat(self, ref: str) -> backend.Seat:
        done, value = self._scripted("get_seat", ref)
        return value if done else self._find(ref)

    def get_terminal(self, handle: str) -> backend.Seat:
        done, value = self._scripted("get_terminal", handle)
        if done:
            return value
        if handle not in self._terminals:
            raise backend.SeatError("not_found", f"fake terminal {handle} not found")
        return self._terminals[handle]

    def read_output(self, ref: str, lines: int) -> str:
        done, value = self._scripted("read_output", ref, lines)
        return value if done else self._output[self._find(ref).handle]

    def prompt(self, ref: str, text: str) -> None:
        done, _ = self._scripted("prompt", ref, text)
        if not done:
            self._find(ref)

    def wait_state(self, ref: str, states: Sequence[str], timeout_ms: int) -> str:
        done, value = self._scripted("wait_state", ref, tuple(states), timeout_ms)
        return value if done else self._find(ref).state

    def processes(self, handle: str) -> list[Any]:
        done, value = self._scripted("processes", handle)
        if done:
            return value
        if handle not in self._processes:
            raise backend.SeatError("not_found", f"fake terminal {handle} not found")
        return self._processes[handle]

    def send_block(self, lead_handle: str, report_path: str) -> str:
        done, value = self._scripted("send_block", lead_handle, report_path)
        return value if done else f"FAKE-SEND {lead_handle} {report_path}"

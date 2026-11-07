#!/usr/bin/env python3
"""The seat-operation seam: detect the terminal tool, then drive seats through one adapter.

Each adapter module in ADAPTERS defines `Adapter(Backend)` with its detection signature, own-handle reader and the
seat operations; the shared tool runner, JSON reader, handle and wait-state checks, process record and report send
block live here. `backend.py whoami` prints this seat's "<backend> <handle>" after identify, and `backend.py
send-block --lead <lead handle> --report <run-dir>/report-<peer>.md` prints the backend's report send block. The
environment is read, never printed or logged.
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import re
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NamedTuple

STATES = ("idle", "working", "done", "blocked", "error", "unknown")
SEAT_ERROR_KINDS = ("not_found", "blocked", "not_started")
HANDLE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_REPORT_PATH_RE = re.compile(r"(?P<dir>.+)/report-(?P<peer>[^/]+)\.md")
_UNSAFE_IN_DOUBLE_QUOTES = frozenset('"$`\\\n')
DEFAULT_TIMEOUT = 30.0

ADAPTERS = {
    "herdr": "backends.herdr",
    "hc": "backends.hc",
    "rex": "backends.rex",
}


class BackendError(RuntimeError):
    def __init__(self, message: str, code: str = "unknown") -> None:
        super().__init__(message)
        self.code = code


class BackendUnavailable(BackendError):
    pass


class Unsupported(BackendError):
    pass


class DetectionError(BackendError):
    pass


class SeatError(BackendError):
    def __init__(self, kind: str, message: str) -> None:
        if kind not in SEAT_ERROR_KINDS:
            raise ValueError(f"unknown seat error kind: {kind}")
        super().__init__(message, code=kind)
        self.kind = kind


@dataclass(frozen=True)
class Session:
    kind: str
    value: str


@dataclass(frozen=True)
class Seat:
    handle: str
    name: str | None = None
    state: str = "unknown"
    kind: str | None = None
    cwd: str | None = None
    argv: tuple[str, ...] = ()
    session: Session | None = None
    workspace: str | None = None

    def __post_init__(self) -> None:
        if self.state not in STATES:
            raise ValueError(f"unknown seat state: {self.state}")


@dataclass(frozen=True)
class Process:
    """A foreground process of a seat. argv_reported is False when the tool hid argv and argv is the (argv0,) or (name,) fallback."""

    argv: tuple[str, ...]
    pid: int | None = None
    cwd: str | None = None
    argv_reported: bool = True

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> Process:
        argv = record.get("argv")
        reported = isinstance(argv, list) and bool(argv) and all(isinstance(arg, str) for arg in argv)
        if not reported:
            word = record.get("argv0") or record.get("name")
            argv = [word] if isinstance(word, str) else []
        pid, cwd = record.get("pid"), record.get("cwd")
        return cls(tuple(argv), pid if isinstance(pid, int) else None, cwd if isinstance(cwd, str) else None, reported)


class SendBlock(NamedTuple):
    """The report-by-prompt block: the command that sends the report and, when the tool has one, the notice run if it fails."""

    send_command: str
    failure_notice: str | None = None

    @property
    def text(self) -> str:
        return self.send_command if self.failure_notice is None else f"{self.send_command}\n{self.failure_notice}"


class Explicit(NamedTuple):
    name: str
    handle: str


Runner = Callable[..., "subprocess.CompletedProcess[str]"]


def run_tool(
    binary: str, args: list[str], *, timeout: float, env: Mapping[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    words = [arg for arg in args if not arg.startswith("-")][:2]
    label = " ".join([Path(binary).name, *words])
    try:
        return subprocess.run(
            [binary, *args], capture_output=True, text=True, encoding="utf-8", check=False, timeout=timeout, env=env
        )
    except subprocess.TimeoutExpired as exc:
        raise BackendUnavailable(f"{label} timed out after {timeout} seconds") from exc
    except OSError as exc:
        raise BackendUnavailable(f"{label} unavailable: {exc}") from exc


def json_object(text: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def require_handle(text: str) -> str:
    if HANDLE_RE.fullmatch(text) is None:
        raise ValueError(f"not a seat handle: {text!r}")
    return text


def require_states(states: Sequence[str]) -> None:
    if not states or any(state not in STATES for state in states):
        raise ValueError(f"wait states must be a non-empty subset of {STATES}")


def require_reached(label: str, reached: str, states: Sequence[str]) -> str:
    if reached not in states:
        raise BackendError(f"{label} reached {reached}, not one of {', '.join(states)}", code="state_not_requested")
    return reached


def report_send_file(report_path: str) -> tuple[str, str]:
    match = _REPORT_PATH_RE.fullmatch(report_path)
    if match is None or _UNSAFE_IN_DOUBLE_QUOTES & set(report_path):
        raise ValueError(f"report path must be <run-dir>/report-<peer>.md without shell metacharacters: {report_path!r}")
    return match["peer"], f"{match['dir']}/send-{match['peer']}.txt"


def adapter_class(name: str) -> type[Backend]:
    if name not in ADAPTERS:
        raise ValueError(f"unknown backend: {name}")
    return importlib.import_module(ADAPTERS[name]).Adapter


def own_handle(name: str, environ: Mapping[str, str]) -> str | None:
    return adapter_class(name).own_handle(environ)


def detect(environ: Mapping[str, str], explicit: Explicit | None = None) -> str:
    matched = [name for name in ADAPTERS if adapter_class(name).matches(environ)]
    if not matched:
        raise DetectionError("no supported terminal tool signature matches this environment")
    if explicit is None:
        if len(matched) > 1:
            raise DetectionError(
                f"more than one backend matches ({', '.join(matched)}); the Human must name this "
                "seat's tool, then pass --backend NAME@HANDLE with this seat's own handle"
            )
        name = matched[0]
    else:
        if explicit.name not in matched:
            raise DetectionError(
                f"--backend names {explicit.name}, which is not among the matched backends "
                f"({', '.join(matched)})"
            )
        if own_handle(explicit.name, environ) != explicit.handle:
            raise DetectionError(
                f"--backend handle is not this seat's own handle under {explicit.name}"
            )
        name = explicit.name
    return name


def parse_explicit(text: str) -> Explicit:
    name, separator, handle = text.partition("@")
    if not separator or name not in ADAPTERS or HANDLE_RE.fullmatch(handle) is None:
        raise ValueError(f"expected NAME@HANDLE with NAME one of {', '.join(ADAPTERS)}, got {text!r}")
    return Explicit(name, handle)


def _backend_argument(text: str) -> Explicit:
    try:
        return parse_explicit(text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def add_backend_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--backend",
        type=_backend_argument,
        default=None,
        metavar="NAME@HANDLE",
        help="this seat's own tool and handle; required only when its environment matches more than one tool",
    )


class Backend:
    name = ""
    handle: str | None = None

    def __init__(self, environ: Mapping[str, str]) -> None:
        self.environ = environ

    def _unsupported(self, operation: str) -> Unsupported:
        return Unsupported(f"{self.name} does not support {operation}")

    def identify(self) -> str:
        raise self._unsupported("identify")

    def list_seats(self) -> list[Seat]:
        raise self._unsupported("list_seats")

    def get_seat(self, ref: str) -> Seat:
        raise self._unsupported("get_seat")

    def get_terminal(self, handle: str) -> Seat:
        raise self._unsupported("get_terminal")

    def read_output(self, ref: str, lines: int) -> str:
        raise self._unsupported("read_output")

    def prompt(self, ref: str, text: str) -> None:
        raise self._unsupported("prompt")

    def wait_state(self, ref: str, states: Sequence[str], timeout_ms: int) -> str:
        raise self._unsupported("wait_state")

    def processes(self, handle: str) -> list[Process]:
        raise self._unsupported("processes")

    def send_block(self, lead_handle: str, report_path: str) -> SendBlock:
        peer, send_path = report_send_file(report_path)
        return self._render_send_block(require_handle(lead_handle), peer, send_path, report_path)

    def _render_send_block(self, lead_handle: str, peer: str, send_path: str, report_path: str) -> SendBlock:
        raise self._unsupported("send_block")


def open_backend(environ: Mapping[str, str], explicit: Explicit | None = None) -> Backend:
    name = detect(environ, explicit)
    adapter = adapter_class(name)(environ)
    try:
        adapter.handle = adapter.identify()
    except BackendUnavailable:
        raise
    except (BackendError, ValueError) as exc:
        raise BackendUnavailable(f"{name} identify failed: {exc}") from exc
    return adapter


def read_seat_record(path: Path) -> Explicit:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) != 1:
        raise ValueError(f"seat record {path} is not one line")
    name, _, handle = lines[0].partition(" ")
    try:
        return parse_explicit(f"{name}@{handle}")
    except ValueError as exc:
        raise ValueError(f"seat record {path} is not '<backend> <handle>'") from exc


def main(argv: Sequence[str] | None = None, environ: Mapping[str, str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    modes = parser.add_subparsers(dest="mode", required=True)
    whoami = modes.add_parser("whoami", help="print this seat's '<backend> <handle>' after identify")
    add_backend_option(whoami)
    send_block = modes.add_parser("send-block", help="print the report-by-prompt send block for one Peer report")
    send_block.add_argument("--lead", required=True, help="Lead seat handle the report is sent to")
    send_block.add_argument("--report", required=True, help="<run-dir>/report-<peer>.md")
    add_backend_option(send_block)
    args = parser.parse_args(argv)
    environ = os.environ if environ is None else environ
    try:
        adapter = open_backend(environ, args.backend)
        if args.mode == "whoami":
            print(f"{adapter.name} {adapter.handle}")
        else:
            print(adapter.send_block(args.lead, args.report).text)
    except (BackendError, ValueError) as exc:
        print(f"backend: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    import backend  # the adapters import `backend`; run that one module, not a second copy of this file

    raise SystemExit(backend.main())

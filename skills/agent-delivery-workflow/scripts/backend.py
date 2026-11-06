#!/usr/bin/env python3
"""The seat-operation seam: detect the terminal tool, then drive seats through one adapter.

Public names (stdlib only):

Errors, all subclasses of BackendError(message, code="unknown"):
  BackendUnavailable  binary missing, timeout, or a failed identify; the run stops.
  Unsupported         the operation, or the whole backend, is not supported.
  DetectionError      no signature matches, several match, or --backend does not hold; names the matches.
  SeatError(kind, message)  a per-seat failure; kind is one of SEAT_ERROR_KINDS
                      ("not_found", "blocked", "not_started"); code equals kind.

Data:
  Seat(handle, name, state, kind, cwd, argv, session, workspace)  one seat; state is in STATES;
                      session is Session(kind, value) or None; name, kind, cwd, workspace may be None.
  Explicit(name, handle)  a parsed NAME@HANDLE: a --backend flag or a seat record line.

Detection (design section 4):
  own_handle(name, environ) -> str | None   this process's own handle under backend `name`, a pure read.
  detect(environ, explicit=None) -> str     the one backend name, or raises DetectionError / Unsupported.
                      A recorded handle that differs from this process's own handle is rejected like
                      any other foreign --backend value: that is the relaunch rule.

Opening a backend:
  add_backend_option(parser) -> None        adds --backend NAME@HANDLE; the parsed value is args.backend.
  open_backend(environ, explicit=None) -> Backend   detect, construct the adapter, run identify (kept in .handle).
  ADAPTERS            one line per backend: name -> adapter module; each module defines `Adapter`.

Seat records (one line "<backend> <handle>", the lead-seat and supervisor-seat files):
  parse_explicit(text) -> Explicit          raises ValueError.
  read_seat_record(path) -> Explicit        raises OSError or ValueError.
  `backend.py whoami [--backend NAME@HANDLE]` prints this seat's "<backend> <handle>" after identify;
  a seat writes its record only after whoami succeeds:
  `r=$(backend.py whoami) && printf '%s\\n' "$r" > <path>`.
  `backend.py send-block --lead <lead handle> --report <run-dir>/report-<peer>.md [--backend NAME@HANDLE]`
  prints the backend's send block, the text `send_block` returns; every charter carries it.

Backend (the adapter base; every operation raises Unsupported until an adapter implements it):
  identify() -> str                         this seat's own handle, confirmed with the tool.
  list_seats() -> list[Seat]
  get_seat(ref) -> Seat                     the agent seat by handle or name.
  get_terminal(handle) -> Seat              the terminal behind a handle, whether or not an agent runs in it.
  read_output(ref, lines) -> str            recent unwrapped output.
  prompt(ref, text) -> None                 send text and submit it; raises SeatError blocked / not_found.
  wait_state(ref, states, timeout_ms) -> str  wait for one of `states`; returns the state reached.
  processes(handle) -> list[Mapping]        foreground processes of a seat, as the backend reports them
                                            (keys argv, argv0, pid, cwd where known).
  send_block(lead_handle, report_path) -> str  the report-by-prompt send block a charter must contain.

Spawn, interrupt, close and notify are not part of this surface: no migrated caller needs them yet.
The environment is read, never printed or logged.
"""
from __future__ import annotations

import argparse
import importlib
import os
import re
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NamedTuple

STATES = ("idle", "working", "done", "blocked", "error", "unknown")
SEAT_ERROR_KINDS = ("not_found", "blocked", "not_started")
HANDLE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")

# One line per backend. Each module defines `Adapter`.
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


class Explicit(NamedTuple):
    name: str
    handle: str


def _all_set(environ: Mapping[str, str], *keys: str) -> bool:
    return all(environ.get(key) for key in keys)


# Section 4 signatures. Every backend is listed so a later slice never edits detection.
_SIGNATURES = {
    "herdr": lambda e: e.get("HERDR_ENV") == "1" and _all_set(e, "HERDR_PANE_ID"),
    "hc": lambda e: _all_set(e, "HC_TERMINAL_ID", "HC_TERMINAL_SOCKET"),
    "rex": lambda e: e.get("TERM_PROGRAM") == "rex" and _all_set(e, "REX_BLOCK", "REX_SESSION"),
}


def own_handle(name: str, environ: Mapping[str, str]) -> str | None:
    if name == "herdr":
        return environ.get("HERDR_PANE_ID") or None
    if name == "hc":
        return environ.get("HC_TERMINAL_ID") or None
    if name == "rex":
        session, block = environ.get("REX_SESSION"), environ.get("REX_BLOCK")
        return f"{session}.{block}" if session and block else None
    raise ValueError(f"unknown backend: {name}")


def detect(environ: Mapping[str, str], explicit: Explicit | None = None) -> str:
    matched = [name for name, signature in _SIGNATURES.items() if signature(environ)]
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
    if name not in ADAPTERS:
        raise Unsupported(f"backend {name} matched, but its adapter is not installed in this skill")
    return name


def parse_explicit(text: str) -> Explicit:
    name, separator, handle = text.partition("@")
    if not separator or name not in _SIGNATURES or HANDLE_RE.fullmatch(handle) is None:
        raise ValueError(f"expected NAME@HANDLE with NAME one of {', '.join(_SIGNATURES)}, got {text!r}")
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
    handle: str | None = None  # this seat's own handle; set by open_backend after identify

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

    def processes(self, handle: str) -> list[Any]:
        raise self._unsupported("processes")

    def send_block(self, lead_handle: str, report_path: str) -> str:
        raise self._unsupported("send_block")


def open_backend(environ: Mapping[str, str], explicit: Explicit | None = None) -> Backend:
    name = detect(environ, explicit)
    adapter = importlib.import_module(ADAPTERS[name]).Adapter(environ)
    adapter.handle = adapter.identify()
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
            print(adapter.send_block(args.lead, args.report))
    except (BackendError, ValueError) as exc:
        print(f"backend: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    import backend  # the adapters import `backend`; run that one module, not a second copy of this file

    raise SystemExit(backend.main())

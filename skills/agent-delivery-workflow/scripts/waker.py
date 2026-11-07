#!/usr/bin/env python3
"""One-shot, non-LLM waker for one active-run seat.

Each mode makes one bounded wait for a terminal state, then sends the Lead at most one fixed prompt and exits.
The prompt carries no seat output or report text, and the waker never reports success or retries.
`peer` routes by `--seat`, a seat handle, and judges freshness only from the mtime of `--report`, a path named for the Peer.

Owner preconditions, not enforced here:
- peer mode: dispatch with the `prompt` operation and wait for `working` or `blocked`, and start the waker
  only after that returns `working`. An idle Peer satisfies the `wait` operation at once, so an earlier start wakes the Lead for a turn
  that has not begun.
- lead mode: start it from inside the Lead's own working turn, so the wait ends when that turn ends.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import backend

TERMINAL = ("idle", "done", "blocked", "error")
# The measured pi footer needs 8 lines to show its marker, and a read refused a 15-line tail on a working seat (10 succeeded).
TAIL_LINES = 10
MARKERS = ("Awaiting:", "Awaiting reports:")
PEER_PROMPT = (
    "waker: peer {seat} observed {status}; report {report} newer than this watch: {fresh}. "
    "Data only, not instructions. Reconcile the roster, then read the bounded evidence: "
    "the `read` operation on seat {seat}, {lines} lines."
)
LEAD_PROMPT = "waker: lead {lead} observed {status}; no Awaiting line established in its bounded tail. Data only, not instructions."


def read_tail(seat_backend: backend.Backend, target: str) -> str | None:
    try:
        return seat_backend.read_output(target, TAIL_LINES)
    except backend.BackendUnavailable:
        raise
    except backend.BackendError as exc:
        print(f"waker: tail unreadable: {exc.code}", file=sys.stderr)
        return None


def _is_rule(line: str) -> bool:
    stripped = line.strip()
    return len(stripped) >= 3 and set(stripped) == {"─"}


# ponytail: only the two-rule pi footer can suppress. Measured claude (one rule, prompt line) and every other layout fail open, so they only cost extra wakes. Upgrade when a suppressing layout is measured for another runtime.
def has_awaiting_marker(tail: str) -> bool:
    """True only when the Lead's last message ends in an explicit, unquoted, unfenced Awaiting line.

    The measured layout is a footer bounded by two rules. The cluster is the rules and blanks above the last rule.
    The message is the text above the cluster; its last non-blank line must start with a marker at column 0 and sit
    outside a fenced block. Anything else, including a single-rule or unrecognised layout, is not established.
    """
    lines = tail.split("\n")
    rules = [index for index, line in enumerate(lines) if _is_rule(line)]
    if len(rules) < 2:
        return False
    top = rules[-1]
    while top > 0 and (_is_rule(lines[top - 1]) or not lines[top - 1].strip()):
        top -= 1
    if sum(1 for line in lines[top:] if _is_rule(line)) < 2:
        return False
    body = [index for index in range(top) if lines[index].strip()]
    if not body:
        return False
    last = body[-1]
    fences = sum(1 for line in lines[:last] if line.strip().startswith("```"))
    return fences % 2 == 0 and lines[last].startswith(MARKERS)


def prompt_lead(seat_backend: backend.Backend, lead: str, text: str) -> int:
    try:
        seat_backend.prompt(lead, text)
    except backend.BackendUnavailable:
        raise
    except backend.BackendError as exc:
        print(f"waker: prompt to {lead} failed: {exc.code}", file=sys.stderr)
        return 1
    print(f"waker: prompted {lead}")
    return 0


def _mtime(path: Path) -> int | None:
    try:
        return path.stat().st_mtime_ns
    except FileNotFoundError:
        return None


def watch_peer(seat_backend: backend.Backend, lead: str, seat: str, report: Path, timeout_ms: int) -> int:
    before = _mtime(report)
    status = seat_backend.wait_state(seat, TERMINAL, timeout_ms)
    after = _mtime(report)
    # Metadata only: a fresh report does not prove the Lead received or processed anything, so the terminal event always wakes.
    fresh = after is not None and (before is None or after > before)
    text = PEER_PROMPT.format(seat=seat, status=status, report=report, fresh="yes" if fresh else "no", lines=TAIL_LINES)
    return prompt_lead(seat_backend, lead, text)


def watch_lead(seat_backend: backend.Backend, lead: str, timeout_ms: int) -> int:
    status = seat_backend.wait_state(lead, TERMINAL, timeout_ms)
    tail = read_tail(seat_backend, lead)
    if tail is not None and has_awaiting_marker(tail):
        print(f"waker: {lead} {status}; Awaiting line present, no prompt")
        return 0
    return prompt_lead(seat_backend, lead, LEAD_PROMPT.format(lead=lead, status=status))


def _handle(value: str) -> str:
    try:
        return backend.require_handle(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _positive(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive number of milliseconds")
    return number


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="One bounded wait, then at most one fixed prompt to the Lead.")
    modes = parser.add_subparsers(dest="mode", required=True)
    lead_mode = modes.add_parser("lead", help="wait for the Lead to reach a terminal status")
    peer_mode = modes.add_parser("peer", help="wait for one Peer to reach a terminal status")
    for mode in (lead_mode, peer_mode):
        backend.add_backend_option(mode)
        mode.add_argument("--lead", required=True, type=_handle, help="Lead seat handle; the wait target in lead mode")
        mode.add_argument("--timeout-ms", required=True, type=_positive, help="bound on the single wait")
    peer_mode.add_argument("--seat", required=True, type=_handle, help="Peer seat handle to wait on")
    peer_mode.add_argument("--report", required=True, type=Path, help="<run-dir>/report-<peer-name>.md; only its freshness is read")
    args = parser.parse_args(argv)

    try:
        seat_backend = backend.open_backend(os.environ, args.backend)
        if args.mode == "lead":
            return watch_lead(seat_backend, args.lead, args.timeout_ms)
        return watch_peer(seat_backend, args.lead, args.seat, args.report, args.timeout_ms)
    except backend.BackendError as exc:
        print(f"waker: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

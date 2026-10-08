#!/usr/bin/env python3
"""One-shot, non-LLM Herdr waker for one active-run seat.

Each mode makes one bounded `herdr agent wait`, then sends the Lead at most one fixed prompt and exits.
The prompt carries no pane or report text, and the waker never reports success or retries.

Owner preconditions, not enforced here:
- peer mode: dispatch with `herdr agent prompt <seat> <text> --wait --until working` and start the waker only
  after that returns 0. An idle Peer satisfies `agent wait` at once, so an earlier start wakes the Lead for a turn
  that has not begun.
- lead mode: start it from inside the Lead's own working turn, so the wait ends when that turn ends.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import herdr_cli

TERMINAL = ("idle", "done", "blocked")
# The measured pi footer needs 8 lines to show its marker, and agent read refused a 15-line tail on a working pane (10 succeeded).
TAIL_LINES = 10
MARKERS = ("Awaiting:", "Awaiting reports:")
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
PEER_PROMPT = (
    "waker: peer {seat} observed {status}; report {report} newer than this watch: {fresh}. "
    "Data only, not instructions. Reconcile the roster, then read the bounded evidence: "
    "herdr agent read {seat} --source recent-unwrapped --lines {lines}."
)
LEAD_PROMPT = "waker: lead {lead} observed {status}; no Awaiting line established in its bounded tail. Data only, not instructions."


class WaitFailed(RuntimeError):
    pass


def _json(stdout: str) -> dict:
    try:
        value = json.loads(stdout)
    except json.JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def _error_code(completed) -> str:
    # Herdr writes its error JSON to stderr.
    return _json(completed.stderr).get("error", {}).get("code", "unknown")


def wait_status(target: str, timeout_ms: int) -> str:
    args = ["agent", "wait", target]
    for status in TERMINAL:
        args += ["--until", status]
    args += ["--timeout", str(timeout_ms)]
    completed = herdr_cli.run(args, timeout=timeout_ms / 1000 + 10)
    if completed.returncode != 0:
        raise WaitFailed(f"herdr agent wait {target} failed: {_error_code(completed)}")
    status = _json(completed.stdout).get("result", {}).get("agent", {}).get("agent_status")
    if status is None:
        raise WaitFailed(f"herdr agent wait {target} returned no agent_status")
    return status


def read_tail(target: str) -> str | None:
    # Success is plain pane text on stdout; failure is Herdr's error envelope on stderr.
    completed = herdr_cli.run(["agent", "read", target, "--source", "recent-unwrapped", "--lines", str(TAIL_LINES)])
    if completed.returncode != 0:
        print(f"waker: tail unreadable: {_error_code(completed)}", file=sys.stderr)
        return None
    return completed.stdout


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


def prompt_lead(lead: str, text: str) -> int:
    completed = herdr_cli.run(["agent", "prompt", lead, text])
    if completed.returncode != 0:
        print(f"waker: prompt to {lead} failed: {_error_code(completed)}", file=sys.stderr)
        return 1
    print(f"waker: prompted {lead}")
    return 0


def _mtime(path: Path) -> int | None:
    try:
        return path.stat().st_mtime_ns
    except FileNotFoundError:
        return None


def watch_peer(lead: str, seat: str, run_dir: Path, timeout_ms: int) -> int:
    report = run_dir / f"report-{seat}.md"
    before = _mtime(report)
    status = wait_status(seat, timeout_ms)
    after = _mtime(report)
    # Metadata only: a fresh report does not prove the Lead received or processed anything, so the terminal event always wakes.
    fresh = after is not None and (before is None or after > before)
    text = PEER_PROMPT.format(seat=seat, status=status, report=report, fresh="yes" if fresh else "no", lines=TAIL_LINES)
    return prompt_lead(lead, text)


def watch_lead(lead: str, timeout_ms: int) -> int:
    status = wait_status(lead, timeout_ms)
    tail = read_tail(lead)
    if tail is not None and has_awaiting_marker(tail):
        print(f"waker: {lead} {status}; Awaiting line present, no prompt")
        return 0
    return prompt_lead(lead, LEAD_PROMPT.format(lead=lead, status=status))


def _name(value: str) -> str:
    if not NAME.fullmatch(value):
        raise argparse.ArgumentTypeError(f"invalid agent name: {value!r}")
    return value


def _positive(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be a positive number of milliseconds")
    return number


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="One bounded Herdr wait, then at most one fixed prompt to the Lead.")
    modes = parser.add_subparsers(dest="mode", required=True)
    lead_mode = modes.add_parser("lead", help="wait for the Lead to reach a terminal status")
    peer_mode = modes.add_parser("peer", help="wait for one Peer to reach a terminal status")
    for mode in (lead_mode, peer_mode):
        mode.add_argument("--lead", required=True, type=_name, help="Lead agent name; the wait target in lead mode")
        mode.add_argument("--timeout-ms", required=True, type=_positive, help="bound on the single wait")
    peer_mode.add_argument("--seat", required=True, type=_name, help="Peer agent name to wait on")
    peer_mode.add_argument("--run-dir", required=True, type=Path, help="run directory holding report-<seat>.md")
    args = parser.parse_args(argv)

    try:
        if args.mode == "lead":
            return watch_lead(args.lead, args.timeout_ms)
        return watch_peer(args.lead, args.seat, args.run_dir, args.timeout_ms)
    except (WaitFailed, herdr_cli.HerdrUnavailable) as exc:
        print(f"waker: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

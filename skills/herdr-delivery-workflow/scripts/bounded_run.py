#!/usr/bin/env python3
"""Run one command under a wall-clock limit and kill its whole process group when the limit passes.

The command starts in its own session, so the group holds it and every child it spawns
(test workers, browsers, a `sleep` under `sh`). At the limit the group gets SIGTERM, then
SIGKILL after the grace period if any member is left, and the exit code is 124. Otherwise
the command's own exit code passes through, after any member it left running is stopped the
same way. A SIGTERM or SIGINT to this wrapper is forwarded to the group the same way, so
stopping the runtime task never orphans the group.
"""
from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time

TIMED_OUT = 124
POLL_S = 0.05


def _group_alive(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
    # macOS answers EPERM for a group left with only zombies awaiting launchd's reap.
    except (ProcessLookupError, PermissionError):
        return False
    return True


def stop_group(proc: subprocess.Popen, grace: float) -> None:
    """SIGTERM the group, reap the leader, and SIGKILL whatever remains after `grace` seconds."""
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        return
    deadline = time.monotonic() + grace
    while time.monotonic() < deadline:
        proc.poll()
        if not _group_alive(proc.pid):
            return
        time.sleep(POLL_S)
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    proc.wait()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", required=True, type=float, help="wall-clock limit for the command")
    parser.add_argument("--grace", type=float, default=5.0, help="seconds between SIGTERM and SIGKILL")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="-- then the command and its arguments")
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command or args.seconds <= 0 or args.grace < 0:
        parser.error("needs --seconds > 0, --grace >= 0 and a command after --")
    proc = subprocess.Popen(command, start_new_session=True)

    def forward(signum: int, _frame: object) -> None:
        stop_group(proc, args.grace)
        sys.exit(128 + signum)

    signal.signal(signal.SIGTERM, forward)
    signal.signal(signal.SIGINT, forward)
    try:
        code = proc.wait(timeout=args.seconds)
    except subprocess.TimeoutExpired:
        stop_group(proc, args.grace)
        print(f"bounded_run: limit {args.seconds:g}s passed; killed process group {proc.pid}: "
              f"{' '.join(command)}", file=sys.stderr)
        return TIMED_OUT
    if _group_alive(proc.pid):
        stop_group(proc, args.grace)
    return code


if __name__ == "__main__":
    sys.exit(main())

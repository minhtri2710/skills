#!/usr/bin/env python3
"""Run one command under a wall-clock limit and kill its whole process group when the limit passes.

The command starts in its own session, so the group holds it and every child it spawns
(test workers, browsers, a `sleep` under `sh`). At the limit the group gets SIGTERM, then
SIGKILL after the grace period if any member is left, and the exit code is 124. Otherwise
the command's own exit code passes through, after any member it left running is stopped the
same way. A SIGTERM or SIGINT to this wrapper is forwarded to the group the same way, so
stopping the runtime task never orphans the group.

With --lock DIR the wrapper first takes a shared lock (the machine-wide heavy slot, or a
project's own lock), and the limit starts only once it holds it, so waiting never eats the
limit. The lock is the directory DIR holding an `owner` JSON record of this wrapper's seat,
pid and nonce; it is released after the group has stopped. A lock whose recorded pid is dead
is broken and named on stderr. A lock held past --wait-seconds, or an owner record with no
pid, exits 75 without running the command.
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import shutil
import signal
import subprocess
import sys
import time

TIMED_OUT = 124
LOCK_BUSY = 75
POLL_S = 0.05
LOCK_POLL_S = 1.0


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


def read_owner(lock: str) -> tuple[dict | None, str | None]:
    """The owner record and its raw text; the record is None when it names no pid and nonce."""
    try:
        with open(os.path.join(lock, "owner"), encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        return None, None
    try:
        rec = json.loads(raw)
    except json.JSONDecodeError:
        return None, raw
    if isinstance(rec, dict) and isinstance(rec.get("pid"), int) and rec.get("nonce"):
        return rec, raw
    return None, raw


def _pid_dead(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    return False


class LockBusy(Exception):
    pass


def acquire(lock: str, seat: str, wait: float, command: list[str]) -> dict:
    """Take the lock, waiting up to `wait` seconds on a live holder; raise LockBusy otherwise."""
    me = {"seat": seat, "pid": os.getpid(), "nonce": secrets.token_hex(8),
          "since": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "cmd": " ".join(command)[:200]}
    deadline = time.monotonic() + wait
    while True:
        try:
            os.mkdir(lock)
        except FileExistsError:
            rec, raw = read_owner(lock)
            if raw is None:
                # A writer has made the directory and not yet placed its record.
                time.sleep(LOCK_POLL_S)
                rec, raw = read_owner(lock)
            if rec is None:
                raise LockBusy(
                    f"{lock} owner has no pid record: {(raw or 'no owner file').strip()!r}; "
                    "incident, not waited on. Only the Lead clears it, after the seat named "
                    "in the record confirms its run has ended") from None
            if _pid_dead(rec["pid"]):
                if read_owner(lock)[1] == raw:
                    shutil.rmtree(lock, ignore_errors=True)
                    print(f"bounded_run: broke {lock} of dead pid {rec['pid']} ({rec.get('seat')}): "
                          f"{raw.strip()}", file=sys.stderr)
                continue
            if time.monotonic() >= deadline:
                raise LockBusy(f"{lock} held by {rec.get('seat')} pid {rec['pid']} since "
                               f"{rec.get('since')}; waited {wait:g}s, command not run") from None
            time.sleep(min(LOCK_POLL_S, max(deadline - time.monotonic(), POLL_S)))
            continue
        tmp = os.path.join(lock, f".owner.{os.getpid()}")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(me, f)
        os.replace(tmp, os.path.join(lock, "owner"))
        return me


def release(lock: str, me: dict) -> None:
    rec, raw = read_owner(lock)
    if rec is not None and rec["pid"] == me["pid"] and rec["nonce"] == me["nonce"]:
        shutil.rmtree(lock, ignore_errors=True)
        return
    print(f"bounded_run: {lock} is no longer ours at release; left as is: {raw!r}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", required=True, type=float, help="wall-clock limit for the command")
    parser.add_argument("--grace", type=float, default=5.0, help="seconds between SIGTERM and SIGKILL")
    parser.add_argument("--lock", help="lock directory to hold while the command runs")
    parser.add_argument("--seat", help="seat named in the lock's owner record")
    parser.add_argument("--wait-seconds", type=float, help="longest wait for a held lock")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="-- then the command and its arguments")
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command or args.seconds <= 0 or args.grace < 0:
        parser.error("needs --seconds > 0, --grace >= 0 and a command after --")
    lock_args = (args.lock, args.seat, args.wait_seconds)
    if any(a is not None for a in lock_args) and (
            not all(a is not None for a in lock_args) or args.wait_seconds < 0):
        parser.error("--lock, --seat and --wait-seconds >= 0 go together")
    proc: subprocess.Popen | None = None
    held: dict | None = None

    def forward(signum: int, _frame: object) -> None:
        if proc is not None:
            stop_group(proc, args.grace)
        sys.exit(128 + signum)

    signal.signal(signal.SIGTERM, forward)
    signal.signal(signal.SIGINT, forward)
    try:
        if args.lock:
            try:
                held = acquire(os.path.expanduser(args.lock), args.seat, args.wait_seconds, command)
            except LockBusy as busy:
                print(f"bounded_run: {busy}", file=sys.stderr)
                return LOCK_BUSY
        proc = subprocess.Popen(command, start_new_session=True)
        try:
            code = proc.wait(timeout=args.seconds)
        except subprocess.TimeoutExpired:
            stop_group(proc, args.grace)
            print(f"bounded_run: limit {args.seconds:g}s passed; killed process group {proc.pid}: "
                  f"{' '.join(command)}", file=sys.stderr)
            return TIMED_OUT
        if _group_alive(proc.pid):
            stop_group(proc, args.grace)
        return 128 - code if code < 0 else code
    finally:
        if held is not None:
            release(os.path.expanduser(args.lock), held)


if __name__ == "__main__":
    sys.exit(main())

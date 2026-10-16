"""bounded_run kills the command's whole process group at the limit, grandchildren included, and holds a lock outside the limit."""
from __future__ import annotations

import contextlib
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts" / "bounded_run.py"


def _gone(pid: int, within: float = 3.0) -> bool:
    deadline = time.monotonic() + within
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return True
        time.sleep(0.05)
    return False


class BoundedRunTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.pidfile = Path(tmp.name) / "grandchild.pid"

    def wrapper(self, seconds: str, script: str) -> list[str]:
        return [sys.executable, str(SCRIPT), "--seconds", seconds, "--grace", "0.5", "--",
                "sh", "-c", script, "sh", str(self.pidfile)]

    def grandchild(self) -> int:
        deadline = time.monotonic() + 3
        while not self.pidfile.exists() or not self.pidfile.read_text().strip():
            self.assertLess(time.monotonic(), deadline, "grandchild never wrote its pid")
            time.sleep(0.05)
        pid = int(self.pidfile.read_text())
        self.addCleanup(self.kill, pid)
        return pid

    @staticmethod
    def kill(pid: int) -> None:
        with contextlib.suppress(ProcessLookupError):
            os.kill(pid, signal.SIGKILL)

    def test_passes_the_command_exit_code_through(self):
        run = subprocess.run([sys.executable, str(SCRIPT), "--seconds", "10", "--", "sh", "-c", "exit 3"],
                             stdin=subprocess.DEVNULL, capture_output=True, text=True)
        self.assertEqual((run.returncode, run.stderr), (3, ""))

    def test_a_signal_killed_command_exits_128_plus_the_signal(self):
        run = subprocess.run([sys.executable, str(SCRIPT), "--seconds", "10", "--", "sh", "-c", "kill -KILL $$"],
                             stdin=subprocess.DEVNULL, capture_output=True, text=True)
        self.assertEqual(run.returncode, 128 + signal.SIGKILL)

    def test_limit_kills_a_grandchild_that_ignores_sigterm(self):
        run = subprocess.run(self.wrapper("1", "trap '' TERM; sleep 300 & echo $! > \"$1\"; wait"),
                             stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=30)
        pid = self.grandchild()
        self.assertEqual(run.returncode, 124)
        self.assertIn("bounded_run: limit 1s passed; killed process group", run.stderr)
        self.assertTrue(_gone(pid), f"grandchild {pid} survived the limit")

    def test_stops_a_grandchild_left_running_after_a_normal_exit(self):
        run = subprocess.run(self.wrapper("10", "sleep 300 & echo $! > \"$1\""),
                             stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=30)
        pid = self.grandchild()
        self.assertEqual(run.returncode, 0)
        self.assertTrue(_gone(pid), f"grandchild {pid} outlived the command")

    def test_sigterm_to_the_wrapper_reaches_the_group(self):
        proc = subprocess.Popen(self.wrapper("60", "sleep 300 & echo $! > \"$1\"; wait"),
                                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pid = self.grandchild()
        proc.send_signal(signal.SIGTERM)
        self.assertEqual(proc.wait(timeout=30), 128 + signal.SIGTERM)
        self.assertTrue(_gone(pid), f"grandchild {pid} outlived the stopped wrapper")


class BoundedRunLockTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.lock = self.root / "heavy-lock"
        self.marker = self.root / "ran"

    def locked(self, seat: str, wait: str, seconds: str, *command: str) -> list[str]:
        return [sys.executable, str(SCRIPT), "--lock", str(self.lock), "--seat", seat, "--wait-seconds", wait,
                "--seconds", seconds, "--grace", "0.5", "--", *command]

    def run_locked(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(self.locked(*args), stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=30)

    def hold(self, seconds: str) -> subprocess.Popen:
        holder = subprocess.Popen(self.locked("holder", "0", "30", "sleep", seconds),
                                  stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(holder.wait)
        self.addCleanup(holder.terminate)
        deadline = time.monotonic() + 3
        while not (self.lock / "owner").exists():
            self.assertLess(time.monotonic(), deadline, "holder never took the lock")
            time.sleep(0.02)
        return holder

    def test_the_limit_starts_after_the_lock_is_taken(self):
        holder = self.hold("1.5")
        began = time.monotonic()
        run = self.run_locked("waiter", "10", "1", "sh", "-c", f"sleep 0.6; touch {self.marker}")
        self.assertEqual((run.returncode, run.stderr), (0, ""))
        self.assertGreater(time.monotonic() - began, 1.5, "the waiter ran before the holder let go")
        self.assertEqual(holder.wait(timeout=5), 0)
        self.assertTrue(self.marker.exists())
        self.assertFalse(self.lock.exists())

    def test_a_lock_held_past_the_wait_exits_75_without_running(self):
        holder = self.hold("30")
        run = self.run_locked("waiter", "0.5", "10", "touch", str(self.marker))
        self.assertEqual(run.returncode, 75)
        self.assertIn(f"held by holder pid {holder.pid}", run.stderr)
        self.assertFalse(self.marker.exists())
        self.assertTrue((self.lock / "owner").exists())

    def test_a_dead_holders_lock_is_broken_and_named(self):
        dead = subprocess.Popen(["true"])
        dead.wait()
        self.lock.mkdir()
        (self.lock / "owner").write_text(json.dumps({"seat": "gone", "pid": dead.pid, "nonce": "ab"}))
        run = self.run_locked("waiter", "0", "10", "touch", str(self.marker))
        self.assertEqual(run.returncode, 0)
        self.assertIn(f"broke {self.lock} of dead pid {dead.pid} (gone)", run.stderr)
        self.assertTrue(self.marker.exists())
        self.assertFalse(self.lock.exists())

    def test_an_owner_with_no_pid_exits_75_at_once_naming_it_and_its_clearer(self):
        record = "street-soccer-brawl review-c547fa4dcb3e c547fa4dcb3e order-check 2026-10-16T03:18:09Z"
        self.lock.mkdir()
        (self.lock / "owner").write_text(record + "\n")
        began = time.monotonic()
        run = self.run_locked("waiter", "20", "10", "touch", str(self.marker))
        self.assertLess(time.monotonic() - began, 10)
        self.assertEqual(run.returncode, 75)
        self.assertIn(f"owner has no pid record: {record!r}", run.stderr)
        self.assertIn("Only the Lead clears it, after the seat named in the record confirms its run has ended",
                      run.stderr)
        self.assertFalse(self.marker.exists())
        self.assertEqual((self.lock / "owner").read_text(), record + "\n")

    def test_the_lock_is_released_after_a_timeout_and_after_sigterm(self):
        run = self.run_locked("timed", "0", "0.5", "sleep", "30")
        self.assertEqual(run.returncode, 124)
        self.assertFalse(self.lock.exists())
        proc = subprocess.Popen(self.locked("stopped", "0", "60", "sleep", "30"),
                                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + 3
        while not (self.lock / "owner").exists():
            self.assertLess(time.monotonic(), deadline, "the run never took the lock")
            time.sleep(0.02)
        proc.send_signal(signal.SIGTERM)
        self.assertEqual(proc.wait(timeout=30), 128 + signal.SIGTERM)
        self.assertFalse(self.lock.exists())

    def test_lock_options_go_together(self):
        run = subprocess.run([sys.executable, str(SCRIPT), "--lock", str(self.lock), "--seconds", "5", "--", "true"],
                             stdin=subprocess.DEVNULL, capture_output=True, text=True)
        self.assertEqual(run.returncode, 2)
        self.assertIn("--lock, --seat and --wait-seconds >= 0 go together", run.stderr)


if __name__ == "__main__":
    unittest.main()

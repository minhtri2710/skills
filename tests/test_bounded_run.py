"""bounded_run kills the command's whole process group at the limit, grandchildren included."""
from __future__ import annotations

import contextlib
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


if __name__ == "__main__":
    unittest.main()

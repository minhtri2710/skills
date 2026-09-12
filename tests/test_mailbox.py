#!/usr/bin/env python3
"""Tests for selective mailbox reads."""
from __future__ import annotations

import contextlib
import io
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import mailbox  # noqa: E402


SAMPLE = """---
## lead-beo-skills -> supervisor | 2026-09-10T00:05Z | first
one
---
## lead-beo-skills -> supervisor | 2026-09-10T00:10Z | second
two
---
## lead-beo-skills -> supervisor | 2026-09-10T00:15Z | third
three
"""


class MailboxTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir="/private/tmp")
        self.path = Path(self.tmp.name) / "mailbox.md"
        self.path.write_text(SAMPLE, encoding="utf-8")
        self.addCleanup(self.tmp.cleanup)

    def test_since_excludes_boundary_and_returns_whole_entry(self):
        self.assertEqual(
            mailbox.select_entries(self.path.read_text(encoding="utf-8"), since="2026-09-10T00:10Z"),
            [
                "## lead-beo-skills -> supervisor | 2026-09-10T00:15Z | third\nthree",
            ],
        )

    def test_last_returns_whole_entries(self):
        self.assertEqual(
            mailbox.select_entries(self.path.read_text(encoding="utf-8"), last=2),
            [
                "## lead-beo-skills -> supervisor | 2026-09-10T00:10Z | second\ntwo",
                "## lead-beo-skills -> supervisor | 2026-09-10T00:15Z | third\nthree",
            ],
        )

    def test_headers_returns_only_header_lines(self):
        self.assertEqual(
            mailbox.select_entries(self.path.read_text(encoding="utf-8"), headers=True),
            [
                "## lead-beo-skills -> supervisor | 2026-09-10T00:05Z | first",
                "## lead-beo-skills -> supervisor | 2026-09-10T00:10Z | second",
                "## lead-beo-skills -> supervisor | 2026-09-10T00:15Z | third",
            ],
        )

    def test_no_selector_returns_all_entries(self):
        self.assertEqual(
            mailbox.select_entries(self.path.read_text(encoding="utf-8")),
            [
                "## lead-beo-skills -> supervisor | 2026-09-10T00:05Z | first\none",
                "## lead-beo-skills -> supervisor | 2026-09-10T00:10Z | second\ntwo",
                "## lead-beo-skills -> supervisor | 2026-09-10T00:15Z | third\nthree",
            ],
        )

    def test_since_and_last_are_mutually_exclusive(self):
        with self.assertRaisesRegex(ValueError, "since and last are mutually exclusive"):
            mailbox.select_entries(
                self.path.read_text(encoding="utf-8"),
                since="2026-09-10T00:10Z",
                last=1,
            )

    def test_main_headers_since_returns_selected_headers(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = mailbox.main(
                [
                    "--file",
                    str(self.path),
                    "--headers",
                    "--since",
                    "2026-09-10T00:05Z",
                ]
            )
        self.assertEqual(result, 0)
        self.assertEqual(
            stdout.getvalue(),
            "## lead-beo-skills -> supervisor | 2026-09-10T00:10Z | second\n"
            "## lead-beo-skills -> supervisor | 2026-09-10T00:15Z | third\n",
        )
        self.assertEqual(stderr.getvalue(), "")

    def test_main_requires_a_selector(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = mailbox.main(["--file", str(self.path)])
        self.assertEqual(result, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("mailbox: at least one of", stderr.getvalue())

    def test_wake_runs_once_for_last_header(self):
        calls = []

        def fake_wake(seat, wake_text):
            calls.append((seat, wake_text))
            return subprocess.CompletedProcess(
                ["herdr", "agent", "prompt", seat, wake_text],
                0,
                stdout="wake output\n",
                stderr="wake diagnostic\n",
            )

        original = mailbox.run_wake
        mailbox.run_wake = fake_wake
        self.addCleanup(setattr, mailbox, "run_wake", original)
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = mailbox.main(["--file", str(self.path), "--wake", "supervisor"])

        self.assertEqual(result, 0)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], "supervisor")
        self.assertIn(str(self.path), calls[0][1])
        self.assertIn("third", calls[0][1])
        self.assertEqual(stdout.getvalue(), "wake output\n")
        self.assertIn("ran herdr agent prompt supervisor", stderr.getvalue())
        self.assertIn("wake diagnostic\n", stderr.getvalue())
        stamped = next(
            line for line in reversed(self.path.read_text(encoding="utf-8").splitlines())
            if mailbox.HEADER_RE.match(line)
        )
        self.assertRegex(stamped, r" sent=\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertEqual(len(mailbox._entries(self.path.read_text(encoding="utf-8"))), 3)

    def test_successful_wake_is_idempotent(self):
        calls = []

        def fake_wake(seat, wake_text):
            calls.append((seat, wake_text))
            return subprocess.CompletedProcess([], 0, stdout="", stderr="")

        original = mailbox.run_wake
        mailbox.run_wake = fake_wake
        self.addCleanup(setattr, mailbox, "run_wake", original)
        argv = ["--file", str(self.path), "--wake", "supervisor"]
        self.assertEqual(mailbox.main(argv), 0)
        first = self.path.read_text(encoding="utf-8")
        self.assertEqual(mailbox.main(argv), 0)
        second = self.path.read_text(encoding="utf-8")
        self.assertEqual(first, second)
        self.assertEqual(second.count(" sent="), 1)
        self.assertEqual(len(calls), 2)
        self.assertIn("sent=", calls[1][1])

    def test_failed_wake_does_not_stamp_header(self):
        def fake_wake(seat, wake_text):
            return subprocess.CompletedProcess([], 1, stdout="", stderr="blocked")

        original = mailbox.run_wake
        mailbox.run_wake = fake_wake
        self.addCleanup(setattr, mailbox, "run_wake", original)
        self.assertEqual(
            mailbox.main(["--file", str(self.path), "--wake", "supervisor"]), 1
        )
        self.assertNotIn(" sent=", self.path.read_text(encoding="utf-8"))

    def test_wake_oserror_does_not_stamp_header(self):
        def fake_wake(seat, wake_text):
            raise OSError("no herdr")

        original = mailbox.run_wake
        mailbox.run_wake = fake_wake
        self.addCleanup(setattr, mailbox, "run_wake", original)
        self.assertEqual(
            mailbox.main(["--file", str(self.path), "--wake", "supervisor"]), 1
        )
        self.assertNotIn(" sent=", self.path.read_text(encoding="utf-8"))

    def test_wake_without_header_is_unsent_and_does_not_wake(self):
        self.path.write_text("not a mailbox entry\n", encoding="utf-8")
        calls = []
        original = mailbox.run_wake
        mailbox.run_wake = lambda seat, wake_text: calls.append((seat, wake_text))
        self.addCleanup(setattr, mailbox, "run_wake", original)
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = mailbox.main(["--file", str(self.path), "--wake", "supervisor"])

        self.assertNotEqual(result, 0)
        self.assertEqual(calls, [])
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("UNSENT", stderr.getvalue())
        self.assertIn("wake not attempted", stderr.getvalue())

    def test_wake_failure_is_not_retried(self):
        calls = []

        def fake_wake(seat, wake_text):
            calls.append((seat, wake_text))
            return subprocess.CompletedProcess(
                ["herdr", "agent", "prompt", seat, wake_text],
                1,
                stdout="",
                stderr="agent_blocked\n",
            )

        original = mailbox.run_wake
        mailbox.run_wake = fake_wake
        self.addCleanup(setattr, mailbox, "run_wake", original)
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = mailbox.main(["--file", str(self.path), "--wake", "supervisor"])

        self.assertEqual(result, 1)
        self.assertEqual(len(calls), 1)
        self.assertIn("ran herdr agent prompt supervisor", stderr.getvalue())
        self.assertIn("agent_blocked\n", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()

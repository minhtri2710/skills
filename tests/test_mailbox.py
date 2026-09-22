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
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import mailbox  # noqa: E402
import gate_row  # noqa: E402
import jev  # noqa: E402


SAMPLE = """---
## lead-beo-skills -> supervisor | 2026-09-10T00:05:01Z | first
one
---
## lead-beo-skills -> supervisor | 2026-09-10T00:10:02Z | second
two
---
## lead-beo-skills -> supervisor | 2026-09-10T00:15:03Z | third
three
"""


class MailboxTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir="/private/tmp")
        # A live wake is only allowed from a real project mailbox, so the
        # fixture lives under a fake herdr projects root and the module
        # constant is pointed at it for the duration of the test.
        root = Path(self.tmp.name) / ".herdr" / "projects"
        project = root / "beo-skills"
        project.mkdir(parents=True)
        self.path = project / "mailbox.md"
        self.path.write_text(SAMPLE, encoding="utf-8")
        prev_root = mailbox.HERDR_PROJECTS_ROOT
        mailbox.HERDR_PROJECTS_ROOT = root
        self._stdout_patch = mock.patch.object(sys, "stdout", io.StringIO())
        self._stderr_patch = mock.patch.object(sys, "stderr", io.StringIO())
        self._stdout_patch.start()
        self._stderr_patch.start()
        self.addCleanup(self._stderr_patch.stop)
        self.addCleanup(self._stdout_patch.stop)
        self.addCleanup(setattr, mailbox, "HERDR_PROJECTS_ROOT", prev_root)
        self.addCleanup(self.tmp.cleanup)

    def test_since_excludes_boundary_and_returns_whole_entry(self):
        self.assertEqual(
            mailbox.select_entries(self.path.read_text(encoding="utf-8"), since="2026-09-10T00:10:02Z"),
            [
                "## lead-beo-skills -> supervisor | 2026-09-10T00:15:03Z | third\nthree",
            ],
        )

    def test_last_returns_whole_entries(self):
        self.assertEqual(
            mailbox.select_entries(self.path.read_text(encoding="utf-8"), last=2),
            [
                "## lead-beo-skills -> supervisor | 2026-09-10T00:10:02Z | second\ntwo",
                "## lead-beo-skills -> supervisor | 2026-09-10T00:15:03Z | third\nthree",
            ],
        )

    def test_headers_returns_only_header_lines(self):
        self.assertEqual(
            mailbox.select_entries(self.path.read_text(encoding="utf-8"), headers=True),
            [
                "## lead-beo-skills -> supervisor | 2026-09-10T00:05:01Z | first",
                "## lead-beo-skills -> supervisor | 2026-09-10T00:10:02Z | second",
                "## lead-beo-skills -> supervisor | 2026-09-10T00:15:03Z | third",
            ],
        )

    def test_no_selector_returns_all_entries(self):
        self.assertEqual(
            mailbox.select_entries(self.path.read_text(encoding="utf-8")),
            [
                "## lead-beo-skills -> supervisor | 2026-09-10T00:05:01Z | first\none",
                "## lead-beo-skills -> supervisor | 2026-09-10T00:10:02Z | second\ntwo",
                "## lead-beo-skills -> supervisor | 2026-09-10T00:15:03Z | third\nthree",
            ],
        )

    def test_triage_entries_preserves_every_entry_and_order(self):
        entries = mailbox._entries(self.path.read_text(encoding="utf-8"))
        calls = []

        def fake_triage(header):
            calls.append(header)
            return jev.UnavailableResult(
                status="unavailable",
                finding={"header": header},
                reason="missing_api_key",
                fallback_actionable=False,
            )

        triaged = mailbox.triage_entries(entries, triage=fake_triage)
        self.assertEqual(len(triaged), len(entries))
        self.assertEqual([item.entry for item in triaged], entries)
        self.assertEqual(calls, [entry.header for entry in entries])
        self.assertEqual(
            [item.advisory.reason for item in triaged],
            ["missing_api_key"] * len(entries),
        )
        self.assertEqual([item.body for item in triaged], [entry.body for entry in entries])

    def test_triage_entries_keeps_malformed_entry_data_once(self):
        entries = [
            mailbox.Entry("not a recognized header", "", "unrecognized body"),
            mailbox.Entry(
                "## malformed -> supervisor | not-a-timestamp | second",
                "",
                "malformed body",
            ),
        ]
        triaged = mailbox.triage_entries(
            entries,
            triage=lambda header: jev.UnavailableResult(
                status="unavailable",
                finding={"header": header},
                reason="invalid_answers",
                fallback_actionable=False,
            ),
        )
        self.assertEqual(len(triaged), 2)
        self.assertEqual([item.header for item in triaged], [entry.header for entry in entries])
        self.assertEqual([item.body for item in triaged], [entry.body for entry in entries])

    def test_since_and_last_are_mutually_exclusive(self):
        with self.assertRaisesRegex(ValueError, "since and last are mutually exclusive"):
            mailbox.select_entries(
                self.path.read_text(encoding="utf-8"),
                since="2026-09-10T00:10:02Z",
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
                    "2026-09-10T00:05:01Z",
                ]
            )
        self.assertEqual(result, 0)
        self.assertEqual(
            stdout.getvalue(),
            "## lead-beo-skills -> supervisor | 2026-09-10T00:10:02Z | second\n"
            "## lead-beo-skills -> supervisor | 2026-09-10T00:15:03Z | third\n",
        )
        self.assertEqual(stderr.getvalue(), "")

    def test_minute_precision_header_and_since_are_rejected(self):
        minute_header = "## lead-beo-skills -> supervisor | 2026-09-10T00:20Z | minute"
        self.assertIsNone(mailbox.HEADER_RE.match(minute_header))
        with self.assertRaisesRegex(ValueError, "ISO-8601"):
            mailbox.select_entries(minute_header, since="2026-09-10T00:20Z")
        stdout = io.StringIO()
        stderr = io.StringIO()
        path = self.path
        path.write_text(minute_header + "\nbody\n", encoding="utf-8")
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = mailbox.main(["--file", str(path), "--headers", "--since", "2026-09-10T00:20Z"])
        self.assertEqual(result, 1)
        self.assertIn("ISO-8601", stderr.getvalue())

    def test_seconds_precision_orders_entries_at_the_same_minute(self):
        text = (
            "## lead-beo-skills -> supervisor | 2026-09-10T04:20:05Z | later\n"
            "later\n---\n"
            "## lead-beo-skills -> supervisor | 2026-09-10T04:20:04Z | earlier\n"
            "earlier\n"
        )
        self.assertEqual(mailbox.select_entries(text, since="2026-09-10T04:20:04Z", headers=True), [
            "## lead-beo-skills -> supervisor | 2026-09-10T04:20:05Z | later",
        ])

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
        self.assertEqual(self.path.read_bytes(), SAMPLE.encode("utf-8"))
        self.assertEqual(len(mailbox._entries(self.path.read_text(encoding="utf-8"))), 3)

    def test_successful_wake_leaves_mailbox_unchanged_and_returns_wake_code(self):
        def fake_wake(seat, wake_text):
            return subprocess.CompletedProcess([], 0, stdout="", stderr="")

        original = mailbox.run_wake
        mailbox.run_wake = fake_wake
        self.addCleanup(setattr, mailbox, "run_wake", original)
        before = self.path.read_bytes()
        result = mailbox.main(["--file", str(self.path), "--wake", "supervisor"])
        self.assertEqual(result, 0)
        self.assertEqual(self.path.read_bytes(), before)

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

    def test_wake_preserves_gate_row_s2_mailbox_evidence(self):
        repo = Path(__file__).resolve().parents[1]
        ledger = self.tmp.name + "/gates.md"
        head = gate_row.git(repo, "rev-parse", "HEAD")
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = gate_row.main([
                "--repo", str(repo), "--ledger", ledger,
                "--kind", "deploy-gate", "--status", "open",
                "--words", "none", "--note", "deploy permission pending", "--quote", "",
            ])
        self.assertEqual(result, 0, stderr.getvalue())
        gate_id = Path(ledger).read_text(encoding="utf-8").split(" | ", 1)[0]
        self.path.write_text(
            f"## lead-beo-skills -> supervisor | 2026-09-10T00:20:00Z | "
            f"ATTENTION deploy gate {gate_id} | HEAD {head}\n",
            encoding="utf-8",
        )

        check_args = [
            "--repo", str(repo), "--ledger", ledger, "--check", "--mailbox", str(self.path),
        ]
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            self.assertEqual(gate_row.main(check_args), 0, stderr.getvalue())

        original = mailbox.run_wake
        mailbox.run_wake = lambda seat, wake_text: subprocess.CompletedProcess([], 0, "", "")
        self.addCleanup(setattr, mailbox, "run_wake", original)
        before = self.path.read_bytes()
        self.assertEqual(mailbox.main(["--file", str(self.path), "--wake", "supervisor"]), 0)
        self.assertEqual(self.path.read_bytes(), before)

        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            self.assertEqual(gate_row.main(check_args), 0, stderr.getvalue())

    def test_wake_refuses_a_file_outside_the_herdr_projects_root(self):
        # A11 lesson: a scratch or test context must never drive a live seat.
        # A mailbox that resolves outside the herdr projects root is refused
        # before run_wake is ever called.
        scratch = Path(self.tmp.name) / "scratch-mailbox.md"
        scratch.write_text(SAMPLE, encoding="utf-8")
        calls = []
        original = mailbox.run_wake
        mailbox.run_wake = lambda seat, wake_text: calls.append((seat, wake_text))
        self.addCleanup(setattr, mailbox, "run_wake", original)
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = mailbox.main(["--file", str(scratch), "--wake", "supervisor"])

        self.assertNotEqual(result, 0)
        self.assertEqual(calls, [])
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("refused", stderr.getvalue())

    def test_wake_text_flag_is_removed(self):
        # The undocumented --wake-text override was dead (no doctrine, no test).
        # It is gone; argparse rejects it as unknown and wake uses only the
        # default pointer text. Patch run_wake first so no path can fire a live
        # wake even if the flag ever regresses.
        calls = []
        original = mailbox.run_wake
        mailbox.run_wake = lambda seat, wake_text: (
            calls.append((seat, wake_text)) or subprocess.CompletedProcess([], 0, "", "")
        )
        self.addCleanup(setattr, mailbox, "run_wake", original)

        with self.assertRaises(SystemExit):
            mailbox.main(["--file", str(self.path), "--wake", "supervisor", "--wake-text", "x"])
        self.assertEqual(calls, [])

        self.assertEqual(mailbox.main(["--file", str(self.path), "--wake", "supervisor"]), 0)
        last_header = "## lead-beo-skills -> supervisor | 2026-09-10T00:15:03Z | third"
        self.assertEqual(
            calls[0][1],
            mailbox._default_wake_text("supervisor", str(self.path), last_header),
        )

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

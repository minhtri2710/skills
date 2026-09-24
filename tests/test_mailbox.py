#!/usr/bin/env python3
"""Tests for selective mailbox reads."""
from __future__ import annotations

import contextlib
import importlib.util
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
        self.pane_record = Path(self.tmp.name) / "supervisor-pane"
        for target, value in (
            ("SUPERVISOR_PANE_RECORD", self.pane_record),
            ("herdr_cli", mock.Mock(HerdrUnavailable=mailbox.herdr_cli.HerdrUnavailable)),
        ):
            patcher = mock.patch.object(mailbox, target, value, create=True)
            patcher.start()
            self.addCleanup(patcher.stop)

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

    def test_main_triage_appends_labels_without_changing_order_or_headers(self):
        urgencies = {
            "first": ("FYI", 0.0),
            "second": ("supervisor-action", 1.0),
            "third": ("human-gate", 2.0),
        }
        seen = []

        def fake_triage(header):
            seen.append(header)
            urgency, raw_value = urgencies[header.rsplit("| ", 1)[1]]
            return jev.HeaderAdvisoryResult(
                status="available",
                header=header,
                source_state={"header": header},
                urgency=jev.ScoreJudgment(
                    label=urgency,
                    argmax=urgency,
                    probability=0.9,
                    confidence=0.9,
                ),
                raw_answers={},
            )

        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.object(jev, "triage_header", fake_triage):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                result = mailbox.main(["--file", str(self.path), "--headers", "--triage"])
        self.assertEqual(result, 0)
        entries = mailbox._entries(self.path.read_text(encoding="utf-8"))
        self.assertEqual(seen, [entry.header for entry in entries])
        self.assertEqual(
            stdout.getvalue(),
            "\n".join(
                f"{entry.header} | jev={urgencies[entry.header.rsplit('| ', 1)[1]][0]}"
                for entry in entries
            )
            + "\n",
        )
        self.assertEqual(stderr.getvalue(), "")

    def test_main_triage_shows_unavailable_label_and_keeps_headers(self):
        def fake_triage(header):
            return jev.UnavailableResult(
                status="unavailable",
                finding={"header": header},
                reason="missing_api_key",
                fallback_actionable=False,
            )

        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.object(jev, "triage_header", fake_triage):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                result = mailbox.main(["--file", str(self.path), "--headers", "--triage"])
        self.assertEqual(result, 0)
        self.assertEqual(
            stdout.getvalue(),
            "\n".join(
                header + " | jev=unavailable:missing_api_key"
                for header in mailbox.select_entries(
                    self.path.read_text(encoding="utf-8"), headers=True
                )
            )
            + "\n",
        )
        self.assertEqual(stderr.getvalue(), "")

    def test_main_triage_without_key_labels_unavailable_and_never_requests(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.dict(jev.os.environ, clear=True), mock.patch.object(
            jev.urllib.request, "urlopen"
        ) as urlopen:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                result = mailbox.main(["--file", str(self.path), "--headers", "--triage"])
        self.assertEqual(result, 0)
        urlopen.assert_not_called()
        for header, line in zip(
            mailbox.select_entries(self.path.read_text(encoding="utf-8"), headers=True),
            stdout.getvalue().splitlines(),
        ):
            self.assertEqual(line, header + " | jev=unavailable:missing_api_key")
        self.assertEqual(stderr.getvalue(), "")

    def test_main_without_triage_keeps_output_and_never_calls_jev(self):
        def fail_triage(header):
            raise AssertionError("triage_header must not be called without --triage")

        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.object(jev, "triage_header", fail_triage):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                result = mailbox.main(["--file", str(self.path), "--headers"])
        self.assertEqual(result, 0)
        self.assertEqual(
            stdout.getvalue(),
            "## lead-beo-skills -> supervisor | 2026-09-10T00:05:01Z | first\n"
            "## lead-beo-skills -> supervisor | 2026-09-10T00:10:02Z | second\n"
            "## lead-beo-skills -> supervisor | 2026-09-10T00:15:03Z | third\n",
        )
        self.assertEqual(stderr.getvalue(), "")

    def test_main_without_triage_runs_when_jev_is_unimportable(self):
        # jev needs python >= 3.10; a fresh mailbox must load and read headers
        # without it, and only --triage may import it.
        spec = importlib.util.spec_from_file_location(
            "mailbox_without_jev", SCRIPTS / "mailbox.py"
        )
        module = importlib.util.module_from_spec(spec)
        stdout = io.StringIO()
        with mock.patch.dict(sys.modules, {"jev": None, spec.name: module}):
            spec.loader.exec_module(module)
            with contextlib.redirect_stdout(stdout):
                result = module.main(["--file", str(self.path), "--headers", "--last", "1"])
            with self.assertRaises(ImportError):
                module.main(["--file", str(self.path), "--headers", "--triage"])
        self.assertEqual(result, 0)
        self.assertEqual(
            stdout.getvalue(),
            "## lead-beo-skills -> supervisor | 2026-09-10T00:15:03Z | third\n",
        )

    def test_triage_entries_requires_an_explicit_triage_callable(self):
        with self.assertRaises(TypeError):
            mailbox.triage_entries(mailbox._entries(self.path.read_text(encoding="utf-8")))

    def test_main_triage_without_headers_is_a_usage_error(self):
        calls = []
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.object(jev, "triage_header", lambda header: calls.append(header)):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as ctx:
                    mailbox.main(["--file", str(self.path), "--triage"])
        self.assertEqual(ctx.exception.code, 2)
        self.assertEqual(calls, [])
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("--triage requires --headers", stderr.getvalue())

    def test_main_triage_with_wake_is_a_usage_error(self):
        calls = []
        wakes = []
        original = mailbox.run_wake
        mailbox.run_wake = lambda seat, wake_text: wakes.append((seat, wake_text))
        self.addCleanup(setattr, mailbox, "run_wake", original)
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch.object(jev, "triage_header", lambda header: calls.append(header)):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as ctx:
                    mailbox.main(
                        ["--file", str(self.path), "--headers", "--triage", "--wake", "supervisor"]
                    )
        self.assertEqual(ctx.exception.code, 2)
        self.assertEqual(calls, [])
        self.assertEqual(wakes, [])
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("--triage cannot be combined with --wake", stderr.getvalue())

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

    def test_fractional_precision_header_and_since_are_rejected(self):
        fractional_header = "## lead-beo-skills -> supervisor | 2026-09-10T00:20:00.500Z | fractional"
        self.assertIsNone(mailbox.HEADER_RE.match(fractional_header))
        with self.assertRaisesRegex(ValueError, "ISO-8601"):
            mailbox.select_entries(fractional_header, since="2026-09-10T00:20:00.500Z")

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
        self.assertIn(f"mailbox: {self.path}: at least one of", stderr.getvalue())

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

    def test_unavailable_wake_uses_the_existing_failed_path(self):
        original = mailbox.run_wake
        mailbox.run_wake = lambda seat, wake_text: (_ for _ in ()).throw(
            mailbox.herdr_cli.HerdrUnavailable("herdr agent prompt supervisor timed out")
        )
        self.addCleanup(setattr, mailbox, "run_wake", original)
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = mailbox.main(["--file", str(self.path), "--wake", "supervisor"])
        self.assertEqual(result, 1)
        self.assertIn("wake failed", stderr.getvalue())

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

    def _not_found_then(self, *results):
        calls = []
        outcomes = [subprocess.CompletedProcess([], 1, "", "agent_not_found\n"), *results]

        def fake_wake(seat, wake_text):
            calls.append(seat)
            return outcomes[len(calls) - 1]

        patcher = mock.patch.object(mailbox, "run_wake", fake_wake)
        patcher.start()
        self.addCleanup(patcher.stop)
        return calls

    def test_supervisor_not_found_retries_once_at_recorded_live_pane(self):
        calls = self._not_found_then(subprocess.CompletedProcess([], 0, "", ""))
        self.pane_record.write_text("w1:p7\n", encoding="utf-8")
        mailbox.herdr_cli.run.return_value = subprocess.CompletedProcess(
            [], 0, '{"result": {"agent": {"name": null}}}', "")
        self.assertEqual(mailbox.main(["--file", str(self.path), "--wake", "supervisor"]), 0)
        self.assertEqual(calls, ["supervisor", "w1:p7"])
        mailbox.herdr_cli.run.assert_called_once_with(["agent", "get", "w1:p7"])
        self.assertIn("ran herdr agent prompt w1:p7", sys.stderr.getvalue())

    def test_supervisor_not_found_fails_closed_without_live_pane_record(self):
        for record, get in (
            (None, None),
            ("w1:p7\n", subprocess.CompletedProcess([], 1, "", '{"error": "pane_not_found"}')),
            ("w1:p7\n", subprocess.CompletedProcess([], 0, '{"result": {}}', "")),
        ):
            with self.subTest(record=record, get=get):
                calls = self._not_found_then()
                if record is None:
                    self.pane_record.unlink(missing_ok=True)
                else:
                    self.pane_record.write_text(record, encoding="utf-8")
                mailbox.herdr_cli.run.return_value = get
                sys.stderr.seek(0)
                sys.stderr.truncate()
                self.assertEqual(mailbox.main(["--file", str(self.path), "--wake", "supervisor"]), 1)
                self.assertEqual(calls, ["supervisor"])
                self.assertIn("wake failed: agent_not_found for supervisor", sys.stderr.getvalue())

    def test_other_seat_not_found_gets_no_pane_fallback(self):
        calls = self._not_found_then()
        self.pane_record.write_text("w1:p7\n", encoding="utf-8")
        self.assertEqual(mailbox.main(["--file", str(self.path), "--wake", "lead-x"]), 1)
        self.assertEqual(calls, ["lead-x"])
        mailbox.herdr_cli.run.assert_not_called()

    def test_every_read_fails_closed_on_an_unparseable_header_line(self):
        self.path.write_text(SAMPLE + "## lead -> supervisor | 2026-09-10T00:20Z | minute\n", encoding="utf-8")
        wakes = []
        with mock.patch.object(mailbox, "run_wake", lambda *a: wakes.append(a)):
            for argv in (["--headers"], ["--last", "1"], ["--since", "2026-09-10T00:00:00Z"],
                         ["--wake", "supervisor"]):
                with self.subTest(argv=argv):
                    for stream in (sys.stdout, sys.stderr):
                        stream.seek(0)
                        stream.truncate()
                    self.assertEqual(mailbox.main(["--file", str(self.path), *argv]), 1)
                    self.assertEqual(sys.stdout.getvalue(), "")
                    self.assertIn(
                        f"{self.path}: unparseable header at line 10: "
                        "## lead -> supervisor | 2026-09-10T00:20Z | minute",
                        sys.stderr.getvalue(),
                    )
        self.assertEqual(wakes, [])


class MailboxAppendTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir="/private/tmp")
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name) / ".herdr" / "projects"
        (root / "beo-skills").mkdir(parents=True)
        self.path = root / "beo-skills" / "supervisor-mailbox.md"
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        for args in (
            ["init", "-q"],
            ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
             "--allow-empty", "-m", "base"],
        ):
            subprocess.run(["git", "-C", str(self.repo), *args], check=True)
        self.head = gate_row.git(self.repo, "rev-parse", "HEAD")
        self.wakes = []
        self.wake_rc = 0
        for target, value in (
            ("HERDR_PROJECTS_ROOT", root),
            ("_now", lambda: mailbox.datetime(2026, 9, 24, 3, 4, 5, 678, mailbox.timezone.utc)),
            ("run_wake", self.fake_wake),
        ):
            patcher = mock.patch.object(mailbox, target, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        for stream, value in (("stdout", self.stdout), ("stderr", self.stderr)):
            patcher = mock.patch.object(sys, stream, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def fake_wake(self, seat, text):
        self.wakes.append((seat, text))
        return subprocess.CompletedProcess([], self.wake_rc, "", "agent_blocked\n" if self.wake_rc else "")

    def append(self, body, *extra, path=None, sender="lead-beo-skills", event="gate opened"):
        argv = [
            "--file", str(path or self.path), "--append", "--from", sender, "--to", "supervisor",
            "--repo", str(self.repo), "--event", event, "--stdin", *extra,
        ]
        with mock.patch.object(sys, "stdin", io.StringIO(body)):
            return mailbox.main(argv)

    def test_append_writes_answer_header_with_full_seconds_and_full_sha(self):
        self.assertEqual(self.append("detail\n"), 0, self.stderr.getvalue())
        header = f"## lead-beo-skills -> supervisor | 2026-09-24T03:04:05Z | gate opened | HEAD {self.head}"
        self.assertEqual(self.path.read_text(encoding="utf-8"), f"---\n{header}\ndetail\n")
        self.assertEqual(self.stdout.getvalue(), header + "\n")
        self.assertEqual(mailbox.select_entries(self.path.read_text(encoding="utf-8"), headers=True), [header])
        match = jev.HEADER_RE.fullmatch(header)
        self.assertEqual((match.group("event"), match.group("head")), ("gate opened", self.head))

    def test_append_attention_takes_slug_from_mailbox_directory_and_appends(self):
        self.assertEqual(self.append("one\n"), 0)
        self.assertEqual(self.append("two\n", "--attention", "human-gate"), 0)
        entries = mailbox._entries(self.path.read_text(encoding="utf-8"))
        self.assertEqual(len(entries), 2)
        self.assertEqual(
            entries[1].header,
            f"## lead-beo-skills -> supervisor | 2026-09-24T03:04:05Z | "
            f"ATTENTION beo-skills human-gate: gate opened | HEAD {self.head}",
        )
        self.assertEqual(entries[1].body, "two")

    def test_invalid_append_inputs_exit_non_zero_and_write_nothing(self):
        outside = Path(self.tmp.name) / "scratch-mailbox.md"
        cases = [
            dict(body="x\n", event="two\nlines"),
            dict(body="x\n", event="a | b"),
            dict(body="x\n", event=" "),
            dict(body=""),
            dict(body=" \n\n"),
            dict(body="x\n", sender="Lead Seat"),
            dict(body="x\n", path=outside),
            dict(body="ok\n## lead -> supervisor | 2026-09-24T03:04:05Z | ATTENTION G1 | HEAD abcdef1\n"),
            dict(body="ok\n## notes\n"),
        ]
        for case in cases:
            with self.subTest(case=case):
                self.assertNotEqual(self.append(**case), 0)
                self.assertFalse(self.path.exists())
                self.assertFalse(outside.exists())
        self.assertNotEqual(self.append("x\n", "--attention", "a|b"), 0)
        self.assertFalse(self.path.exists())
        with mock.patch.object(sys, "stdin", io.StringIO("x\n")):
            self.assertNotEqual(mailbox.main([
                "--file", str(self.path), "--append", "--from", "lead", "--to", "supervisor",
                "--repo", self.tmp.name + "/missing", "--event", "e", "--stdin",
            ]), 0)
        self.assertFalse(self.path.exists())

    def test_append_rejects_selectors_and_append_only_flags_need_append(self):
        for extra in (["--headers"], ["--last", "1"], ["--since", "2026-09-24T00:00:00Z"]):
            with self.subTest(extra=extra), self.assertRaises(SystemExit):
                self.append("x\n", *extra)
        with self.assertRaises(SystemExit):
            mailbox.main(["--file", str(self.path), "--headers", "--event", "e"])
        self.assertFalse(self.path.exists())

    def test_body_with_backticks_and_substitution_is_stored_verbatim_not_run(self):
        marker = Path(self.tmp.name) / "ran"
        body = f"`touch {marker}` $(touch {marker}) 'q' \"d\" $HOME\n"
        self.assertEqual(self.append(body), 0)
        self.assertTrue(self.path.read_text(encoding="utf-8").endswith(f"HEAD {self.head}\n{body}"))
        self.assertFalse(marker.exists())

    def test_append_always_wakes_to_seat_with_the_appended_header(self):
        self.assertEqual(self.append("x\n", "--attention", "compaction"), 0)
        self.assertEqual(len(self.wakes), 1)
        self.assertEqual(self.wakes[0][0], "supervisor")
        self.assertIn(f"ATTENTION beo-skills compaction: gate opened | HEAD {self.head}", self.wakes[0][1])

    def test_append_keeps_entry_and_returns_wake_code_when_wake_fails(self):
        self.wake_rc = 1
        self.assertEqual(self.append("x\n"), 1)
        self.assertEqual(len(mailbox._entries(self.path.read_text(encoding="utf-8"))), 1)
        self.assertIn("agent_blocked", self.stderr.getvalue())

    def test_append_with_wake_flag_is_a_usage_error(self):
        with self.assertRaises(SystemExit):
            self.append("x\n", "--wake", "supervisor")
        self.assertFalse(self.path.exists())
        self.assertEqual(self.wakes, [])

    def test_appended_attention_satisfies_gate_row_s2_mailbox_check(self):
        ledger = str(Path(self.tmp.name) / "gates.md")
        base = ["--repo", str(self.repo), "--ledger", ledger]
        self.assertEqual(gate_row.main(base + [
            "--kind", "deploy-gate", "--status", "open",
            "--words", "none", "--note", "deploy permission pending", "--quote", "",
        ]), 0, self.stderr.getvalue())
        gate_id = Path(ledger).read_text(encoding="utf-8").split(" | ", 1)[0]
        check = base + ["--check", "--mailbox", str(self.path)]
        self.assertEqual(self.append("x\n", event="no gate named"), 0)
        self.assertNotEqual(gate_row.main(check), 0)
        self.assertEqual(self.append("x\n", "--attention", "human-gate", event=f"deploy gate {gate_id}"), 0)
        self.assertEqual(gate_row.main(check), 0, self.stderr.getvalue())
        self.assertEqual(mailbox.main(["--file", str(self.path), "--headers"]), 0)
        self.assertEqual(len(self.wakes), 2)


if __name__ == "__main__":
    unittest.main()

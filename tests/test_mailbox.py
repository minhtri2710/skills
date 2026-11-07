#!/usr/bin/env python3
"""Tests for selective mailbox reads."""
from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import support
import backend
import mailbox
import gate_row
import state_root
from fake_backend import FakeBackend

_real_open_backend = backend.open_backend


def setUpModule() -> None:
    support.never_run("git")


def seats_under_test(handles: dict[str, str | None]) -> FakeBackend:
    """A fake standing in for the herdr adapter (the seat record names `herdr`)."""
    fake = FakeBackend()
    fake.name = "herdr"
    for handle, name in handles.items():
        fake.add_seat(handle, name=name)
    return fake


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
        self.tmp = tempfile.TemporaryDirectory(dir=os.path.realpath("/tmp"))
        root = Path(self.tmp.name) / ".agent-delivery" / "projects"
        project = root / "beo-skills"
        project.mkdir(parents=True)
        self.path = project / "supervisor-mailbox.md"
        self.path.write_text(SAMPLE, encoding="utf-8")
        root_patch = mock.patch.object(state_root, "STATE_ROOT", root)
        root_patch.start()
        self._stdout_patch = mock.patch.object(sys, "stdout", io.StringIO())
        self._stderr_patch = mock.patch.object(sys, "stderr", io.StringIO())
        self._stdout_patch.start()
        self._stderr_patch.start()
        self.addCleanup(self._stderr_patch.stop)
        self.addCleanup(self._stdout_patch.stop)
        self.addCleanup(root_patch.stop)
        self.addCleanup(self.tmp.cleanup)
        self.seat_record = project / "supervisor-seat"
        self.seat_record.write_text("herdr w1:p7\n", encoding="utf-8")
        self.fake = seats_under_test({"w1:p7": "supervisor", "w1:p8": "lead-x"})
        opener = mock.patch.object(backend, "open_backend", return_value=self.fake)
        self.open_backend = opener.start()
        self.addCleanup(opener.stop)

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

    def test_since_and_last_are_mutually_exclusive(self):
        with contextlib.redirect_stderr(io.StringIO()) as stderr:
            with self.assertRaises(SystemExit) as ctx:
                mailbox.main(
                    ["--file", str(self.path), "--since", "2026-09-10T00:10:02Z", "--last", "1"]
                )
        self.assertEqual(ctx.exception.code, 2)
        self.assertIn("not allowed with argument", stderr.getvalue())

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

    def test_parse_header_reads_the_fields_this_module_writes_and_refuses_other_lines(self):
        head = "a" * 40
        line = f"## lead-x -> supervisor | 2026-09-24T03:04:05Z | ATTENTION beo-skills human-gate: G1 | HEAD {head}"
        self.assertEqual(
            mailbox.parse_header(line),
            mailbox.Header(line, "lead-x", "supervisor", "2026-09-24T03:04:05Z",
                           "ATTENTION beo-skills human-gate: G1", head, "beo-skills human-gate: G1"),
        )
        answer = mailbox.parse_header("## lead-x -> supervisor | 2026-09-24T03:04:05Z | first")
        self.assertEqual((answer.event, answer.head, answer.attention), ("first", None, None))
        for text in ("ATTENTION G1 | HEAD " + head, "## lead-x -> supervisor | 2026-09-24T03:04Z | e",
                     "## lead-x -> supervisor | 2026-09-24T03:04:05.5Z | e", "## notes"):
            with self.subTest(text=text):
                self.assertIsNone(mailbox.parse_header(text))

    def test_attention_text_is_what_parse_header_reads_back_as_the_attention(self):
        event = mailbox.attention_text("beo-skills", "human-gate", "gate opened")
        header = mailbox.parse_header(f"## a -> supervisor | 2026-09-24T03:04:05Z | {event} | HEAD {'b' * 40}")
        self.assertEqual(header.attention, "beo-skills human-gate: gate opened")

    def test_minute_and_fractional_precision_header_and_since_are_rejected(self):
        minute_header = "## lead-beo-skills -> supervisor | 2026-09-10T00:20Z | minute"
        fractional_header = "## lead-beo-skills -> supervisor | 2026-09-10T00:20:00.500Z | fractional"
        for header, since in ((minute_header, "2026-09-10T00:20Z"), (fractional_header, "2026-09-10T00:20:00.500Z")):
            with self.subTest(since=since):
                self.assertIsNone(mailbox.parse_header(header))
                with self.assertRaisesRegex(ValueError, "ISO-8601"):
                    mailbox.select_entries(header, since=since)
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
        self.assertIn(f"mailbox: {self.path}: at least one of", stderr.getvalue())

    def clear_streams(self):
        for stream in (sys.stdout, sys.stderr):
            stream.seek(0)
            stream.truncate()

    def wake(self, seat="supervisor", *extra):
        return mailbox.main(["--file", str(self.path), "--wake", seat, *extra])

    def test_wake_prompts_the_recorded_supervisor_handle_once_for_last_header(self):
        self.assertEqual(self.wake(), 0)
        [(operation, handle, text)] = self.fake.calls
        self.assertEqual((operation, handle), ("prompt", "w1:p7"))
        self.assertIn(str(self.path), text)
        self.assertIn("third", text)
        self.assertEqual(sys.stdout.getvalue(), "")
        self.assertIn("prompted w1:p7 on herdr", sys.stderr.getvalue())
        self.assertEqual(self.path.read_bytes(), SAMPLE.encode("utf-8"))
        self.assertEqual(len(mailbox.select_entries(self.path.read_text(encoding="utf-8"), headers=True)), 3)

    def test_wake_without_header_is_unsent_and_does_not_wake(self):
        self.path.write_text("not a mailbox entry\n", encoding="utf-8")
        self.assertNotEqual(self.wake(), 0)
        self.open_backend.assert_not_called()
        self.assertEqual(self.fake.calls, [])
        self.assertEqual(sys.stdout.getvalue(), "")
        self.assertIn("UNSENT", sys.stderr.getvalue())
        self.assertIn("wake not attempted", sys.stderr.getvalue())

    def test_wake_refuses_a_file_outside_the_projects_root(self):
        scratch = Path(self.tmp.name) / "scratch-mailbox.md"
        scratch.write_text(SAMPLE, encoding="utf-8")
        self.assertNotEqual(mailbox.main(["--file", str(scratch), "--wake", "supervisor"]), 0)
        self.open_backend.assert_not_called()
        self.assertEqual(self.fake.calls, [])
        self.assertEqual(sys.stdout.getvalue(), "")
        self.assertIn("refused", sys.stderr.getvalue())

    def test_unavailable_wake_uses_the_existing_failed_path(self):
        self.fake.script("prompt", backend.BackendUnavailable("herdr agent prompt w1:p7 timed out"))
        self.assertEqual(self.wake(), 1)
        self.assertIn("wake failed: herdr agent prompt w1:p7 timed out", sys.stderr.getvalue())

    def test_wake_failure_is_not_retried(self):
        self.fake.script("prompt", backend.SeatError("blocked", "herdr agent prompt failed: agent_blocked"))
        self.assertEqual(self.wake(), 1)
        self.assertEqual([call[:2] for call in self.fake.calls], [("prompt", "w1:p7")])
        self.assertIn("agent_blocked", sys.stderr.getvalue())

    def test_supervisor_not_found_at_the_recorded_handle_fails_without_a_second_try(self):
        self.fake.script("prompt", backend.SeatError("not_found", "herdr agent prompt failed: agent_not_found"))
        self.assertEqual(self.wake(), 1)
        self.assertEqual([call[:2] for call in self.fake.calls], [("prompt", "w1:p7")])
        self.assertIn("wake failed: herdr agent prompt failed: agent_not_found", sys.stderr.getvalue())

    def test_supervisor_wake_fails_closed_on_a_missing_or_malformed_seat_record(self):
        for label, text in (
            ("missing", None),
            ("empty", ""),
            ("two lines", "herdr w1:p7\nherdr w1:p8\n"),
            ("no backend", "w1:p7\n"),
            ("unknown backend", "tmux w1:p7\n"),
            ("bad handle", "herdr w1 p7\n"),
            ("old pane-only record", "w1:p7 extra\n"),
        ):
            with self.subTest(label):
                self.clear_streams()
                if text is None:
                    self.seat_record.unlink()
                else:
                    self.seat_record.write_text(text, encoding="utf-8")
                self.assertEqual(self.wake(), 1)
                self.assertIn("wake failed: no usable supervisor seat record", sys.stderr.getvalue())
                self.open_backend.assert_not_called()
                self.assertEqual(self.fake.calls, [])

    def test_supervisor_wake_refuses_a_record_from_another_backend(self):
        self.seat_record.write_text("hc t7\n", encoding="utf-8")
        self.assertEqual(self.wake(), 1)
        self.assertIn("no cross-backend wake", sys.stderr.getvalue())
        self.assertEqual(self.fake.calls, [])

    def test_supervisor_name_is_not_looked_up_without_a_record(self):
        self.seat_record.unlink()
        self.assertEqual(self.wake(), 1)
        self.assertEqual(self.fake.calls, [])

    def test_the_lead_is_woken_at_its_recorded_handle_and_refused_without_a_record(self):
        lead_record = self.path.parent / "lead-seat"
        self.assertEqual(self.wake("lead"), 1)
        self.assertIn("wake failed: no usable lead seat record", sys.stderr.getvalue())
        self.assertEqual(self.fake.calls, [])
        self.open_backend.assert_not_called()
        lead_record.write_text("herdr w1:p8\n", encoding="utf-8")
        self.clear_streams()
        self.assertEqual(self.wake("lead"), 0)
        [(operation, handle, text)] = self.fake.calls
        self.assertEqual((operation, handle), ("prompt", "w1:p8"))
        self.assertIn("Seat lead:", text)

    def test_a_seat_that_is_not_a_role_is_refused_by_name(self):
        self.assertEqual(self.wake("lead-x"), 1)
        self.assertIn("wake failed: 'lead-x' is not a seat role", sys.stderr.getvalue())
        self.assertEqual(self.fake.calls, [])

    def test_wake_refuses_a_mailbox_that_is_not_a_project_mailbox_path(self):
        nested = self.path.parent / "runs" / "x" / "supervisor-mailbox.md"
        nested.parent.mkdir(parents=True)
        renamed = self.path.parent / "notes.md"
        for refused in (nested, renamed):
            with self.subTest(path=refused.name):
                refused.write_text(SAMPLE, encoding="utf-8")
                self.assertEqual(mailbox.main(["--file", str(refused), "--wake", "supervisor"]), 1)
                self.assertIn("refused", sys.stderr.getvalue())
                self.assertEqual(self.fake.calls, [])

    def test_backend_flag_reaches_detect_as_explicit(self):
        error = backend.DetectionError("no supported terminal tool signature matches this environment")
        with mock.patch.object(backend, "open_backend", _real_open_backend), \
                mock.patch.object(backend, "detect", side_effect=error) as detect:
            self.assertEqual(self.wake("supervisor", "--backend", "herdr@w1:p7"), 1)
        self.assertEqual(detect.call_args.args[1], backend.Explicit("herdr", "w1:p7"))
        self.assertIn(f"wake failed: {error}", sys.stderr.getvalue())

    def test_every_read_fails_closed_on_an_unparseable_header_line(self):
        self.path.write_text(SAMPLE + "## lead -> supervisor | 2026-09-10T00:20Z | minute\n", encoding="utf-8")
        for argv in (["--headers"], ["--last", "1"], ["--since", "2026-09-10T00:00:00Z"],
                     ["--wake", "supervisor"]):
            with self.subTest(argv=argv):
                self.clear_streams()
                self.assertEqual(mailbox.main(["--file", str(self.path), *argv]), 1)
                self.assertEqual(sys.stdout.getvalue(), "")
                self.assertIn(
                    f"{self.path}: unparseable header at line 10: "
                    "## lead -> supervisor | 2026-09-10T00:20Z | minute",
                    sys.stderr.getvalue(),
                )
        self.assertEqual(self.fake.calls, [])


class MailboxAppendTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.path.realpath("/tmp"))
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name) / ".agent-delivery" / "projects"
        (root / "beo-skills").mkdir(parents=True)
        self.path = root / "beo-skills" / "supervisor-mailbox.md"
        self.repo = support.temp_git_repo(Path(self.tmp.name) / "repo")
        support.git(self.repo, "commit", "-q", "--allow-empty", "-m", "base")
        self.head = support.git(self.repo, "rev-parse", "HEAD")
        (root / "beo-skills" / "supervisor-seat").write_text("herdr w1:p7\n", encoding="utf-8")
        self.fake = seats_under_test({"w1:p7": "supervisor"})
        for module, name, value in (
            (mailbox, "_now", lambda: mailbox.datetime(2026, 9, 24, 3, 4, 5, 678, mailbox.timezone.utc)),
            (backend, "open_backend", lambda environ, explicit=None: self.fake),
        ):
            patcher = mock.patch.object(module, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        root_patch = mock.patch.object(state_root, "STATE_ROOT", root)
        root_patch.start()
        self.addCleanup(root_patch.stop)
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        for stream, value in (("stdout", self.stdout), ("stderr", self.stderr)):
            patcher = mock.patch.object(sys, stream, value)
            patcher.start()
            self.addCleanup(patcher.stop)

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
        self.assertRegex(
            header,
            r"^## lead-beo-skills -> supervisor \| "
            r"2026-09-24T03:04:05Z \| gate opened \| HEAD "
            r"[0-9a-f]{40}$",
        )
        self.assertEqual(
            mailbox.parse_header(header),
            mailbox.Header(header, "lead-beo-skills", "supervisor", "2026-09-24T03:04:05Z", "gate opened", self.head, None),
        )

    def test_append_without_stdin_writes_a_header_only_entry(self):
        argv = ["--file", str(self.path), "--append", "--from", "lead-beo-skills", "--to", "supervisor",
                "--repo", str(self.repo), "--event", "G1 PR#1"]
        self.assertEqual(mailbox.main(argv), 0, self.stderr.getvalue())
        self.assertEqual(self.append("two\n"), 0)
        header = f"## lead-beo-skills -> supervisor | 2026-09-24T03:04:05Z | G1 PR#1 | HEAD {self.head}"
        self.assertTrue(self.path.read_text(encoding="utf-8").startswith(f"---\n{header}\n---\n"))
        self.assertEqual(
            mailbox.select_entries(self.path.read_text(encoding="utf-8")),
            [f"{header}\n", f"{header.replace('G1 PR#1', 'gate opened')}\ntwo"],
        )

    def test_append_attention_takes_slug_from_mailbox_directory_and_appends(self):
        self.assertEqual(self.append("one\n"), 0)
        self.assertEqual(self.append("two\n", "--attention", "human-gate"), 0)
        header = (
            f"## lead-beo-skills -> supervisor | 2026-09-24T03:04:05Z | "
            f"ATTENTION beo-skills human-gate: gate opened | HEAD {self.head}"
        )
        entries = mailbox.select_entries(self.path.read_text(encoding="utf-8"))
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[1], f"{header}\ntwo")
        self.assertEqual(mailbox.parse_header(header).attention, "beo-skills human-gate: gate opened")

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

    def test_a_mailbox_other_than_the_project_mailbox_path_is_refused(self):
        nested = self.path.parent / "runs" / "x" / "supervisor-mailbox.md"
        nested.parent.mkdir(parents=True)
        renamed = self.path.parent / "notes.md"
        for refused in (nested, renamed):
            with self.subTest(path=refused.name):
                self.assertNotEqual(self.append("x\n", "--attention", "human-gate", path=refused), 0)
                self.assertIn("refused", self.stderr.getvalue())
                self.assertFalse(refused.exists())
        self.assertEqual(self.fake.calls, [])

    def test_append_to_a_seat_that_is_not_a_role_writes_nothing_and_wakes_nothing(self):
        argv = ["--file", str(self.path), "--append", "--from", "lead-beo-skills", "--to", "lead-x",
                "--repo", str(self.repo), "--event", "gate opened"]
        self.assertNotEqual(mailbox.main(argv), 0)
        self.assertIn("'lead-x' is not a seat role", self.stderr.getvalue())
        self.assertFalse(self.path.exists())
        self.assertEqual(self.fake.calls, [])

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
        self.assertEqual(self.append("x\n", "--attention", "human-gate"), 0)
        [(operation, handle, text)] = self.fake.calls
        self.assertEqual((operation, handle), ("prompt", "w1:p7"))
        self.assertIn(f"ATTENTION beo-skills human-gate: gate opened | HEAD {self.head}", text)

    def test_append_keeps_entry_and_returns_wake_code_when_wake_fails(self):
        self.fake.script("prompt", backend.SeatError("blocked", "herdr agent prompt failed: agent_blocked"))
        self.assertEqual(self.append("x\n"), 1)
        self.assertEqual(len(mailbox.select_entries(self.path.read_text(encoding="utf-8"), headers=True)), 1)
        self.assertIn("agent_blocked", self.stderr.getvalue())

    def test_append_with_wake_flag_is_a_usage_error(self):
        with self.assertRaises(SystemExit):
            self.append("x\n", "--wake", "supervisor")
        self.assertFalse(self.path.exists())
        self.assertEqual(self.fake.calls, [])

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
        self.assertEqual(len(self.fake.calls), 2)


if __name__ == "__main__":
    unittest.main()

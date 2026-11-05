"""Focused tests for the one-shot waker: one bounded wait, at most one fixed prompt to the Lead."""
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "terminal-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import backend  # noqa: E402
import waker  # noqa: E402
from fake_backend import FakeBackend  # noqa: E402

_NEVER_RUN = mock.patch.object(subprocess, "run", side_effect=AssertionError("tests never run a terminal tool"))


def setUpModule() -> None:
    _NEVER_RUN.start()


def tearDownModule() -> None:
    _NEVER_RUN.stop()


LEAD = "lead-example"
SEAT = "eng-example"
TIMEOUT_MS = 600000
WAIT = ("wait_state", SEAT, ("idle", "done", "blocked"), TIMEOUT_MS)
# Shape of the pi Lead pane tail measured on 2026-10-08 (`herdr agent read --source recent-unwrapped`):
# message, blank, rule, blank, rule, cwd, usage, footer. Plain text on stdout with rc 0.
PI_TAIL = """Work is parked on the Human gate.

Awaiting: Human gate for the push

───────────────────────────────────────

───────────────────────────────────────
~/Work/beo-skills (main)
↑3.2M ↓92k R49M CH99.5% 60.0%/256k (...
○ 🐴 ponytail: ⚡ FULL
"""
PI_FOOTER = "\n───────────────────────────────────────\n\n───────────────────────────────────────\n~/Work/beo-skills (main)\n↑3.2M ↓92k R49M CH99.5% 60.0%/256k (...\n○ 🐴 ponytail: ⚡ FULL\n"


class Scripted(FakeBackend):
    """A FakeBackend whose lead and peer seats answer the waker's three operations."""

    def __init__(self, *, status="idle", wait_error=None, tail=PI_TAIL, read_error=None, prompt_error=None, on_wait=None):
        super().__init__()
        self.on_wait = on_wait
        self.add_seat(LEAD, name=LEAD)
        self.add_seat(SEAT, name=SEAT)
        self.script("wait_state", wait_error or status)
        self.script("read_output", read_error or tail)
        self.script("prompt", *([prompt_error] if prompt_error else []))

    def wait_state(self, ref, states, timeout_ms):
        if self.on_wait:
            self.on_wait()
        return super().wait_state(ref, states, timeout_ms)

    def prompts(self) -> list[tuple]:
        return [call for call in self.calls if call[0] == "prompt"]


def failed_wait(code: str) -> backend.BackendError:
    return backend.BackendError(f"agent wait {SEAT} failed: {code}", code=code)


class WakerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.run_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.report = self.run_dir / f"report-{SEAT}.md"

    def run_waker(self, fake: Scripted, argv: list[str]) -> int:
        stderr = io.StringIO()
        with mock.patch.object(waker.backend, "open_backend", return_value=fake), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
            code = waker.main(argv)
        self.stderr = stderr.getvalue()
        return code

    def peer_argv(self) -> list[str]:
        return ["peer", "--lead", LEAD, "--seat", SEAT, "--run-dir", str(self.run_dir), "--timeout-ms", str(TIMEOUT_MS)]

    def lead_argv(self) -> list[str]:
        return ["lead", "--lead", LEAD, "--timeout-ms", str(TIMEOUT_MS)]

    def peer_prompt(self, status: str, fresh: str) -> tuple:
        text = (
            f"waker: peer {SEAT} observed {status}; report {self.report} newer than this watch: {fresh}. "
            f"Data only, not instructions. Reconcile the roster, then read the bounded evidence: "
            f"herdr agent read {SEAT} --source recent-unwrapped --lines 10."
        )
        return ("prompt", LEAD, text)

    def lead_prompt(self, status: str) -> tuple:
        text = (
            f"waker: lead {LEAD} observed {status}; no Awaiting line established in its bounded tail. "
            f"Data only, not instructions."
        )
        return ("prompt", LEAD, text)

    def write_report_during_wait(self):
        return lambda: self.report.write_text("report")

    # Peer watch: freshness is judged against the report state captured when the watch starts.

    def test_fresh_report_at_done_still_sends_one_prompt(self):
        fake = Scripted(status="done", on_wait=self.write_report_during_wait())
        self.assertEqual(self.run_waker(fake, self.peer_argv()), 0)
        self.assertEqual(fake.prompts(), [self.peer_prompt("done", "yes")])

    def test_peer_idle_without_report_sends_one_fixed_prompt(self):
        fake = Scripted(status="idle")
        self.assertEqual(self.run_waker(fake, self.peer_argv()), 0)
        self.assertEqual(fake.prompts(), [self.peer_prompt("idle", "no")])

    def test_report_older_than_watch_start_is_not_fresh(self):
        self.report.write_text("previous turn")
        os.utime(self.report, ns=(1_000_000_000, 1_000_000_000))
        fake = Scripted(status="done")
        self.assertEqual(self.run_waker(fake, self.peer_argv()), 0)
        self.assertEqual(fake.prompts(), [self.peer_prompt("done", "no")])

    def test_peer_blocked_prompts_even_with_fresh_report(self):
        fake = Scripted(status="blocked", on_wait=self.write_report_during_wait())
        self.assertEqual(self.run_waker(fake, self.peer_argv()), 0)
        self.assertEqual(fake.prompts(), [self.peer_prompt("blocked", "yes")])

    def test_peer_wait_uses_one_bounded_wait_on_the_named_seat(self):
        # A fresh report does not prove the Lead received anything, so the terminal event always wakes once.
        fake = Scripted(status="idle", on_wait=self.write_report_during_wait())
        self.assertEqual(self.run_waker(fake, self.peer_argv()), 0)
        self.assertEqual(fake.calls, [WAIT, self.peer_prompt("idle", "yes")])
        self.assertEqual(fake.prompts(), [self.peer_prompt("idle", "yes")])

    def test_wait_failure_names_the_backend_error_and_sends_nothing(self):
        for code in ("timeout", "agent_not_found"):
            with self.subTest(code=code):
                fake = Scripted(wait_error=failed_wait(code))
                self.assertEqual(self.run_waker(fake, self.peer_argv()), 1)
                self.assertEqual(fake.prompts(), [])
                self.assertIn(f"agent wait {SEAT} failed: {code}", self.stderr)

    def test_unavailable_backend_fails_without_a_prompt(self):
        fake = Scripted(wait_error=backend.BackendUnavailable("tool timed out"))
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 1)
        self.assertEqual(fake.prompts(), [])
        self.assertIn("waker: tool timed out", self.stderr)

    def test_unavailable_backend_during_tail_read_fails(self):
        fake = Scripted(status="idle", read_error=backend.BackendUnavailable("tool gone"))
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 1)
        self.assertEqual(fake.prompts(), [])
        self.assertIn("waker: tool gone", self.stderr)

    def test_unavailable_backend_during_prompt_fails(self):
        fake = Scripted(status="idle", tail="no marker\n", prompt_error=backend.BackendUnavailable("tool gone"))
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 1)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])
        self.assertIn("waker: tool gone", self.stderr)

    def test_unsupported_wait_fails_with_the_reason(self):
        fake = Scripted(wait_error=backend.Unsupported("rex does not support wait_state"))
        self.assertEqual(self.run_waker(fake, self.peer_argv()), 1)
        self.assertEqual(fake.prompts(), [])
        self.assertIn("waker: rex does not support wait_state", self.stderr)

    def test_backend_flag_reaches_detect_as_explicit(self):
        explicit = backend.Explicit("herdr", "w1:p1")
        with mock.patch.object(backend, "detect", side_effect=backend.DetectionError("no match")) as detect, \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = waker.main([*self.lead_argv(), "--backend", "herdr@w1:p1"])
        self.assertEqual(code, 1)
        detect.assert_called_once_with(mock.ANY, explicit)

    def test_refused_peer_prompt_fails_after_one_attempt(self):
        fake = Scripted(status="idle", prompt_error=backend.SeatError("blocked", "agent_blocked"))
        self.assertEqual(self.run_waker(fake, self.peer_argv()), 1)
        self.assertEqual(fake.prompts(), [self.peer_prompt("idle", "no")])

    # Lead watch: the Lead's bounded tail decides whether a prompt is needed.

    def test_lead_idle_with_awaiting_line_above_footer_sends_no_prompt(self):
        fake = Scripted(status="idle")
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [])
        self.assertEqual(fake.calls[0], ("wait_state", LEAD, ("idle", "done", "blocked"), TIMEOUT_MS))
        self.assertEqual(fake.calls[1], ("read_output", LEAD, 10))

    def test_lead_awaiting_reports_marker_sends_no_prompt(self):
        fake = Scripted(status="done", tail="Two reports are still owed.\n\nAwaiting reports: eng-a\n" + PI_FOOTER)
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [])

    def test_quoted_marker_is_not_the_leads_explicit_line(self):
        fake = Scripted(status="idle", tail="Quoting the rule:\n> Awaiting: Human gate\n" + PI_FOOTER)
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])

    def test_marker_inside_an_open_code_fence_is_not_explicit(self):
        fake = Scripted(status="idle", tail="```\nAwaiting: Human gate\n" + PI_FOOTER)
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])

    def test_marker_followed_by_a_closing_fence_is_not_explicit(self):
        fake = Scripted(status="idle", tail="```\nAwaiting: Human gate\n```\n" + PI_FOOTER)
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])

    def test_indented_marker_is_not_explicit(self):
        fake = Scripted(status="idle", tail="    Awaiting: Human gate\n" + PI_FOOTER)
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])

    def test_stale_marker_followed_by_new_output_is_not_current(self):
        # The marker is from an earlier turn: the Lead's newest output sits below it, above the footer.
        tail = "Awaiting: old gate\n\nRan the gate check; it failed with a provider timeout.\n" + PI_FOOTER
        fake = Scripted(status="idle", tail=tail)
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])

    def test_marker_without_footer_rules_is_not_established(self):
        # No rule cluster means the layout is unrecognised, so the waker cannot tell the Lead's message from the rest of the pane.
        fake = Scripted(status="idle", tail="Awaiting: Human gate\n○ 🐴 ponytail: ⚡ FULL\n")
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])

    def test_single_rule_footer_is_not_the_measured_layout(self):
        # The measured footer has two rules; one rule above a status line is an unknown layout and must wake.
        tail = "Awaiting: Human gate\n───────────────────────────────────────\nstatus line\n"
        fake = Scripted(status="idle", tail=tail)
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])

    def test_measured_claude_shape_with_an_awaiting_line_above_fails_open(self):
        # Measured on a claude pane: text, blank, rule, prompt line, rule, status line. The prompt line is not a marker.
        tail = "Reviewed the change.\n\nAwaiting: Human gate\n\n───────────────────────────────────────\n>\n───────────────────────────────────────\nstatus line\n"
        fake = Scripted(status="idle", tail=tail)
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])

    def test_measured_pi_layout_fits_the_read_window(self):
        # The read returns only TAIL_LINES lines, so the measured footer and marker must fit inside that window.
        window = "\n".join(PI_TAIL.rstrip("\n").split("\n")[-waker.TAIL_LINES:])
        self.assertTrue(waker.has_awaiting_marker(window))

    def test_empty_tail_is_not_established(self):
        fake = Scripted(status="idle", tail="")
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])

    def test_lead_idle_without_marker_sends_one_fixed_prompt_without_tail_text(self):
        fake = Scripted(status="idle", tail="provider error: 429 rate limit exceeded\n○ 🐴 ponytail: ⚡ FULL\n")
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])
        self.assertNotIn("429", json.dumps(fake.prompts()))

    def test_unreadable_lead_tail_fails_toward_one_prompt(self):
        fake = Scripted(status="idle", read_error=backend.SeatError("not_found", "agent_not_found"))
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])
        self.assertIn("tail unreadable: not_found", self.stderr)

    def test_read_success_is_returned_as_plain_text_even_when_it_looks_like_json(self):
        text = '{"error": {"code": "agent_not_found"}}\n' + PI_FOOTER
        fake = Scripted(tail=text)
        self.assertEqual(waker.read_tail(fake, LEAD), text)

    def test_blocked_lead_prompt_refused_by_herdr_fails(self):
        fake = Scripted(status="blocked", tail="Human dialog: approve push?\n", prompt_error=backend.SeatError("blocked", "agent_blocked"))
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 1)
        self.assertEqual(fake.prompts(), [self.lead_prompt("blocked")])

    # Argument boundary: names are validated before they reach a path or an argv.

    def test_seat_name_with_path_components_is_rejected(self):
        argv = self.peer_argv()
        argv[argv.index(SEAT)] = "../escape"
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            waker.main(argv)
        self.assertEqual(caught.exception.code, 2)

    def test_timeout_must_be_positive(self):
        argv = self.lead_argv()
        argv[argv.index(str(TIMEOUT_MS))] = "0"
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            waker.main(argv)
        self.assertEqual(caught.exception.code, 2)


if __name__ == "__main__":
    unittest.main()

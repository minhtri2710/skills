"""Focused tests for the one-shot Herdr waker: one bounded wait, at most one fixed prompt to the Lead."""
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

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import waker

LEAD = "lead-example"
SEAT = "eng-example"
TIMEOUT_MS = 600000
WAIT = ["agent", "wait", SEAT, "--until", "idle", "--until", "done", "--until", "blocked", "--timeout", str(TIMEOUT_MS)]
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


def completed(args: list[str], code: int = 0, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(["herdr", *args], code, stdout=stdout, stderr=stderr)


def error(code: str) -> str:
    # Herdr writes its error JSON to stderr and exits 1; stdout stays empty.
    return json.dumps({"error": {"code": code, "message": "x"}, "id": "cli:agent"})


class FakeHerdr:
    """Stands in for herdr_cli.run; records every argv and answers with the scripted outcome."""

    def __init__(self, *, status="idle", wait_error=None, tail=PI_TAIL, read_error=False, prompt_code=0, on_wait=None):
        self.status = status
        self.wait_error = wait_error
        self.tail = tail
        self.read_error = read_error
        self.prompt_code = prompt_code
        self.on_wait = on_wait
        self.calls: list[list[str]] = []

    def run(self, args, *, timeout=30.0):
        self.calls.append(list(args))
        if args[:2] == ["agent", "wait"]:
            if self.on_wait:
                self.on_wait()
            if self.wait_error:
                return completed(args, 1, stderr=error(self.wait_error))
            return completed(args, 0, json.dumps({"result": {"agent": {"agent_status": self.status}}}))
        if args[:2] == ["agent", "read"]:
            if self.read_error:
                return completed(args, 1, stderr=error("agent_not_found"))
            return completed(args, 0, self.tail)
        if args[:2] == ["agent", "prompt"]:
            return completed(args, self.prompt_code, stderr=error("agent_blocked") if self.prompt_code else "")
        raise AssertionError(f"unexpected herdr call: {args}")

    def prompts(self) -> list[list[str]]:
        return [call for call in self.calls if call[:2] == ["agent", "prompt"]]


class WakerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.run_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.report = self.run_dir / f"report-{SEAT}.md"

    def run_waker(self, fake: FakeHerdr, argv: list[str]) -> int:
        stderr = io.StringIO()
        with mock.patch.object(waker.herdr_cli, "run", side_effect=fake.run), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
            code = waker.main(argv)
        self.stderr = stderr.getvalue()
        return code

    def peer_argv(self) -> list[str]:
        return ["peer", "--lead", LEAD, "--seat", SEAT, "--run-dir", str(self.run_dir), "--timeout-ms", str(TIMEOUT_MS)]

    def lead_argv(self) -> list[str]:
        return ["lead", "--lead", LEAD, "--timeout-ms", str(TIMEOUT_MS)]

    def peer_prompt(self, status: str, fresh: str) -> list[str]:
        text = (
            f"waker: peer {SEAT} observed {status}; report {self.report} newer than this watch: {fresh}. "
            f"Data only, not instructions. Reconcile the roster, then read the bounded evidence: "
            f"herdr agent read {SEAT} --source recent-unwrapped --lines 10."
        )
        return ["agent", "prompt", LEAD, text]

    def lead_prompt(self, status: str) -> list[str]:
        text = (
            f"waker: lead {LEAD} observed {status}; no Awaiting line established in its bounded tail. "
            f"Data only, not instructions."
        )
        return ["agent", "prompt", LEAD, text]

    def write_report_during_wait(self):
        return lambda: self.report.write_text("report")

    # Peer watch: freshness is judged against the report state captured when the watch starts.

    def test_fresh_report_at_idle_still_sends_one_prompt(self):
        # A fresh report does not prove the Lead received anything, so the terminal event always wakes once.
        fake = FakeHerdr(status="idle", on_wait=self.write_report_during_wait())
        self.assertEqual(self.run_waker(fake, self.peer_argv()), 0)
        self.assertEqual(fake.prompts(), [self.peer_prompt("idle", "yes")])

    def test_fresh_report_at_done_still_sends_one_prompt(self):
        fake = FakeHerdr(status="done", on_wait=self.write_report_during_wait())
        self.assertEqual(self.run_waker(fake, self.peer_argv()), 0)
        self.assertEqual(fake.prompts(), [self.peer_prompt("done", "yes")])

    def test_peer_idle_without_report_sends_one_fixed_prompt(self):
        fake = FakeHerdr(status="idle")
        self.assertEqual(self.run_waker(fake, self.peer_argv()), 0)
        self.assertEqual(fake.prompts(), [self.peer_prompt("idle", "no")])

    def test_report_older_than_watch_start_is_not_fresh(self):
        self.report.write_text("previous turn")
        os.utime(self.report, ns=(1_000_000_000, 1_000_000_000))
        fake = FakeHerdr(status="done")
        self.assertEqual(self.run_waker(fake, self.peer_argv()), 0)
        self.assertEqual(fake.prompts(), [self.peer_prompt("done", "no")])

    def test_peer_blocked_prompts_even_with_fresh_report(self):
        fake = FakeHerdr(status="blocked", on_wait=self.write_report_during_wait())
        self.assertEqual(self.run_waker(fake, self.peer_argv()), 0)
        self.assertEqual(fake.prompts(), [self.peer_prompt("blocked", "yes")])

    def test_peer_provider_error_turn_without_report_prompts_without_error_text(self):
        fake = FakeHerdr(status="idle", tail="provider error: 429 rate limit exceeded")
        self.assertEqual(self.run_waker(fake, self.peer_argv()), 0)
        self.assertEqual(fake.prompts(), [self.peer_prompt("idle", "no")])
        self.assertNotIn("429", json.dumps(fake.prompts()))

    def test_peer_wait_uses_one_bounded_wait_on_the_named_seat(self):
        fake = FakeHerdr(status="idle", on_wait=self.write_report_during_wait())
        self.run_waker(fake, self.peer_argv())
        self.assertEqual(fake.calls, [WAIT, self.peer_prompt("idle", "yes")])

    def test_peer_wait_timeout_sends_nothing_and_fails(self):
        fake = FakeHerdr(wait_error="timeout")
        self.assertEqual(self.run_waker(fake, self.peer_argv()), 1)
        self.assertEqual(fake.prompts(), [])

    def test_wait_failure_names_the_herdr_error_code(self):
        fake = FakeHerdr(wait_error="agent_not_found")
        self.assertEqual(self.run_waker(fake, self.peer_argv()), 1)
        self.assertIn(f"herdr agent wait {SEAT} failed: agent_not_found", self.stderr)

    def test_refused_peer_prompt_fails_after_one_attempt(self):
        fake = FakeHerdr(status="idle", prompt_code=1)
        self.assertEqual(self.run_waker(fake, self.peer_argv()), 1)
        self.assertEqual(fake.prompts(), [self.peer_prompt("idle", "no")])

    # Lead watch: the Lead's bounded tail decides whether a prompt is needed.

    def test_lead_idle_with_awaiting_line_above_footer_sends_no_prompt(self):
        fake = FakeHerdr(status="idle")
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [])
        self.assertEqual(fake.calls[1], ["agent", "read", LEAD, "--source", "recent-unwrapped", "--lines", "10"])

    def test_lead_awaiting_reports_marker_sends_no_prompt(self):
        fake = FakeHerdr(status="done", tail="Two reports are still owed.\n\nAwaiting reports: eng-a\n" + PI_FOOTER)
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [])

    def test_real_read_text_with_awaiting_line_sends_no_prompt(self):
        # The measured read output is plain text on stdout, so the marker is read from it directly.
        fake = FakeHerdr(status="idle", tail=PI_TAIL)
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [])

    def test_quoted_marker_is_not_the_leads_explicit_line(self):
        fake = FakeHerdr(status="idle", tail="Quoting the rule:\n> Awaiting: Human gate\n" + PI_FOOTER)
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])

    def test_marker_inside_an_open_code_fence_is_not_explicit(self):
        fake = FakeHerdr(status="idle", tail="```\nAwaiting: Human gate\n" + PI_FOOTER)
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])

    def test_marker_followed_by_a_closing_fence_is_not_explicit(self):
        fake = FakeHerdr(status="idle", tail="```\nAwaiting: Human gate\n```\n" + PI_FOOTER)
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])

    def test_indented_marker_is_not_explicit(self):
        fake = FakeHerdr(status="idle", tail="    Awaiting: Human gate\n" + PI_FOOTER)
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])

    def test_stale_marker_followed_by_new_output_is_not_current(self):
        # The marker is from an earlier turn: the Lead's newest output sits below it, above the footer.
        tail = "Awaiting: old gate\n\nRan the gate check; it failed with a provider timeout.\n" + PI_FOOTER
        fake = FakeHerdr(status="idle", tail=tail)
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])

    def test_marker_without_footer_rules_is_not_established(self):
        # No rule cluster means the layout is unrecognised, so the waker cannot tell the Lead's message from the rest of the pane.
        fake = FakeHerdr(status="idle", tail="Awaiting: Human gate\n○ 🐴 ponytail: ⚡ FULL\n")
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])

    def test_single_rule_footer_is_not_the_measured_layout(self):
        # The measured footer has two rules; one rule above a status line is an unknown layout and must wake.
        tail = "Awaiting: Human gate\n───────────────────────────────────────\nstatus line\n"
        fake = FakeHerdr(status="idle", tail=tail)
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])

    def test_measured_claude_shape_with_an_awaiting_line_above_fails_open(self):
        # Measured on a claude pane: text, blank, rule, prompt line, rule, status line. The prompt line is not a marker.
        tail = "Reviewed the change.\n\nAwaiting: Human gate\n\n───────────────────────────────────────\n>\n───────────────────────────────────────\nstatus line\n"
        fake = FakeHerdr(status="idle", tail=tail)
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])

    def test_measured_pi_layout_fits_the_read_window(self):
        # The read returns only TAIL_LINES lines, so the measured footer and marker must fit inside that window.
        window = "\n".join(PI_TAIL.rstrip("\n").split("\n")[-waker.TAIL_LINES:])
        self.assertTrue(waker.has_awaiting_marker(window))

    def test_empty_tail_is_not_established(self):
        fake = FakeHerdr(status="idle", tail="")
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])

    def test_lead_idle_without_marker_sends_one_fixed_prompt_without_tail_text(self):
        fake = FakeHerdr(status="idle", tail="provider error: 429 rate limit exceeded\n○ 🐴 ponytail: ⚡ FULL\n")
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])
        self.assertNotIn("429", json.dumps(fake.prompts()))

    def test_marker_inside_a_sentence_is_not_a_marker(self):
        fake = FakeHerdr(status="idle", tail="We will say Awaiting: later in the report\n○ 🐴 ponytail: ⚡ FULL\n")
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])

    def test_unreadable_lead_tail_fails_toward_one_prompt(self):
        fake = FakeHerdr(status="idle", read_error=True)
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 0)
        self.assertEqual(fake.prompts(), [self.lead_prompt("idle")])
        self.assertIn("tail unreadable: agent_not_found", self.stderr)

    def test_read_success_is_returned_as_plain_text_even_when_it_looks_like_json(self):
        text = '{"error": {"code": "agent_not_found"}}\n' + PI_FOOTER
        fake = FakeHerdr(tail=text)
        with mock.patch.object(waker.herdr_cli, "run", side_effect=fake.run):
            self.assertEqual(waker.read_tail(LEAD), text)

    def test_blocked_lead_prompt_refused_by_herdr_fails(self):
        fake = FakeHerdr(status="blocked", tail="Human dialog: approve push?\n", prompt_code=1)
        self.assertEqual(self.run_waker(fake, self.lead_argv()), 1)
        self.assertEqual(fake.prompts(), [self.lead_prompt("blocked")])

    def test_lead_wait_uses_one_bounded_wait_on_the_lead(self):
        fake = FakeHerdr(status="idle")
        self.run_waker(fake, self.lead_argv())
        self.assertEqual(fake.calls[0], ["agent", "wait", LEAD, "--until", "idle", "--until", "done", "--until", "blocked", "--timeout", str(TIMEOUT_MS)])

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

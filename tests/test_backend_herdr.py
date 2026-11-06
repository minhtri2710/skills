"""Herdr adapter: argv building and parsing against an injected runner and recorded fixtures.

Replaces test_herdr_cli.py. Fixtures under tests/fixtures/backends/herdr are hand-written shapes
(see SOURCES.txt there); nothing here runs herdr.
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "agent-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import backend  # noqa: E402
from backends import herdr  # noqa: E402

_NEVER_RUN = mock.patch.object(subprocess, "run", side_effect=AssertionError("tests never run herdr"))


def setUpModule() -> None:
    _NEVER_RUN.start()


def tearDownModule() -> None:
    _NEVER_RUN.stop()


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "backends" / "herdr"
ENVIRON = {"HERDR_ENV": "1", "HERDR_PANE_ID": "w1:p3"}
LEAD = "lead-demo"
REPORT = "/state/projects/demo/runs/r1/report-eng-a.md"


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def reply(stdout: str = "", returncode: int = 0, stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(["herdr"], returncode, stdout, stderr)


class Recorder:
    """The injected runner: records (args, timeout) and answers the queued replies in order."""

    def __init__(self, *replies: subprocess.CompletedProcess[str]) -> None:
        self.replies = list(replies)
        self.calls: list[tuple[list[str], float]] = []

    def __call__(self, args: list[str], *, timeout: float = 30.0) -> subprocess.CompletedProcess[str]:
        self.calls.append((list(args), timeout))
        return self.replies.pop(0)

    @property
    def argv(self) -> list[list[str]]:
        return [args for args, _ in self.calls]


def adapter(*replies: subprocess.CompletedProcess[str]) -> tuple[herdr.Adapter, Recorder]:
    runner = Recorder(*replies)
    return herdr.Adapter(ENVIRON, runner=runner), runner


class RunnerTest(unittest.TestCase):
    """The behavior test_herdr_cli.py pinned, now on the adapter's runner."""

    def test_run_uses_the_shared_subprocess_contract(self) -> None:
        completed = subprocess.CompletedProcess(["herdr", "agent", "list"], 0, stdout="{}", stderr="")
        with mock.patch.object(herdr.subprocess, "run", return_value=completed) as run:
            result = herdr.run(["agent", "list"], timeout=4.5)
        self.assertIs(result, completed)
        run.assert_called_once_with(
            ["herdr", "agent", "list"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=4.5,
        )

    def test_default_timeout_is_thirty_seconds(self) -> None:
        with mock.patch.object(herdr.subprocess, "run", return_value=reply("{}")) as run:
            herdr.run(["agent", "list"])
        self.assertEqual(run.call_args.kwargs["timeout"], 30.0)

    def test_oserror_becomes_named_unavailable_error(self) -> None:
        with mock.patch.object(herdr.subprocess, "run", side_effect=OSError("binary not found")):
            with self.assertRaisesRegex(backend.BackendUnavailable, r"herdr agent list.*binary not found"):
                herdr.run(["agent", "list"])

    def test_timeout_becomes_named_unavailable_error(self) -> None:
        timeout = subprocess.TimeoutExpired(["herdr", "agent", "prompt", "lead"], 30.0)
        with mock.patch.object(herdr.subprocess, "run", side_effect=timeout):
            with self.assertRaisesRegex(backend.BackendUnavailable, r"herdr agent prompt lead.*timed out"):
                herdr.run(["agent", "prompt", "lead"])

    def test_adapter_defaults_to_the_herdr_runner_and_propagates_unavailable(self) -> None:
        with mock.patch.object(herdr.subprocess, "run", side_effect=OSError("gone")):
            with self.assertRaises(backend.BackendUnavailable):
                herdr.Adapter(ENVIRON).list_seats()

    def test_adapter_is_the_registered_herdr_adapter(self) -> None:
        self.assertEqual(backend.ADAPTERS["herdr"], "backends.herdr")
        self.assertEqual(herdr.Adapter.name, "herdr")


class ListAndGetTest(unittest.TestCase):
    def test_list_seats_builds_agent_list_and_normalizes(self) -> None:
        a, runner = adapter(reply(fixture("agent-list.json")))
        seats = a.list_seats()
        self.assertEqual(runner.argv, [["agent", "list"]])
        self.assertEqual([seat.handle for seat in seats], ["w1:p1", "w1:p2", "w2:p1", "w1:p3"])
        lead, eng, agy, rev = seats
        self.assertEqual((lead.name, lead.kind, lead.state, lead.workspace, lead.cwd), ("lead", "claude", "working", "w1", "/work/checkout"))
        self.assertEqual(lead.session, backend.Session("id", "6f1b7c52-0a4e-4d52-9d1e-3b1f6a7c9e10"))
        self.assertEqual((eng.name, eng.kind, eng.state, eng.session), ("eng", None, "unknown", None))
        self.assertEqual((agy.name, agy.kind, agy.state), (None, "agy", "idle"))
        self.assertEqual(rev.session, backend.Session("path", "/home/u/.pi/agent/sessions/2026-11-06_ab12.jsonl"))
        self.assertEqual(rev.argv, ())

    def test_unrecognised_state_is_unknown(self) -> None:
        payload = {"result": {"agents": [{"pane_id": "w1:p1", "agent_status": "sleeping"}]}}
        a, _ = adapter(reply(json.dumps(payload)))
        self.assertEqual(a.list_seats()[0].state, "unknown")

    def test_list_refuses_malformed_output(self) -> None:
        rows = {
            "agent record lacks agent_status": fixture("agent-list-missing-status.json"),
            "non-object agent": fixture("agent-list-non-object.json"),
            "returned no result.agents": "{}",
            "not a list": '{"result": {"agents": {}}}',
            "returned no result.agents ": "not json",
        }
        for pattern, stdout in rows.items():
            with self.subTest(pattern):
                a, _ = adapter(reply(stdout))
                with self.assertRaisesRegex(backend.BackendError, pattern.strip()):
                    a.list_seats()

    def test_failed_list_is_a_backend_error_with_the_herdr_code(self) -> None:
        a, _ = adapter(reply(returncode=1, stderr=fixture("error-other.stderr.json")))
        with self.assertRaises(backend.BackendError) as caught:
            a.list_seats()
        self.assertEqual(caught.exception.code, "agent_prompt_stalled")
        self.assertNotIsInstance(caught.exception, backend.SeatError)

    def test_get_seat_uses_agent_get_by_name_or_handle(self) -> None:
        a, runner = adapter(reply(fixture("agent-get.json")), reply(fixture("agent-get.json")))
        by_name, by_handle = a.get_seat("supervisor"), a.get_seat("w1:p7")
        self.assertEqual(runner.argv, [["agent", "get", "supervisor"], ["agent", "get", "w1:p7"]])
        self.assertEqual(by_name, by_handle)
        self.assertEqual((by_name.handle, by_name.name, by_name.state), ("w1:p7", "supervisor", "idle"))

    def test_get_seat_accepts_a_minimal_agent_and_falls_back_to_the_ref(self) -> None:
        a, _ = adapter(reply(fixture("agent-get-minimal.json")))
        seat = a.get_seat("w1:p7")
        self.assertEqual((seat.handle, seat.name, seat.state), ("w1:p7", None, "unknown"))

    def test_get_seat_missing_agent_is_not_found(self) -> None:
        for stderr in (fixture("error-agent-not-found.stderr.json"), "agent_not_found\n"):
            with self.subTest(stderr):
                a, _ = adapter(reply(returncode=1, stderr=stderr))
                with self.assertRaises(backend.SeatError) as caught:
                    a.get_seat("gone")
                self.assertEqual((caught.exception.kind, caught.exception.code), ("not_found", "not_found"))

    def test_get_seat_without_a_result_agent_is_malformed_not_not_found(self) -> None:
        a, _ = adapter(reply('{"result": {}}'))
        with self.assertRaises(backend.BackendError) as caught:
            a.get_seat("w1:p7")
        self.assertNotIsInstance(caught.exception, backend.SeatError)

    def test_get_terminal_uses_pane_get(self) -> None:
        a, runner = adapter(reply(fixture("pane-get.json")))
        seat = a.get_terminal("w1:p3")
        self.assertEqual(runner.argv, [["pane", "get", "w1:p3"]])
        self.assertEqual((seat.handle, seat.cwd), ("w1:p3", "/work/checkout"))

    def test_get_terminal_missing_pane_is_not_found(self) -> None:
        a, _ = adapter(reply(returncode=1, stderr=fixture("error-pane-not-found.stderr.json")))
        with self.assertRaises(backend.SeatError) as caught:
            a.get_terminal("w1:p9")
        self.assertEqual(caught.exception.kind, "not_found")

    def test_agent_not_found_from_a_pane_call_is_not_a_missing_pane(self) -> None:
        for call in (lambda a: a.get_terminal("w1:p3"), lambda a: a.processes("w1:p3")):
            for stderr in (fixture("error-agent-not-found.stderr.json"), "agent_not_found\n"):
                with self.subTest(stderr):
                    a, _ = adapter(reply(returncode=1, stderr=stderr))
                    with self.assertRaises(backend.BackendError) as caught:
                        call(a)
                    self.assertNotIsInstance(caught.exception, backend.SeatError)
                    self.assertEqual(caught.exception.code, "agent_not_found")

    def test_get_terminal_without_a_pane_id_is_malformed(self) -> None:
        for stdout in ('{"result": {"pane": {}}}', '{"result": {"pane": {"pane_id": 3}}}', "{}"):
            with self.subTest(stdout):
                a, _ = adapter(reply(stdout))
                with self.assertRaises(backend.BackendError):
                    a.get_terminal("w1:p3")


class ErrorKindTest(unittest.TestCase):
    def test_blocked_prompt_is_a_blocked_seat_error(self) -> None:
        for stderr in (fixture("error-agent-blocked.stderr.json"), fixture("error-agent-blocked.stderr.txt")):
            with self.subTest(stderr):
                a, _ = adapter(reply(returncode=1, stderr=stderr))
                with self.assertRaises(backend.SeatError) as caught:
                    a.prompt(LEAD, "text")
                self.assertEqual(caught.exception.kind, "blocked")

    def test_error_code_may_arrive_on_stdout(self) -> None:
        a, _ = adapter(reply(stdout=fixture("error-agent-not-found.stderr.json"), returncode=1))
        with self.assertRaises(backend.SeatError) as caught:
            a.read_output("gone", 5)
        self.assertEqual(caught.exception.kind, "not_found")

    def test_unknown_failure_keeps_code_unknown(self) -> None:
        a, _ = adapter(reply(returncode=2, stderr="boom"))
        with self.assertRaises(backend.BackendError) as caught:
            a.prompt(LEAD, "text")
        self.assertEqual(caught.exception.code, "unknown")

    def test_not_started_is_a_defined_kind_the_herdr_adapter_does_not_emit(self) -> None:
        self.assertIn("not_started", backend.SEAT_ERROR_KINDS)
        self.assertEqual(backend.SeatError("not_started", "x").code, "not_started")
        with self.assertRaises(ValueError):
            backend.SeatError("stuck", "x")


class ReadPromptWaitTest(unittest.TestCase):
    def test_read_output_argv_and_text(self) -> None:
        a, runner = adapter(reply(fixture("agent-read.txt")))
        self.assertEqual(a.read_output("eng-a", 120), fixture("agent-read.txt"))
        self.assertEqual(runner.argv, [["agent", "read", "eng-a", "--source", "recent-unwrapped", "--lines", "120"]])

    def test_prompt_argv_has_no_other_flags(self) -> None:
        a, runner = adapter(reply())
        self.assertIsNone(a.prompt(LEAD, 'text with "quotes" and $HOME'))
        self.assertEqual(runner.argv, [["agent", "prompt", LEAD, 'text with "quotes" and $HOME']])

    def test_wait_state_argv_and_runner_timeout(self) -> None:
        a, runner = adapter(reply(fixture("agent-wait.json")))
        self.assertEqual(a.wait_state("eng-a", ["idle", "done", "blocked"], 30000), "idle")
        self.assertEqual(
            runner.calls,
            [(["agent", "wait", "eng-a", "--until", "idle", "--until", "done", "--until", "blocked", "--timeout", "30000"], 40.0)],
        )

    def test_wait_state_failures(self) -> None:
        a, _ = adapter(reply(returncode=1, stderr=fixture("error-agent-not-found.stderr.json")))
        with self.assertRaises(backend.SeatError):
            a.wait_state("eng-a", ["idle"], 1000)
        a, _ = adapter(reply(fixture("agent-wait-no-status.json")))
        with self.assertRaisesRegex(backend.BackendError, "no agent_status"):
            a.wait_state("eng-a", ["idle"], 1000)

    def test_wait_state_refuses_states_outside_the_seat_model(self) -> None:
        a, runner = adapter()
        for states in ([], ["sleeping"], ["idle", "asleep"]):
            with self.subTest(states), self.assertRaises(ValueError):
                a.wait_state("eng-a", states, 1000)
        self.assertEqual(runner.calls, [])

    def test_processes_argv_and_passthrough(self) -> None:
        a, runner = adapter(reply(fixture("process-info.json")))
        processes = a.processes("w1:p3")
        self.assertEqual(runner.argv, [["pane", "process-info", "--pane", "w1:p3"]])
        self.assertEqual(processes[1]["argv0"], "claude")
        self.assertEqual(processes[2], {"command": "npm run dev", "alive": True})
        self.assertEqual(len(processes), 3)

    def test_processes_without_foreground_list_is_malformed(self) -> None:
        a, _ = adapter(reply(fixture("process-info-no-foreground.json")))
        with self.assertRaisesRegex(backend.BackendError, "lacks foreground_processes"):
            a.processes("w1:p3")

    def test_processes_missing_pane_is_not_found(self) -> None:
        a, _ = adapter(reply(returncode=1, stderr=fixture("error-pane-not-found.stderr.json")))
        with self.assertRaises(backend.SeatError):
            a.processes("w1:p9")


class IdentifyTest(unittest.TestCase):
    def test_identify_confirms_the_own_pane_with_pane_get(self) -> None:
        a, runner = adapter(reply(fixture("pane-get.json")))
        self.assertEqual(a.identify(), "w1:p3")
        self.assertEqual(runner.argv, [["pane", "get", "w1:p3"]])

    def test_identify_fails_closed(self) -> None:
        rows = {
            "non-zero": reply(returncode=1, stderr=fixture("error-pane-not-found.stderr.json")),
            "other pane": reply('{"result": {"pane": {"pane_id": "w9:p9"}}}'),
            "no json": reply("hello"),
        }
        for label, answer in rows.items():
            with self.subTest(label):
                a, _ = adapter(answer)
                with self.assertRaises(backend.BackendUnavailable):
                    a.identify()

    def test_identify_without_a_pane_in_the_environment_runs_nothing(self) -> None:
        runner = Recorder()
        with self.assertRaises(backend.BackendUnavailable):
            herdr.Adapter({}, runner=runner).identify()
        self.assertEqual(runner.calls, [])

    def test_identify_propagates_a_missing_binary(self) -> None:
        with mock.patch.object(herdr.subprocess, "run", side_effect=OSError("no herdr")):
            with self.assertRaisesRegex(backend.BackendUnavailable, "no herdr"):
                herdr.Adapter(ENVIRON).identify()

    def test_open_backend_runs_identify_once_and_keeps_the_handle(self) -> None:
        runner = Recorder(reply(fixture("pane-get.json")))
        with mock.patch.object(herdr, "run", runner):
            opened = backend.open_backend(ENVIRON)
        self.assertEqual((opened.name, opened.handle), ("herdr", "w1:p3"))
        self.assertEqual(runner.argv, [["pane", "get", "w1:p3"]])


class SendBlockTest(unittest.TestCase):
    def test_block_is_the_report_by_prompt_send_and_failure_notice(self) -> None:
        a, runner = adapter()
        self.assertEqual(
            a.send_block(LEAD, REPORT),
            'herdr agent prompt lead-demo "$(cat /state/projects/demo/runs/r1/send-eng-a.txt)"\n'
            'herdr notification show "eng-a: report send failed" --body "/state/projects/demo/runs/r1/report-eng-a.md" --sound request',
        )
        self.assertEqual(runner.calls, [])

    def test_block_refuses_unsafe_or_misshapen_inputs(self) -> None:
        a, _ = adapter()
        for lead, report in (
            ("lead demo", REPORT),
            ("lead;rm", REPORT),
            ("", REPORT),
            (LEAD, "report-eng-a.md"),
            (LEAD, "/state/runs/r1/eng-a.md"),
            (LEAD, "/state/runs/r1/report-.md"),
            (LEAD, '/state/runs/"r1"/report-eng-a.md'),
            (LEAD, "/state/runs/$HOME/report-eng-a.md"),
            (LEAD, "/state/runs/`x`/report-eng-a.md"),
            (LEAD, "/state/runs/r1/report-eng-a.md\nrm"),
        ):
            with self.subTest(lead=lead, report=report), self.assertRaises(ValueError):
                a.send_block(lead, report)

    def test_a_handle_the_other_backends_use_is_accepted(self) -> None:
        a, _ = adapter()
        for handle in ("w1:p1", "t7", "session:s1.block:b1"):
            self.assertIn(f"herdr agent prompt {handle} ", a.send_block(handle, REPORT))


if __name__ == "__main__":
    unittest.main()

"""Herdr adapter: argv building and parsing against an injected runner and recorded fixtures.

Fixtures under tests/fixtures/backends/herdr are hand-written shapes
(see SOURCES.txt there); nothing here runs herdr.
"""
from __future__ import annotations

import json
import subprocess
import unittest
from functools import partial
from unittest import mock

import support
import backend
from backends import herdr
from support import Recorder


def setUpModule() -> None:
    support.never_run()


ENVIRON = {"HERDR_ENV": "1", "HERDR_PANE_ID": "w1:p3"}
LEAD = "lead-demo"
REPORT = "/state/projects/demo/runs/r1/report-eng-a.md"


fixture = partial(support.fixture, "herdr")
reply = partial(support.reply, "herdr")


def adapter(*replies: subprocess.CompletedProcess[str]) -> tuple[herdr.Adapter, Recorder]:
    return support.adapter(herdr, ENVIRON, *replies)


class RunnerTest(unittest.TestCase):
    """backend.run_tool, the one tool runner the three adapters bind their binary to."""

    def test_run_tool_passes_the_shared_subprocess_contract(self) -> None:
        completed = subprocess.CompletedProcess(["herdr", "agent", "list"], 0, stdout="{}", stderr="")
        env = {"X": "1"}
        with mock.patch.object(backend.subprocess, "run", return_value=completed) as run:
            result = backend.run_tool("herdr", ["agent", "list"], timeout=4.5, env=env)
        self.assertIs(result, completed)
        run.assert_called_once_with(
            ["herdr", "agent", "list"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=4.5,
            env=env,
        )

    def test_a_timeout_or_oserror_is_unavailable_and_names_the_command_not_the_argv(self) -> None:
        secret = "text-that-must-not-leak"
        failures = {
            "timed out": subprocess.TimeoutExpired(["herdr"], 30.0),
            "binary not found": OSError("binary not found"),
        }
        for message, failure in failures.items():
            for binary, args, label in (
                ("herdr", ["agent", "prompt", "lead", secret], "herdr agent prompt"),
                ("/home/u/.local/bin/herdr-core", ["send", "--json", "t7", secret], "herdr-core send t7"),
                ("rex", ["--autostart=false", "whoami", "--json"], "rex whoami"),
            ):
                with self.subTest(message, label=label), mock.patch.object(backend.subprocess, "run", side_effect=failure):
                    with self.assertRaises(backend.BackendUnavailable) as caught:
                        backend.run_tool(binary, args, timeout=30.0)
                    self.assertTrue(str(caught.exception).startswith(label), str(caught.exception))
                    self.assertIn(message, str(caught.exception))
                    self.assertNotIn(secret, str(caught.exception))

    def test_adapter_defaults_to_the_herdr_runner_and_propagates_unavailable(self) -> None:
        with mock.patch.object(backend.subprocess, "run", side_effect=OSError("gone")):
            with self.assertRaises(backend.BackendUnavailable):
                herdr.Adapter(ENVIRON).list_seats()


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

    def test_wait_state_drops_error_which_herdr_never_reports(self) -> None:
        a, runner = adapter(reply(fixture("agent-wait.json")))
        self.assertEqual(a.wait_state("eng-a", ["idle", "done", "blocked", "error"], 30000), "idle")
        self.assertEqual(runner.argv[0].count("--until"), 3)
        self.assertNotIn("error", runner.argv[0])

    def test_wait_state_failures(self) -> None:
        a, _ = adapter(reply(returncode=1, stderr=fixture("error-agent-not-found.stderr.json")))
        with self.assertRaises(backend.SeatError):
            a.wait_state("eng-a", ["idle"], 1000)
        a, _ = adapter(reply(fixture("agent-wait-no-status.json")))
        with self.assertRaisesRegex(backend.BackendError, "no agent_status"):
            a.wait_state("eng-a", ["idle"], 1000)

    def test_a_reply_state_outside_the_requested_ones_is_an_error(self) -> None:
        a, runner = adapter(reply(fixture("agent-wait.json")))
        with self.assertRaises(backend.BackendError) as caught:
            a.wait_state("eng-a", ["done", "blocked"], 1000)
        self.assertEqual(caught.exception.code, "state_not_requested")
        self.assertEqual(len(runner.calls), 1)

    def test_wait_state_refuses_states_outside_the_seat_model(self) -> None:
        a, runner = adapter()
        for states in ([], ["sleeping"], ["idle", "asleep"], ["error"]):
            with self.subTest(states), self.assertRaises(ValueError):
                a.wait_state("eng-a", states, 1000)
        self.assertEqual(runner.calls, [])

    def test_processes_argv_and_normalized_records(self) -> None:
        a, runner = adapter(reply(fixture("process-info.json")))
        self.assertEqual(
            a.processes("w1:p3"),
            [
                backend.Process(("caffeinate", "-i")),
                backend.Process(("/usr/local/bin/claude", "--model", "opus"), 4242, "/work/checkout"),
                backend.Process(("npm", "run", "dev"), 4343, "/work/checkout/app"),
                backend.Process(("pi",), 4545),
                backend.Process(("node",), 4444, argv_reported=False),
                backend.Process(("zsh",), argv_reported=False),
            ],
        )
        self.assertEqual(runner.argv, [["pane", "process-info", "--pane", "w1:p3"]])

    def test_processes_with_a_non_object_entry_is_malformed(self) -> None:
        a, _ = adapter(reply('{"result": {"process_info": {"foreground_processes": ["npm"]}}}'))
        with self.assertRaisesRegex(backend.BackendError, "non-object process"):
            a.processes("w1:p3")

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
                with self.assertRaises(backend.BackendError):
                    a.identify()

    def test_identify_without_a_pane_in_the_environment_runs_nothing(self) -> None:
        runner = Recorder()
        with self.assertRaises(backend.BackendUnavailable):
            herdr.Adapter({}, runner=runner).identify()
        self.assertEqual(runner.calls, [])

    def test_identify_propagates_a_missing_binary(self) -> None:
        with mock.patch.object(backend.subprocess, "run", side_effect=OSError("no herdr")):
            with self.assertRaisesRegex(backend.BackendUnavailable, "no herdr"):
                herdr.Adapter(ENVIRON).identify()

    def test_open_backend_runs_identify_once_and_keeps_the_handle(self) -> None:
        with mock.patch.object(backend.subprocess, "run", return_value=reply(fixture("pane-get.json"))) as run:
            opened = backend.open_backend(ENVIRON)
        self.assertEqual((opened.name, opened.handle), ("herdr", "w1:p3"))
        run.assert_called_once()
        self.assertEqual(run.call_args.args[0], ["herdr", "pane", "get", "w1:p3"])


class SendBlockTest(unittest.TestCase):
    def test_block_is_the_report_by_prompt_send_and_failure_notice(self) -> None:
        a, runner = adapter()
        self.assertEqual(
            a.send_block(LEAD, REPORT),
            backend.SendBlock(
                'herdr agent prompt lead-demo "$(cat "/state/projects/demo/runs/r1/send-eng-a.txt")"',
                'herdr notification show "eng-a: report send failed" --body "/state/projects/demo/runs/r1/report-eng-a.md" --sound request',
            ),
        )
        self.assertEqual(runner.calls, [])

    def test_block_refuses_unsafe_or_misshapen_inputs(self) -> None:
        a, _ = adapter()
        for lead, report in (
            ("lead demo", REPORT),
            ("lead;rm", REPORT),
            ("", REPORT),
            (LEAD, "report-eng-a.md"),
        ):
            with self.subTest(lead=lead, report=report), self.assertRaises(ValueError):
                a.send_block(lead, report)


if __name__ == "__main__":
    unittest.main()

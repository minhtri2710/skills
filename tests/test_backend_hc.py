"""hc adapter: argv building and parsing against an injected runner and schema-derived fixtures.

Fixtures under tests/fixtures/backends/hc are hand-written from herdr-core source (see SOURCES.txt
there); nothing here runs hc, herdr-core, or herdr. subprocess.run raises for the whole module, so a
default-bound runner that reached a real binary fails the test instead of running it.
"""
from __future__ import annotations

import json
import os
import re
import stat
import subprocess
import tempfile
import unittest
from functools import partial
from pathlib import Path
from unittest import mock

import support
import backend
from backends import hc
from support import Recorder


def setUpModule() -> None:
    support.never_run()


REFERENCE = support.ADW / "references" / "backend-hc.md"
SOCKET = "/run/user/501/herdr-core/default.sock"
ENVIRON = {"HC_TERMINAL_ID": "t7", "HC_TERMINAL_SOCKET": SOCKET, "PATH": "/usr/bin", "HOME": "/home/u"}
LEAD = "t3"
REPORT = "/state/projects/demo/runs/r1/report-eng-a.md"


fixture = partial(support.fixture, "hc")
reply = partial(support.reply, "hc")


def adapter(*replies: subprocess.CompletedProcess[str]) -> tuple[hc.Adapter, Recorder]:
    return support.adapter(hc, ENVIRON, *replies, binary="hc")


# The whole command surface the adapter may use: verb -> flags it may pass (design 9.3 allow-list).
ALLOWED = {
    "get": {"--json"},
    "ls": {"--json"},
    "read": {"--lines"},
    "send": {"--json"},
    "wait": {"--json", "--timeout"},
    "run": {"--bg", "--json", "--no-parent", "--name", "--cwd"},
    "interrupt": {"--json"},
    "kill": {"--json"},
    "rm": {"--json"},
}


def violation(args: list[str]) -> str | None:
    """Why argv is outside ALLOWED, or None. Everything after a lone `--` is the program's own argv."""
    if not args or args[0] not in ALLOWED:
        return f"unknown hc command: {args[:1]}"
    own = args[1 : args.index("--")] if "--" in args else args[1:]
    flags = {word for word in own if word.startswith("-")}
    if args[0] == "run" and ("--no-parent" not in flags or "--bg" not in flags):
        return "run must pass --bg and --no-parent"
    stray = flags - ALLOWED[args[0]]
    return f"flags outside the allow-list: {sorted(stray)}" if stray else None


class RunnerTest(unittest.TestCase):
    def test_run_uses_the_shared_subprocess_contract(self) -> None:
        completed = subprocess.CompletedProcess(["hc", "ls"], 0, stdout="{}", stderr="")
        env = {"HC_SOCKET": SOCKET}
        with mock.patch.object(hc.subprocess, "run", return_value=completed) as run:
            result = hc.run("/bin/hc-x", ["ls", "--json"], timeout=4.5, env=env)
        self.assertIs(result, completed)
        run.assert_called_once_with(
            ["/bin/hc-x", "ls", "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=4.5,
            env=env,
        )

    def test_default_timeout_is_thirty_seconds(self) -> None:
        with mock.patch.object(hc.subprocess, "run", return_value=reply("{}")) as run:
            hc.run("hc", ["ls"])
        self.assertEqual(run.call_args.kwargs["timeout"], 30.0)

    def test_oserror_and_timeout_become_unavailable_and_name_only_the_command(self) -> None:
        secret = "text-that-must-not-leak"
        with mock.patch.object(hc.subprocess, "run", side_effect=OSError("binary not found")):
            with self.assertRaisesRegex(backend.BackendUnavailable, r"hc send unavailable: binary not found") as caught:
                hc.run("hc", ["send", "t7", secret])
        self.assertNotIn(secret, str(caught.exception))
        timeout = subprocess.TimeoutExpired(["hc", "wait"], 30.0)
        with mock.patch.object(hc.subprocess, "run", side_effect=timeout):
            with self.assertRaisesRegex(backend.BackendUnavailable, r"hc wait timed out"):
                hc.run("hc", ["wait", "t7"])

    def test_binary_is_herdr_core_when_executable_else_hc_on_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            self.assertEqual(hc.resolve_binary(home), "hc")
            binary = home / ".local" / "bin" / "herdr-core"
            binary.parent.mkdir(parents=True)
            binary.write_text("", encoding="utf-8")
            binary.chmod(stat.S_IRUSR | stat.S_IWUSR)
            self.assertEqual(hc.resolve_binary(home), "hc")  # present but not executable
            binary.chmod(stat.S_IRWXU)
            self.assertEqual(hc.resolve_binary(home), str(binary))
            (home / ".local" / "bin" / "herdr-core").unlink()
            (home / ".local" / "bin" / "herdr-core").mkdir()
            self.assertEqual(hc.resolve_binary(home), "hc")  # a directory is not a binary

    def test_default_runner_binds_the_resolved_binary_at_construction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / ".local" / "bin" / "herdr-core"
            binary.parent.mkdir(parents=True)
            binary.write_text("", encoding="utf-8")
            binary.chmod(stat.S_IRWXU)
            with mock.patch.object(hc.Path, "home", return_value=Path(tmp)):
                bound = hc.Adapter(ENVIRON)
            with mock.patch.object(hc.subprocess, "run", return_value=reply(fixture("ls.json"))) as run:
                bound.list_seats()
        self.assertEqual(run.call_args.args[0], [str(binary), "ls", "--json"])

    def test_default_runner_propagates_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(hc.Path, "home", return_value=Path(tmp)):
            bound = hc.Adapter(ENVIRON)
        with mock.patch.object(hc.subprocess, "run", side_effect=OSError("gone")):
            with self.assertRaises(backend.BackendUnavailable):
                bound.list_seats()

    def test_adapter_is_the_registered_hc_adapter(self) -> None:
        self.assertEqual(backend.ADAPTERS["hc"], "backends.hc")
        self.assertEqual(hc.Adapter.name, "hc")


class CorePinTest(unittest.TestCase):
    def test_every_call_runs_with_hc_socket_set_to_the_terminal_socket(self) -> None:
        stale = {**ENVIRON, "HC_SOCKET": "/elsewhere/other.sock"}
        runner = Recorder(*[reply(fixture("get-live.json")) for _ in range(3)])
        a = hc.Adapter(stale, runner=runner, binary="hc")
        a.get_seat("t7")
        a.processes("t7")
        a.identify()
        for env in runner.envs:
            self.assertEqual(env["HC_SOCKET"], SOCKET)
            self.assertEqual({k: v for k, v in env.items() if k != "HC_SOCKET"}, {k: v for k, v in stale.items() if k != "HC_SOCKET"})
        self.assertEqual(stale["HC_SOCKET"], "/elsewhere/other.sock")  # the caller's mapping is not mutated

    def test_without_a_socket_nothing_runs(self) -> None:
        runner = Recorder()
        a = hc.Adapter({"HC_TERMINAL_ID": "t7"}, runner=runner, binary="hc")
        for call in (a.identify, a.list_seats, lambda: a.get_seat("t7")):
            with self.assertRaises(backend.BackendUnavailable):
                call()
        self.assertEqual(runner.calls, [])

    def test_errors_never_carry_the_environment(self) -> None:
        a, _ = adapter(reply(returncode=1, stderr=fixture("error-not-found.stderr.json")))
        with self.assertRaises(backend.SeatError) as caught:
            a.get_seat("t99")
        for value in (SOCKET, "/usr/bin", "/home/u"):
            self.assertNotIn(value, str(caught.exception))


class NormalizeTest(unittest.TestCase):
    def test_get_seat_normalizes_a_reporting_agent(self) -> None:
        a, runner = adapter(reply(fixture("get-live.json")))
        seat = a.get_seat("eng-a")
        self.assertEqual(runner.argv, [["get", "eng-a", "--json"]])
        self.assertEqual(
            seat,
            backend.Seat(
                handle="t7",
                name="eng-a",
                state="working",
                kind="claude",
                cwd="/work/checkout",
                argv=("/usr/local/bin/claude", "--model", "opus"),
                session=None,
                workspace=None,
            ),
        )

    def test_a_program_that_reports_no_status_is_unknown(self) -> None:
        a, _ = adapter(reply(fixture("get-live-no-status.json")))
        seat = a.get_seat("t3")
        self.assertEqual((seat.handle, seat.name, seat.state, seat.kind, seat.argv), ("t3", None, "unknown", "zsh", ("zsh",)))

    def test_a_finished_terminal_is_done_on_exit_zero_and_error_otherwise(self) -> None:
        for name, state in (("get-finished-ok.json", "done"), ("get-finished-failed.json", "error"), ("kill.json", "error")):
            with self.subTest(name):
                a, _ = adapter(reply(fixture(name)))
                self.assertEqual(a.get_seat("t9").state, state)

    def test_an_unrecognised_status_word_is_unknown(self) -> None:
        record = {"address": "t1", "state": "live", "status": {"state": "sleeping"}}
        a, _ = adapter(reply(json.dumps(record)))
        self.assertEqual(a.get_seat("t1").state, "unknown")

    def test_get_terminal_is_the_same_record(self) -> None:
        a, runner = adapter(reply(fixture("get-live.json")), reply(fixture("get-live.json")))
        self.assertEqual(a.get_terminal("t7"), a.get_seat("t7"))
        self.assertEqual(runner.argv, [["get", "t7", "--json"], ["get", "t7", "--json"]])

    def test_every_record_has_the_normalized_fields(self) -> None:
        for name in ("get-live.json", "get-live-no-status.json", "get-finished-ok.json", "get-finished-failed.json"):
            with self.subTest(name):
                a, _ = adapter(reply(fixture(name)))
                seat = a.get_seat("t1")
                self.assertIsInstance(seat, backend.Seat)
                self.assertIsInstance(seat.handle, str)
                self.assertTrue(seat.handle)
                self.assertIn(seat.state, backend.STATES)
                self.assertIsInstance(seat.argv, tuple)

    def test_list_seats_uses_ls_and_reads_the_short_rows(self) -> None:
        a, runner = adapter(reply(fixture("ls.json")))
        seats = a.list_seats()
        self.assertEqual(runner.argv, [["ls", "--json"]])
        self.assertEqual([seat.handle for seat in seats], ["t7", "t3", "t9", "t11"])
        self.assertEqual([seat.state for seat in seats], ["working", "unknown", "done", "blocked"])
        self.assertEqual([seat.kind for seat in seats], ["claude", "zsh", "pi", "claude"])
        self.assertEqual([seat.name for seat in seats], ["eng-a", None, "eng-b", "rev"])
        self.assertTrue(all(seat.argv == () and seat.session is None and seat.workspace is None for seat in seats))

    def test_list_refuses_malformed_output(self) -> None:
        rows = {
            "non-object terminal": fixture("ls-non-object.json"),
            "terminals is not a list": '{"terminals": {}}',
            "terminal record lacks address": '{"terminals": [{"state": "live"}]}',
            "terminal record lacks state": '{"terminals": [{"address": "t1"}]}',
            "returned no JSON object": "not json",
        }
        for pattern, stdout in rows.items():
            with self.subTest(pattern):
                a, _ = adapter(reply(stdout))
                with self.assertRaisesRegex(backend.BackendError, pattern):
                    a.list_seats()

    def test_a_ref_that_is_not_an_address_or_name_runs_nothing(self) -> None:
        for ref in ("", "-x", "--json", "t7 t8", "t7;rm", "a/b"):
            with self.subTest(ref):
                a, runner = adapter()
                for call in (a.get_seat, a.get_terminal, a.processes, lambda r: a.read_output(r, 5), lambda r: a.prompt(r, "x")):
                    with self.assertRaises(ValueError):
                        call(ref)
                with self.assertRaises(ValueError):
                    a.wait_state(ref, ["idle"], 1000)
                self.assertEqual(runner.calls, [])


class ErrorKindTest(unittest.TestCase):
    def test_not_found_by_json_by_text_and_by_exit_code(self) -> None:
        rows = {
            "json": reply(returncode=3, stderr=fixture("error-not-found.stderr.json")),
            "json on stdout": reply(stdout=fixture("error-not-found.stderr.json"), returncode=1),
            "text with exit 3": reply(returncode=3, stderr=fixture("error-not-found.stderr.txt")),
        }
        for label, answer in rows.items():
            with self.subTest(label):
                a, _ = adapter(answer)
                with self.assertRaises(backend.SeatError) as caught:
                    a.get_seat("t99")
                self.assertEqual((caught.exception.kind, caught.exception.code), ("not_found", "not_found"))

    def test_every_per_seat_call_maps_not_found(self) -> None:
        calls = {
            "read": lambda a: a.read_output("t99", 5),
            "prompt": lambda a: a.prompt("t99", "x"),
            "wait": lambda a: a.wait_state("t99", ["idle"], 1000),
            "processes": lambda a: a.processes("t99"),
        }
        for label, call in calls.items():
            with self.subTest(label):
                a, _ = adapter(reply(returncode=3, stderr=fixture("error-not-found.stderr.json")))
                with self.assertRaises(backend.SeatError) as caught:
                    call(a)
                self.assertEqual(caught.exception.kind, "not_found")

    def test_other_kinds_stay_backend_errors_with_the_hc_kind_as_code(self) -> None:
        rows = {
            "live": reply(returncode=1, stderr=fixture("error-live.stderr.json")),
            "finished": reply(returncode=11, stderr="error: t9 has finished\n"),
            "status_mismatch": reply(returncode=10, stderr="boom"),
            "unknown": reply(returncode=2, stderr="boom"),
        }
        for code, answer in rows.items():
            with self.subTest(code):
                a, _ = adapter(answer)
                with self.assertRaises(backend.BackendError) as caught:
                    a.read_output("t9", 5)
                self.assertNotIsInstance(caught.exception, backend.SeatError)
                self.assertEqual(caught.exception.code, code)

    def test_error_messages_name_the_command_and_not_the_text(self) -> None:
        text = "confidential task text"
        a, _ = adapter(reply(returncode=9, stderr=fixture("error-blocked.stderr.json")))
        with self.assertRaises(backend.SeatError) as caught:
            a.prompt("t7", text)
        self.assertEqual(str(caught.exception), "hc send failed: blocked")
        self.assertNotIn(text, str(caught.exception))


class ReadPromptTest(unittest.TestCase):
    def test_read_output_argv_and_text(self) -> None:
        a, runner = adapter(reply(fixture("read.txt")))
        self.assertEqual(a.read_output("eng-a", 120), fixture("read.txt"))
        self.assertEqual(runner.argv, [["read", "--lines", "120", "eng-a"]])

    def test_read_output_refuses_negative_lines(self) -> None:
        a, runner = adapter()
        with self.assertRaises(ValueError):
            a.read_output("t7", -1)
        self.assertEqual(runner.calls, [])

    def test_prompt_argv_passes_the_text_verbatim_with_no_force_wait_or_if(self) -> None:
        a, runner = adapter(reply(fixture("send-started.json")))
        self.assertIsNone(a.prompt(LEAD, 'text with "quotes" and $HOME\nsecond line'))
        self.assertEqual(runner.argv, [["send", "--json", LEAD, 'text with "quotes" and $HOME\nsecond line']])

    def test_prompt_to_a_seat_that_reports_no_status_is_accepted(self) -> None:
        a, _ = adapter(reply(fixture("send-unreported.json")))
        self.assertIsNone(a.prompt("t3", "go"))

    def test_prompt_that_did_not_start_a_turn_is_not_started(self) -> None:
        a, _ = adapter(reply(fixture("send-not-started.json")))
        with self.assertRaises(backend.SeatError) as caught:
            a.prompt("t7", "go")
        self.assertEqual((caught.exception.kind, caught.exception.code), ("not_started", "not_started"))

    def test_blocked_seat_is_refused_with_the_blocked_kind(self) -> None:
        for answer in (
            reply(returncode=9, stderr=fixture("error-blocked.stderr.json")),
            reply(returncode=9, stderr="error: t7 is blocked (permission)\n"),
        ):
            with self.subTest(answer.stderr):
                a, _ = adapter(answer)
                with self.assertRaises(backend.SeatError) as caught:
                    a.prompt("t7", "go")
                self.assertEqual(caught.exception.kind, "blocked")

    def test_a_text_that_would_read_as_an_option_runs_nothing(self) -> None:
        a, runner = adapter()
        for text in ("-f", "--force", "- item"):
            with self.subTest(text), self.assertRaises(ValueError):
                a.prompt("t7", text)
        self.assertEqual(runner.calls, [])


class WaitTest(unittest.TestCase):
    def test_wait_state_argv_and_runner_timeout(self) -> None:
        a, runner = adapter(reply(fixture("wait-idle.json")))
        self.assertEqual(a.wait_state("eng-a", ["idle", "done", "blocked"], 30000), "idle")
        self.assertEqual(runner.calls[0][:2], (["wait", "--json", "--timeout", "30", "eng-a"], 40.0))

    def test_timeout_rounds_up_to_whole_seconds_and_is_never_zero(self) -> None:
        for ms, seconds in ((1500, "2"), (1, "1"), (0, "1"), (180000, "180")):
            with self.subTest(ms):
                a, runner = adapter(reply(fixture("wait-idle.json")))
                a.wait_state("t7", ["idle"], ms)
                self.assertEqual(runner.argv[0][3], seconds)

    def test_exit_is_done_on_zero_and_error_otherwise(self) -> None:
        a, _ = adapter(reply(fixture("wait-exit-ok.json")))
        self.assertEqual(a.wait_state("t9", ["done"], 1000), "done")
        a, _ = adapter(reply(fixture("wait-exit-failed.json")))
        self.assertEqual(a.wait_state("t9", ["done", "error"], 1000), "error")
        a, _ = adapter(reply(fixture("wait-error.json")))
        self.assertEqual(a.wait_state("t7", ["idle", "done", "blocked", "error"], 1000), "error")

    def test_a_state_outside_the_requested_ones_is_an_error_not_a_spin(self) -> None:
        for name in ("wait-error.json", "wait-exit-failed.json"):
            with self.subTest(name):
                a, runner = adapter(reply(fixture(name)))
                with self.assertRaises(backend.BackendError) as caught:
                    a.wait_state("t7", ["idle", "done", "blocked"], 1000)
                self.assertEqual(caught.exception.code, "state_not_requested")
                self.assertEqual(len(runner.calls), 1)

    def test_a_check_in_is_not_a_state(self) -> None:
        a, runner = adapter(reply(fixture("wait-timeout.json")))
        with self.assertRaises(backend.BackendError) as caught:
            a.wait_state("t7", ["idle"], 1000)
        self.assertEqual(caught.exception.code, "timeout")
        self.assertEqual(len(runner.calls), 1)

    def test_a_message_ends_the_wait_and_the_same_wait_is_reissued_for_the_time_left(self) -> None:
        a, runner = adapter(reply(fixture("wait-message.json")), reply(fixture("wait-idle.json")))
        with mock.patch.object(hc.time, "monotonic", side_effect=[0.0, 0.0, 12.0, 12.0]):
            self.assertEqual(a.wait_state("t7", ["idle"], 30000), "idle")
        self.assertEqual(
            runner.calls[0][:2] + runner.calls[1][:2],
            (["wait", "--json", "--timeout", "30", "t7"], 40.0, ["wait", "--json", "--timeout", "18", "t7"], 28.0),
        )

    def test_messages_until_the_deadline_end_in_a_timeout(self) -> None:
        a, runner = adapter(reply(fixture("wait-message.json")), reply(fixture("wait-message.json")))
        with mock.patch.object(hc.time, "monotonic", side_effect=[0.0, 0.0, 10.0, 10.0, 31.0]):
            with self.assertRaises(backend.BackendError) as caught:
                a.wait_state("t7", ["idle"], 30000)
        self.assertEqual(caught.exception.code, "timeout")
        self.assertEqual([args[3] for args in runner.argv], ["30", "20"])

    def test_wait_state_refuses_states_outside_the_seat_model(self) -> None:
        a, runner = adapter()
        for states in ([], ["sleeping"], ["idle", "asleep"]):
            with self.subTest(states), self.assertRaises(ValueError):
                a.wait_state("t7", states, 1000)
        self.assertEqual(runner.calls, [])


class ProcessesTest(unittest.TestCase):
    def test_processes_reports_the_foreground_leader(self) -> None:
        a, runner = adapter(reply(fixture("get-live.json")), reply(fixture("get-live-no-status.json")))
        self.assertEqual(
            a.processes("t7"),
            [{"pid": 4242, "name": "claude", "argv": ["/usr/local/bin/claude", "--model", "opus"], "cwd": "/work/checkout", "argv0": "/usr/local/bin/claude"}],
        )
        self.assertEqual(a.processes("t3")[0]["argv"], ["npm", "run", "dev"])
        self.assertEqual(runner.argv, [["get", "t7", "--json"], ["get", "t3", "--json"]])

    def test_a_finished_terminal_has_no_process(self) -> None:
        a, _ = adapter(reply(fixture("get-finished-ok.json")))
        self.assertEqual(a.processes("t9"), [])

    def test_a_malformed_foreground_is_refused(self) -> None:
        for foreground in ('"npm"', '{"argv": "npm"}', '{"argv": [1]}'):
            with self.subTest(foreground):
                a, _ = adapter(reply('{"address": "t1", "state": "live", "foreground": %s}' % foreground))
                with self.assertRaisesRegex(backend.BackendError, "malformed foreground"):
                    a.processes("t1")


class IdentifyTest(unittest.TestCase):
    def test_identify_confirms_the_own_terminal_with_an_explicit_target(self) -> None:
        a, runner = adapter(reply(fixture("get-live.json")))
        self.assertEqual(a.identify(), "t7")
        self.assertEqual(runner.argv, [["get", "t7", "--json"]])

    def test_identify_fails_closed(self) -> None:
        rows = {
            "non-zero": reply(returncode=3, stderr=fixture("error-not-found.stderr.json")),
            "other terminal": reply(fixture("get-live-no-status.json")),
            "finished terminal": reply(fixture("get-finished-ok.json")),
            "no json": reply("hello"),
            "no address": reply('{"state": "live"}'),
        }
        for label, answer in rows.items():
            with self.subTest(label):
                a, _ = adapter(answer)
                with self.assertRaises(backend.BackendUnavailable):
                    a.identify()

    def test_identify_without_a_terminal_id_runs_nothing(self) -> None:
        runner = Recorder()
        with self.assertRaises(backend.BackendUnavailable):
            hc.Adapter({"HC_TERMINAL_SOCKET": SOCKET}, runner=runner, binary="hc").identify()
        self.assertEqual(runner.calls, [])

    def test_identify_propagates_a_missing_binary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(hc.Path, "home", return_value=Path(tmp)):
            bound = hc.Adapter(ENVIRON)
        with mock.patch.object(hc.subprocess, "run", side_effect=OSError("no hc")):
            with self.assertRaisesRegex(backend.BackendUnavailable, "no hc"):
                bound.identify()

    def test_open_backend_runs_identify_once_and_keeps_the_handle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(hc.Path, "home", return_value=Path(tmp)):
            with mock.patch.object(hc.subprocess, "run", return_value=reply(fixture("get-live.json"))) as run:
                opened = backend.open_backend(ENVIRON)
        self.assertEqual((opened.name, opened.handle), ("hc", "t7"))
        run.assert_called_once()
        self.assertEqual(run.call_args.args[0], ["hc", "get", "t7", "--json"])
        self.assertEqual(run.call_args.kwargs["env"]["HC_SOCKET"], SOCKET)

    def test_backend_detection_now_returns_hc(self) -> None:
        only_hc = {"HC_TERMINAL_ID": "t7", "HC_TERMINAL_SOCKET": SOCKET}
        self.assertEqual(backend.detect(only_hc), "hc")
        self.assertEqual(backend.detect({**only_hc, "HERDR_ENV": "1", "HERDR_PANE_ID": "w1:p1"}, backend.parse_explicit("hc@t7")), "hc")
        with self.assertRaises(backend.DetectionError):
            backend.detect({**only_hc, "HERDR_ENV": "1", "HERDR_PANE_ID": "w1:p1"})


class SendBlockTest(unittest.TestCase):
    def test_block_is_the_report_by_prompt_send_with_no_notification_line(self) -> None:
        a, runner = adapter()
        block = a.send_block(LEAD, REPORT)
        self.assertEqual(block, 'hc send t3 "$(cat /state/projects/demo/runs/r1/send-eng-a.txt)"')
        self.assertNotIn("\n", block)
        self.assertNotIn("notif", block)
        self.assertEqual(runner.calls, [])

    def test_block_renders_the_binary_the_adapter_resolved(self) -> None:
        resolved = hc.Adapter(ENVIRON, runner=Recorder(), binary="/home/u/.local/bin/herdr-core")
        self.assertEqual(
            resolved.send_block(LEAD, REPORT),
            '"$HOME/.local/bin/herdr-core" send t3 "$(cat /state/projects/demo/runs/r1/send-eng-a.txt)"',
        )

    def test_block_refuses_unsafe_or_misshapen_inputs(self) -> None:
        a, _ = adapter()
        for lead, report in (
            ("t3 t4", REPORT),
            ("t3;rm", REPORT),
            ("", REPORT),
            (LEAD, "report-eng-a.md"),
        ):
            with self.subTest(lead=lead, report=report), self.assertRaises(ValueError):
                a.send_block(lead, report)

    def test_a_handle_the_other_backends_use_is_accepted(self) -> None:
        a, _ = adapter()
        for handle in ("w1:p1", "t7", "session:s1.block:b1"):
            self.assertIn(f"hc send {handle} ", a.send_block(handle, REPORT))


def template_matches(template: str, args: list[str]) -> bool:
    """`hc <verb> ...` with <placeholder> words and an optional trailing `<argv>...`, against built argv."""
    words = template.split()[1:]
    variadic = words[-1].endswith("...") if words else False
    fixed = words[:-1] if variadic else words
    if len(args) < len(fixed) or (not variadic and len(args) != len(fixed)):
        return False
    return all(word.startswith("<") or word == arg for word, arg in zip(fixed, args))


class ReferenceTest(unittest.TestCase):
    """The argv the adapter builds, the command the reference documents, and the allow-list agree."""

    def exercise(self) -> list[tuple[str, list[str]]]:
        """Every operation the adapter implements once, as (operation, argv) read back from the runner."""
        steps = {
            "identify": (["get-live.json"], lambda a: a.identify()),
            "prompt": (["send-started.json"], lambda a: a.prompt("t7", "go")),
            "read": (["read.txt"], lambda a: a.read_output("t7", 50)),
            "state": (["get-live.json"], lambda a: a.get_seat("t7")),
            "wait": (["wait-idle.json"], lambda a: a.wait_state("t7", ["idle"], 5000)),
            "list": (["ls.json"], lambda a: a.list_seats()),
            "processes": (["get-live.json"], lambda a: a.processes("t7")),
        }
        built = []
        for operation, (replies, step) in steps.items():
            a, runner = adapter(*[reply(fixture(name)) for name in replies])
            step(a)
            built += [(operation, args) for args in runner.argv]
        return built

    BUILT = {
        "identify": "hc get <t> --json",
        "prompt": "hc send --json <t> <text>",
        "read": "hc read --lines <n> <t>",
        "state": "hc get <t> --json",
        "wait": "hc wait --json --timeout <s> <t>",
        "list": "hc ls --json",
        "processes": "hc get <t> --json",
    }
    # The seam has no spawn, interrupt or close yet (backend.py docstring): the reference documents
    # their commands and the allow-list bounds them, but the adapter builds no argv for them.
    REFERENCE_ONLY = (
        "hc run --bg --json --no-parent --name <name> --cwd <dir> -- <argv>...",
        "hc interrupt --json <t>",
        "hc kill --json <t>",
        "hc rm --json <t>",
    )

    def test_each_built_argv_is_the_command_the_reference_documents(self) -> None:
        reference = REFERENCE.read_text(encoding="utf-8")
        built = self.exercise()
        self.assertEqual([operation for operation, _ in built], list(self.BUILT))
        for operation, args in built:
            template = self.BUILT[operation]
            with self.subTest(operation=operation):
                self.assertIn(f"`{template}`", reference)
                self.assertTrue(template_matches(template, args), f"{args} does not fit {template}")

    def test_the_reference_only_commands_are_documented_and_inside_the_allow_list(self) -> None:
        reference = REFERENCE.read_text(encoding="utf-8")
        for template in self.REFERENCE_ONLY:
            with self.subTest(template):
                self.assertIn(f"`{template}`", reference)
                self.assertIsNone(violation(template.split()[1:]))

    def test_every_built_argv_is_inside_the_allow_list(self) -> None:
        for operation, args in self.exercise():
            with self.subTest(operation=operation):
                self.assertIsNone(violation(args))

    def test_the_allow_list_rejects_an_invented_command(self) -> None:
        invented = [
            ["keys", "t7", "enter"],
            ["server", "stop"],
            ["send", "--force", "t7", "x"],
            ["send", "--wait", "t7", "x"],
            ["send", "--if", "idle", "t7", "x"],
            ["run", "--bg", "--name", "x", "claude"],
            ["run", "--no-parent", "--name", "x", "claude"],
            ["run", "--outlive-parent", "--bg", "--no-parent", "claude"],
            ["get", "t7", "--all"],
            [],
        ]
        for args in invented:
            with self.subTest(args):
                self.assertIsNotNone(violation(args))

    def test_the_reference_has_one_heading_per_operation_in_order(self) -> None:
        headings = re.findall(r"^## (.+)$", REFERENCE.read_text(encoding="utf-8"), flags=re.MULTILINE)
        self.assertEqual(headings, ["identify", "spawn", "prompt", "read", "state", "wait", "list", "processes", "interrupt", "close", "notify"])

    def test_every_operation_section_has_a_command_or_unsupported_and_a_provisional_line(self) -> None:
        text = REFERENCE.read_text(encoding="utf-8")
        sections = dict(re.findall(r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", text, flags=re.MULTILINE | re.DOTALL))
        for operation, body in sections.items():
            with self.subTest(operation):
                if "Command:" in body or "Commands:" in body:
                    self.assertIn("Source:", body)
                else:
                    self.assertIn("Unsupported:", body)
                self.assertIn("Provisional:", body)


if __name__ == "__main__":
    unittest.main()

"""Rex adapter: argv building and parsing against an injected runner and recorded fixtures.

Fixtures under tests/fixtures/backends/rex are copies and hand-written shapes (see SOURCES.txt there);
nothing here runs rex.
"""
from __future__ import annotations

import json
import re
import shlex
import subprocess
import tempfile
import unittest
from functools import partial
from pathlib import Path
from unittest import mock

import support
import backend
from backends import rex
from support import Recorder


def setUpModule() -> None:
    support.never_run()


REFERENCE = support.ADW / "references" / "backend-rex.md"
SESSION = "session:aaaa"
LEAD = f"{SESSION}.block:a1"
ENG_A = f"{SESSION}.block:a2"
ENDPOINT = "unix:///tmp/rex-test/server.sock"
ENVIRON = {"TERM_PROGRAM": "rex", "REX_SESSION": SESSION, "REX_BLOCK": "block:a1"}
REPORT = "/state/projects/demo/runs/r1/report-eng-a.md"
BASE = ["--autostart=false"]
PINNED = ["--autostart=false", "-S", ENDPOINT]
NOT_NONE_PROVISIONAL = ["identify", "spawn", "prompt", "state", "wait", "list", "notify"]


fixture = partial(support.fixture, "rex")
reply = partial(support.reply, "rex")


def fresh(*replies: subprocess.CompletedProcess[str]) -> tuple[rex.Adapter, Recorder]:
    return support.adapter(rex, ENVIRON, *replies)


def adapter(*replies: subprocess.CompletedProcess[str]) -> tuple[rex.Adapter, Recorder]:
    """An identified adapter whose runner has answered only the identify calls; `replies` answer what the test calls next."""
    a, runner = fresh(reply(fixture("whoami.json")), reply(fixture("block-ls.json")), *replies)
    a.identify()
    runner.calls.clear()
    return a, runner


def block_call(block: str, method: str) -> list[str]:
    return [*PINNED, "block", "call", "-s", SESSION, "-b", block, method]


class Scripted:
    """A runner that answers any rex call from the fixtures, so one scenario can drive every operation."""

    STATUS = {"block:a1": "status_working", "block:a2": "status_blocked", "block:a3": "status_empty", "block:a4": "status_working"}

    def __init__(self) -> None:
        self.argv: list[list[str]] = []

    def __call__(self, args: list[str], *, timeout: float = 30.0, **_: object) -> subprocess.CompletedProcess[str]:
        self.argv.append(list(args))
        rest = [arg for arg in args if arg != "--autostart=false"]
        if rest[:1] == ["-S"]:
            rest = rest[2:]
        if rest[:1] == ["whoami"]:
            return reply(fixture("whoami.json"))
        if rest[:2] == ["block", "ls"]:
            return reply(fixture("block-ls.json"))
        if rest[:2] == ["block", "call"] and rest[-1] == "program_status":
            return reply(fixture(self.STATUS[rest[rest.index("-b") + 1]] + ".json"))
        if rest[:2] == ["block", "call"] and rest[-1] == "process":
            return reply(fixture("process_claude.json"))
        if rest[:1] == ["capture"]:
            return reply(fixture("capture.txt"))
        if rest[:1] in (["send"], ["send-key"]):
            return reply()
        raise AssertionError(f"unscripted rex call: {args}")


def normalized(args: list[str], *placeholders: tuple[str, str]) -> str:
    """The argv as the reference writes it: no global flags, ids and text as placeholders."""
    rest = [arg for arg in args if arg != "--autostart=false"]
    if rest[:1] == ["-S"]:
        rest = rest[2:]
    pairs = {SESSION: "<S>", **{f"block:a{n}": "<B>" for n in range(1, 5)}, **dict(placeholders)}
    return " ".join(pairs.get(arg, arg) for arg in rest)


ALLOWED = [
    r"whoami --json",
    r"block ls -s <S> --json",
    r"block call -s <S> -b <B> (program_status|process)",
    r"capture -s <S> -b <B> --trim",
    r"send -s <S> -b <B> -- <text>",
    r"send-key -s <S> -b <B> enter",
]


def is_allowed(command: str) -> bool:
    return any(re.fullmatch(pattern, command) for pattern in ALLOWED)


class RunnerTest(unittest.TestCase):
    def test_the_adapter_runs_rex_bin_dir_when_executable_else_rex_from_path(self) -> None:
        def binary_run(environ: dict[str, str]) -> str:
            with mock.patch.object(backend.subprocess, "run", return_value=reply("{}")) as run:
                with self.assertRaises(backend.BackendError):
                    rex.Adapter(environ).identify()
            return run.call_args.args[0][0]

        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(binary_run({**ENVIRON, "REX_BIN_DIR": tmp}), "rex")
            binary = Path(tmp) / "rex"
            binary.write_text("#!/bin/sh\n", encoding="utf-8")
            binary.chmod(0o755)
            self.assertEqual(binary_run({**ENVIRON, "REX_BIN_DIR": tmp}), str(binary))
        self.assertEqual(binary_run(ENVIRON), "rex")
        self.assertEqual(binary_run({**ENVIRON, "REX_BIN_DIR": ""}), "rex")

    def test_default_runner_is_resolved_at_construction_and_passes_the_binary(self) -> None:
        completed = reply("{}")
        with mock.patch.object(rex.subprocess, "run", return_value=completed) as run:
            built = rex.Adapter({**ENVIRON})
            with self.assertRaises(backend.BackendError):
                built.identify()
        self.assertEqual(run.call_args.args[0][:2], ["rex", "--autostart=false"])
        self.assertEqual(run.call_args.kwargs["timeout"], backend.DEFAULT_TIMEOUT)

    def test_default_runner_propagates_unavailable(self) -> None:
        with mock.patch.object(backend.subprocess, "run", side_effect=OSError("gone")):
            with self.assertRaises(backend.BackendUnavailable):
                rex.Adapter(ENVIRON).identify()


class DetectionTest(unittest.TestCase):
    def test_backend_detection_returns_rex(self) -> None:
        self.assertEqual(backend.detect(ENVIRON), "rex")

    def test_a_rex_seat_in_a_nested_environment_needs_its_own_handle(self) -> None:
        nested = {**ENVIRON, "HC_TERMINAL_ID": "t7", "HC_TERMINAL_SOCKET": "/run/hc.sock"}
        with self.assertRaises(backend.DetectionError):
            backend.detect(nested)
        self.assertEqual(backend.detect(nested, backend.Explicit("rex", LEAD)), "rex")
        with self.assertRaises(backend.DetectionError):
            backend.detect(nested, backend.Explicit("rex", ENG_A))

    def test_open_backend_runs_identify_once_and_keeps_the_handle(self) -> None:
        runner = Scripted()
        with mock.patch.object(backend.subprocess, "run", side_effect=lambda command, **kwargs: runner(command[1:], **kwargs)):
            opened = backend.open_backend(ENVIRON)
        self.assertEqual((opened.name, opened.handle), ("rex", LEAD))
        self.assertEqual([normalized(args) for args in runner.argv], ["whoami --json", "block ls -s <S> --json"])


class IdentifyTest(unittest.TestCase):
    def test_identify_reads_the_endpoint_then_confirms_the_own_block(self) -> None:
        a, runner = fresh(reply(fixture("whoami.json")), reply(fixture("block-ls.json")))
        self.assertEqual(a.identify(), LEAD)
        self.assertEqual(
            runner.argv,
            [[*BASE, "whoami", "--json"], [*PINNED, "block", "ls", "-s", SESSION, "--json"]],
        )

    def test_every_call_after_identify_pins_the_server(self) -> None:
        a, runner = fresh(reply(fixture("whoami.json")), reply(fixture("block-ls.json")), reply(fixture("block-ls.json")))
        a.identify()
        a.get_terminal(LEAD)
        self.assertEqual(runner.argv[2][:3], PINNED)

    def test_identify_fails_closed(self) -> None:
        rows = {
            "server unreachable": [reply(returncode=4)],
            "whoami fails": [reply(returncode=1)],
            "no endpoint": [reply("{}")],
            "empty endpoint": [reply('{"endpoint": ""}')],
            "block ls not found": [reply(fixture("whoami.json")), reply(returncode=3)],
            "block ls malformed": [reply(fixture("whoami.json")), reply("{}")],
            "own block not listed": [reply(fixture("whoami.json")), reply('{"blocks": [{"block_id": "block:zz"}]}')],
        }
        for label, answers in rows.items():
            with self.subTest(label):
                a, _ = fresh(*answers)
                with self.assertRaises(backend.BackendError):
                    a.identify()

    def test_identify_without_a_usable_own_handle_runs_nothing(self) -> None:
        for environ in ({}, {"REX_SESSION": SESSION}, {**ENVIRON, "REX_BLOCK": "block:a.b"}):
            with self.subTest(environ):
                runner = Recorder()
                with self.assertRaises(backend.BackendUnavailable):
                    rex.Adapter(environ, runner=runner).identify()
                self.assertEqual(runner.calls, [])


    def test_a_call_before_identify_is_refused_and_runs_nothing(self) -> None:
        a, runner = fresh()
        calls = (
            a.list_seats,
            lambda: a.get_seat(LEAD),
            lambda: a.get_terminal(LEAD),
            lambda: a.read_output(ENG_A, 5),
            lambda: a.prompt(ENG_A, "text"),
            lambda: a.processes(ENG_A),
        )
        for call in calls:
            with self.assertRaisesRegex(backend.BackendUnavailable, "before identify"):
                call()
        self.assertEqual(runner.calls, [])


class SeatTest(unittest.TestCase):
    def test_list_seats_is_block_ls_then_program_status_per_block(self) -> None:
        a, runner = adapter(
            reply(fixture("block-ls.json")),
            reply(fixture("status_working.json")),
            reply(fixture("status_blocked.json")),
            reply(fixture("status_empty.json")),
            reply(fixture("status_blocked_other.json")),
        )
        seats = a.list_seats()
        self.assertEqual(
            runner.argv,
            [
                [*PINNED, "block", "ls", "-s", SESSION, "--json"],
                block_call("block:a1", "program_status"),
                block_call("block:a2", "program_status"),
                block_call("block:a3", "program_status"),
                block_call("block:a4", "program_status"),
            ],
        )
        self.assertEqual(
            [(seat.handle, seat.name, seat.state, seat.workspace, seat.kind, seat.session) for seat in seats],
            [
                (LEAD, "lead", "working", SESSION, None, None),
                (ENG_A, "eng-a", "blocked", SESSION, None, None),
                (f"{SESSION}.block:a3", "eng-b", "unknown", SESSION, None, None),
                (f"{SESSION}.block:a4", None, "blocked", SESSION, None, None),
            ],
        )

    def test_list_skips_a_block_that_closed_between_the_calls(self) -> None:
        a, _ = adapter(reply(fixture("block-ls.json")), reply(fixture("status_working.json")), reply(returncode=3), reply(fixture("status_empty.json")), reply(fixture("status_empty.json")))
        self.assertEqual([seat.handle for seat in a.list_seats()], [LEAD, f"{SESSION}.block:a3", f"{SESSION}.block:a4"])

    def test_list_refuses_malformed_output(self) -> None:
        for label, answers in {
            "no blocks": [reply("{}")],
            "not json": [reply("nope")],
            "block without id": [reply('{"blocks": [{"label": "x"}]}')],
            "bad status": [reply(fixture("block-ls.json")), reply(fixture("status_bad.json"))],
        }.items():
            with self.subTest(label):
                a, _ = adapter(*answers)
                with self.assertRaises(backend.BackendError):
                    a.list_seats()

    def test_get_seat_by_handle_lists_the_handles_session(self) -> None:
        a, runner = adapter(reply(fixture("block-ls.json")), reply(fixture("status_working.json")))
        seat = a.get_seat(ENG_A)
        self.assertEqual(runner.argv[0], [*PINNED, "block", "ls", "-s", SESSION, "--json"])
        self.assertEqual(runner.argv[1], block_call("block:a2", "program_status"))
        self.assertEqual((seat.handle, seat.name, seat.state), (ENG_A, "eng-a", "working"))

    def test_get_seat_by_name_looks_in_the_own_session(self) -> None:
        a, runner = adapter(reply(fixture("block-ls.json")), reply(fixture("status_working.json")))
        self.assertEqual(a.get_seat("eng-a").handle, ENG_A)
        self.assertEqual(runner.argv[0], [*PINNED, "block", "ls", "-s", SESSION, "--json"])

    def test_get_seat_in_another_session_lists_that_session(self) -> None:
        a, runner = adapter(reply('{"blocks": [{"block_id": "block:b1", "label": "x"}]}'), reply(fixture("status_empty.json")))
        self.assertEqual(a.get_seat("session:bbbb.block:b1").handle, "session:bbbb.block:b1")
        self.assertEqual(runner.argv[0], [*PINNED, "block", "ls", "-s", "session:bbbb", "--json"])

    def test_missing_seat_is_not_found(self) -> None:
        rows = {
            "unknown name": (lambda a: a.get_seat("nobody"), [reply(fixture("block-ls.json"))]),
            "unknown handle": (lambda a: a.get_seat(f"{SESSION}.block:zz"), [reply(fixture("block-ls.json"))]),
            "unknown terminal": (lambda a: a.get_terminal(f"{SESSION}.block:zz"), [reply(fixture("block-ls.json"))]),
            "exit 3 on ls": (lambda a: a.get_terminal(LEAD), [reply(returncode=3)]),
            "exit 3 on status": (lambda a: a.get_seat(LEAD), [reply(fixture("block-ls.json")), reply(returncode=3)]),
        }
        for label, (call, answers) in rows.items():
            with self.subTest(label):
                a, _ = adapter(*answers)
                with self.assertRaises(backend.SeatError) as caught:
                    call(a)
                self.assertEqual((caught.exception.kind, caught.exception.code), ("not_found", "not_found"))

    def test_an_ambiguous_label_is_an_error_not_a_guess(self) -> None:
        duplicate = '{"blocks": [{"block_id": "block:a2", "label": "eng-a"}, {"block_id": "block:a9", "label": "eng-a"}]}'
        a, _ = adapter(reply(duplicate))
        with self.assertRaises(backend.BackendError) as caught:
            a.get_seat("eng-a")
        self.assertEqual(caught.exception.code, "ambiguous")
        self.assertNotIsInstance(caught.exception, backend.SeatError)

    def test_a_name_needs_the_own_session_and_a_bad_handle_is_refused(self) -> None:
        runner = Recorder()
        with self.assertRaises(backend.BackendUnavailable):
            rex.Adapter({}, runner=runner).get_seat("eng-a")
        a = rex.Adapter(ENVIRON, runner=runner)
        for ref in ("a.b.c", ".block:a1", "session:aaaa.", "x y.z"):
            with self.subTest(ref), self.assertRaises(ValueError):
                a.get_seat(ref)
        self.assertEqual(runner.calls, [])

    def test_get_terminal_returns_the_handle_and_label(self) -> None:
        a, runner = adapter(reply(fixture("block-ls.json")))
        seat = a.get_terminal(ENG_A)
        self.assertEqual(runner.argv, [[*PINNED, "block", "ls", "-s", SESSION, "--json"]])
        self.assertEqual((seat.handle, seat.name, seat.state), (ENG_A, "eng-a", "unknown"))


class StateTest(unittest.TestCase):
    def state(self, stdout: str) -> str:
        a, _ = adapter(reply(fixture("block-ls.json")), reply(stdout))
        return a.get_seat(LEAD).state

    def test_program_status_maps_to_the_seat_state(self) -> None:
        rows = {
            "status_empty.json": "unknown",
            "status_working.json": "working",
            "status_blocked.json": "blocked",
            "status_blocked_other.json": "blocked",
        }
        for name, expected in rows.items():
            with self.subTest(name):
                self.assertEqual(self.state(fixture(name)), expected)

    def test_the_most_urgent_record_wins_and_unknown_states_are_ignored(self) -> None:
        def records(*states: object) -> str:
            return json.dumps({"records": [{"state": state} for state in states]})

        self.assertEqual(self.state(records("done", "working")), "working")
        self.assertEqual(self.state(records("working", "error")), "error")
        self.assertEqual(self.state(records("error", "blocked")), "blocked")
        self.assertEqual(self.state(records("done")), "done")
        self.assertEqual(self.state(records("sleeping", 3, None)), "unknown")

    def test_a_malformed_status_is_a_backend_error(self) -> None:
        for stdout in (fixture("status_bad.json"), "{}", "nope", '{"records": [1]}'):
            with self.subTest(stdout):
                a, _ = adapter(reply(fixture("block-ls.json")), reply(stdout))
                with self.assertRaises(backend.BackendError):
                    a.get_seat(LEAD)


class ReadTest(unittest.TestCase):
    def test_read_output_argv_and_tail(self) -> None:
        a, runner = adapter(reply(fixture("capture.txt")))
        self.assertEqual(a.read_output(ENG_A, 2), "Awaiting: lead review\n> last visible line\n")
        self.assertEqual(runner.argv, [[*PINNED, "capture", "-s", SESSION, "-b", "block:a2", "--trim"]])

    def test_read_output_by_name_resolves_the_label_first_and_strips_cr(self) -> None:
        a, runner = adapter(reply(fixture("block-ls.json")), reply("one\r\ntwo\r\n"))
        self.assertEqual(a.read_output("eng-a", 10), "one\ntwo\n")
        self.assertEqual(runner.argv[0][3:5], ["block", "ls"])

    def test_read_output_rejects_a_non_positive_count_and_maps_exit_3(self) -> None:
        a, runner = adapter()
        for lines in (0, -1):
            with self.subTest(lines), self.assertRaises(ValueError):
                a.read_output(ENG_A, lines)
        self.assertEqual(runner.calls, [])
        a, _ = adapter(reply(returncode=3))
        with self.assertRaises(backend.SeatError):
            a.read_output(ENG_A, 5)


class PromptTest(unittest.TestCase):
    def test_prompt_reads_status_then_sends_text_then_enter(self) -> None:
        a, runner = adapter(reply(fixture("status_working.json")), reply(), reply())
        self.assertIsNone(a.prompt(ENG_A, 'line one\nline "two" $HOME'))
        self.assertEqual(
            runner.argv,
            [
                block_call("block:a2", "program_status"),
                [*PINNED, "send", "-s", SESSION, "-b", "block:a2", "--", 'line one\nline "two" $HOME'],
                [*PINNED, "send-key", "-s", SESSION, "-b", "block:a2", "enter"],
            ],
        )

    def test_text_that_looks_like_an_option_follows_the_separator(self) -> None:
        a, runner = adapter(reply(fixture("status_empty.json")), reply(), reply())
        a.prompt(ENG_A, "--help")
        self.assertEqual(runner.argv[1][-2:], ["--", "--help"])

    def test_a_blocked_seat_is_refused_before_anything_is_sent(self) -> None:
        a, runner = adapter(reply(fixture("status_blocked.json")))
        with self.assertRaises(backend.SeatError) as caught:
            a.prompt(ENG_A, "text")
        self.assertEqual(caught.exception.kind, "blocked")
        self.assertEqual(len(runner.calls), 1)

    def test_an_unreadable_status_still_sends(self) -> None:
        for answer in (reply(fixture("status_bad.json")), reply("{}"), reply(returncode=1)):
            with self.subTest(answer.stdout or answer.returncode):
                a, runner = adapter(answer, reply(), reply())
                a.prompt(ENG_A, "text")
                self.assertEqual([args[3] for args in runner.argv], ["block", "send", "send-key"])

    def test_a_gone_or_unreachable_seat_sends_nothing(self) -> None:
        a, runner = adapter(reply(returncode=3))
        with self.assertRaises(backend.SeatError) as caught:
            a.prompt(ENG_A, "text")
        self.assertEqual(caught.exception.kind, "not_found")
        a, runner = adapter(reply(returncode=4))
        with self.assertRaises(backend.BackendUnavailable):
            a.prompt(ENG_A, "text")
        self.assertEqual(len(runner.calls), 1)

    def test_a_failed_send_does_not_press_enter(self) -> None:
        a, runner = adapter(reply(fixture("status_empty.json")), reply(returncode=2))
        with self.assertRaises(backend.BackendError) as caught:
            a.prompt(ENG_A, "text")
        self.assertEqual(caught.exception.code, "exit_2")
        self.assertEqual(len(runner.calls), 2)

    def test_empty_text_and_a_bad_handle_run_nothing(self) -> None:
        a, runner = adapter()
        with self.assertRaises(ValueError):
            a.prompt(ENG_A, "")
        with self.assertRaises(ValueError):
            a.prompt("a.b.c", "text")
        self.assertEqual(runner.calls, [])

    def test_prompt_by_name_resolves_the_label_first(self) -> None:
        a, runner = adapter(reply(fixture("block-ls.json")), reply(fixture("status_empty.json")), reply(), reply())
        a.prompt("eng-a", "text")
        self.assertEqual(runner.argv[0][3:5], ["block", "ls"])
        self.assertEqual(runner.argv[1], block_call("block:a2", "program_status"))


class WaitTest(unittest.TestCase):
    def test_wait_state_is_unsupported_and_runs_nothing(self) -> None:
        a, runner = adapter()
        with self.assertRaises(backend.Unsupported):
            a.wait_state(ENG_A, ["idle", "done"], 1000)
        self.assertEqual(runner.calls, [])


class ProcessesTest(unittest.TestCase):
    def test_processes_argv_and_foreground_passthrough(self) -> None:
        a, runner = adapter(reply(fixture("process_claude.json")))
        processes = a.processes(ENG_A)
        self.assertEqual(runner.argv, [block_call("block:a2", "process")])
        self.assertEqual(processes, [backend.Process(("claude",), 4242, "/tmp/sku-proj-a", argv_reported=False)])

    def test_other_foregrounds_and_none(self) -> None:
        a, _ = adapter(reply(fixture("process_codex.json")), reply(fixture("process_shell.json")), reply(fixture("process_none.json")))
        self.assertEqual(a.processes(ENG_A), [backend.Process(("node",), 4242, "/tmp/sku-proj-b", argv_reported=False)])
        self.assertEqual(a.processes(ENG_A), [backend.Process(("-zsh",), 4242, "/tmp/sku-proj-a", argv_reported=False)])
        self.assertEqual(a.processes(ENG_A), [])

    def test_malformed_replies_fail_closed(self) -> None:
        for stdout in (fixture("process_bad.json"), "{}", "nope", '{"foreground": "x"}'):
            with self.subTest(stdout):
                a, _ = adapter(reply(stdout))
                with self.assertRaises(backend.BackendError):
                    a.processes(ENG_A)

    def test_missing_block_is_not_found(self) -> None:
        a, _ = adapter(reply(returncode=3))
        with self.assertRaises(backend.SeatError):
            a.processes(ENG_A)


class SendBlockTest(unittest.TestCase):
    def test_block_is_the_report_by_prompt_send_then_enter(self) -> None:
        a, runner = adapter()
        self.assertEqual(
            a.send_block(LEAD, REPORT),
            backend.SendBlock(
                '"$REX_BIN_DIR/rex" send -s session:aaaa -b block:a1 -- "$(cat "/state/projects/demo/runs/r1/send-eng-a.txt")"'
                ' && "$REX_BIN_DIR/rex" send-key -s session:aaaa -b block:a1 enter'
            ),
        )
        self.assertEqual(runner.calls, [])

    def test_block_never_relies_on_a_bare_rex_on_the_peers_path(self) -> None:
        a, _ = adapter()
        block = a.send_block(LEAD, REPORT).send_command
        self.assertEqual(block.count('"$REX_BIN_DIR/rex"'), 2)
        self.assertNotRegex(block, r"(^|&& )rex ")

    def test_block_refuses_unsafe_or_misshapen_inputs(self) -> None:
        a, _ = adapter()
        for lead, report in (
            ("lead-demo", REPORT),
            ("w1:p1", REPORT),
            ("t7", REPORT),
            ("session:a.block:b.c", REPORT),
            ("session:aaaa.block:a1;rm", REPORT),
            ("", REPORT),
            (LEAD, "report-eng-a.md"),
        ):
            with self.subTest(lead=lead, report=report), self.assertRaises(ValueError):
                a.send_block(lead, report)

    def test_a_real_shaped_handle_fits_the_handle_pattern(self) -> None:
        uuid = "0b9a3f1e-7c2d-4e55-9a10-6f2b8d4c1e77"
        handle = f"session:{uuid}.block:{uuid}"
        self.assertIsNotNone(backend.HANDLE_RE.fullmatch(handle))
        a, _ = adapter()
        self.assertIn(f"-s session:{uuid} -b block:{uuid}", a.send_block(handle, REPORT).send_command)


class ContractTest(unittest.TestCase):
    def run_every_operation(self) -> Scripted:
        runner = Scripted()
        a = rex.Adapter(ENVIRON, runner=runner)
        a.identify()
        a.list_seats()
        a.get_seat("eng-a")
        a.get_terminal(ENG_A)
        a.read_output(ENG_A, 5)
        a.prompt(f"{SESSION}.block:a3", "hello text")
        a.processes(ENG_A)
        return runner

    def test_every_argv_is_in_the_allow_list_and_targets_a_session_and_block(self) -> None:
        runner = self.run_every_operation()
        seen = set()
        for args in runner.argv:
            self.assertEqual(args[0], "--autostart=false")
            command = normalized(args, ("hello text", "<text>"))
            seen.add(command)
            self.assertTrue(is_allowed(command), command)
            if not command.startswith("whoami"):
                self.assertIn("-s <S>", command)
            if not command.startswith(("whoami", "block ls")):
                self.assertIn("-b <B>", command)
        self.assertEqual(
            seen,
            {
                "whoami --json",
                "block ls -s <S> --json",
                "block call -s <S> -b <B> program_status",
                "block call -s <S> -b <B> process",
                "capture -s <S> -b <B> --trim",
                "send -s <S> -b <B> -- <text>",
                "send-key -s <S> -b <B> enter",
            },
        )

    def test_the_send_block_commands_are_in_the_allow_list(self) -> None:
        a, _ = adapter()
        block = a.send_block(LEAD, REPORT).send_command
        for part in block.split(" && "):
            tokens = shlex.split(part)
            self.assertEqual(tokens[0], "$REX_BIN_DIR/rex")
            self.assertTrue(is_allowed(normalized(tokens[1:], ('$(cat /state/projects/demo/runs/r1/send-eng-a.txt)', "<text>"))), part)

    def test_error_kinds_are_the_shared_ones(self) -> None:
        a, _ = adapter(reply(returncode=3))
        with self.assertRaises(backend.SeatError) as caught:
            a.get_terminal(LEAD)
        self.assertIn(caught.exception.kind, backend.SEAT_ERROR_KINDS)
        a, _ = adapter(reply(returncode=4))
        with self.assertRaises(backend.BackendUnavailable):
            a.list_seats()
        a, _ = adapter(reply(returncode=2))
        with self.assertRaises(backend.BackendError) as other:
            a.list_seats()
        self.assertEqual(other.exception.code, "exit_2")
        self.assertNotIsInstance(other.exception, (backend.SeatError, backend.BackendUnavailable))

    def test_operations_the_adapter_does_not_support_raise_unsupported(self) -> None:
        a, runner = adapter()
        with self.assertRaises(backend.Unsupported):
            a.wait_state(LEAD, ["idle"], 1)
        self.assertEqual(runner.calls, [])


class ReferenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        text = REFERENCE.read_text(encoding="utf-8")
        parts = re.split(r"^## (.+)$", text, flags=re.MULTILINE)
        cls.text = text
        cls.sections = dict(zip(parts[1::2], parts[2::2]))

    def test_pending_operations_say_what_is_pending(self) -> None:
        for operation in NOT_NONE_PROVISIONAL:
            with self.subTest(operation):
                self.assertNotRegex(self.sections[operation], r"Provisional: none")
        self.assertIn("Unsupported:", self.sections["wait"])
        self.assertRegex(self.sections["notify"], r"Provisional: L8")

    def test_fenced_rex_commands_stay_inside_the_documented_set(self) -> None:
        documented = {
            ("whoami",), ("block", "ls"), ("block", "call"), ("block", "rename"), ("block", "close"),
            ("split",), ("send",), ("send-key",), ("capture",),
        }
        commands = []
        for body in self.sections.values():
            for block in re.findall(r"```\n(.*?)```", body, flags=re.DOTALL):
                commands += [line for line in block.splitlines() if line.startswith("rex ")]
        self.assertTrue(commands)
        for line in commands:
            tokens = [t for t in shlex.split(line)[1:] if t != "--autostart=false"]
            if tokens[:1] == ["-S"]:
                tokens = tokens[2:]
            with self.subTest(line):
                self.assertTrue(tokens[:2] in map(list, documented) or tokens[:1] in map(list, documented), line)

    def test_the_adapter_argv_golden_against_the_reference(self) -> None:
        runner = ContractTest().run_every_operation()
        for args in runner.argv:
            command = normalized(args, ("hello text", "<text>"))
            self.assertIn(f"rex {command}", self.text, command)

    def test_the_reference_says_wait_state_raises_unsupported(self) -> None:
        self.assertIn("`wait_state` raises `Unsupported`", self.sections["wait"])


if __name__ == "__main__":
    unittest.main()

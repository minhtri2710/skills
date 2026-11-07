"""The backend.py command line: `whoami` and `send-block` print one line or fail with `backend: <reason>` and exit 1."""
from __future__ import annotations

import contextlib
import io
import re
import unittest
from unittest import mock

import support
import backend
from backends import hc, herdr, rex
from fake_backend import FakeBackend


def setUpModule() -> None:
    support.never_run()


HERDR = {"HERDR_ENV": "1", "HERDR_PANE_ID": "w1:p1"}
LEAD = "w1:p9"
REPORT = "/tmp/runs/r1/report-eng-a.md"


def run_main(argv: list[str], opened: backend.Backend | None = None, environ: dict[str, str] | None = None):
    if opened is None:
        return support.run_main(lambda args: backend.main(args, environ if environ is not None else {}), argv)
    with mock.patch.object(backend, "open_backend", return_value=opened):
        return support.run_main(lambda args: backend.main(args, {}), argv)


class WhoamiTest(unittest.TestCase):
    def test_prints_the_backend_and_the_own_handle(self) -> None:
        self.assertEqual(run_main(["whoami"], FakeBackend(handle="f1:p4")), (0, "fake f1:p4\n", ""))

    def test_the_backend_flag_reaches_open_backend_as_explicit(self) -> None:
        with mock.patch.object(backend, "open_backend", return_value=FakeBackend()) as opening, \
                contextlib.redirect_stdout(io.StringIO()):
            backend.main(["whoami", "--backend", "herdr@w1:p1"], {})
        self.assertEqual(opening.call_args.args[1], backend.Explicit("herdr", "w1:p1"))


class SendBlockPartsTest(unittest.TestCase):
    """Bug A2: the report-by-prompt template names a send command and a failure notice only when the block has one."""

    def test_each_backend_renders_one_send_command_and_a_notice_only_herdr_has(self) -> None:
        rows = (
            (herdr.Adapter({}), "w1:p9", "herdr notification show"),
            (hc.Adapter({}, runner=support.Recorder(), binary="hc"), "t3", None),
            (rex.Adapter({}, runner=support.Recorder()), "session:s1.block:b1", None),
        )
        for adapter, lead, notice in rows:
            with self.subTest(adapter.name):
                block = adapter.send_block(lead, REPORT)
                self.assertIsInstance(block, backend.SendBlock)
                self.assertNotIn("\n", block.send_command)
                self.assertIn("/tmp/runs/r1/send-eng-a.txt", block.send_command)
                if notice is None:
                    self.assertIsNone(block.failure_notice)
                    self.assertEqual(block.text, block.send_command)
                else:
                    self.assertTrue(block.failure_notice.startswith(notice))
                    self.assertEqual(block.text, f"{block.send_command}\n{block.failure_notice}")


class SendBlockTest(unittest.TestCase):
    def test_prints_the_block_the_backend_renders_for_the_lead_and_report(self) -> None:
        fake = FakeBackend()
        code, out, err = run_main(["send-block", "--lead", LEAD, "--report", REPORT], fake)
        self.assertEqual((code, out, err), (0, fake.send_block(LEAD, REPORT).text + "\n", ""))
        self.assertEqual(fake.calls[-1], ("send_block", LEAD, REPORT))

    def test_the_backend_flag_reaches_open_backend_as_explicit(self) -> None:
        with mock.patch.object(backend, "open_backend", return_value=FakeBackend()) as opening, \
                contextlib.redirect_stdout(io.StringIO()):
            backend.main(["send-block", "--lead", LEAD, "--report", REPORT, "--backend", "herdr@w1:p1"], {})
        self.assertEqual(opening.call_args.args[1], backend.Explicit("herdr", "w1:p1"))

    def test_the_herdr_adapter_block_routes_by_the_lead_handle(self) -> None:
        with mock.patch.object(herdr.Adapter, "identify", return_value="w1:p1"):
            code, out, err = run_main(["send-block", "--lead", LEAD, "--report", REPORT], environ=HERDR)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out, herdr.Adapter(HERDR).send_block(LEAD, REPORT).text + "\n")
        self.assertIn(f"agent prompt {LEAD} ", out)

    def test_a_value_the_backend_refuses_fails_closed_with_no_output(self) -> None:
        for lead, report in (("not a handle", REPORT), (LEAD, "report.md")):
            with self.subTest(lead=lead, report=report), mock.patch.object(herdr.Adapter, "identify", return_value="w1:p1"):
                code, out, err = run_main(["send-block", "--lead", lead, "--report", report], environ=HERDR)
                self.assertEqual((code, out), (1, ""))
                self.assertTrue(err.startswith("backend: "), err)

    def test_report_send_file_names_the_peer_and_refuses_unsafe_or_misshapen_paths(self) -> None:
        self.assertEqual(backend.report_send_file("/state/runs/r1/report-eng-a.md"), ("eng-a", "/state/runs/r1/send-eng-a.txt"))
        for report in (
            "report-eng-a.md",
            "/state/runs/r1/eng-a.md",
            "/state/runs/r1/report-.md",
            '/state/runs/"r1"/report-eng-a.md',
            "/state/runs/$HOME/report-eng-a.md",
            "/state/runs/`x`/report-eng-a.md",
            "/state/runs/r1/report-eng-a.md\nrm",
            "/state/runs/r\\1/report-eng-a.md",
        ):
            with self.subTest(report=report), self.assertRaises(ValueError):
                backend.report_send_file(report)

    def test_the_template_file_names_are_the_ones_report_send_file_derives(self) -> None:
        for template in ("report-by-prompt.txt",):
            text = (support.ADW / "templates" / template).read_text(encoding="utf-8")
            named = re.findall(r"[^\s`\"]+/report-<[a-z_-]+>\.md", text)
            self.assertTrue(named, template)
            for report in named:
                with self.subTest(template=template, report=report):
                    self.assertIn(backend.report_send_file(report)[1], text)

    def test_a_backend_without_a_send_block_fails_closed(self) -> None:
        fake = FakeBackend()
        fake.script("send_block", backend.Unsupported("fake does not support send_block"))
        self.assertEqual(run_main(["send-block", "--lead", LEAD, "--report", REPORT], fake),
                         (1, "", "backend: fake does not support send_block\n"))

    def test_a_detection_failure_prints_nothing_and_exits_1(self) -> None:
        code, out, err = run_main(["send-block", "--lead", LEAD, "--report", REPORT])
        self.assertEqual((code, out), (1, ""))
        self.assertTrue(err.startswith("backend: no supported terminal tool"), err)

    def test_the_lead_and_the_report_are_required(self) -> None:
        for argv in (["send-block", "--report", REPORT], ["send-block", "--lead", LEAD]):
            with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                backend.main(argv, {})
            self.assertEqual(caught.exception.code, 2)


if __name__ == "__main__":
    unittest.main()

"""The backend.py command line: `whoami` and `send-block` print one line or fail with `backend: <reason>` and exit 1."""
from __future__ import annotations

import contextlib
import io
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
from fake_backend import FakeBackend  # noqa: E402

_NEVER_RUN = mock.patch.object(subprocess, "run", side_effect=AssertionError("tests never run a terminal tool"))


def setUpModule() -> None:
    _NEVER_RUN.start()


def tearDownModule() -> None:
    _NEVER_RUN.stop()


HERDR = {"HERDR_ENV": "1", "HERDR_PANE_ID": "w1:p1"}
LEAD = "w1:p9"
REPORT = "/tmp/runs/r1/report-eng-a.md"


def run_main(argv: list[str], opened: backend.Backend | None = None, environ: dict[str, str] | None = None):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        if opened is None:
            code = backend.main(argv, environ if environ is not None else {})
        else:
            with mock.patch.object(backend, "open_backend", return_value=opened):
                code = backend.main(argv, {})
    return code, out.getvalue(), err.getvalue()


class WhoamiTest(unittest.TestCase):
    def test_prints_the_backend_and_the_own_handle(self) -> None:
        self.assertEqual(run_main(["whoami"], FakeBackend(handle="f1:p4")), (0, "fake f1:p4\n", ""))

    def test_the_backend_flag_reaches_open_backend_as_explicit(self) -> None:
        with mock.patch.object(backend, "open_backend", return_value=FakeBackend()) as opening, \
                contextlib.redirect_stdout(io.StringIO()):
            backend.main(["whoami", "--backend", "herdr@w1:p1"], {})
        self.assertEqual(opening.call_args.args[1], backend.Explicit("herdr", "w1:p1"))


class SendBlockTest(unittest.TestCase):
    def test_prints_the_block_the_backend_renders_for_the_lead_and_report(self) -> None:
        fake = FakeBackend()
        code, out, err = run_main(["send-block", "--lead", LEAD, "--report", REPORT], fake)
        self.assertEqual((code, out, err), (0, fake.send_block(LEAD, REPORT) + "\n", ""))
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
        self.assertEqual(out, herdr.Adapter(HERDR).send_block(LEAD, REPORT) + "\n")
        self.assertIn(f"agent prompt {LEAD} ", out)

    def test_a_value_the_backend_refuses_fails_closed_with_no_output(self) -> None:
        for lead, report in (("not a handle", REPORT), (LEAD, "report.md")):
            with self.subTest(lead=lead, report=report), mock.patch.object(herdr.Adapter, "identify", return_value="w1:p1"):
                code, out, err = run_main(["send-block", "--lead", lead, "--report", report], environ=HERDR)
                self.assertEqual((code, out), (1, ""))
                self.assertTrue(err.startswith("backend: "), err)

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

from __future__ import annotations

import argparse
import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import support
import backend
from fake_backend import FakeBackend


def setUpModule() -> None:
    support.never_run()


HERDR = {"HERDR_ENV": "1", "HERDR_PANE_ID": "w1:p1"}
HC = {"HC_TERMINAL_ID": "t7", "HC_TERMINAL_SOCKET": "/run/hc.sock"}
REX = {"TERM_PROGRAM": "rex", "REX_BLOCK": "block:b1", "REX_SESSION": "session:s1"}
REX_HANDLE = "session:s1.block:b1"
FAKE = {"FAKE_HANDLE": "f1:p1"}


def explicit(text: str) -> backend.Explicit:
    return backend.parse_explicit(text)


class SingleSignatureTest(unittest.TestCase):
    def test_only_herdr(self) -> None:
        self.assertEqual(backend.detect(HERDR), "herdr")

    def test_each_signature_detects_its_backend(self) -> None:
        for name, environ in (("herdr", HERDR), ("hc", HC), ("rex", REX)):
            with self.subTest(name):
                self.assertEqual(backend.detect(environ), name)

    def test_incomplete_signatures_do_not_match(self) -> None:
        rows = {
            "rex without TERM_PROGRAM": {"REX_BLOCK": "block:b1", "REX_SESSION": "session:s1"},
            "rex with REX_BLOCK only": {"TERM_PROGRAM": "rex", "REX_BLOCK": "block:b1"},
            "rex with another TERM_PROGRAM": {**REX, "TERM_PROGRAM": "ghostty"},
            "rex with an empty REX_SESSION": {**REX, "REX_SESSION": ""},
            "herdr without a pane id": {"HERDR_ENV": "1"},
            "herdr with an empty pane id": {"HERDR_ENV": "1", "HERDR_PANE_ID": ""},
            "herdr without HERDR_ENV": {"HERDR_PANE_ID": "w1:p1"},
            "herdr with HERDR_ENV not 1": {"HERDR_ENV": "0", "HERDR_PANE_ID": "w1:p1"},
            "hc id without socket": {"HC_TERMINAL_ID": "t7"},
            "hc socket without id": {"HC_TERMINAL_SOCKET": "/run/hc.sock"},
        }
        for label, environ in rows.items():
            with self.subTest(label), self.assertRaisesRegex(backend.DetectionError, "no supported"):
                backend.detect(environ)

    def test_none(self) -> None:
        with self.assertRaisesRegex(backend.DetectionError, "no supported"):
            backend.detect({})
        with self.assertRaisesRegex(backend.DetectionError, "no supported"):
            backend.detect({}, explicit("herdr@w1:p1"))

    def test_signatures_are_pure_reads_of_the_argument(self) -> None:
        with mock.patch.dict("os.environ", {**HC, **REX}, clear=True):
            self.assertEqual(backend.detect(HERDR), "herdr")


class AmbiguousTest(unittest.TestCase):
    PAIRS = {"hc+rex": {**HC, **REX}, "hc+herdr": {**HC, **HERDR}, "rex+herdr": {**REX, **HERDR}}

    def test_each_pair_fails_closed_and_names_the_matches(self) -> None:
        for label, environ in self.PAIRS.items():
            first, second = label.split("+")
            with self.subTest(label), self.assertRaises(backend.DetectionError) as caught:
                backend.detect(environ)
            self.assertIn(first, str(caught.exception))
            self.assertIn(second, str(caught.exception))

    def test_all_three_match(self) -> None:
        with self.assertRaisesRegex(backend.DetectionError, r"hc.*rex.*herdr|herdr.*hc.*rex"):
            backend.detect({**HC, **REX, **HERDR})

    def test_explicit_equal_to_a_matched_backend_with_its_own_handle_returns_it(self) -> None:
        environ = {**HC, **HERDR}
        self.assertEqual(backend.detect(environ, explicit("herdr@w1:p1")), "herdr")
        self.assertEqual(backend.detect(environ, explicit("hc@t7")), "hc")

    def test_explicit_naming_a_backend_whose_signature_does_not_hold_fails_closed(self) -> None:
        for label, environ in self.PAIRS.items():
            absent = next(name for name in ("herdr", "hc", "rex") if name not in label)
            handle = {"herdr": "w1:p1", "hc": "t7", "rex": REX_HANDLE}[absent]
            with self.subTest(label), self.assertRaisesRegex(backend.DetectionError, "not among the matched"):
                backend.detect(environ, explicit(f"{absent}@{handle}"))

    def test_explicit_naming_a_backend_absent_from_a_single_match_fails_closed(self) -> None:
        with self.assertRaisesRegex(backend.DetectionError, "not among the matched"):
            backend.detect(HERDR, explicit("hc@t7"))


class OwnHandleTest(unittest.TestCase):
    """N1: the flag carries the caller's own handle, so a value from another seat fails closed."""

    def test_explicit_with_the_environments_own_handle_returns_the_backend(self) -> None:
        self.assertEqual(backend.detect(HERDR, explicit("herdr@w1:p1")), "herdr")

    def test_explicit_from_another_seat_fails_closed_even_when_the_backend_matches(self) -> None:
        for environ in (HERDR, {**HERDR, **HC}):
            with self.subTest(environ=sorted(environ)), self.assertRaisesRegex(backend.DetectionError, "own handle"):
                backend.detect(environ, explicit("herdr@w1:p9"))

    def test_hc_in_herdr_is_answered_only_by_the_seat_that_owns_the_handle(self) -> None:
        supervisor = {**HC, "HERDR_ENV": "1", "HERDR_PANE_ID": "w1:p7"}
        lead = {**HC, "HERDR_ENV": "1", "HERDR_PANE_ID": "w1:p2"}
        answer = explicit("herdr@w1:p7")
        self.assertEqual(backend.detect(supervisor, answer), "herdr")
        with self.assertRaisesRegex(backend.DetectionError, "own handle"):
            backend.detect(lead, answer)

    def test_rex_own_handle_joins_session_and_block(self) -> None:
        environ = {**REX, **HERDR}
        self.assertEqual(backend.own_handle("rex", environ), REX_HANDLE)
        self.assertEqual(backend.detect(environ, explicit(f"rex@{REX_HANDLE}")), "rex")
        with self.assertRaisesRegex(backend.DetectionError, "own handle"):
            backend.detect(environ, explicit("rex@session:s1.block:other"))

    def test_own_handle_per_backend(self) -> None:
        self.assertEqual(backend.own_handle("herdr", HERDR), "w1:p1")
        self.assertEqual(backend.own_handle("hc", HC), "t7")
        self.assertIsNone(backend.own_handle("herdr", {}))
        self.assertIsNone(backend.own_handle("rex", {"REX_BLOCK": "block:b1"}))
        with self.assertRaises(ValueError):
            backend.own_handle("tmux", {})

    def test_error_text_never_carries_environment_values(self) -> None:
        environ = {**HERDR, **HC, "SECRET_TOKEN": "s3cr3t-value"}
        for call in (lambda: backend.detect(environ), lambda: backend.detect(environ, explicit("herdr@w1:p9"))):
            with self.assertRaises(backend.DetectionError) as caught:
                call()
            for value in ("w1:p1", "/run/hc.sock", "s3cr3t-value", "t7"):
                self.assertNotIn(value, str(caught.exception))


class RelaunchTest(unittest.TestCase):
    """A relaunched seat is a fresh session: the recorded line is compared, never trusted."""

    def test_recorded_handle_equal_to_the_new_own_handle_is_reused(self) -> None:
        self.assertEqual(backend.detect({**HERDR, **HC}, explicit("herdr@w1:p1")), "herdr")

    def test_recorded_handle_that_differs_from_the_new_own_handle_is_rejected(self) -> None:
        relaunched = {**HERDR, "HERDR_PANE_ID": "w1:p4", **HC}
        with self.assertRaisesRegex(backend.DetectionError, "own handle"):
            backend.detect(relaunched, explicit("herdr@w1:p1"))

    def test_a_recorded_backend_no_longer_matching_is_rejected(self) -> None:
        with self.assertRaisesRegex(backend.DetectionError, "not among the matched"):
            backend.detect(HC, explicit("herdr@w1:p1"))

    def test_record_file_feeds_detect(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            record = Path(directory) / "lead-seat"
            record.write_text("herdr w1:p1\n", encoding="utf-8")
            recorded = backend.read_seat_record(record)
            self.assertEqual(backend.detect({**HERDR, **HC}, recorded), "herdr")
            with self.assertRaises(backend.DetectionError):
                backend.detect({**HERDR, **HC, "HERDR_PANE_ID": "w1:p4"}, recorded)


class ParseAndRecordTest(unittest.TestCase):
    def test_parse_explicit(self) -> None:
        self.assertEqual(backend.parse_explicit(f"rex@{REX_HANDLE}"), ("rex", REX_HANDLE))
        for bad in ("herdr", "herdr@", "@w1:p1", "tmux@w1:p1", "herdr@w1 p1", "herdr@w1:p1@x", "herdr@-bad"):
            with self.subTest(bad), self.assertRaises(ValueError):
                backend.parse_explicit(bad)

    def test_a_record_is_one_backend_handle_line(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "supervisor-seat"
            path.write_text(f"rex {REX_HANDLE}\n", encoding="utf-8")
            self.assertEqual(backend.read_seat_record(path), ("rex", REX_HANDLE))

    def test_bad_records_are_refused(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "lead-seat"
            for text in ("", "herdr\n", "herdr w1:p1 extra\n", "herdr w1:p1\nherdr w1:p2\n", "tmux w1:p1\n", "herdr  w1:p1\n"):
                path.write_text(text, encoding="utf-8")
                with self.subTest(text), self.assertRaises(ValueError):
                    backend.read_seat_record(path)
            with self.assertRaises(OSError):
                backend.read_seat_record(Path(directory) / "missing")


class SeatErrorTest(unittest.TestCase):
    def test_a_seat_error_takes_only_a_defined_kind_and_carries_it_as_its_code(self) -> None:
        self.assertIn("not_started", backend.SEAT_ERROR_KINDS)
        for kind in backend.SEAT_ERROR_KINDS:
            with self.subTest(kind):
                self.assertEqual(backend.SeatError(kind, "x").code, kind)
        with self.assertRaises(ValueError):
            backend.SeatError("stuck", "x")


class OpenAndCliTest(unittest.TestCase):
    def test_add_backend_option_parses_name_at_handle(self) -> None:
        parser = argparse.ArgumentParser()
        backend.add_backend_option(parser)
        self.assertIsNone(parser.parse_args([]).backend)
        self.assertEqual(parser.parse_args(["--backend", "herdr@w1:p1"]).backend, ("herdr", "w1:p1"))
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parser.parse_args(["--backend", "nonsense"])

    def test_flag_reaches_detect_as_explicit(self) -> None:
        parser = argparse.ArgumentParser()
        backend.add_backend_option(parser)
        with mock.patch.dict(backend.ADAPTERS, {"fake": "fake_backend"}):
            opened = backend.open_backend(FAKE, parser.parse_args(["--backend", "fake@f1:p1"]).backend)
            self.assertIsInstance(opened, FakeBackend)
            self.assertEqual((opened.environ, opened.handle, opened.calls), (FAKE, "f1:p1", [("identify",)]))
            with self.assertRaisesRegex(backend.DetectionError, "own handle"):
                backend.open_backend(FAKE, parser.parse_args(["--backend", "fake@f1:p9"]).backend)

    def test_open_backend_fails_closed_when_identify_fails(self) -> None:
        failures = {
            "an adapter error": (backend.BackendError("boom"), "fake identify failed: boom"),
            "a refused handle": (ValueError("bad id"), "fake identify failed: bad id"),
            "an unavailable tool": (backend.BackendUnavailable("fake is gone"), "fake is gone"),
        }
        for label, (failure, message) in failures.items():
            with self.subTest(label), mock.patch.dict(backend.ADAPTERS, {"fake": "fake_backend"}), \
                    mock.patch.object(FakeBackend, "identify", side_effect=failure):
                with self.assertRaises(backend.BackendUnavailable) as caught:
                    backend.open_backend(FAKE)
                self.assertEqual(str(caught.exception), message)

    def test_open_backend_does_not_identify_when_detection_fails(self) -> None:
        for environ in ({}, {**HC, **HERDR}, {"HC_TERMINAL_ID": "t7"}):
            with self.subTest(environ=sorted(environ)), self.assertRaises(backend.BackendError):
                backend.open_backend(environ)

    def test_whoami_prints_backend_and_own_handle(self) -> None:
        fake = FakeBackend(handle="w1:p1")
        fake.name = "herdr"
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(backend, "open_backend", return_value=fake) as opened, contextlib.redirect_stdout(
            out
        ), contextlib.redirect_stderr(err):
            code = backend.main(["whoami", "--backend", "herdr@w1:p1"], HERDR)
        self.assertEqual((code, out.getvalue(), err.getvalue()), (0, "herdr w1:p1\n", ""))
        with tempfile.TemporaryDirectory() as directory:  # `whoami > <path>` writes a readable record
            record = Path(directory) / "lead-seat"
            record.write_text(out.getvalue(), encoding="utf-8")
            self.assertEqual(backend.read_seat_record(record), ("herdr", "w1:p1"))
        opened.assert_called_once_with(HERDR, ("herdr", "w1:p1"))

    def test_whoami_fails_closed_on_ambiguity_without_printing_the_environment(self) -> None:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = backend.main(["whoami"], {**HERDR, **HC})
        self.assertEqual((code, out.getvalue()), (1, ""))
        self.assertIn("more than one backend matches", err.getvalue())
        self.assertNotIn("w1:p1", err.getvalue())


if __name__ == "__main__":
    unittest.main()

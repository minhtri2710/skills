"""Focused tests for the optional TypeSafe/Jev triage helper."""
from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock
import urllib.error

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import jev  # noqa: E402


FINDING = {
    "severity": "high",
    "project": "beo-skills",
    "anti_pattern": "gate bypass",
    "lens": "authority",
    "observation": "A watcher proposed moving a Human-owned gate.",
    "evidence": "watcher report: gate ownership was unclear",
    "impact": "could hide an approval boundary",
    "recommendation": "retain the finding for Lead review",
    "escalation": "Human-owned gate remains unchanged",
}


class Response:
    def __init__(self, payload: object, status: int = 200) -> None:
        self.status = status
        self._body = io.BytesIO(json.dumps(payload).encode("utf-8"))

    def __enter__(self) -> "Response":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self, *args: object) -> bytes:
        return self._body.read(*args)


class JevTest(unittest.TestCase):
    def setUp(self) -> None:
        self.env = mock.patch.dict(jev.os.environ, {"TYPESAFE_API_KEY": "test-key"}, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)

    def assert_unavailable(self, result: jev.JevResult, reason: str) -> None:
        self.assertIsInstance(result, jev.UnavailableResult)
        self.assertEqual(result.status, "unavailable")
        self.assertEqual(result.reason, reason)
        self.assertTrue(result.fallback_actionable)
        self.assertEqual(result.finding, FINDING)

    def test_missing_and_empty_api_key_are_unavailable_without_http(self) -> None:
        for value in (None, "", "   "):
            with self.subTest(value=value):
                patcher = mock.patch.dict(jev.os.environ, {}, clear=True)
                if value is not None:
                    patcher = mock.patch.dict(
                        jev.os.environ, {"TYPESAFE_API_KEY": value}, clear=True
                    )
                with patcher, mock.patch.object(jev.urllib.request, "urlopen") as urlopen:
                    result = jev.triage_finding(FINDING)
                self.assert_unavailable(result, "missing_api_key")
                urlopen.assert_not_called()

    def test_network_timeout_and_http_failures_fail_open(self) -> None:
        failures = (
            (urllib.error.URLError("offline"), "network_error"),
            (TimeoutError("slow"), "network_error"),
            (
                urllib.error.HTTPError(
                    jev.API_URL, 503, "unavailable", {}, io.BytesIO(b"secret")
                ),
                "http_error",
            ),
        )
        for failure, reason in failures:
            with self.subTest(reason=reason):
                with mock.patch.object(jev.urllib.request, "urlopen", side_effect=failure):
                    result = jev.triage_finding(FINDING)
                self.assert_unavailable(result, reason)
                self.assertNotIn("offline", result.reason)
                self.assertNotIn("secret", result.reason)

    def test_malformed_json_is_unavailable(self) -> None:
        response = mock.Mock()
        response.status = 200
        response.__enter__ = mock.Mock(return_value=response)
        response.__exit__ = mock.Mock(return_value=None)
        response.read.return_value = b"{not-json"
        with mock.patch.object(jev.urllib.request, "urlopen", return_value=response):
            result = jev.triage_finding(FINDING)
        self.assert_unavailable(result, "malformed_json")

    def test_unusable_answers_are_unavailable(self) -> None:
        responses = (
            {},
            {"answers": {}},
            {
                "answers": {
                    "noul": {"type": "choice", "noul": 0.5},
                    "score": {"type": "score", "score": 1.0},
                }
            },
            {
                "answers": {
                    "noul": {"type": "noul", "noul": 0.5},
                    "score": {"type": "choice", "score": 1.0},
                }
            },
            {
                "answers": {
                    "noul": {"type": "noul", "noul": 0.5},
                    "score": {"type": "score", "score": 2.1},
                }
            },
            {
                "answers": {
                    "noul": {"type": "noul", "noul": 1.1},
                    "score": {"type": "score", "score": 1.0},
                }
            },
            {
                "answers": {
                    "noul": {"type": "noul", "noul": float("nan")},
                    "score": {"type": "score", "score": 1.0},
                }
            },
            {
                "answers": {
                    "noul": {"type": "noul", "noul": 0.5},
                    "score": {"type": "score", "score": 10**1_000},
                }
            },
            {
                "answers": {
                    "noul": {"type": "noul", "noul": 0.5},
                    "score": {"type": "score", "score": 1.0, "rationale": {"unexpected": True}},
                }
            },
        )
        for payload in responses:
            with self.subTest(payload=payload):
                with mock.patch.object(
                    jev.urllib.request, "urlopen", return_value=Response(payload)
                ):
                    result = jev.triage_finding(FINDING)
                self.assert_unavailable(result, "invalid_answers")

    def test_valid_typed_answers_retain_finding_and_bounded_raw_data(self) -> None:
        payload = {
            "answers": {
                "noul": {
                    "type": "noul",
                    "noul": 0.8,
                    "rationale": "The observation identifies a real ownership misfit.",
                    "evidence": ["gate row", "watcher report"],
                },
                "score": {
                    "type": "score",
                    "score": 1.6,
                    "rationale": ["High impact", "requires attention"],
                    "evidence": "The recommendation preserves the gate.",
                },
                "ignored": {"free_form": "not parsed into a judgment"},
            }
        }
        with mock.patch.object(
            jev.urllib.request, "urlopen", return_value=Response(payload)
        ) as urlopen:
            result = jev.triage_finding(FINDING)

        self.assertIsInstance(result, jev.AdvisoryResult)
        self.assertEqual(result.status, "available")
        self.assertTrue(result.available)
        self.assertEqual(result.finding, FINDING)
        self.assertIsNot(result.finding, FINDING)
        self.assertEqual(result.noul.value, "actionable")
        self.assertEqual(result.noul.probability, 0.8)
        self.assertTrue(result.noul.actionable)
        self.assertEqual(result.score.value, 0.8)
        self.assertEqual(result.score.severity, "high")
        self.assertFalse(result.score.noise)
        self.assertEqual(
            result.rationale,
            ("The observation identifies a real ownership misfit.", "High impact", "requires attention"),
        )
        self.assertEqual(
            result.evidence,
            ("gate row", "watcher report", "The recommendation preserves the gate."),
        )
        self.assertEqual(result.raw_answers, payload["answers"])
        self.assertIsNot(result.raw_answers, payload["answers"])

        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, jev.API_URL)
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")
        body = json.loads(request.data)
        self.assertEqual(json.loads(body["state"]), FINDING)
        self.assertEqual(body["model"], "jev-latest")
        self.assertEqual(body["questions"]["noul"]["type"], "noul")
        self.assertEqual(body["questions"]["noul"]["criteria"].keys(), {"true", "false"})
        self.assertEqual(body["questions"]["score"]["type"], "score")
        self.assertEqual(len(body["questions"]["score"]["criteria"]), 3)

    def test_documented_typed_answers_without_optional_prose_are_accepted(self) -> None:
        payload = {
            "answers": {
                "noul": {"type": "noul", "noul": 0.2},
                "score": {"type": "score", "score": 2.0},
            }
        }
        with mock.patch.object(
            jev.urllib.request, "urlopen", return_value=Response(payload)
        ):
            result = jev.triage_finding(FINDING)

        self.assertIsInstance(result, jev.AdvisoryResult)
        self.assertEqual(result.noul.value, "noise")
        self.assertEqual(result.noul.probability, 0.2)
        self.assertEqual(result.rationale, ())
        self.assertEqual(result.evidence, ())
        self.assertEqual(result.score.value, 1.0)
        self.assertEqual(result.score.severity, "high")
        self.assertEqual(result.raw_answers, payload["answers"])

    def test_unavailable_result_is_a_fail_open_pass_through(self) -> None:
        with mock.patch.object(
            jev.urllib.request, "urlopen", side_effect=urllib.error.URLError("offline")
        ):
            result = jev.triage_finding(FINDING)

        self.assertIsInstance(result, jev.UnavailableResult)
        self.assertTrue(result.fallback_actionable)
        self.assertEqual(result.finding["recommendation"], FINDING["recommendation"])
        self.assertEqual(result.finding["escalation"], FINDING["escalation"])


if __name__ == "__main__":
    unittest.main()

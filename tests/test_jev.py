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
HEADER = (
    "## lead-beo-skills -> supervisor | 2026-09-19T12:34:56Z | "
    "ATTENTION beo-skills staffing: reviewer needs assignment | HEAD "
    "08642aa02d8ff65f7c84b70ed2e21d480edc1"
)
FORK = {
    "hard_gate": False,
    "question": "Which reversible implementation should remain in scope?",
    "options": ["keep-current", "use-alternative"],
}
DELEGATION = {
    "in_force": True,
    "who": "supervisor",
    "scope": "bounded reversible fork",
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

    def test_header_scores_normalize_to_ordered_urgency_levels(self) -> None:
        for raw_score, expected_value, expected_urgency in (
            (0, 0.0, "FYI"),
            (1, 0.5, "supervisor-action"),
            (2, 1.0, "human-gate"),
        ):
            payload = {
                "answers": {
                    "score": {
                        "type": "score",
                        "score": raw_score,
                        "rationale": "bounded explanation",
                        "evidence": ["header fact"],
                        "ignored": "retained but not interpreted",
                    }
                }
            }
            with self.subTest(raw_score=raw_score), mock.patch.object(
                jev.urllib.request, "urlopen", return_value=Response(payload)
            ) as urlopen:
                result = jev.triage_header(HEADER)

            self.assertIsInstance(result, jev.HeaderAdvisoryResult)
            self.assertEqual(result.header, HEADER)
            self.assertEqual(result.source_state["header"], HEADER)
            self.assertEqual(result.source_state["sender"], "lead-beo-skills")
            self.assertEqual(result.source_state["recipient"], "supervisor")
            self.assertEqual(result.source_state["timestamp"], "2026-09-19T12:34:56Z")
            self.assertEqual(
                result.source_state["event"],
                "ATTENTION beo-skills staffing: reviewer needs assignment",
            )
            self.assertEqual(result.source_state["head"], "08642aa02d8ff65f7c84b70ed2e21d480edc1")
            self.assertNotIn("body", result.source_state)
            self.assertNotIn("anti_pattern", result.source_state)
            self.assertNotIn("impact", result.source_state)
            self.assertNotIn("urgency", result.source_state)
            self.assertEqual(result.score.raw_value, raw_score)
            self.assertEqual(result.score.value, expected_value)
            self.assertEqual(result.score.urgency, expected_urgency)
            self.assertEqual(result.raw_answers, payload["answers"])
            self.assertEqual(result.raw_answers["score"]["ignored"], "retained but not interpreted")
            self.assertEqual(result.raw_answers["score"]["rationale"], "bounded explanation")
            self.assertEqual(result.raw_answers["score"]["evidence"], ["header fact"])

            request_body = json.loads(urlopen.call_args.args[0].data)
            state = json.loads(request_body["state"])
            self.assertEqual(state["header"], HEADER)
            self.assertEqual(request_body["questions"], jev.HEADER_QUESTIONS)
            self.assertEqual(request_body["questions"]["score"]["type"], "score")
            self.assertEqual(len(request_body["questions"]["score"]["criteria"]), 3)

    def test_header_unavailable_retains_header_state_without_raising(self) -> None:
        for key, failure, reason in (
            ("", None, "missing_api_key"),
            ("test-key", urllib.error.URLError("offline"), "network_error"),
        ):
            with self.subTest(reason=reason):
                patch_key = mock.patch.dict(jev.os.environ, {"TYPESAFE_API_KEY": key}, clear=True)
                patch_http = mock.patch.object(
                    jev.urllib.request, "urlopen", side_effect=failure
                )
                with patch_key, patch_http:
                    result = jev.triage_header(HEADER)

                self.assertIsInstance(result, jev.UnavailableResult)
                self.assertEqual(result.status, "unavailable")
                self.assertEqual(result.reason, reason)
                self.assertTrue(result.fallback_actionable)
                self.assertEqual(
                    result.finding,
                    {
                        "header": HEADER,
                        "sender": "lead-beo-skills",
                        "recipient": "supervisor",
                        "timestamp": "2026-09-19T12:34:56Z",
                        "event": "ATTENTION beo-skills staffing: reviewer needs assignment",
                        "head": "08642aa02d8ff65f7c84b70ed2e21d480edc1",
                    },
                )

    def test_fractional_and_minute_header_timestamps_are_not_objective_timestamps(self) -> None:
        for timestamp in ("2026-09-19T12:34:56.500Z", "2026-09-19T12:34Z"):
            with self.subTest(timestamp=timestamp):
                state = jev._header_state(
                    f"## lead-beo-skills -> supervisor | {timestamp} | event"
                )
                self.assertNotIn("timestamp", state)

    def test_header_malformed_score_or_prose_is_unavailable(self) -> None:
        responses = (
            {"answers": {"score": {"type": "choice", "score": 1}}},
            {"answers": {"score": {"type": "score", "score": -1}}},
            {"answers": {"score": {"type": "score", "score": 3}}},
            {"answers": {"score": {"type": "score", "score": float("nan")}}},
            {
                "answers": {
                    "score": {
                        "type": "score",
                        "score": 1,
                        "rationale": {"unexpected": True},
                    }
                }
            },
        )
        for payload in responses:
            with self.subTest(payload=payload), mock.patch.object(
                jev.urllib.request, "urlopen", return_value=Response(payload)
            ):
                result = jev.triage_header(HEADER)
            self.assertIsInstance(result, jev.UnavailableResult)
            self.assertEqual(result.status, "unavailable")
            self.assertEqual(result.reason, "invalid_answers")
            self.assertTrue(result.fallback_actionable)
            self.assertEqual(result.finding["header"], HEADER)

    def test_header_state_keeps_unrecognized_header_objective_text_only(self) -> None:
        malformed = "not a recognized mailbox header with no body"
        with mock.patch.object(jev.urllib.request, "urlopen", return_value=Response(
            {"answers": {"score": {"type": "score", "score": 0}}}
        )) as urlopen:
            result = jev.triage_header(malformed)

        self.assertIsInstance(result, jev.HeaderAdvisoryResult)
        self.assertEqual(result.source_state, {"header": malformed})
        self.assertNotIn("body", json.loads(json.loads(urlopen.call_args.args[0].data)["state"]))

    def test_charter_coherence_thresholds_and_request_contract(self) -> None:
        body = "Disposition body with bounded responsibilities and authority."
        for score, expected in ((0.0, "incoherent"), (0.5, "coherent"), (1.0, "coherent")):
            payload = {
                "answers": {
                    "noul": {
                        "type": "noul",
                        "noul": score,
                        "rationale": "bounded rationale",
                        "evidence": ["bounded evidence"],
                    }
                }
            }
            with self.subTest(score=score), mock.patch.object(
                jev.urllib.request, "urlopen", return_value=Response(payload)
            ) as urlopen:
                result = jev.triage_charter("Engineer", body)

            self.assertIsInstance(result, jev.CharterAdvisoryResult)
            self.assertEqual(result.coherence.value, expected)
            self.assertEqual(result.coherence.probability, score)
            self.assertEqual(result.source_state, {"disposition": "Engineer", "body": body})
            request_body = json.loads(urlopen.call_args.args[0].data)
            self.assertEqual(json.loads(request_body["state"]), result.source_state)
            self.assertEqual(request_body["questions"], jev.CHARTER_QUESTIONS)
            self.assertEqual(set(request_body["questions"]), {"noul"})
            self.assertEqual(request_body["questions"]["noul"]["type"], "noul")
            self.assertIn("responsibilities", request_body["questions"]["noul"]["instructions"])
            self.assertIn("authority", request_body["questions"]["noul"]["instructions"])
            self.assertIn("prohibitions", request_body["questions"]["noul"]["instructions"])
            self.assertNotIn("test-key", urlopen.call_args.args[0].data.decode("utf-8"))

    def test_charter_body_is_bounded_and_secret_safe(self) -> None:
        secret = "test-key"
        body = "prefix " + secret + " " + ("x" * jev.MAX_CHARTER_BODY_CHARS) + " suffix"
        payload = {
            "answers": {
                "noul": {
                    "type": "noul",
                    "noul": 0.8,
                    "rationale": f"answer mentions {secret}",
                    "evidence": [f"evidence mentions {secret}"],
                },
                "ignored": f"ignored {secret}",
            }
        }
        with mock.patch.object(
            jev.urllib.request, "urlopen", return_value=Response(payload)
        ) as urlopen:
            result = jev.triage_charter("Reviewer", body)

        self.assertIsInstance(result, jev.CharterAdvisoryResult)
        self.assertNotIn(secret, repr(result))
        self.assertEqual(len(result.source_state["body"]), jev.MAX_CHARTER_BODY_CHARS)
        self.assertNotIn(secret, urlopen.call_args.args[0].data.decode("utf-8"))
        self.assertNotIn(secret, json.dumps(result.raw_answers))
        self.assertNotIn(secret, " ".join(result.rationale + result.evidence))

    def test_charter_missing_key_invalid_input_and_invalid_answers_fail_open(self) -> None:
        with mock.patch.dict(jev.os.environ, {}, clear=True), mock.patch.object(
            jev.urllib.request, "urlopen"
        ) as urlopen:
            result = jev.triage_charter("Engineer", "body")
            invalid_disposition = jev.triage_charter("Builder", "body")
            invalid_body = jev.triage_charter("Engineer", None)

        self.assertIsInstance(result, jev.UnavailableResult)
        self.assertEqual(result.reason, "missing_api_key")
        self.assertIsInstance(invalid_disposition, jev.UnavailableResult)
        self.assertEqual(invalid_disposition.reason, "invalid_charter")
        self.assertIsInstance(invalid_body, jev.UnavailableResult)
        self.assertEqual(invalid_body.reason, "invalid_charter")
        urlopen.assert_not_called()

        invalid_answers = (
            {"answers": {}},
            {"answers": {"noul": {"type": "choice", "noul": 0.5}}},
            {"answers": {"noul": {"type": "noul", "noul": "0.5"}}},
            {"answers": {"noul": {"type": "noul", "noul": True}}},
            {"answers": {"noul": {"type": "noul", "noul": -0.1}}},
            {"answers": {"noul": {"type": "noul", "noul": 1.1}}},
            {"answers": {"noul": {"type": "noul", "noul": float("nan")}}},
            {"answers": {"noul": {"type": "noul", "noul": 0.5, "rationale": {}}}},
        )
        for payload in invalid_answers:
            with self.subTest(payload=payload), mock.patch.object(
                jev.urllib.request, "urlopen", return_value=Response(payload)
            ):
                result = jev.triage_charter("Architect", "body")
            self.assertIsInstance(result, jev.UnavailableResult)
            self.assertEqual(result.reason, "invalid_answers")
            self.assertNotIn("test-key", repr(result))

    def test_charter_transport_and_malformed_json_fail_open(self) -> None:
        failures = (
            (urllib.error.URLError("charter-secret"), "network_error"),
            (TimeoutError("charter-secret"), "network_error"),
            (
                urllib.error.HTTPError(
                    jev.API_URL, 503, "unavailable", {}, io.BytesIO(b"charter-secret")
                ),
                "http_error",
            ),
        )
        for failure, reason in failures:
            with self.subTest(reason=reason), mock.patch.object(
                jev.urllib.request, "urlopen", side_effect=failure
            ):
                result = jev.triage_charter("Engineer", "body")
            self.assertIsInstance(result, jev.UnavailableResult)
            self.assertEqual(result.reason, reason)
            self.assertNotIn("charter-secret", repr(result))

        response = mock.Mock()
        response.status = 200
        response.__enter__ = mock.Mock(return_value=response)
        response.__exit__ = mock.Mock(return_value=None)
        response.read.return_value = b"{not-json"
        with mock.patch.object(jev.urllib.request, "urlopen", return_value=response):
            result = jev.triage_charter("Engineer", "body")
        self.assertIsInstance(result, jev.UnavailableResult)
        self.assertEqual(result.reason, "malformed_json")

    def test_fork_hard_gate_and_missing_delegation_are_deterministic_human_gate(self):
        for fork, delegation in (
            ({**FORK, "hard_gate": True}, DELEGATION),
            (FORK, None),
            (FORK, {}),
            (FORK, {"in_force": False}),
        ):
            with self.subTest(delegation=delegation), mock.patch.object(
                jev, "_request_answers"
            ) as request_answers:
                result = jev.route_fork(fork, delegation)

            self.assertIsInstance(result, jev.ForkAdvisoryResult)
            self.assertEqual(result.route, "human_gate")
            self.assertEqual(result.choice, "human_gate")
            self.assertTrue(result.deterministic)
            self.assertEqual(result.probabilities, {
                "supervisor_decide": 0.0,
                "human_gate": 1.0,
            })
            self.assertEqual(result.source_state["fork"], fork)
            self.assertEqual(result.source_state["delegation"], delegation)
            request_answers.assert_not_called()

    def test_fork_missing_key_stays_unavailable_even_when_deterministic(self):
        with mock.patch.dict(jev.os.environ, {}, clear=True), mock.patch.object(
            jev.urllib.request, "urlopen"
        ) as urlopen:
            result = jev.route_fork({**FORK, "hard_gate": True}, DELEGATION)

        self.assertIsInstance(result, jev.UnavailableResult)
        self.assertEqual(result.reason, "missing_api_key")
        self.assertEqual(result.finding["fork"], {**FORK, "hard_gate": True})
        urlopen.assert_not_called()

    def test_fork_choice_request_and_available_result_retain_objective_state(self):
        payload = {
            "answers": {
                "route": {
                    "type": "choice",
                    "choice": "supervisor_decide",
                    "probabilities": {
                        "supervisor_decide": 0.8,
                        "human_gate": 0.2,
                    },
                    "confidence": 0.75,
                    "ignored": "untrusted answer text",
                }
            }
        }
        with mock.patch.object(
            jev.urllib.request, "urlopen", return_value=Response(payload)
        ) as urlopen:
            result = jev.route_fork(FORK, DELEGATION)

        self.assertIsInstance(result, jev.ForkAdvisoryResult)
        self.assertEqual(result.route, "supervisor_decide")
        self.assertEqual(result.choice, "supervisor_decide")
        self.assertFalse(result.deterministic)
        self.assertEqual(result.probabilities, {
            "supervisor_decide": 0.8,
            "human_gate": 0.2,
        })
        self.assertEqual(result.confidence, 0.75)
        self.assertEqual(result.source_state, {"fork": FORK, "delegation": DELEGATION})
        self.assertEqual(result.raw_answers, payload["answers"])
        self.assertIsNot(result.raw_answers, payload["answers"])

        request = urlopen.call_args.args[0]
        body = json.loads(request.data)
        self.assertEqual(json.loads(body["state"]), result.source_state)
        self.assertEqual(body["model"], "jev-latest")
        self.assertEqual(set(body["questions"]), {"route"})
        question = body["questions"]["route"]
        self.assertEqual(question["type"], "choice")
        self.assertEqual(set(question["criteria"]), {
            "supervisor_decide",
            "human_gate",
        })
        self.assertIn("delegated Supervisor", question["instructions"])
        self.assertIn("Human routing", question["instructions"])
        self.assertNotIn("test-key", request.data.decode("utf-8"))

    def test_fork_model_answer_cannot_override_hard_gate(self):
        payload = {
            "answers": {
                "route": {
                    "type": "choice",
                    "choice": "supervisor_decide",
                    "probabilities": {
                        "supervisor_decide": 1.0,
                        "human_gate": 0.0,
                    },
                    "confidence": 1.0,
                }
            }
        }
        with mock.patch.object(jev, "_request_answers", return_value=(payload, None)) as request_answers:
            result = jev.route_fork({**FORK, "hard_gate": True}, DELEGATION)

        self.assertIsInstance(result, jev.ForkAdvisoryResult)
        self.assertEqual(result.route, "human_gate")
        self.assertTrue(result.deterministic)
        request_answers.assert_not_called()

    def test_fork_invalid_input_and_optional_data_fail_open(self):
        cases = (
            (None, None, "invalid_fork"),
            ({}, None, "invalid_fork"),
            ({"hard_gate": 1}, None, "invalid_fork"),
            (FORK, [], "invalid_delegation"),
            (FORK, {"in_force": "yes"}, "invalid_delegation"),
            (FORK, {"in_force": True, "bad": float("nan")}, "invalid_delegation"),
        )
        with mock.patch.object(jev.urllib.request, "urlopen") as urlopen:
            for fork, delegation, reason in cases:
                with self.subTest(fork=fork, delegation=delegation):
                    result = jev.route_fork(fork, delegation)
                    self.assertIsInstance(result, jev.UnavailableResult)
                    self.assertEqual(result.reason, reason)
        urlopen.assert_not_called()

    def test_fork_invalid_choice_answers_fail_open_without_exception_or_secret(self):
        answers = (
            {"answers": []},
            {"answers": {"route": {"type": "score"}}},
            {"answers": {"route": {
                "type": "choice",
                "choice": "unknown",
                "probabilities": {"supervisor_decide": 0.5, "human_gate": 0.5},
                "confidence": 0.5,
            }}},
            {"answers": {"route": {
                "type": "choice",
                "choice": "human_gate",
                "probabilities": {"supervisor_decide": 0.5},
                "confidence": 0.5,
            }}},
            {"answers": {"route": {
                "type": "choice",
                "choice": "human_gate",
                "probabilities": {
                    "supervisor_decide": 0.5,
                    "human_gate": 0.5,
                    "extra": 0.0,
                },
                "confidence": 0.5,
            }}},
            {"answers": {"route": {
                "type": "choice",
                "choice": "human_gate",
                "probabilities": {"supervisor_decide": float("inf"), "human_gate": 0.0},
                "confidence": 0.5,
            }}},
            {"answers": {"route": {
                "type": "choice",
                "choice": "human_gate",
                "probabilities": {"supervisor_decide": 0.5, "human_gate": -0.1},
                "confidence": 0.5,
            }}},
            {"answers": {"route": {
                "type": "choice",
                "choice": "human_gate",
                "probabilities": {"supervisor_decide": 0.5, "human_gate": 0.5},
                "confidence": float("nan"),
            }}},
            {"answers": {"route": {
                "type": "choice",
                "choice": "human_gate",
                "probabilities": {"supervisor_decide": 0.5, "human_gate": 0.5},
            }}},
        )
        for payload in answers:
            with self.subTest(payload=payload), mock.patch.object(
                jev.urllib.request, "urlopen", return_value=Response(payload)
            ):
                result = jev.route_fork(FORK, DELEGATION)
            self.assertIsInstance(result, jev.UnavailableResult)
            self.assertEqual(result.reason, "invalid_answers")
            self.assertNotIn("test-key", repr(result))

    def test_fork_transport_and_malformed_json_fail_open(self):
        failures = (
            (urllib.error.URLError("fork-secret"), "network_error"),
            (TimeoutError("fork-secret"), "network_error"),
            (urllib.error.HTTPError(
                jev.API_URL, 503, "unavailable", {}, io.BytesIO(b"fork-secret")
            ), "http_error"),
        )
        for failure, reason in failures:
            with self.subTest(reason=reason), mock.patch.object(
                jev.urllib.request, "urlopen", side_effect=failure
            ):
                result = jev.route_fork(FORK, DELEGATION)
            self.assertIsInstance(result, jev.UnavailableResult)
            self.assertEqual(result.reason, reason)
            self.assertNotIn("fork-secret", repr(result))

        response = mock.Mock()
        response.status = 200
        response.__enter__ = mock.Mock(return_value=response)
        response.__exit__ = mock.Mock(return_value=None)
        response.read.return_value = b"{not-json"
        with mock.patch.object(jev.urllib.request, "urlopen", return_value=response):
            result = jev.route_fork(FORK, DELEGATION)
        self.assertIsInstance(result, jev.UnavailableResult)
        self.assertEqual(result.reason, "malformed_json")


if __name__ == "__main__":
    unittest.main()

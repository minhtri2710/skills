"""Focused tests for the optional TypeSafe/Jev triage helper."""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import urllib.error

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "jev" / "scripts"
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


def score_answer(probabilities: tuple[float, ...], confidence: float) -> dict[str, object]:
    return {
        "type": "score",
        "score": sum(index * p for index, p in enumerate(probabilities)),
        "legend": {str(index): f"level {index}" for index in range(len(probabilities))},
        "probabilities": {str(index): p for index, p in enumerate(probabilities)},
        "confidence": confidence,
    }


def finding_answers(
    actionable: float = 0.9,
    cites: float = 0.85,
    severity: tuple[float, ...] = (0.1, 0.2, 0.7),
    confidence: float = 0.6,
) -> dict[str, object]:
    return {
        "actionable_misfit": {"type": "noul", "noul": actionable},
        "cites_artifact": {"type": "noul", "noul": cites},
        "severity": score_answer(severity, confidence),
    }


def fork_answer(choice: str, confidence: float) -> dict[str, object]:
    return {
        "answers": {
            "route": {
                "type": "choice",
                "choice": choice,
                "probabilities": {"supervisor_decide": 0.7, "human_gate": 0.3},
                "confidence": confidence,
            }
        }
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
                with mock.patch.object(jev.urllib.request, "urlopen", side_effect=failure) as urlopen:
                    result = jev.triage_finding(FINDING)
                self.assert_unavailable(result, reason)
                self.assertEqual(json.loads(urlopen.call_args.args[0].data)["state"], FINDING)
                self.assertNotIn("offline", result.reason)
                self.assertNotIn("secret", result.reason)

    def test_malformed_json_is_unavailable(self) -> None:
        response = mock.Mock()
        response.status = 200
        response.__enter__ = mock.Mock(return_value=response)
        response.__exit__ = mock.Mock(return_value=None)
        response.read.return_value = b"{not-json"
        with mock.patch.object(jev.urllib.request, "urlopen", return_value=response) as urlopen:
            result = jev.triage_finding(FINDING)
        self.assert_unavailable(result, "malformed_json")
        self.assertEqual(json.loads(urlopen.call_args.args[0].data)["state"], FINDING)

    def test_unusable_answers_are_unavailable(self) -> None:
        valid = finding_answers()
        responses = (
            {},
            {"answers": {}},
            {"answers": []},
            {"answers": {**valid, "actionable_misfit": {"type": "choice", "noul": 0.5}}},
            {"answers": {**valid, "cites_artifact": {"type": "noul", "noul": 1.1}}},
            {"answers": {**valid, "actionable_misfit": {"type": "noul", "noul": float("nan")}}},
            {"answers": {**valid, "actionable_misfit": {"type": "noul", "noul": True}}},
            {"answers": {k: v for k, v in valid.items() if k != "cites_artifact"}},
            {"answers": {**valid, "severity": {**valid["severity"], "type": "choice"}}},
            {"answers": {**valid, "severity": {"type": "score", "score": 1.0}}},
        )
        for payload in responses:
            with self.subTest(payload=payload):
                with mock.patch.object(
                    jev.urllib.request, "urlopen", return_value=Response(payload)
                ) as urlopen:
                    result = jev.triage_finding(FINDING)
                self.assert_unavailable(result, "invalid_answers")
                self.assertEqual(json.loads(urlopen.call_args.args[0].data)["state"], FINDING)

    def test_finding_asks_three_one_dimension_questions_in_one_request(self) -> None:
        payload = {"answers": {**finding_answers(), "ignored": {"free_form": "kept raw"}}}
        with mock.patch.object(
            jev.urllib.request, "urlopen", return_value=Response(payload)
        ) as urlopen:
            result = jev.triage_finding(FINDING)

        self.assertIsInstance(result, jev.AdvisoryResult)
        self.assertEqual(result.status, "available")
        self.assertTrue(result.available)
        self.assertEqual(result.actionable_misfit, jev.NoulJudgment("actionable", 0.9))
        self.assertEqual(result.cites_artifact, jev.NoulJudgment("cited", 0.85))
        self.assertEqual(
            result.severity,
            jev.ScoreJudgment(label="high", argmax="high", probability=0.7, confidence=0.6),
        )
        self.assertFalse(hasattr(result, "rationale"))
        self.assertFalse(hasattr(result, "evidence"))

        urlopen.assert_called_once()
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, jev.API_URL)
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")
        body = json.loads(request.data)
        self.assertEqual(body["state"], FINDING)
        self.assertEqual(body["model"], "jev-latest")
        questions = body["questions"]
        self.assertEqual(set(questions), {"actionable_misfit", "cites_artifact", "severity"})
        self.assertEqual(questions["actionable_misfit"]["type"], "noul")
        self.assertEqual(questions["cites_artifact"]["type"], "noul")
        self.assertEqual(questions["severity"]["type"], "score")
        self.assertEqual(len(questions["severity"]["criteria"]), 3)
        self.assertEqual(
            len({question["instructions"] for question in questions.values()}), 3
        )

    def test_noul_bands_are_asymmetric_with_an_uncertain_middle(self) -> None:
        for probability, expected in (
            (0.0, "noise"),
            (0.19, "noise"),
            (0.2, "uncertain"),
            (0.5, "uncertain"),
            (0.79, "uncertain"),
            (0.8, "actionable"),
            (1.0, "actionable"),
        ):
            payload = {"answers": finding_answers(actionable=probability, cites=probability)}
            with self.subTest(probability=probability), mock.patch.object(
                jev.urllib.request, "urlopen", return_value=Response(payload)
            ):
                result = jev.triage_finding(FINDING)
            self.assertIsInstance(result, jev.AdvisoryResult)
            self.assertEqual(result.actionable_misfit.label, expected)
            self.assertEqual(result.actionable_misfit.probability, probability)
            self.assertEqual(
                result.cites_artifact.label,
                {"noise": "uncited", "actionable": "cited"}.get(expected, expected),
            )

    def test_severity_is_labelled_from_probabilities_not_the_mean(self) -> None:
        for probabilities, expected, argmax in (
            ((0.9, 0.1, 0.0), "low", "low"),
            ((0.53, 0.43, 0.04), "medium", "low"),
            ((0.6, 0.19, 0.21), "high", "low"),
            ((0.3, 0.5, 0.2), "high", "medium"),
            ((0.0, 0.0, 1.0), "high", "high"),
        ):
            payload = {"answers": finding_answers(severity=probabilities)}
            with self.subTest(probabilities=probabilities), mock.patch.object(
                jev.urllib.request, "urlopen", return_value=Response(payload)
            ):
                result = jev.triage_finding(FINDING)
            self.assertIsInstance(result, jev.AdvisoryResult)
            self.assertEqual(result.severity.label, expected)
            self.assertEqual(result.severity.argmax, argmax)
            self.assertEqual(
                result.severity.probability,
                probabilities[jev.SEVERITY_LEVELS.index(expected)],
            )

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
            self.assertIsNone(result.choice)
            self.assertTrue(result.deterministic)
            self.assertEqual(result.probabilities, {
                "supervisor_decide": 0.0,
                "human_gate": 1.0,
            })
            request_answers.assert_not_called()

    def test_fork_missing_key_stays_unavailable_when_jev_is_needed(self):
        with mock.patch.dict(jev.os.environ, {}, clear=True), mock.patch.object(
            jev.urllib.request, "urlopen"
        ) as urlopen:
            result = jev.route_fork(FORK, DELEGATION)

        self.assertIsInstance(result, jev.UnavailableResult)
        self.assertEqual(result.reason, "missing_api_key")
        urlopen.assert_not_called()

    def test_fork_deterministic_human_gate_without_api_key(self):
        with mock.patch.dict(jev.os.environ, {}, clear=True), mock.patch.object(
            jev.urllib.request, "urlopen"
        ) as urlopen:
            for fork, delegation in (
                ({**FORK, "hard_gate": True}, DELEGATION),
                (FORK, None),
                (FORK, {}),
                (FORK, {"in_force": False}),
            ):
                with self.subTest(delegation=delegation):
                    result = jev.route_fork(fork, delegation)

                    self.assertIsInstance(result, jev.ForkAdvisoryResult)
                    self.assertEqual(result.route, "human_gate")
                    self.assertIsNone(result.choice)
                    self.assertTrue(result.deterministic)
                    self.assertEqual(result.probabilities, {
                        "supervisor_decide": 0.0,
                        "human_gate": 1.0,
                    })
        urlopen.assert_not_called()

    def test_fork_choice_request_and_available_result_retain_objective_state(self):
        payload = {
            "answers": {
                "route": {
                    "type": "choice",
                    "choice": "supervisor_decide",
                    "probabilities": {
                        "supervisor_decide": 0.95,
                        "human_gate": 0.05,
                    },
                    "confidence": 0.92,
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
            "supervisor_decide": 0.95,
            "human_gate": 0.05,
        })
        self.assertEqual(result.confidence, 0.92)

        request = urlopen.call_args.args[0]
        body = json.loads(request.data)
        self.assertEqual(body["state"], {"fork": FORK, "delegation": DELEGATION})
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

    def test_fork_confidence_floor_only_brakes_and_keeps_jev_choice(self):
        for choice, confidence, expected in (
            ("supervisor_decide", 0.89, "human_gate"),
            ("supervisor_decide", 0.9, "supervisor_decide"),
            ("supervisor_decide", 1.0, "supervisor_decide"),
            ("human_gate", 0.99, "human_gate"),
            ("human_gate", 0.1, "human_gate"),
        ):
            with self.subTest(choice=choice, confidence=confidence), mock.patch.object(
                jev.urllib.request, "urlopen", return_value=Response(fork_answer(choice, confidence))
            ):
                result = jev.route_fork(FORK, DELEGATION)
            self.assertIsInstance(result, jev.ForkAdvisoryResult)
            self.assertEqual(result.route, expected)
            self.assertEqual(result.choice, choice)
            self.assertEqual(result.confidence, confidence)
            self.assertFalse(result.deterministic)

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


CLI_AVAILABLE_PAYLOADS = {
    "finding": {"answers": finding_answers()},
    "fork": fork_answer("supervisor_decide", 0.75),
}

CLI_AVAILABLE_OUTPUTS = {
    "finding": {
        "status": "available",
        "actionable_misfit": {"label": "actionable", "probability": 0.9},
        "cites_artifact": {"label": "cited", "probability": 0.85},
        "severity": {
            "label": "high",
            "argmax": "high",
            "probability": 0.7,
            "confidence": 0.6,
        },
    },
    "fork": {
        "status": "available",
        "route": "human_gate",
        "choice": "supervisor_decide",
        "deterministic": False,
        "confidence": 0.75,
        "probabilities": {"supervisor_decide": 0.7, "human_gate": 0.3},
    },
}

CLI_MODE_INPUTS = {
    "finding": json.dumps(FINDING),
    "fork": json.dumps({"fork": FORK, "delegation": DELEGATION}),
}


class JevCliTest(unittest.TestCase):
    FAKE_KEY = "sk-fake-jev-probe-7f3a9-non-disclosure"

    def setUp(self) -> None:
        self.env = mock.patch.dict(
            jev.os.environ, {"TYPESAFE_API_KEY": self.FAKE_KEY}, clear=True
        )
        self.env.start()
        self.addCleanup(self.env.stop)

    def run_main(
        self, argv: list[str], stdin_text: str | None = None
    ) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            if stdin_text is not None:
                with mock.patch.object(sys, "stdin", io.StringIO(stdin_text)):
                    code = jev.main(argv)
            else:
                code = jev.main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_cli_source_never_gates_on_isatty(self) -> None:
        source = Path(jev.__file__).read_text(encoding="utf-8")
        self.assertNotIn("isatty", source)

    def test_cli_fork_without_key_deterministic_hard_gate_and_unavailable_soft_fork(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            hard = Path(tmp) / "hard.json"
            hard.write_text(
                json.dumps({"fork": {**FORK, "hard_gate": True}, "delegation": DELEGATION}),
                encoding="utf-8",
            )
            soft = Path(tmp) / "soft.json"
            soft.write_text(
                json.dumps({"fork": FORK, "delegation": DELEGATION}), encoding="utf-8"
            )
            for path, expected in (
                (hard, {"status": "available", "route": "human_gate", "deterministic": True}),
                (soft, {"status": "unavailable", "reason": "missing_api_key"}),
            ):
                with self.subTest(input=path.name), mock.patch.dict(
                    jev.os.environ, {}, clear=True
                ), mock.patch.object(jev.urllib.request, "urlopen") as urlopen:
                    code, out, err = self.run_main(["fork", "--file", str(path)])

                self.assertEqual(code, 0)
                output = json.loads(out)
                for key, value in expected.items():
                    self.assertEqual(output[key], value)
                if expected["status"] == "available":
                    self.assertTrue(output["deterministic"])
                    self.assertIsNone(output["choice"])
                    self.assertEqual(
                        output["probabilities"],
                        {"supervisor_decide": 0.0, "human_gate": 1.0},
                    )
        urlopen.assert_not_called()

    def test_cli_finding_without_key_is_unavailable_with_exit_zero(self) -> None:
        with mock.patch.dict(jev.os.environ, {}, clear=True), mock.patch.object(
            jev.urllib.request, "urlopen"
        ) as urlopen:
            code, out, err = self.run_main(["finding", "--stdin"], json.dumps(FINDING))

        self.assertEqual(code, 0)
        self.assertEqual(err, "")
        self.assertEqual(
            json.loads(out),
            {"status": "unavailable", "reason": "missing_api_key"},
        )
        urlopen.assert_not_called()

    def test_cli_usage_and_input_errors_exit_two_without_output_or_key(self) -> None:
        cases = (
            [],
            ["triage"],
            ["finding"],
            ["fork"],
            ["fork", "--stdin", "--file", "fork.json"],
            ["finding", "--file", "/nonexistent/jev-input.json"],
            ["finding", "--stdin"],
            ["finding", "--stdin"],
        )
        stdin_by_index = {
            6: "{not-json",
            7: json.dumps(["not", "an", "object"]),
        }
        for index, argv in enumerate(cases):
            with self.subTest(argv=argv):
                code, out, err = self.run_main(argv, stdin_by_index.get(index))

                self.assertEqual(code, 2)
                self.assertEqual(out, "")
                self.assertTrue(err.strip())
                self.assertNotIn(self.FAKE_KEY, out)
                self.assertNotIn(self.FAKE_KEY, err)

    def test_cli_never_prints_the_key_across_modes_and_failures(self) -> None:
        http_error = urllib.error.HTTPError(
            jev.API_URL, 503, "upstream", {}, io.BytesIO(self.FAKE_KEY.encode("utf-8"))
        )
        transport_error = urllib.error.URLError(
            f"dns resolution failed for {self.FAKE_KEY}"
        )
        for mode in ("finding", "fork"):
            scenarios = (
                ("available", CLI_MODE_INPUTS[mode], Response(CLI_AVAILABLE_PAYLOADS[mode]), 0),
                ("http_error", CLI_MODE_INPUTS[mode], http_error, 0),
                ("network_error", CLI_MODE_INPUTS[mode], transport_error, 0),
            )
            scenarios += (("input_error", "{not-json", None, 2),)
            for scenario, stdin_text, failure, expected_code in scenarios:
                if scenario == "available":
                    argv = [mode, "--stdin"]
                    patch_kwargs = {"return_value": failure}
                else:
                    argv = [mode, "--stdin"]
                    patch_kwargs = {"side_effect": failure}
                with self.subTest(mode=mode, scenario=scenario), mock.patch.object(
                    jev.urllib.request, "urlopen", **patch_kwargs
                ) as urlopen:
                    code, out, err = self.run_main(argv, stdin_text)

                self.assertEqual(code, expected_code)
                self.assertNotIn(self.FAKE_KEY, out)
                self.assertNotIn(self.FAKE_KEY, err)
                if scenario == "available":
                    self.assertEqual(json.loads(out), CLI_AVAILABLE_OUTPUTS[mode])
                    self.assertEqual(err, "")
                    self.assertEqual(urlopen.call_count, 1)
                elif scenario == "input_error":
                    self.assertEqual(out, "")
                    self.assertTrue(err.strip())
                    urlopen.assert_not_called()
                else:
                    output = json.loads(out)
                    self.assertEqual(output["status"], "unavailable")
                    self.assertIn(
                        output["reason"],
                        ("http_error", "network_error"),
                    )


if __name__ == "__main__":
    unittest.main()

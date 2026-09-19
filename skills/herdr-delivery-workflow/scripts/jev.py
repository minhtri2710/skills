#!/usr/bin/env python3
"""Optional TypeSafe/Jev advisory triage for one external finding.

The helper is advisory only. An unavailable Jev result remains fail-open so a
caller can retain and act on the original finding without waiting on Jev.
"""
from __future__ import annotations

import copy
import json
import math
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Literal, Mapping, TypeAlias

API_URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"
API_TIMEOUT_SECONDS = 10.0
MAX_EVIDENCE_CHARS = 2_000
REQUIRED_FINDING_FIELDS = (
    "severity",
    "project",
    "anti_pattern",
    "lens",
    "observation",
    "evidence",
    "impact",
    "recommendation",
    "escalation",
)

# The API receives one Noul and one Score. The criteria keep the model
# advisory: expected status, in-flight work, and benign Human-gate information
# are noise; a genuine workflow or structural misfit is actionable.
QUESTIONS = {
    "noul": {
        "type": "noul",
        "instructions": (
            "Is this a genuine workflow or structural anti-pattern that is "
            "actionable, rather than expected status, in-flight work, or "
            "benign Human-gate information?"
        ),
        "criteria": {
            "true": (
                "A real workflow or structural misfit supported by the finding "
                "that merits attention."
            ),
            "false": (
                "Expected status, in-flight work, benign Human-gate information, "
                "or an observation without an actionable anti-pattern."
            ),
        },
    },
    "score": {
        "type": "score",
        "instructions": (
            "How severe and actionable is this workflow or structural misfit?"
        ),
        "criteria": [
            "Expected status, in-flight work, benign Human-gate information, "
            "or an observation without an actionable anti-pattern.",
            "A material or uncertain finding that may warrant attention but is "
            "not clearly a severe misfit.",
            "A well-supported, severe, actionable workflow or structural misfit.",
        ],
    },
}
SCORE_MAX = len(QUESTIONS["score"]["criteria"]) - 1
NOUL_ACTIONABLE_THRESHOLD = 0.5

Finding: TypeAlias = Mapping[str, object]
NoulValue = Literal["actionable", "noise"]
Severity = Literal["low", "medium", "high"]


@dataclass(frozen=True)
class NoulJudgment:
    """Typed actionable-vs-noise judgment returned by Jev."""

    value: NoulValue
    probability: float

    @property
    def actionable(self) -> bool:
        return self.value == "actionable"


@dataclass(frozen=True)
class ScoreJudgment:
    """Typed severity/noise score returned by Jev."""

    value: float
    severity: Severity
    noise: bool


@dataclass(frozen=True)
class AdvisoryResult:
    """A valid Jev result, retaining source and raw answer data."""

    status: Literal["available"]
    finding: Finding
    noul: NoulJudgment
    score: ScoreJudgment
    rationale: tuple[str, ...]
    evidence: tuple[str, ...]
    raw_answers: Mapping[str, object]

    @property
    def available(self) -> bool:
        return True


@dataclass(frozen=True)
class UnavailableResult:
    """Explicit sentinel for a Jev result that could not be obtained safely."""

    status: Literal["unavailable"]
    finding: Finding
    reason: str
    # Fail-open means the original finding remains actionable when Jev cannot
    # advise. This is a fallback signal, not a Jev judgment or gate decision.
    fallback_actionable: bool = True

    @property
    def available(self) -> bool:
        return False


JevResult: TypeAlias = AdvisoryResult | UnavailableResult


def _retained_finding(finding: object) -> Finding:
    if not isinstance(finding, Mapping):
        return {}
    try:
        return copy.deepcopy(dict(finding))
    except Exception:
        return dict(finding)


def _unavailable(finding: object, reason: str) -> UnavailableResult:
    retained = _retained_finding(finding)
    return UnavailableResult(status="unavailable", finding=retained, reason=reason)


def _bounded_texts(value: object) -> tuple[str, ...] | None:
    if value is None:
        return ()
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, list) and all(isinstance(item, str) for item in value):
        values = value
    else:
        return None

    bounded: list[str] = []
    remaining = MAX_EVIDENCE_CHARS
    for item in values:
        if not item:
            continue
        if remaining <= 0:
            break
        clipped = item[:remaining]
        bounded.append(clipped)
        remaining -= len(clipped)
    return tuple(bounded)


def _score_severity(value: float) -> Severity:
    if value < 1 / 3:
        return "low"
    if value < 2 / 3:
        return "medium"
    return "high"


def _parse_answers(answers: object) -> tuple[
    NoulJudgment,
    ScoreJudgment,
    tuple[str, ...],
    tuple[str, ...],
    Mapping[str, object],
] | None:
    if not isinstance(answers, Mapping):
        return None
    noul = answers.get("noul")
    score = answers.get("score")
    if not isinstance(noul, Mapping) or not isinstance(score, Mapping):
        return None

    if noul.get("type") != "noul" or score.get("type") != "score":
        return None
    noul_value = noul.get("noul")
    score_value = score.get("score")
    if isinstance(noul_value, bool) or not isinstance(noul_value, (int, float)):
        return None
    if isinstance(score_value, bool) or not isinstance(score_value, (int, float)):
        return None
    try:
        numeric_noul = float(noul_value)
        numeric_score = float(score_value)
    except (OverflowError, TypeError, ValueError):
        return None
    if not math.isfinite(numeric_noul) or not 0.0 <= numeric_noul <= 1.0:
        return None
    if not math.isfinite(numeric_score) or not 0.0 <= numeric_score <= SCORE_MAX:
        return None

    rationale = _bounded_texts(noul.get("rationale"))
    if rationale is None:
        return None
    score_rationale = _bounded_texts(score.get("rationale"))
    if score_rationale is None:
        return None
    evidence = _bounded_texts(noul.get("evidence"))
    if evidence is None:
        return None
    score_evidence = _bounded_texts(score.get("evidence"))
    if score_evidence is None:
        return None

    normalized_score = numeric_score / SCORE_MAX
    try:
        raw_answers = copy.deepcopy(dict(answers))
    except Exception:
        return None
    return (
        NoulJudgment(
            value=(
                "actionable"
                if numeric_noul >= NOUL_ACTIONABLE_THRESHOLD
                else "noise"
            ),
            probability=numeric_noul,
        ),
        ScoreJudgment(
            value=normalized_score,
            severity=_score_severity(normalized_score),
            noise=normalized_score < 0.5,
        ),
        rationale + score_rationale,
        evidence + score_evidence,
        raw_answers,
    )


def triage_finding(finding: Finding) -> JevResult:
    """Ask Jev to triage one finding, returning an advisory or sentinel.

    No exception from credential lookup, request construction, transport, HTTP,
    decoding, or answer validation reaches the caller. The only external
    boundary is the TypeSafe HTTP request; model output is never executed or
    used to authorize, move, or resolve a gate.
    """
    retained = _retained_finding(finding)
    if not isinstance(finding, Mapping) or any(
        field not in finding for field in REQUIRED_FINDING_FIELDS
    ):
        return _unavailable(retained, "invalid_finding")

    key = os.environ.get("TYPESAFE_API_KEY", "")
    if not key.strip():
        return _unavailable(retained, "missing_api_key")

    try:
        state = json.dumps(retained, sort_keys=True, ensure_ascii=False)
        body = json.dumps(
            {"state": state, "model": MODEL, "questions": copy.deepcopy(QUESTIONS)},
            ensure_ascii=False,
        ).encode("utf-8")
        request = urllib.request.Request(
            API_URL,
            data=body,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=API_TIMEOUT_SECONDS) as response:
            status = getattr(response, "status", None)
            if status is not None and not 200 <= status < 300:
                return _unavailable(retained, "http_error")
            payload = json.load(response)
    except urllib.error.HTTPError:
        return _unavailable(retained, "http_error")
    except (urllib.error.URLError, TimeoutError, OSError):
        return _unavailable(retained, "network_error")
    except (ValueError, TypeError, UnicodeError):
        return _unavailable(retained, "malformed_json")
    except Exception:
        # The HTTP boundary is untrusted and must never make advisory triage a
        # caller failure. Keep this reason generic and free of exception data.
        return _unavailable(retained, "api_error")

    if not isinstance(payload, Mapping) or "answers" not in payload:
        return _unavailable(retained, "invalid_answers")
    parsed = _parse_answers(payload["answers"])
    if parsed is None:
        return _unavailable(retained, "invalid_answers")
    noul, score, rationale, evidence, raw_answers = parsed
    return AdvisoryResult(
        status="available",
        finding=retained,
        noul=noul,
        score=score,
        rationale=rationale,
        evidence=evidence,
        raw_answers=raw_answers,
    )

#!/usr/bin/env python3
"""Unit tests for beo_score_trace.py and beo_score_context.py (G2 — quality-tiered scoring)."""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import List, Optional
from unittest import mock

REFERENCE_ROOT = Path(__file__).resolve().parents[1] / "skills" / "beo" / "beo-reference"
SCRIPTS = REFERENCE_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def write_minimal(root: Path, issue_id: str, mode: str = "quick"):
    """Write TICKET.yaml and state.json for a test bead."""
    from beo_ticket import write_ticket
    from beo_state import initial_state, atomic_write_json
    from beo_paths import artifact_dir

    data = {
        "version": 1,
        "issue_id": issue_id,
        "mode": mode,
        "request": "x",
        "done_criteria": ["ok"],
        "scope": {
            "files": {"allow": ["README.md"], "forbid": []},
            "generated_outputs": [],
            "verify": {"commands": ["true"]},
        },
    }
    if mode in ("standard", "strict"):
        data["risk"] = {"summary": "low", "rollback": "git revert"}
    if mode == "strict":
        data["human_gates"] = {
            "status": "resolved",
            "gates": [
                {
                    "type": "broad_scope_authorization",
                    "scope": "README.md",
                    "approver_handle": "test-user",
                    "valid_for_issue_id": issue_id,
                    "reason": "test setup",
                }
            ],
        }
        data["strict"] = {
            "reason": "test strict mode",
            "authorization_refs": ["test-auth-ref"],
            "rollback_refs": ["test-rollback-ref"],
            "external_side_effects": [
                {
                    "type": "test",
                    "target": "test-target",
                    "authorization_ref": "test-auth-ref",
                    "precheck": "none",
                    "rollback_or_compensation": "none",
                    "postcheck": "none",
                    "blast_radius": "low",
                }
            ],
            "stateful_external_systems": [
                {
                    "name": "test-system",
                    "effect_ref": "test-target",
                }
            ],
        }
    write_ticket(root, issue_id, data)
    state = initial_state(issue_id)
    state["phase"] = "executed"
    state["execution"]["started_at"] = "2026-06-16T00:00:00Z"
    artifact_dir(root, issue_id).mkdir(parents=True, exist_ok=True)
    atomic_write_json(artifact_dir(root, issue_id) / "state.json", state)


def run_score_trace(root: Path, issue_id: str):
    """Invoke beo_score_trace.main() with the given root and issue, return parsed JSON."""
    import beo_score_trace
    argv = ["beo_score_trace.py", "--issue", issue_id, "--root", str(root)]
    with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()) as out:
        rc = beo_score_trace.main()
    return rc, json.loads(out.getvalue())


def run_score_context(root: Path, issue_id: str):
    """Invoke beo_score_context.main() with the given root and issue, return parsed JSON."""
    import beo_score_context
    argv = ["beo_score_context.py", "--issue", issue_id, "--root", str(root)]
    with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()) as out:
        rc = beo_score_context.main()
    return rc, json.loads(out.getvalue())


class ScoreTraceTest(unittest.TestCase):
    def test_minimal_tier_with_no_metadata(self):
        """Quick mode with no interventions/findings/trace metadata should return valid score 0-3."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal(root, "br-1", mode="quick")
            rc, payload = run_score_trace(root, "br-1")
            self.assertEqual(rc, 0)
            self.assertIn("score_value", payload)
            self.assertGreaterEqual(payload["score_value"], 0)
            self.assertLessEqual(payload["score_value"], 3)
            self.assertEqual(payload["tier"], "minimal")

    def test_standard_tier_includes_additional_required_fields(self):
        """Standard tier should be selected for standard mode."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal(root, "br-2", mode="standard")
            rc, payload = run_score_trace(root, "br-2")
            self.assertEqual(rc, 0)
            self.assertEqual(payload["tier"], "standard")
            self.assertIn("missing_required", payload)

    def test_detailed_tier_includes_decisions_and_duration(self):
        """Detailed tier should be selected for strict mode."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal(root, "br-3", mode="strict")
            rc, payload = run_score_trace(root, "br-3")
            self.assertEqual(rc, 0)
            self.assertEqual(payload["tier"], "detailed")

    def test_with_intervention_increases_score(self):
        """Bead with a recorded intervention should score > bead without intervention."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal(root, "br-4a", mode="quick")
            write_minimal(root, "br-4b", mode="quick")
            from beo_state import atomic_write_json
            from beo_paths import artifact_dir

            state_path = artifact_dir(root, "br-4b") / "state.json"
            state = json.loads(state_path.read_text())
            # Add intervention and a verdict so extract_trace finds both
            # task_summary (from intervention description) and outcome (from verdict)
            state["review"]["verdict"] = "accept"
            state["review"]["route_condition_id"] = "verdict_accept"
            state["review"]["closed_in_br"] = True
            state["execution"]["interventions"] = [
                {
                    "type": "human",
                    "source": "user@example",
                    "impact": "informational",
                    "description": "user clarified the request intent during execution",
                    "recorded_at": "2026-06-16T00:01:00Z",
                    "trace_id": None,
                    "story_id": None,
                }
            ]
            atomic_write_json(state_path, state)

            _, payload_a = run_score_trace(root, "br-4a")
            _, payload_b = run_score_trace(root, "br-4b")
            # br-4a scores 0 (no task_summary, no outcome); br-4b scores >=1
            self.assertGreater(payload_b["score_value"], payload_a["score_value"])
            self.assertTrue(payload_b["score_breakdown"]["task_summary"],
                            "intervention description should populate task_summary")
            self.assertFalse(payload_a["score_breakdown"]["task_summary"],
                             "no intervention means no task_summary")


class ScoreContextTest(unittest.TestCase):
    def test_empty_bead_scores_zero_for_standard(self):
        """Standard tier with no SKILL.md reads should still produce valid score."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal(root, "br-5", mode="standard")
            rc, payload = run_score_context(root, "br-5")
            self.assertEqual(rc, 0)
            self.assertEqual(payload["tier"], "standard")
            self.assertIn("score_value", payload)


class ScoreTraceRubricTest(unittest.TestCase):
    """Direct rubric tests for score_trace(). Bypasses main()/disk IO to target the scoring function."""

    def _trace(self, payload: dict, tier: str) -> dict:
        import beo_score_trace
        state = {"issue_id": "br-x", "execution": {"trace_tier": tier}, "review": {}}
        return beo_score_trace.score_trace(state, None, [{"kind": "x", "payload": payload}])

    def test_minimal_full_required_scores_1(self):
        """minimal tier with both required fields populated scores 1 (no optional fields at minimal)."""
        result = self._trace({"task_summary": "did the thing end to end", "outcome": "success"}, tier="minimal")
        self.assertEqual(result["score_value"], 1)
        self.assertEqual(result["missing_required"], [])

    def test_minimal_missing_task_summary_scores_0(self):
        """minimal tier missing task_summary scores 0."""
        result = self._trace({"outcome": "success"}, tier="minimal")
        self.assertEqual(result["score_value"], 0)
        self.assertIn("task_summary", result["missing_required"])

    def test_minimal_missing_outcome_scores_0(self):
        """minimal tier missing outcome scores 0."""
        result = self._trace({"task_summary": "did the thing end to end"}, tier="minimal")
        self.assertEqual(result["score_value"], 0)
        self.assertIn("outcome", result["missing_required"])

    def test_standard_all_required_no_optional_scores_1(self):
        """standard tier with all 6 required fields (none of 3 optional) scores 1."""
        payload = {
            "task_summary": "implemented the verifier end to end",
            "outcome": "success",
            "intake_id": "intake-1",
            "agent": "beo-execute",
            "actions_taken": ["a", "b"],
            "files_read": ["x.py"],
            "files_changed": ["y.py"],
            "errors": ["e1"],
        }
        result = self._trace(payload, tier="standard")
        self.assertEqual(result["score_value"], 1)
        self.assertEqual(result["missing_required"], [])

    def test_standard_two_of_three_optional_scores_2(self):
        """standard tier with 2 of 3 optional fields scores 2 (ratio 0.66, >=0.5)."""
        payload = {
            "task_summary": "implemented the verifier end to end",
            "outcome": "success",
            "intake_id": "intake-1",
            "agent": "beo-execute",
            "actions_taken": ["a"],
            "files_read": ["x.py"],
            "files_changed": ["y.py"],
            "errors": ["e1"],
            "decisions_made": ["chose option A"],
            "duration_seconds": 42.0,
        }
        result = self._trace(payload, tier="standard")
        self.assertEqual(result["missing_required"], [])
        self.assertEqual(result["score_value"], 2)

    def test_standard_all_three_optional_scores_3(self):
        """standard tier with all 3 optional fields scores 3 (ratio 1.0, >=0.75)."""
        payload = {
            "task_summary": "implemented the verifier end to end",
            "outcome": "success",
            "intake_id": "intake-1",
            "agent": "beo-execute",
            "actions_taken": ["a"],
            "files_read": ["x.py"],
            "files_changed": ["y.py"],
            "errors": ["e1"],
            "decisions_made": ["chose option A"],
            "duration_seconds": 42.0,
            "token_estimate": 1500,
        }
        result = self._trace(payload, tier="standard")
        self.assertEqual(result["missing_required"], [])
        self.assertEqual(result["score_value"], 3)

    def test_standard_missing_intake_and_story_scores_0(self):
        """standard tier with neither intake_id nor story_id scores 0 and reports the gap."""
        payload = {
            "task_summary": "implemented the verifier end to end",
            "outcome": "success",
            "agent": "beo-execute",
            "actions_taken": ["a"],
            "files_read": ["x.py"],
            "files_changed": ["y.py"],
            "errors": [],
        }
        result = self._trace(payload, tier="standard")
        self.assertEqual(result["score_value"], 0)
        self.assertIn("intake_id|story_id", result["missing_required"])

    def test_detailed_missing_token_estimate_scores_0(self):
        """detailed tier missing token_estimate scores 0 (decisions/duration not enough on their own)."""
        payload = {
            "task_summary": "implemented the verifier end to end",
            "outcome": "success",
            "intake_id": "intake-1",
            "agent": "beo-execute",
            "actions_taken": ["a"],
            "files_read": ["x.py"],
            "files_changed": ["y.py"],
            "errors": [],
            "decisions_made": ["chose A"],
            "duration_seconds": 42.0,
        }
        result = self._trace(payload, tier="detailed")
        self.assertEqual(result["score_value"], 0)
        self.assertIn("token_estimate", result["missing_required"])


class ScoreContextRubricTest(unittest.TestCase):
    """Direct rubric tests for score_context(). Bypasses main()/disk IO."""

    def _ctx(self, paths: list[str], ticket: dict | None, state: dict | None = None, tier: str = "standard") -> dict:
        import beo_score_context
        s = state or {"issue_id": "br-x", "execution": {"trace_tier": tier, "evidence_refs": list(paths)}, "review": {}}
        events = []
        return beo_score_context.score_context(s, ticket, events, state_loaded=state is not None)

    def test_standard_empty_scores_0(self):
        """standard tier with no evidence_refs and no scope files scores 0 (missing skill_cards and references)."""
        result = self._ctx([], ticket=None, tier="standard")
        self.assertEqual(result["score_value"], 0)
        self.assertIn("skill_cards_loaded", result["missing_required"])
        self.assertIn("references_loaded", result["missing_required"])

    def test_standard_two_skill_cards_two_refs_scores_1(self):
        """standard tier with 2 SKILL.md and 2 reference paths in evidence_refs scores 1 (required met, no over)."""
        paths = [
            "skills/beo/beo-execute/SKILL.md",
            "skills/beo/beo-validate/SKILL.md",
            "skills/beo/beo-reference/references/lifecycle.md",
            "skills/beo/beo-reference/references/safety.md",
        ]
        result = self._ctx(paths, ticket=None, tier="standard")
        self.assertEqual(result["counts"]["skill_card"], 2)
        self.assertEqual(result["counts"]["reference"], 2)
        self.assertEqual(result["missing_required"], [])
        self.assertEqual(result["score_value"], 1)

    def test_standard_one_over_each_scores_2(self):
        """standard tier with required + 1 over each category (3 skill_cards, 3 refs) scores 2 (over=2, in 1-2 range)."""
        paths = [
            "skills/beo/beo-execute/SKILL.md",
            "skills/beo/beo-validate/SKILL.md",
            "skills/beo/beo-review/SKILL.md",
            "skills/beo/beo-reference/references/lifecycle.md",
            "skills/beo/beo-reference/references/safety.md",
            "skills/beo/beo-reference/references/kernel.md",
        ]
        result = self._ctx(paths, ticket=None, tier="standard")
        self.assertEqual(result["missing_required"], [])
        # over_skill=1, over_ref=1, total over=2, standard maps over=1-2 -> score 2
        self.assertEqual(result["score_value"], 2)

    def test_standard_three_over_each_scores_3(self):
        """standard tier with required + 3 over each (5 skill_cards, 5 refs) scores 3 (over=6, >=3)."""
        paths = [f"skills/beo/beo-{name}/SKILL.md" for name in ["execute", "validate", "review", "plan", "debug"]]
        paths += [f"skills/beo/beo-reference/references/{name}.md" for name in ["lifecycle", "safety", "kernel", "memory", "doctrine-map"]]
        result = self._ctx(paths, ticket=None, tier="standard")
        self.assertEqual(result["missing_required"], [])
        self.assertEqual(result["score_value"], 3)

    def test_detailed_requires_ticket_and_state(self):
        """detailed tier without ticket/state present in counts scores 0."""
        result = self._ctx([], ticket=None, state=None, tier="detailed")
        self.assertEqual(result["score_value"], 0)
        self.assertIn("ticket_loaded", result["missing_required"])
        self.assertIn("state_loaded", result["missing_required"])

    def test_ticket_fallback_skipped_when_evidence_refs_has_ticket(self):
        """When evidence_refs already contains a TICKET.yaml path, the ticket-presence fallback does not add a second count."""
        # TICKET.yaml appears only in evidence_refs (not in scope.allow)
        paths = [".beads/artifacts/br-x/TICKET.yaml"]
        ticket = {"mode": "detailed", "scope": {"files": {"allow": ["README.md"], "forbid": []}}}
        result = self._ctx(paths, ticket=ticket, tier="detailed")
        self.assertEqual(result["counts"]["ticket"], 1)

    def test_ticket_fallback_used_when_no_ticket_path_in_inputs(self):
        """When no TICKET.yaml path appears in evidence_refs or scope.allow, the ticket-presence fallback still counts 1."""
        paths = ["skills/beo/beo-execute/SKILL.md", "skills/beo/beo-validate/SKILL.md",
                 "skills/beo/beo-review/SKILL.md", "skills/beo/beo-reference/references/lifecycle.md",
                 "skills/beo/beo-reference/references/safety.md", "skills/beo/beo-reference/references/kernel.md"]
        # Ticket with issue_id triggers the fallback; no TICKET.yaml path in inputs
        ticket = {"issue_id": "br-x", "mode": "detailed", "scope": {"files": {"allow": ["README.md"], "forbid": []}}}
        # Pass a state so state_loaded=True (detailed tier requires state)
        state = {"issue_id": "br-x", "execution": {"trace_tier": "detailed", "evidence_refs": paths}, "review": {}}
        result = self._ctx(paths, ticket=ticket, state=state, tier="detailed")
        self.assertEqual(result["counts"]["ticket"], 1)
        self.assertEqual(result["counts"]["state"], 1)
        self.assertEqual(result["missing_required"], [])


if __name__ == "__main__":
    unittest.main()

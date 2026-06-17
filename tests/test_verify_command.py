#!/usr/bin/env python3
"""Unit tests for beo_verify.py (G3 — verification as queryable command)."""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import List, Optional

REFERENCE_ROOT = Path(__file__).resolve().parents[1] / "skills" / "beo" / "beo-reference"
SCRIPTS = REFERENCE_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def write_ticket(root: Path, issue_id: str, mode: str = "quick", verify_commands_list: Optional[List[str]] = None):
    from beo_ticket import write_ticket
    data = {
        "version": 1,
        "issue_id": issue_id,
        "mode": mode,
        "request": "x",
        "done_criteria": ["ok"],
        "scope": {
            "files": {"allow": ["README.md"], "forbid": []},
            "generated_outputs": [],
            "verify": {"commands": verify_commands_list or ["true"]},
        },
    }
    write_ticket(root, issue_id, data)


def write_state(root: Path, issue_id: str, phase: str = "approved"):
    from beo_state import initial_state, atomic_write_json
    from beo_paths import artifact_dir
    state = initial_state(issue_id)
    state["phase"] = phase
    artifact_dir(root, issue_id).mkdir(parents=True, exist_ok=True)
    atomic_write_json(artifact_dir(root, issue_id) / "state.json", state)


class VerifyRunTest(unittest.TestCase):
    def test_run_passing_command_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_ticket(root, "br-1", verify_commands_list=["true"])
            write_state(root, "br-1", phase="approved")
            import beo_verify
            with mock_argv(["beo_verify.py", "run", "--issue", "br-1", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as out:
                rc = beo_verify.main()
            payload = json.loads(out.getvalue())
            self.assertEqual(rc, 0)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["summary"]["pass"], 1)
            self.assertEqual(payload["summary"]["fail"], 0)

    def test_run_failing_command_exits_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_ticket(root, "br-2", verify_commands_list=["false"])
            write_state(root, "br-2", phase="approved")
            import beo_verify
            with mock_argv(["beo_verify.py", "run", "--issue", "br-2", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as out:
                rc = beo_verify.main()
            payload = json.loads(out.getvalue())
            self.assertEqual(rc, 1)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["summary"]["fail"], 1)

    def test_refuses_planned_phase(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_ticket(root, "br-3", verify_commands_list=["true"])
            write_state(root, "br-3", phase="planned")
            import beo_verify
            with mock_argv(["beo_verify.py", "run", "--issue", "br-3", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as out:
                rc = beo_verify.main()
            payload = json.loads(out.getvalue())
            self.assertEqual(rc, 2)
            self.assertTrue(payload["refused"])
            self.assertIn("planned", payload["refusal_reason"])

    def test_refuses_missing_ticket(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_state(root, "br-4", phase="approved")
            import beo_verify
            with mock_argv(["beo_verify.py", "run", "--issue", "br-4", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as out:
                rc = beo_verify.main()
            payload = json.loads(out.getvalue())
            self.assertEqual(rc, 2)
            self.assertIn("ticket_missing", payload["refusal_reason"])

    def test_all_no_artifacts_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".beads" / "artifacts").mkdir(parents=True)
            import beo_verify
            with mock_argv(["beo_verify.py", "--all", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as out:
                rc = beo_verify.main()
            payload = json.loads(out.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["issue_results"], [])


from unittest import mock


def mock_argv(args):
    return mock.patch.object(sys, "argv", args)


class VerifyErrorPathsTest(unittest.TestCase):
    """Cover the four error/refusal paths in verify_issue not exercised by VerifyRunTest."""

    def test_refuses_invalid_ticket(self):
        """A ticket that exists but fails validation must produce 'ticket_invalid'."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = root / ".beads" / "artifacts" / "br-bad"
            artifact.mkdir(parents=True)
            (artifact / "TICKET.yaml").write_text("not a valid ticket: [:]", encoding="utf-8")
            write_state(root, "br-bad", phase="approved")
            import beo_verify
            with mock_argv(["beo_verify.py", "run", "--issue", "br-bad", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as out:
                rc = beo_verify.main()
            payload = json.loads(out.getvalue())
            self.assertEqual(rc, 2)
            self.assertTrue(payload["refused"])
            self.assertIn("ticket_invalid", payload["refusal_reason"])

    def test_refuses_missing_state(self):
        """A state.json FileNotFoundError must produce 'state_missing'."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_ticket(root, "br-5")
            import beo_verify
            with mock_argv(["beo_verify.py", "run", "--issue", "br-5", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as out:
                rc = beo_verify.main()
            payload = json.loads(out.getvalue())
            self.assertEqual(rc, 2)
            self.assertTrue(payload["refused"])
            self.assertIn("state_missing", payload["refusal_reason"])

    def test_refuses_invalid_state(self):
        """A state.json that exists but is malformed must produce 'state_invalid'."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_ticket(root, "br-6")
            artifact = root / ".beads" / "artifacts" / "br-6"
            artifact.mkdir(parents=True, exist_ok=True)
            (artifact / "state.json").write_text("{not valid json", encoding="utf-8")
            import beo_verify
            with mock_argv(["beo_verify.py", "run", "--issue", "br-6", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as out:
                rc = beo_verify.main()
            payload = json.loads(out.getvalue())
            self.assertEqual(rc, 2)
            self.assertTrue(payload["refused"])
            self.assertIn("state_invalid", payload["refusal_reason"])

    def test_worktree_missing_emits_skipped_results(self):
        """When strict worktree_isolation is true but the worktree dir is absent, every command is skipped."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Build a strict-mode ticket with worktree_isolation=true from the start.
            # (read+rewrite would require upgrading mode; write directly instead.)
            from beo_ticket import write_ticket as _write_ticket
            from beo_state import initial_state, atomic_write_json
            from beo_paths import artifact_dir
            artifact_dir(root, "br-7").mkdir(parents=True, exist_ok=True)
            data = {
                "version": 1,
                "issue_id": "br-7",
                "mode": "strict",
                "request": "x",
                "done_criteria": ["ok"],
                "risk": {"summary": "low", "rollback": "git revert"},
                "human_gates": {
                    "status": "resolved",
                    "gates": [
                        {
                            "type": "broad_scope_authorization",
                            "scope": "README.md",
                            "approver_handle": "test-user",
                            "valid_for_issue_id": "br-7",
                            "reason": "test setup",
                        }
                    ],
                },
                "strict": {
                    "reason": "test strict mode",
                    "authorization_refs": ["a"],
                    "rollback_refs": ["r"],
                    "external_side_effects": [
                        {
                            "type": "test",
                            "target": "test-target",
                            "authorization_ref": "a",
                            "precheck": "none",
                            "rollback_or_compensation": "none",
                            "postcheck": "none",
                            "blast_radius": "low",
                        }
                    ],
                    "stateful_external_systems": [
                        {"name": "test-system", "effect_ref": "test-target"}
                    ],
                    "worktree_isolation": True,
                },
                "scope": {
                    "files": {"allow": ["README.md"], "forbid": []},
                    "generated_outputs": [],
                    "verify": {"commands": ["true", "echo hi"]},
                },
            }
            _write_ticket(root, "br-7", data)
            state = initial_state("br-7")
            state["phase"] = "approved"
            atomic_write_json(artifact_dir(root, "br-7") / "state.json", state)
            import beo_verify
            with mock_argv(["beo_verify.py", "run", "--issue", "br-7", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as out:
                rc = beo_verify.main()
            payload = json.loads(out.getvalue())
            self.assertEqual(rc, 0, f"all-skipped should still exit 0; got payload={payload}")
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["summary"]["skipped"], 2)
            self.assertEqual(payload["summary"]["pass"], 0)
            self.assertEqual(payload["summary"]["fail"], 0)
            for result in payload["issue_results"]:
                self.assertEqual(result["status"], "skipped")
                self.assertEqual(result["skip_reason"], "worktree_missing")
                self.assertIsNone(result["worktree_path"])


class FastTrackGlobTest(unittest.TestCase):
    """M1: fast-track no-glob enforcement in beo_ticket.validate_plan_only."""

    def test_quick_fast_track_rejects_glob_allow(self):
        """A quick+fast_track ticket with glob in scope.files.allow must be rejected."""
        from beo_ticket import validate_plan_only
        bad = {
            "version": 1,
            "issue_id": "br-bad",
            "mode": "quick",
            "fast_track": True,
            "request": "x",
            "done_criteria": ["ok"],
            "scope": {"files": {"allow": ["*.md"], "forbid": []}, "generated_outputs": [], "verify": {"commands": ["true"]}},
        }
        with self.assertRaises(ValueError) as ctx:
            validate_plan_only(bad)
        self.assertIn("glob", str(ctx.exception).lower())
        self.assertIn("*.md", str(ctx.exception))

    def test_quick_fast_track_accepts_exact_path(self):
        """A quick+fast_track ticket with exact paths in scope.files.allow must be accepted (for the glob check at least)."""
        from beo_ticket import validate_plan_only
        good = {
            "version": 1,
            "issue_id": "br-test",
            "mode": "quick",
            "fast_track": True,
            "request": "do the thing",
            "done_criteria": ["it works"],
            "scope": {
                "files": {"allow": ["README.md", "src/main.py"], "forbid": []},
                "generated_outputs": [],
                "verify": {"commands": ["true"]},
            },
        }
        try:
            validate_plan_only(good)
        except ValueError as exc:
            self.fail(f"validate_plan_only raised unexpected ValueError: {exc}")

if __name__ == "__main__":
    unittest.main()

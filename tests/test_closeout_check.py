#!/usr/bin/env python3
"""Tests for the repository-owned, pane-level closeout checker."""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
import sys
from typing import Any
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import closeout_check  # noqa: E402


class FakeHerdr:
    """Small read boundary with a pane-close operation for the red/green path."""

    def __init__(self, canonical: Path) -> None:
        self.canonical = canonical
        self.panes: dict[str, dict[str, Any]] = {}
        self.agents: dict[str, dict[str, Any]] = {}
        self.processes: dict[str, dict[str, Any]] = {}

    def add_peer(self, name: str, pane: str, *, agent_status: str = "present",
                 processes: list[dict[str, Any]] | None = None) -> None:
        self.panes[pane] = {"status": "open", "pane_id": pane, "cwd": str(self.canonical)}
        self.agents[name] = {"status": agent_status}
        self.processes[pane] = {"foreground_processes": processes or []}

    def add_persistent(self, pane: str) -> None:
        self.panes[pane] = {"status": "open", "pane_id": pane, "cwd": str(self.canonical)}

    def close(self, pane: str) -> None:
        self.panes.pop(pane, None)
        self.processes.pop(pane, None)

    def read_pane(self, pane_id: str) -> dict[str, Any]:
        return self.panes.get(pane_id, {"status": "absent"})

    def read_agent(self, agent_name: str) -> dict[str, Any]:
        return self.agents.get(agent_name, {"status": "agent_not_found"})

    def read_processes(self, pane_id: str) -> dict[str, Any]:
        return self.processes.get(pane_id, {"foreground_processes": []})


class CloseoutCheckTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.canonical = Path(self.tmp.name) / "checkout"
        self.canonical.mkdir()
        self.herdr = FakeHerdr(self.canonical)
        self.record = {
            "canonical_checkout": str(self.canonical),
            "persistent": [
                {"role": "Lead", "name": "lead-beo-skills", "pane": "w1:p1"},
                {"role": "Human Supervisor", "name": "supervisor", "pane": "w1:p2"},
            ],
            "peers": [
                {"issue": "teardown-clarify", "role": "Engineer",
                 "name": "eng-teardown", "pane": "w1:p3"},
                {"issue": "teardown-clarify", "role": "Reviewer",
                 "name": "review-teardown", "pane": "w1:p4"},
            ],
        }
        self.herdr.add_persistent("w1:p1")
        self.herdr.add_persistent("w1:p2")
        self.herdr.add_peer("eng-teardown", "w1:p3", agent_status="agent_not_found")
        self.herdr.add_peer("review-teardown", "w1:p4")
        self.addCleanup(self.tmp.cleanup)

    def test_open_recorded_peer_fails_even_when_agent_is_not_found_then_passes_after_close(self):
        result = closeout_check.check_closeout(self.record, self.herdr)
        self.assertFalse(result.passed)
        self.assertIn("eng-teardown", "\n".join(result.findings))
        self.assertIn("agent_not_found", "\n".join(result.findings))

        self.herdr.close("w1:p3")
        self.herdr.close("w1:p4")
        result = closeout_check.check_closeout(self.record, self.herdr)
        self.assertTrue(result.passed, result.findings)

    def test_live_server_in_peer_pane_names_squatting_server_anti_pattern(self):
        self.herdr.processes["w1:p3"] = {
            "foreground_processes": [{
                "argv0": "npm",
                "command": "npm run dev",
                "cwd": str(self.canonical),
                "alive": True,
            }],
        }
        result = closeout_check.check_closeout(self.record, self.herdr)
        self.assertFalse(result.passed)
        self.assertTrue(any("squatting-server anti-pattern" in finding
                            for finding in result.findings))

    def test_interpreter_server_script_in_peer_pane_names_squatting_server_anti_pattern(self):
        self.herdr.processes["w1:p3"] = {
            "foreground_processes": [{
                "argv0": "node",
                "command": "node server.js",
                "cwd": str(self.canonical),
                "alive": True,
            }],
        }
        result = closeout_check.check_closeout(self.record, self.herdr)
        self.assertFalse(result.passed)
        self.assertTrue(any("squatting-server anti-pattern" in finding
                            for finding in result.findings))

    def test_server_detection_matches_argv_tokens_not_substrings(self):
        cases = (
            (["node", "vitest"], False),
            (["tail", "-f", "/dev/null"], False),
            (["vim", "server.py"], False),
            (["npm", "run", "dev"], True),
            (["vite"], True),
            (["/usr/bin/python3", "-m", "http.server"], True),
            (["next", "dev"], True),
            (["uvicorn", "app:app"], True),
            (["node", "server.js"], True),
            (["python3", "serve.py"], True),
            (["bun", "./src/server.ts"], True),
            (["deno", "run", "-A", "server.ts"], True),
            (["/usr/local/bin/node", "--inspect", "dev.mjs"], True),
            (["cat", "server.js"], False),
            (["less", "dev.log"], False),
            (["node", "build.js", "server.js"], False),
            (["python3", "-c", "import server"], False),
            (["node", "-e", "require('./server.js')"], False),
        )
        for argv, expected in cases:
            with self.subTest(argv=argv):
                self.assertEqual(closeout_check._is_server_process({"cmdline": argv}), expected)

    def test_persistent_lead_and_supervisor_are_not_teardown_targets(self):
        self.herdr.close("w1:p3")
        self.herdr.close("w1:p4")
        result = closeout_check.check_closeout(self.record, self.herdr)
        self.assertTrue(result.passed, result.findings)
        self.assertEqual(result.checked_panes, ("w1:p3", "w1:p4"))

    def test_lead_only_persistent_record_passes_validation_and_closeout(self):
        record = dict(self.record)
        record["persistent"] = [self.record["persistent"][0]]
        self.herdr.close("w1:p3")
        self.herdr.close("w1:p4")
        result = closeout_check.check_closeout(record, self.herdr)
        self.assertTrue(result.passed, result.findings)

    def test_zero_lead_persistent_record_refuses(self):
        record = dict(self.record)
        record["persistent"] = [self.record["persistent"][1]]
        result = closeout_check.check_closeout(record, self.herdr)
        self.assertFalse(result.passed)
        self.assertIn(
            "persistent must record exactly one Lead and at most one Human Supervisor",
            result.findings[0],
        )

    def test_two_human_supervisors_refuse(self):
        record = dict(self.record)
        record["persistent"] = [
            self.record["persistent"][0],
            self.record["persistent"][1],
            {"role": "Human Supervisor", "name": "supervisor-2", "pane": "w1:p5"},
        ]
        result = closeout_check.check_closeout(record, self.herdr)
        self.assertFalse(result.passed)
        self.assertIn(
            "persistent must record exactly one Lead and at most one Human Supervisor",
            result.findings[0],
        )

    def test_unknown_persistent_role_refuses(self):
        record = dict(self.record)
        record["persistent"] = [
            self.record["persistent"][0],
            {"role": "Architect", "name": "architect", "pane": "w1:p5"},
        ]
        result = closeout_check.check_closeout(record, self.herdr)
        self.assertFalse(result.passed)
        self.assertIn(
            "persistent must record exactly one Lead and at most one Human Supervisor",
            result.findings[0],
        )

    def test_duplicate_persistent_pane_is_rejected(self):
        record = dict(self.record)
        record["persistent"] = [
            self.record["persistent"][0],
            {"role": "Human Supervisor", "name": "supervisor", "pane": "w1:p1"},
        ]
        with self.assertRaisesRegex(ValueError, "persistent pane 'w1:p1' is duplicated"):
            closeout_check._validate_record(record)

    def test_duplicate_persistent_name_is_rejected(self):
        record = dict(self.record)
        record["persistent"] = [
            self.record["persistent"][0],
            {"role": "Human Supervisor", "name": "lead-beo-skills", "pane": "w1:p2"},
        ]
        with self.assertRaisesRegex(ValueError, "persistent name 'lead-beo-skills' is duplicated"):
            closeout_check._validate_record(record)

    def test_missing_pane_evidence_fails_closed(self):
        class MissingPane(FakeHerdr):
            def read_pane(self, pane_id: str) -> dict[str, Any]:
                return {"status": "unknown"}

        result = closeout_check.check_closeout(self.record, MissingPane(self.canonical))
        self.assertFalse(result.passed)
        self.assertIn("unknown or missing pane evidence", "\n".join(result.findings))

    def test_malformed_opaque_handle_is_rejected_without_boundary_call(self):
        record = dict(self.record)
        record["peers"] = [dict(self.record["peers"][0], pane="$(touch should-not-run)")]
        result = closeout_check.check_closeout(record, self.herdr)
        self.assertFalse(result.passed)
        self.assertIn("malformed staffing record", result.findings[0])

    def test_template_loads_and_validates(self):
        template = (
            Path(__file__).resolve().parents[1]
            / "skills"
            / "herdr-delivery-workflow"
            / "templates"
            / "staffing-closeout.json"
        )
        with template.open(encoding="utf-8") as handle:
            record = json.load(handle)
        canonical, peers = closeout_check._validate_record(record)
        self.assertTrue(canonical.is_absolute())
        self.assertEqual([peer["role"] for peer in peers], ["Engineer", "Reviewer"])
        self.assertEqual(
            record["persistent"],
            [
                {"role": "Lead", "name": "lead-project-slug", "pane": "w0:pLead"},
                {"role": "Human Supervisor", "name": "supervisor", "pane": "w0:pSupervisor"},
            ],
        )

        unsupervised = dict(record)
        unsupervised["persistent"] = [record["persistent"][0]]
        canonical, peers = closeout_check._validate_record(unsupervised)
        self.assertTrue(canonical.is_absolute())
        self.assertEqual([peer["role"] for peer in peers], ["Engineer", "Reviewer"])

    def test_subprocess_herdr_unavailable_fails_closeout_closed(self):
        with mock.patch.object(
            closeout_check.herdr_cli,
            "run",
            side_effect=closeout_check.herdr_cli.HerdrUnavailable("herdr pane get timed out"),
        ):
            result = closeout_check.check_closeout(self.record, closeout_check._SubprocessHerdr())
        self.assertFalse(result.passed)
        self.assertTrue(any("pane read failed" in finding for finding in result.findings))

    def test_cli_reads_json_closeout_staffing_record_and_returns_pass(self):
        self.herdr.close("w1:p3")
        self.herdr.close("w1:p4")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "staffing.json"
            path.write_text(json.dumps(self.record), encoding="utf-8")
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.ExitStack() as stack:
                stack.enter_context(mock.patch.object(
                    closeout_check, "_SubprocessHerdr", return_value=self.herdr
                ))
                stack.enter_context(contextlib.redirect_stdout(stdout))
                stack.enter_context(contextlib.redirect_stderr(stderr))
                code = closeout_check.main(["--staffing", str(path)])
        self.assertEqual(code, 0)
        self.assertIn("PASS:", stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")


if __name__ == "__main__":
    unittest.main()

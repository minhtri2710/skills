#!/usr/bin/env python3
"""Tests for the compact roster read helper."""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import roster  # noqa: E402


class RosterTest(unittest.TestCase):
    def setUp(self) -> None:
        self._stdout_patch = mock.patch.object(sys, "stdout", io.StringIO())
        self._stderr_patch = mock.patch.object(sys, "stderr", io.StringIO())
        self._stdout_patch.start()
        self._stderr_patch.start()
        self.addCleanup(self._stderr_patch.stop)
        self.addCleanup(self._stdout_patch.stop)

    def test_formats_agents_and_filters_workspace(self):
        payload = {
            "result": {
                "agents": [
                    {
                        "pane_id": "w1:p1",
                        "name": "lead",
                        "agent": "claude",
                        "agent_status": "working",
                        "workspace_id": "w1",
                    },
                    {
                        "pane_id": "w2:p1",
                        "agent": "agy",
                        "agent_status": "idle",
                        "workspace_id": "w2",
                    },
                ]
            }
        }
        self.assertEqual(
            roster.format_roster(payload),
            ["w1:p1 lead claude working", "w2:p1 - agy idle"],
        )
        self.assertEqual(
            roster.format_roster(payload, workspace="w1"),
            ["w1:p1 lead claude working"],
        )

    _SAMPLE = '{"result":{"agents":[{"pane_id":"w1:p1","name":"lead","agent":"claude","agent_status":"working","workspace_id":"w1"}]}}'

    def test_default_runs_agent_list_even_with_empty_nontty_stdin(self):
        # The live path: an agent's Bash gives an empty non-tty stdin. Without
        # --stdin the script must ignore stdin and run `herdr agent list`.
        completed = subprocess.CompletedProcess(
            args=["herdr", "agent", "list"], returncode=0, stdout=self._SAMPLE, stderr=""
        )
        with mock.patch.object(roster.herdr_cli.subprocess, "run", return_value=completed) as run, \
                mock.patch.object(roster.sys, "stdin", io.StringIO("")):
            output = io.StringIO()
            error = io.StringIO()
            with mock.patch("sys.stdout", output), mock.patch("sys.stderr", error):
                rc = roster.main(["--workspace", "w1"])
        self.assertEqual(rc, 0)
        self.assertEqual(output.getvalue(), "w1:p1 lead claude working\n")
        self.assertEqual(error.getvalue(), "")
        run.assert_called_once()

    def test_herdr_unavailable_maps_to_the_existing_cli_error(self):
        with mock.patch.object(
            roster.herdr_cli,
            "run",
            side_effect=roster.herdr_cli.HerdrUnavailable("herdr agent list timed out"),
        ), mock.patch.object(roster.sys, "stdin", io.StringIO("")):
            error = io.StringIO()
            with mock.patch("sys.stdout", io.StringIO()), mock.patch("sys.stderr", error):
                rc = roster.main([])
        self.assertEqual(rc, 1)
        self.assertIn("could not run herdr agent list", error.getvalue())

    def test_stdin_flag_reads_stdin_and_skips_subprocess(self):
        with mock.patch.object(roster.herdr_cli.subprocess, "run") as run, \
                mock.patch.object(roster.sys, "stdin", io.StringIO(self._SAMPLE)), \
                mock.patch("sys.stdout", io.StringIO()), mock.patch("sys.stderr", io.StringIO()):
            rc = roster.main(["--stdin", "--workspace", "w1"])
        self.assertEqual(rc, 0)
        run.assert_not_called()

    def test_stalled_requires_report_absent_and_stale_progress_across_interval(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "report.md"
            progress = root / "progress.md"
            progress.write_text("old")
            stale_mtime = time.time() - 120
            os.utime(progress, (stale_mtime, stale_mtime))
            previous = root / "previous.json"
            previous.write_text(
                json.dumps({"peers": {"peer-1": {
                    "state": "working", "progress_mtime": stale_mtime,
                }}})
            )
            payload = {"result": {"agents": [{
                "pane_id": "w1:p1", "name": "peer-1", "agent": "claude",
                "agent_status": "idle", "workspace_id": "w1",
            }]}}
            with mock.patch.object(roster.sys, "stdin", io.StringIO(json.dumps(payload))):
                output = io.StringIO()
                with mock.patch("sys.stdout", output):
                    rc = roster.main([
                        "--stdin", "--stalled", "--workspace", "w1",
                        "--peer", f"peer-1:{report}:{progress}",
                        "--previous-sample", str(previous), "--stale-after", "60",
                    ])
            self.assertEqual(rc, 0)
            self.assertEqual(output.getvalue(), "w1:p1 peer-1 claude STALLED\n")

    def test_never_started_requires_explicit_evidence_and_missing_progress(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "report.md"
            progress = root / "progress.md"
            payload = {"result": {"agents": [{
                "pane_id": "w1:p1", "name": "peer-1", "agent": "claude",
                "agent_status": "idle", "workspace_id": "w1",
                "tokens": {"sort_key": "000000000001"},
            }]}}
            with mock.patch.object(roster.sys, "stdin", io.StringIO(json.dumps(payload))):
                output = io.StringIO()
                with mock.patch("sys.stdout", output):
                    rc = roster.main([
                        "--stdin", "--never-started", "peer-1", "--workspace", "w1",
                        "--peer", f"peer-1:{report}:{progress}",
                    ])
            self.assertEqual(rc, 0)
            self.assertEqual(output.getvalue(), "w1:p1 peer-1 claude NEVER-STARTED\n")

    def test_never_started_is_not_reported_when_progress_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "report.md"
            progress = root / "progress.md"
            progress.write_text("progress")
            payload = {"result": {"agents": [{
                "pane_id": "w1:p1", "name": "peer-1", "agent": "claude",
                "agent_status": "done", "workspace_id": "w1",
            }]}}
            with mock.patch.object(roster.sys, "stdin", io.StringIO(json.dumps(payload))):
                output = io.StringIO()
                with mock.patch("sys.stdout", output):
                    rc = roster.main([
                        "--stdin", "--never-started", "peer-1",
                        "--peer", f"peer-1:{report}:{progress}",
                    ])
            self.assertEqual(rc, 0)
            self.assertEqual(output.getvalue(), "")

    def test_never_started_is_not_reported_when_report_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "report.md"
            progress = root / "progress.md"
            report.write_text("done")
            payload = {"result": {"agents": [{
                "pane_id": "w1:p1", "name": "peer-1", "agent": "claude",
                "agent_status": "done", "workspace_id": "w1",
            }]}}
            with mock.patch.object(roster.sys, "stdin", io.StringIO(json.dumps(payload))):
                output = io.StringIO()
                with mock.patch("sys.stdout", output):
                    rc = roster.main([
                        "--stdin", "--never-started", "peer-1",
                        "--peer", f"peer-1:{report}:{progress}",
                    ])
            self.assertEqual(rc, 0)
            self.assertEqual(output.getvalue(), "")

    def test_stalled_missing_progress_remains_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "report.md"
            progress = root / "progress.md"
            previous = root / "previous.json"
            previous.write_text(json.dumps({"peers": {
                "peer-1": {"state": "working", "progress_mtime": 0},
            }}))
            payload = {"result": {"agents": [{
                "pane_id": "w1:p1", "name": "peer-1", "agent": "claude",
                "agent_status": "idle", "workspace_id": "w1",
            }]}}
            with mock.patch.object(roster.sys, "stdin", io.StringIO(json.dumps(payload))):
                output = io.StringIO()
                with mock.patch("sys.stdout", output):
                    rc = roster.main([
                        "--stdin", "--stalled", "--peer", f"peer-1:{report}:{progress}",
                        "--previous-sample", str(previous), "--stale-after", "60",
                    ])
            self.assertEqual(rc, 0)
            self.assertEqual(output.getvalue(), "")

    def test_stalled_single_idle_sample_with_report_is_not_stalled(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "report.md"
            report.write_text("done")
            progress = root / "progress.md"
            progress.write_text("old")
            stale_mtime = time.time() - 120
            os.utime(progress, (stale_mtime, stale_mtime))
            previous = root / "previous.json"
            previous.write_text(json.dumps({"peers": {
                "peer-1": {"state": "working", "progress_mtime": stale_mtime},
            }}))
            payload = {"result": {"agents": [{
                "pane_id": "w1:p1", "name": "peer-1", "agent": "claude",
                "agent_status": "idle", "workspace_id": "w1",
            }]}}
            with mock.patch.object(roster.sys, "stdin", io.StringIO(json.dumps(payload))):
                output = io.StringIO()
                with mock.patch("sys.stdout", output):
                    rc = roster.main([
                        "--stdin", "--stalled", "--peer", f"peer-1:{report}:{progress}",
                        "--previous-sample", str(previous), "--stale-after", "60",
                    ])
            self.assertEqual(rc, 0)
            self.assertEqual(output.getvalue(), "")

    def test_stalled_single_idle_sample_with_fresh_progress_is_not_stalled(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "report.md"
            progress = root / "progress.md"
            progress.write_text("fresh")
            current_mtime = progress.stat().st_mtime
            previous = {
                "peer-1": {
                    "state": "working",
                    "progress_mtime": current_mtime - 1,
                }
            }
            payload = {"result": {"agents": [{
                "pane_id": "w1:p1", "name": "peer-1", "agent": "claude",
                "agent_status": "idle", "workspace_id": "w1",
            }]}}
            lines = roster.format_stalled_roster(
                payload,
                {"peer-1": (report, progress)},
                previous,
                stale_after=60,
                now=current_mtime + 61,
            )
            self.assertEqual(lines, [])


if __name__ == "__main__":
    unittest.main()

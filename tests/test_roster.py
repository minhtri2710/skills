#!/usr/bin/env python3
"""Tests for the compact roster read helper."""
from __future__ import annotations

import io
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import roster  # noqa: E402


class RosterTest(unittest.TestCase):
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
        with mock.patch.object(roster.subprocess, "run", return_value=completed) as run, \
                mock.patch.object(roster.sys, "stdin", io.StringIO("")):
            rc = roster.main(["--workspace", "w1"])
        self.assertEqual(rc, 0)
        run.assert_called_once()

    def test_stdin_flag_reads_stdin_and_skips_subprocess(self):
        with mock.patch.object(roster.subprocess, "run") as run, \
                mock.patch.object(roster.sys, "stdin", io.StringIO(self._SAMPLE)):
            rc = roster.main(["--stdin", "--workspace", "w1"])
        self.assertEqual(rc, 0)
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()

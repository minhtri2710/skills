#!/usr/bin/env python3
"""Unit tests for tracked skill deployment acceptance."""
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
import sys
sys.path.insert(0, str(SCRIPTS))

import deploy_skill  # noqa: E402
import gate_row  # noqa: E402


class DeploySkillTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir="/private/tmp")
        self.tmp = Path(self._tmp.name)
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.invalid")
        self.git("config", "user.name", "t")
        self.source = self.repo / "skills" / "herdr-delivery-workflow"
        self.source.mkdir(parents=True)
        (self.source / "SKILL.md").write_text("tracked skill\n")
        self.git("add", "skills")
        self.git("commit", "-qm", "skill")
        self.install = self.tmp / "installed"
        self.addCleanup(self._tmp.cleanup)

    def git(self, *args: str) -> None:
        subprocess.run(["git", "-C", str(self.repo), *args], check=True,
                       capture_output=True, text=True)

    def test_tampered_installed_file_fails_hash_comparison(self):
        self.install.mkdir()
        installed = self.install / "SKILL.md"
        installed.write_text("tampered\n")
        head = deploy_skill.git(self.repo, "rev-parse", "HEAD")
        paths = deploy_skill.tracked_files(self.repo, head, "skills/herdr-delivery-workflow")
        with self.assertRaises(deploy_skill.DeployError):
            deploy_skill.verify_install(
                self.repo, head, self.install, paths, "skills/herdr-delivery-workflow"
            )

    def test_deploy_resolves_open_gate_in_same_invocation(self):
        gate_row_script = SCRIPTS / "gate_row.py"
        append = [
            sys.executable,
            str(gate_row_script),
            "--repo", str(self.repo),
            "--ledger", str(self.tmp / "gates.md"),
        ]
        open_gate = subprocess.run(
            append + [
                "--kind", "deploy-gate", "--status", "open",
                "--words", "none", "--note", "deploy permission pending", "--quote", "",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(open_gate.returncode, 0, open_gate.stderr)
        self.assertIn("G1", open_gate.stdout)

        result = deploy_skill.main([
            "--repo", str(self.repo),
            "--source-dir", str(self.source),
            "--install-dir", str(self.install),
            "--ledger", str(self.tmp / "gates.md"),
            "--status", "resolved:deploy",
            "--words", "seat",
            "--note", "installed the skill",
            "--quote", "deploy completed",
            "--resolves", "G1",
        ])

        self.assertEqual(result, 0)
        rows = gate_row.ledger_rows((self.tmp / "gates.md").read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 2)
        self.assertIn("resolves=G1", rows[-1])
        open_gates = subprocess.run(
            append + ["--open-gates"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(open_gates.returncode, 0, open_gates.stderr)
        self.assertEqual(open_gates.stdout, "")


if __name__ == "__main__":
    unittest.main()

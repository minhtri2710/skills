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


if __name__ == "__main__":
    unittest.main()

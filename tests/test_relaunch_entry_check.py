#!/usr/bin/env python3
"""Unit tests for relaunch_entry_check.py's CLI paths."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import support
import relaunch_entry_check

SCRIPTS = support.ADW / "scripts"


def setUpModule() -> None:
    support.never_run("git", sys.executable)


class RelaunchEntryCheckTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=os.path.realpath("/tmp"))
        self.tmp = Path(self._tmp.name)
        self.repo = support.temp_git_repo(self.tmp / "repo")
        self.skill = self.repo / "skills" / "example"
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("skill\n", encoding="utf-8")
        (self.skill / "script.py").write_text("print('ok')\n", encoding="utf-8")
        support.git(self.repo, "add", "skills/example")
        support.git(self.repo, "commit", "-qm", "skill")
        self.ledger = self.tmp / "gates.md"
        self.install = self.tmp / "installed"
        self.install.mkdir()
        for name in ("SKILL.md", "script.py"):
            (self.install / name).write_bytes((self.skill / name).read_bytes())
        (self.install / "__pycache__").mkdir()
        (self.install / "__pycache__" / "ignored.pyc").write_bytes(b"runtime")
        self.addCleanup(self._tmp.cleanup)

    def deploy_row(self, *skills: str) -> None:
        args = [
            sys.executable, str(SCRIPTS / "gate_row.py"), "--repo", str(self.repo),
            "--ledger", str(self.ledger), "--kind", "deploy", "--status", "resolved:deploy",
            "--words", "seat", "--note", "deployed", "--quote", "ok",
        ]
        for skill in skills:
            args.extend(["--skill", skill])
        subprocess.run(args, check=True, capture_output=True, text=True, stdin=subprocess.DEVNULL)

    def test_verify_passes_for_verbatim_next_item_block(self):
        source = self.tmp / "staffing.md"
        source.write_text(
            "# Staffing\n\n"
            "## R4 — Shared contact form + minor items (NEXT; scope ratified G167, G168)\n"
            "Base: updated main after R2.\n",
            encoding="utf-8",
        )
        block = self.tmp / "next-item.txt"
        block.write_text(
            "## R4 — Shared contact form + minor items (NEXT; scope ratified G167, G168)",
            encoding="utf-8",
        )
        code, stdout, stderr = support.run_main(relaunch_entry_check.main, [
            "--verify", "--block-file", str(block), "--source-file", str(source),
        ])
        self.assertEqual(code, 0)
        self.assertEqual(stdout, "G167 G168\n")
        self.assertEqual(stderr, "")

    def test_verify_fails_for_memory_reconstructed_r3_as_r4_block(self):
        source = self.tmp / "staffing.md"
        source.write_text(
            "## R3 — BĐS services page [G164]\n"
            "## R4 — Shared contact form + minor items (NEXT; scope ratified G167, G168)\n",
            encoding="utf-8",
        )
        altered = self.tmp / "next-item.txt"
        altered.write_text("## R4 — BĐS services page [G164]", encoding="utf-8")
        code, stdout, stderr = support.run_main(relaunch_entry_check.main, [
            "--verify", "--block-file", str(altered), "--source-file", str(source),
        ])
        self.assertNotEqual(code, 0)
        self.assertEqual(stdout, "")
        self.assertIn("not a verbatim contiguous block", stderr)

    def count(self) -> tuple[int, str, str]:
        return support.run_main(relaunch_entry_check.main, [
            "--count", "--repo", str(self.repo), "--ledger", str(self.ledger),
            "--skill", "example", "--skill-path", "skills/example",
            "--installed-path", str(self.install),
        ])

    def test_count_refuses_a_relative_ledger(self):
        self.ledger = Path("gates.md")
        refused = self.count()
        self.assertEqual(refused[0], 1)
        self.assertIn("not absolute", refused[2])

    def test_count_requires_latest_target_row_and_checks_file_parity(self):
        absent = self.count()
        self.assertEqual(absent[0], 1)
        self.assertIn("holds no gate ledger", absent[2])
        self.ledger.write_text("", encoding="utf-8")
        no_row = self.count()
        self.assertEqual(no_row[0], 1)
        self.assertIn("no completed target-bearing deploy row", no_row[2])
        self.deploy_row("example")
        rows = self.ledger.read_text(encoding="utf-8").splitlines()
        self.ledger.write_text(rows[0] + "\n", encoding="utf-8")
        self.deploy_row("example")
        rows = self.ledger.read_text(encoding="utf-8").splitlines()
        self.ledger.write_text(rows[0] + "\n" + rows[1].replace("skills=example", "skills=missing") + "\n", encoding="utf-8")
        self.assertIn("absent from the deploy row head", self.count()[2])
        self.ledger.write_text("\n".join(rows) + "\n", encoding="utf-8")
        self.assertEqual(self.count(), (0, "tracked=2 installed=2 drifted=0\n", ""))
        (self.install / "SKILL.md").write_text("tampered\n", encoding="utf-8")
        mismatch = self.count()
        self.assertEqual(mismatch[0], 1)
        self.assertEqual(mismatch[1], "tracked=2 installed=2 drifted=1\n")

    def test_count_uses_selected_deploy_head_instead_of_checkout_head(self):
        self.deploy_row("example")
        deployed = support.git(self.repo, "rev-parse", "HEAD")
        (self.skill / "script.py").write_text("new checkout\n", encoding="utf-8")
        support.git(self.repo, "add", "skills/example/script.py")
        support.git(self.repo, "commit", "-qm", "new checkout head")
        self.assertEqual(self.count(), (0, "tracked=2 installed=2 drifted=0\n", ""))
        self.assertNotEqual(deployed, support.git(self.repo, "rev-parse", "HEAD"))

    def test_count_refuses_a_symlinked_subdirectory_in_the_installed_tree(self):
        self.deploy_row("example")
        outside = self.tmp / "outside"
        outside.mkdir()
        (outside / "payload.py").write_text("elsewhere\n", encoding="utf-8")
        (self.install / "linked").symlink_to(outside, target_is_directory=True)
        result = self.count()
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], "tracked=2 installed=3 drifted=0\n")

    def test_count_flags_installed_mode_drift(self):
        (self.skill / "script.py").chmod(0o755)
        support.git(self.repo, "add", "skills/example")
        support.git(self.repo, "commit", "-qm", "executable script")
        (self.install / "script.py").chmod(0o755)
        self.deploy_row("example")
        self.assertEqual(self.count(), (0, "tracked=2 installed=2 drifted=0\n", ""))
        (self.install / "script.py").chmod(0o644)
        result = self.count()
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], "tracked=2 installed=2 drifted=1\n")


if __name__ == "__main__":
    unittest.main()

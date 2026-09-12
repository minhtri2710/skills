#!/usr/bin/env python3
"""Unit tests for relaunch_entry_check.py's CLI paths."""
from __future__ import annotations

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import relaunch_entry_check  # noqa: E402


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True,
                   capture_output=True, text=True)


class RelaunchEntryCheckTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir="/private/tmp")
        self.tmp = Path(self._tmp.name)
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.email", "t@example.invalid")
        git(self.repo, "config", "user.name", "test")
        self.skill = self.repo / "skills" / "example"
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("skill\n", encoding="utf-8")
        (self.skill / "script.py").write_text("print('ok')\n", encoding="utf-8")
        git(self.repo, "add", "skills/example")
        git(self.repo, "commit", "-qm", "skill")
        self.install = self.tmp / "installed"
        self.install.mkdir()
        for name in ("SKILL.md", "script.py"):
            (self.install / name).write_bytes((self.skill / name).read_bytes())
        (self.install / "__pycache__").mkdir()
        (self.install / "__pycache__" / "ignored.pyc").write_bytes(b"runtime")
        self.addCleanup(self._tmp.cleanup)

    def run_main(self, argv: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = relaunch_entry_check.main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

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

        code, stdout, stderr = self.run_main([
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
        altered.write_text(
            "## R4 — BĐS services page [G164]",
            encoding="utf-8",
        )

        code, stdout, stderr = self.run_main([
            "--verify", "--block-file", str(altered), "--source-file", str(source),
        ])

        self.assertNotEqual(code, 0)
        self.assertEqual(stdout, "")
        self.assertIn("not a verbatim contiguous block", stderr)

    def test_count_returns_tracked_installed_and_hash_mismatch_triple(self):
        code, stdout, stderr = self.run_main([
            "--count", "--repo", str(self.repo), "--head", "HEAD",
            "--skill-path", "skills/example", "--installed-path", str(self.install),
        ])

        self.assertEqual(code, 0)
        self.assertEqual(stdout, "tracked=2 installed=2 hash-mismatches=0\n")
        self.assertEqual(stderr, "")


if __name__ == "__main__":
    unittest.main()

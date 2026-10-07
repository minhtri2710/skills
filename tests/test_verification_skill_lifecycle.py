#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

FIXTURE = Path(__file__).resolve().parents[1] / "skills" / "verification-skill-lifecycle" / "fixtures" / "cli_app.py"
OWNER = "fixture-owner"


class VerificationSkillLifecycleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Path(__file__).resolve().parents[1]
        self.temp_parent = Path(tempfile.gettempdir()).resolve(strict=True)
        if self.repo == self.temp_parent or self.repo in self.temp_parent.parents:
            self.fail("temporary workspace parent is inside the repository")
        self.temp = tempfile.TemporaryDirectory(prefix="verification-skill-lifecycle-", dir=self.temp_parent)
        self.base = Path(self.temp.name).resolve(strict=True)
        if self.base == self.repo or self.repo in self.base.parents or self.base in self.repo.parents:
            self.temp.cleanup()
            self.fail("temporary workspace overlaps the repository")

        self.workspace = self.base / "workspace"
        self.invocation = self.base / "invocation"
        self.home = self.base / "home"
        self.tmp = self.base / "tmp"
        self.evidence = self.base / "evidence.jsonl"
        for path in (self.workspace, self.invocation, self.home, self.tmp):
            path.mkdir()
        self.env = {
            "PATH": os.defpath,
            "HOME": str(self.home),
            "TMPDIR": str(self.tmp),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        self.assertNotIn(self.workspace, self.evidence.parents)

    def tearDown(self) -> None:
        if self.base.is_symlink():
            self.fail("refusing temporary cleanup through a symlink")
        checked_base = self.base.resolve(strict=True)
        if checked_base != self.base or checked_base.parent != self.temp_parent:
            self.fail("refusing temporary cleanup outside its checked parent")
        if checked_base == self.repo or self.repo in checked_base.parents or checked_base in self.repo.parents:
            self.fail("refusing temporary cleanup that overlaps the repository")
        self.temp.cleanup()

    def command(self, run_id: str, action: str, *args: str, owner: str = OWNER) -> subprocess.CompletedProcess[str]:
        argv = [
            sys.executable,
            "-I",
            "-B",
            str(FIXTURE),
            "--workspace",
            str(self.workspace),
            "--run-id",
            run_id,
            "--owner",
            owner,
            action,
            *args,
        ]
        result = subprocess.run(
            argv,
            cwd=self.invocation,
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )
        record = {
            "action": action,
            "argv": argv[4:],
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
        with self.evidence.open("a", encoding="utf-8") as evidence:
            evidence.write(json.dumps(record, sort_keys=True) + "\n")
        return result

    def records(self) -> list[dict[str, object]]:
        self.assertTrue(self.evidence.is_file())
        return [json.loads(line) for line in self.evidence.read_text(encoding="utf-8").splitlines()]

    def test_cli_create_doctor_show_and_owned_cleanup_preserve_evidence(self) -> None:
        run_id = "success"
        run_dir = self.workspace / f"run-{run_id}"
        before = self.command(run_id, "doctor")
        self.assertEqual(before.returncode, 0, before.stderr)
        self.assertEqual(json.loads(before.stdout), {"run_id": run_id, "status": "ready", "tasks": 0})

        created = self.command(run_id, "create", "--title", "Keep evidence", "--body", "saved by the CLI")
        self.assertEqual(created.returncode, 0, created.stderr)
        self.assertEqual(json.loads(created.stdout), {"id": 1, "title": "Keep evidence"})

        health = self.command(run_id, "doctor")
        self.assertEqual(health.returncode, 0, health.stderr)
        self.assertEqual(json.loads(health.stdout), {"run_id": run_id, "status": "healthy", "tasks": 1})
        shown = self.command(run_id, "show", "--title", "Keep evidence")
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertEqual(json.loads(shown.stdout), {"body": "saved by the CLI", "id": 1, "title": "Keep evidence"})

        before_cleanup = self.records()
        self.assertEqual([record["action"] for record in before_cleanup], ["doctor", "create", "doctor", "show"])
        self.assertTrue(run_dir.is_dir())
        self.assertTrue(self.evidence.is_file())
        self.assertNotIn(run_dir, self.evidence.parents)

        cleanup = self.command(run_id, "cleanup")
        self.assertEqual(cleanup.returncode, 0, cleanup.stderr)
        self.assertEqual(json.loads(cleanup.stdout), {"removed": True, "run_id": run_id})
        self.assertFalse(run_dir.exists())
        after_cleanup = self.records()
        self.assertEqual(after_cleanup[: len(before_cleanup)], before_cleanup)
        self.assertEqual(after_cleanup[-1]["action"], "cleanup")
        self.assertTrue(self.evidence.is_file())

    def test_failed_cli_action_is_doctored_and_evidence_survives_cleanup(self) -> None:
        run_id = "failed"
        run_dir = self.workspace / f"run-{run_id}"
        before = self.command(run_id, "doctor")
        self.assertEqual(before.returncode, 0, before.stderr)
        self.assertEqual(json.loads(before.stdout)["status"], "ready")

        failed = self.command(
            run_id,
            "create",
            "--title",
            "Persisted before failure",
            "--body",
            "side effect",
            "--fail-after-save",
        )
        self.assertEqual(failed.returncode, 1)
        self.assertEqual(json.loads(failed.stdout), {"id": 1, "title": "Persisted before failure"})
        self.assertTrue(run_dir.is_dir())

        health = self.command(run_id, "doctor")
        self.assertEqual(health.returncode, 0, health.stderr)
        self.assertEqual(json.loads(health.stdout), {"run_id": run_id, "status": "healthy", "tasks": 1})
        shown = self.command(run_id, "show", "--title", "Persisted before failure")
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertEqual(json.loads(shown.stdout), {"body": "side effect", "id": 1, "title": "Persisted before failure"})

        before_cleanup = self.records()
        actions = [record["action"] for record in before_cleanup]
        failed_at = actions.index("create")
        self.assertEqual(actions[failed_at + 1], "doctor")
        self.assertEqual(before_cleanup[failed_at]["returncode"], 1)
        self.assertTrue(self.evidence.is_file())

        cleanup = self.command(run_id, "cleanup")
        self.assertEqual(cleanup.returncode, 0, cleanup.stderr)
        self.assertFalse(run_dir.exists())
        after_cleanup = self.records()
        self.assertEqual(after_cleanup[: len(before_cleanup)], before_cleanup)
        self.assertEqual(after_cleanup[-1]["action"], "cleanup")
        self.assertTrue(self.evidence.is_file())

    def test_cli_rejects_workspace_that_overlaps_its_repository(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-I",
                "-B",
                str(FIXTURE),
                "--workspace",
                str(self.repo),
                "--run-id",
                "must-not-exist",
                "--owner",
                OWNER,
                "create",
                "--title",
                "No repository write",
            ],
            cwd=self.invocation,
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertFalse((self.repo / "run-must-not-exist").exists())
        self.assertIn("workspace must not overlap", result.stderr)

    def test_cleanup_refuses_wrong_owner_unowned_symlink_and_traversal_targets(self) -> None:
        owned_run = self.workspace / "run-owner-check"
        created = self.command("owner-check", "create", "--title", "Owned")
        self.assertEqual(created.returncode, 0, created.stderr)
        wrong_owner = self.command("owner-check", "cleanup", owner="someone-else")
        self.assertEqual(wrong_owner.returncode, 1)
        self.assertTrue(owned_run.is_dir())
        self.assertTrue((owned_run / "tasks.json").is_file())

        unowned = self.workspace / "run-unowned"
        unowned.mkdir()
        unowned_file = unowned / "keep.txt"
        unowned_file.write_text("not owned", encoding="utf-8")
        refused_unowned = self.command("unowned", "cleanup")
        self.assertEqual(refused_unowned.returncode, 1)
        self.assertTrue(unowned_file.is_file())

        outside = self.base / "outside"
        outside.mkdir()
        outside_file = outside / "keep.txt"
        outside_file.write_text("outside workspace", encoding="utf-8")
        refused_traversal = self.command("../../../outside", "cleanup")
        self.assertEqual(refused_traversal.returncode, 1)
        self.assertTrue(outside_file.is_file())

        link = self.workspace / "run-link"
        link.symlink_to(outside, target_is_directory=True)
        refused_link = self.command("link", "cleanup")
        self.assertEqual(refused_link.returncode, 1)
        self.assertTrue(outside_file.is_file())


if __name__ == "__main__":
    unittest.main()

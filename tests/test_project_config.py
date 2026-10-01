#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "herdr-delivery-workflow"
SCRIPT = SKILL / "scripts" / "project_config.py"
sys.path.insert(0, str(SKILL / "scripts"))

import project_config  # noqa: E402

_FULL = {
    "engineer-kind": "claude",
    "reviewer-kind": "claude",
    "engineer-fallback": "pi",
    "reviewer-fallback": "pi",
    "engineer-args": ["--model", "m1", "--permission-mode", "auto", ""],
    "reviewer-args": ["--model", "m1"],
    "engineer-fallback-args": ["--approve"],
    "reviewer-fallback-args": [],
    "checks-light": ["python -m unittest"],
    "checks-heavy": ["python -m unittest discover"],
    "ci": {"trigger": "push", "workflows": [".github/workflows/ci.yml"]},
    "local-ops": ["make dev"],
    "lane-defaults": {"docs/": "tiny", "src/": "high-risk"},
    "target-line": "main",
    "always-gate": ["push"],
    "worker-cap": 3,
    "provenance": {"file": ["why"], "worker-cap": ["why"]},
}


class ProjectConfigTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "config.json"

    def _write(self, content) -> Path:
        self.path.write_text(
            content if isinstance(content, str) else json.dumps(content), encoding="utf-8"
        )
        return self.path

    def test_accepts_a_config_with_every_key(self):
        self.assertEqual(project_config.load(self._write(_FULL)), _FULL)

    def test_refuses_each_class_naming_the_path_and_the_key(self):
        cases = [
            ({**_FULL, "engineer-arg": []}, "engineer-arg: unknown key"),
            ({**_FULL, "engineer-args": "--model m1"}, "engineer-args: must be an array of strings"),
            ({**_FULL, "worker-cap": True}, "worker-cap: must be an integer >= 1"),
            ({**_FULL, "worker-cap": 0}, "worker-cap: must be an integer >= 1"),
            ({**_FULL, "ci": {"trigger": "none", "workflows": ["ci.yml"]}}, "ci: workflows must be empty"),
            ({**_FULL, "provenance": {"engineer-arg": ["x"]}}, "provenance.engineer-arg: unknown key"),
            ('{"worker-cap": 1, "worker-cap": 2}', "duplicate key 'worker-cap'"),
            ('{"ci": {"trigger": "pr", "trigger": "pr"}}', "duplicate key 'trigger'"),
            ("[]", "top level must be an object"),
            ("{", "Expecting property name"),
        ]
        for content, message in cases:
            with self.subTest(message=message):
                with self.assertRaises(ValueError) as caught:
                    project_config.load(self._write(content))
                self.assertTrue(
                    str(caught.exception).startswith(f"{self.path}: "), str(caught.exception)
                )
                self.assertIn(message, str(caught.exception))
        with self.assertRaises(ValueError) as caught:
            project_config.load(self.path.with_name("absent.json"))
        self.assertIn("absent.json", str(caught.exception))

    def _check(self, path: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--check", str(path)],
            capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL,
        )

    def test_check_prints_ok_or_one_refusal_line(self):
        ok = self._check(self._write(_FULL))
        self.assertEqual((ok.returncode, ok.stdout, ok.stderr), (0, f"ok: {self.path}\n", ""))
        refused = self._check(self._write({"nope": 1}))
        self.assertEqual(
            (refused.returncode, refused.stdout, refused.stderr),
            (1, "", f"{self.path}: nope: unknown key\n"),
        )

    def test_the_shipped_template_loads(self):
        project_config.load(SKILL / "templates" / "config.json")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Tests for the human-step-wizard bash library (the part above the STAGES marker)."""
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parents[1] / "skills" / "human-step-wizard" / "scripts" / "wizard-template.sh"


def library() -> str:
    text = TEMPLATE.read_text()
    marker = text.index("# STAGES:")
    return text[:marker]


class WizardTemplateTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.lib = self.dir / "lib.sh"
        self.lib.write_text(library())

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_bash(self, body: str, stdin: str = "") -> subprocess.CompletedProcess[str]:
        script = f"source {self.lib}\n{body}\n"
        return subprocess.run(
            ["bash", "-c", script], cwd=self.dir, input=stdin, capture_output=True, text=True, env={"PATH": "/usr/bin:/bin", "ENV_FILE": ".env"}
        )

    def test_library_parses(self) -> None:
        self.assertEqual(subprocess.run(["bash", "-n", str(TEMPLATE)], capture_output=True).returncode, 0)

    def test_write_env_upserts_without_duplicating(self) -> None:
        result = self.run_bash('write_env API_KEY first\nwrite_env OTHER x\nwrite_env API_KEY second')
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = (self.dir / ".env").read_text().splitlines()
        self.assertEqual(lines.count("API_KEY=second"), 1)
        self.assertNotIn("API_KEY=first", lines)
        self.assertIn("OTHER=x", lines)

    def test_ask_keeps_existing_value_on_empty_input(self) -> None:
        (self.dir / ".env").write_text("TOKEN=kept\n")
        result = self.run_bash('ask TOKEN "Paste:"\nprintf "%s" "$TOKEN"', stdin="\n")
        self.assertEqual(result.stdout.strip().rsplit(" ", 1)[-1], "kept")

    def test_ask_takes_new_input(self) -> None:
        result = self.run_bash('ask TOKEN "Paste:"\nprintf "|%s|" "$TOKEN"', stdin="fresh\n")
        self.assertIn("|fresh|", result.stdout)

    def test_ask_refuses_empty_required_input_and_reasks(self) -> None:
        result = self.run_bash('ask TOKEN "Paste:"\nprintf "|%s|" "$TOKEN"', stdin="\nfresh\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("|fresh|", result.stdout)

    def test_ask_eof_without_value_names_key_and_fails(self) -> None:
        result = self.run_bash('ask TOKEN "Paste:"', stdin="")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("TOKEN", result.stderr)

    def test_set_secret_records_skip_when_gh_is_absent(self) -> None:
        result = self.run_bash('set_secret NAME value\nprintf "%s" "${SKIPPED[0]}"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("GitHub secret NAME", result.stdout)
        self.assertNotIn("value", result.stdout.split("GitHub secret NAME")[-1])


if __name__ == "__main__":
    unittest.main()

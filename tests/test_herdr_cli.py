"""Focused tests for the shared Herdr subprocess boundary."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import herdr_cli  # noqa: E402


class HerdrCliTest(unittest.TestCase):
    def test_run_uses_the_shared_subprocess_contract(self) -> None:
        completed = subprocess.CompletedProcess(
            ["herdr", "agent", "list"], 0, stdout="{}", stderr=""
        )
        with mock.patch.object(herdr_cli.subprocess, "run", return_value=completed) as run:
            result = herdr_cli.run(["agent", "list"], timeout=4.5)

        self.assertIs(result, completed)
        run.assert_called_once_with(
            ["herdr", "agent", "list"],
            capture_output=True,
            text=True,
            check=False,
            timeout=4.5,
        )

    def test_oserror_becomes_named_unavailable_error(self) -> None:
        with mock.patch.object(
            herdr_cli.subprocess,
            "run",
            side_effect=OSError("binary not found"),
        ):
            with self.assertRaisesRegex(
                herdr_cli.HerdrUnavailable,
                r"herdr agent list.*binary not found",
            ):
                herdr_cli.run(["agent", "list"])

    def test_timeout_becomes_named_unavailable_error(self) -> None:
        with mock.patch.object(
            herdr_cli.subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired(["herdr", "agent", "prompt", "lead"], 30.0),
        ):
            with self.assertRaisesRegex(
                herdr_cli.HerdrUnavailable,
                r"herdr agent prompt lead.*timed out",
            ):
                herdr_cli.run(["agent", "prompt", "lead"])


if __name__ == "__main__":
    unittest.main()

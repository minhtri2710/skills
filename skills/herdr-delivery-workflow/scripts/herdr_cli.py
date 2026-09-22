"""Shared subprocess boundary for workflow calls to Herdr."""
from __future__ import annotations

import subprocess


class HerdrUnavailable(RuntimeError):
    """Herdr could not be invoked or did not finish before the deadline."""


def _subcommand(args: list[str]) -> str:
    return "herdr " + " ".join(args[:3]) if args else "herdr"


def run(args: list[str], *, timeout: float = 30.0) -> subprocess.CompletedProcess[str]:
    """Run one Herdr subcommand with bounded, captured execution."""
    command = ["herdr", *args]
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise HerdrUnavailable(f"{_subcommand(args)} timed out after {timeout} seconds") from exc
    except OSError as exc:
        raise HerdrUnavailable(f"{_subcommand(args)} unavailable: {exc}") from exc

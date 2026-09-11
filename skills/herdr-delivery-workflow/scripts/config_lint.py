#!/usr/bin/env python3
"""Check reviewer fallback independence in a project config."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

MODEL_RE = re.compile(r"--model\s+(\S+)")
SETTING_RE = re.compile(r"^-\s+([^:]+):\s*(.*)$")


def parse_config(path: Path) -> dict[str, str]:
    settings: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = SETTING_RE.match(line)
        if match:
            settings[match.group(1).strip()] = match.group(2).strip()
    return settings


def model_for(settings: dict[str, str], key: str) -> str | None:
    value = settings.get(key, "")
    match = MODEL_RE.search(value)
    return match.group(1) if match else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint reviewer fallback independence.")
    parser.add_argument("--config", required=True, type=Path,
                        help="path to the project config.md")
    args = parser.parse_args(argv)
    settings = parse_config(args.config)

    reviewer_fallback = settings.get("reviewer-fallback")
    engineer_kind = settings.get("engineer-kind")
    if not reviewer_fallback or not engineer_kind or reviewer_fallback != engineer_kind:
        print("OK: reviewer-fallback and engineer-kind are distinct")
        return 0

    reviewer_model = model_for(settings, "reviewer-fallback-args")
    engineer_model = model_for(settings, "engineer-args")
    conflict = reviewer_model is None or reviewer_model == engineer_model
    if conflict:
        reason = ("missing --model in reviewer-fallback-args"
                  if reviewer_model is None else
                  "reviewer-fallback-args --model matches engineer-args --model")
        print("CONFLICT: reviewer-fallback=engineer-kind; "
              f"reviewer-fallback-args and engineer-args ({reason})")

    engineer_fallback_model = model_for(settings, "engineer-fallback-args")
    warning = reviewer_model is not None and reviewer_model == engineer_fallback_model
    if warning:
        print("WARNING: reviewer-fallback=engineer-kind; "
              "reviewer-fallback-args --model matches engineer-fallback-args --model")
    if not conflict and not warning:
        print("OK: reviewer-fallback=engineer-kind uses a distinct reviewer-fallback-args --model")

    return 1 if conflict else 0


if __name__ == "__main__":
    raise SystemExit(main())

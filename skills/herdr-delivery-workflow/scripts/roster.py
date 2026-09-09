#!/usr/bin/env python3
"""Print the compact roster view from ``herdr agent list`` JSON."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


def format_roster(payload: dict[str, Any], workspace: str | None = None) -> list[str]:
    """Return one compact roster line for each matching agent."""
    try:
        agents = payload["result"]["agents"]
    except (KeyError, TypeError) as exc:
        raise ValueError("agent-list JSON lacks result.agents") from exc
    if not isinstance(agents, list):
        raise ValueError("agent-list JSON result.agents is not a list")

    lines = []
    for agent in agents:
        if not isinstance(agent, dict):
            raise ValueError("agent-list JSON contains a non-object agent")
        if workspace is not None and agent.get("workspace_id") != workspace:
            continue
        try:
            pane_id = agent["pane_id"]
            kind = agent["agent"]
            state = agent["agent_status"]
        except KeyError as exc:
            raise ValueError(f"agent record lacks {exc.args[0]}") from exc
        lines.append(f"{pane_id} {agent.get('name') or '-'} {kind} {state}")
    return lines


def _agent_list_json(use_stdin: bool) -> str:
    if use_stdin:
        return sys.stdin.read()
    try:
        proc = subprocess.run(
            ["herdr", "agent", "list"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise RuntimeError(f"could not run herdr agent list: {exc}") from exc
    if proc.returncode:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise RuntimeError(f"herdr agent list failed: {detail or proc.returncode}")
    return proc.stdout


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="compact herdr agent roster")
    parser.add_argument("--workspace", metavar="ID", help="only show this workspace")
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="read agent-list JSON from stdin instead of running `herdr agent list`",
    )
    args = parser.parse_args(argv)

    try:
        payload = json.loads(_agent_list_json(args.stdin))
        lines = format_roster(payload, args.workspace)
    except (json.JSONDecodeError, ValueError, RuntimeError) as exc:
        print(f"roster: {exc}", file=sys.stderr)
        return 1

    if lines:
        print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

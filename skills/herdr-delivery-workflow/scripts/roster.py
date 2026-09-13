#!/usr/bin/env python3
"""Print the compact roster view from ``herdr agent list`` JSON."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


_SETTLED_STATES = frozenset({"idle", "done"})


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


def _load_previous_sample(path: str) -> dict[str, dict[str, Any]]:
    try:
        raw = json.loads(Path(path).read_text())
    except OSError as exc:
        raise RuntimeError(f"could not read previous sample: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"previous sample is not valid JSON: {exc}") from exc

    if not isinstance(raw, dict) or not isinstance(raw.get("peers"), dict):
        raise ValueError("previous sample must contain a peers object")

    samples: dict[str, dict[str, Any]] = {}
    for name, sample in raw["peers"].items():
        if not isinstance(name, str) or not isinstance(sample, dict):
            raise ValueError("previous sample peers must map names to objects")
        state = sample.get("state")
        progress_mtime = sample.get("progress_mtime")
        if not isinstance(state, str):
            raise ValueError(f"previous sample for {name!r} lacks string state")
        if isinstance(progress_mtime, bool) or not isinstance(
            progress_mtime, (int, float)
        ):
            raise ValueError(f"previous sample for {name!r} lacks numeric progress_mtime")
        samples[name] = {
            "state": state,
            "progress_mtime": float(progress_mtime),
        }
    return samples


def _peer_specs(raw_peers: list[str] | None) -> dict[str, tuple[Path, Path]]:
    specs: dict[str, tuple[Path, Path]] = {}
    for raw_peer in raw_peers or []:
        name, name_separator, paths = raw_peer.partition(":")
        report_path, path_separator, progress_path = paths.rpartition(":")
        if not name_separator or not path_separator or not name or not report_path or not progress_path:
            raise ValueError(
                "peer must use NAME:REPORT_PATH:PROGRESS_PATH"
            )
        if name in specs:
            raise ValueError(f"duplicate peer specification: {name}")
        specs[name] = (Path(report_path), Path(progress_path))
    return specs


def format_stalled_roster(
    payload: dict[str, Any],
    peer_specs: dict[str, tuple[Path, Path]],
    previous_sample: dict[str, dict[str, Any]],
    stale_after: float,
    workspace: str | None = None,
    now: float | None = None,
) -> list[str]:
    """Return settled peers stalled across two supplied samples.

    A peer must be settled in both samples, have no report, and have a
    progress mtime that did not advance and is older than ``stale_after``.
    Missing or unreadable progress files fail closed and are not stalls.
    """
    if stale_after < 0:
        raise ValueError("stale-after must be non-negative")
    if now is None:
        now = time.time()

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
        name = agent.get("name")
        if not isinstance(name, str) or name not in peer_specs:
            continue
        try:
            pane_id = agent["pane_id"]
            kind = agent["agent"]
            state = agent["agent_status"]
        except KeyError as exc:
            raise ValueError(f"agent record lacks {exc.args[0]}") from exc
        if state not in _SETTLED_STATES:
            continue

        prior = previous_sample.get(name)
        if prior is None or prior["state"] in _SETTLED_STATES:
            continue
        report_path, progress_path = peer_specs[name]
        try:
            report_path.stat()
        except FileNotFoundError:
            pass
        except OSError:
            continue
        else:
            continue
        try:
            current_mtime = progress_path.stat().st_mtime
        except OSError:
            continue
        if current_mtime > prior["progress_mtime"]:
            continue
        if now - current_mtime <= stale_after:
            continue
        lines.append(f"{pane_id} {name or '-'} {kind} STALLED")
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
    parser.add_argument(
        "--stalled",
        action="store_true",
        help="report peers stalled across the supplied sample interval",
    )
    parser.add_argument(
        "--peer",
        action="append",
        metavar="NAME:REPORT_PATH:PROGRESS_PATH",
        help="peer paths; repeat this option for each peer",
    )
    parser.add_argument(
        "--previous-sample",
        metavar="PATH",
        help="JSON file containing the prior peer state and progress mtime",
    )
    parser.add_argument(
        "--stale-after",
        type=float,
        default=60.0,
        metavar="SECONDS",
        help="minimum progress-file age for a stall (default: 60)",
    )
    args = parser.parse_args(argv)

    try:
        payload = json.loads(_agent_list_json(args.stdin))
        if args.stalled:
            if not args.peer:
                raise ValueError("--stalled requires at least one --peer")
            if args.previous_sample is None:
                raise ValueError("--stalled requires --previous-sample")
            lines = format_stalled_roster(
                payload,
                _peer_specs(args.peer),
                _load_previous_sample(args.previous_sample),
                args.stale_after,
                args.workspace,
            )
        else:
            lines = format_roster(payload, args.workspace)
    except (json.JSONDecodeError, ValueError, RuntimeError) as exc:
        print(f"roster: {exc}", file=sys.stderr)
        return 1

    if lines:
        print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

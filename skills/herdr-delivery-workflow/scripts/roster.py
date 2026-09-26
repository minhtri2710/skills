#!/usr/bin/env python3
"""Print the compact roster view from ``herdr agent list`` JSON."""
from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
import time
from pathlib import Path
from typing import Any

import herdr_cli


_SETTLED_STATES = frozenset({"idle", "done"})
_ROLES = ("engineer", "reviewer")
_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_KEY_RE = re.compile(r"^\s*-\s*([a-z][a-z-]*):[ \t]*(.*?)\s*$", re.MULTILINE)


def _agents(payload: dict[str, Any]) -> list[Any]:
    try:
        agents = payload["result"]["agents"]
    except (KeyError, TypeError) as exc:
        raise ValueError("agent-list JSON lacks result.agents") from exc
    if not isinstance(agents, list):
        raise ValueError("agent-list JSON result.agents is not a list")
    return agents


def format_roster(payload: dict[str, Any], workspace: str | None = None) -> list[str]:
    """Return one compact roster line for each matching agent."""
    agents = _agents(payload)

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
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
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


def format_never_started_roster(
    payload: dict[str, Any],
    peer_specs: dict[str, tuple[Path, Path]],
    never_started: set[str],
    workspace: str | None = None,
) -> list[str]:
    """Return explicitly identified never-prompted peers.

    The caller supplies the no-prompt evidence for each named peer. The
    roster still requires a settled current seat, an absent report, and an
    absent progress file. Pane text and token counters are deliberately not
    parsed here: a token counter may corroborate the explicit evidence, but
    cannot be the verdict.
    """
    lines = []
    for agent in _agents(payload):
        if not isinstance(agent, dict):
            raise ValueError("agent-list JSON contains a non-object agent")
        if workspace is not None and agent.get("workspace_id") != workspace:
            continue
        name = agent.get("name")
        if not isinstance(name, str) or name not in never_started:
            continue
        if name not in peer_specs:
            raise ValueError(f"never-started peer {name!r} lacks a peer specification")
        try:
            pane_id = agent["pane_id"]
            kind = agent["agent"]
            state = agent["agent_status"]
        except KeyError as exc:
            raise ValueError(f"agent record lacks {exc.args[0]}") from exc
        if state not in _SETTLED_STATES:
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
            progress_path.stat()
        except FileNotFoundError:
            pass
        except OSError:
            continue
        else:
            continue
        lines.append(f"{pane_id} {name} {kind} NEVER-STARTED")
    return lines


def format_stalled_roster(
    payload: dict[str, Any],
    peer_specs: dict[str, tuple[Path, Path]],
    previous_sample: dict[str, dict[str, Any]],
    stale_after: float,
    workspace: str | None = None,
    now: float | None = None,
) -> list[str]:
    """Return peers settled now after a prior non-settled sample that stalled.

    A peer must be settled now after a prior non-settled sample, have no report,
    and have a progress mtime that did not advance and is older than
    ``stale_after``. Missing or unreadable progress files fail closed and are
    not stalls.
    """
    if stale_after < 0:
        raise ValueError("stale-after must be non-negative")
    if now is None:
        now = time.time()

    agents = _agents(payload)

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


def _config_keys(path: str) -> dict[str, str]:
    """Read `- key: value` lines; comments are provenance and never read."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"could not read config: {exc}") from exc
    return dict(_KEY_RE.findall(_COMMENT_RE.sub("", text)))


def _model(args: list[str]) -> str | None:
    for i, arg in enumerate(args):
        if arg == "--model" and i + 1 < len(args):
            return args[i + 1]
        if arg.startswith("--model="):
            return arg.split("=", 1)[1]
    return None


def _expected(keys: dict[str, str], role: str) -> list[tuple[str, str | None]]:
    kind = keys.get(f"{role}-kind")
    if not kind:
        raise ValueError(f"config lacks {role}-kind")
    expected = [(kind, _model(shlex.split(keys.get(f"{role}-args", ""))))]
    fallback = keys.get(f"{role}-fallback")
    if fallback:
        expected.append((fallback, _model(shlex.split(keys.get(f"{role}-fallback-args", "")))))
    return expected


def _seat_specs(raw_seats: list[str] | None) -> dict[str, str]:
    seats: dict[str, str] = {}
    for raw in raw_seats or []:
        name, _, role = raw.partition(":")
        if not name or role not in _ROLES:
            raise ValueError("seat must use NAME:engineer or NAME:reviewer")
        if name in seats:
            raise ValueError(f"duplicate seat specification: {name}")
        seats[name] = role
    return seats


def _launch_args(pane_id: str, kind: str) -> list[str] | None:
    """Arguments after the seat's own binary, when its foreground process exposes them."""
    try:
        proc = herdr_cli.run(["pane", "process-info", "--pane", pane_id])
    except herdr_cli.HerdrUnavailable as exc:
        raise RuntimeError(f"could not run herdr pane process-info: {exc}") from exc
    if proc.returncode:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise RuntimeError(f"herdr pane process-info {pane_id} failed: {detail or proc.returncode}")
    try:
        processes = json.loads(proc.stdout)["result"]["process_info"]["foreground_processes"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ValueError(f"process-info JSON for {pane_id} lacks foreground_processes") from exc
    for process in processes:
        if not isinstance(process, dict):
            continue
        argv = process.get("argv")
        if isinstance(argv, list):
            for i, arg in enumerate(argv):
                if isinstance(arg, str) and Path(arg).name == kind:
                    return [str(a) for a in argv[i + 1:]]
        argv0 = process.get("argv0")
        if isinstance(argv0, str) and Path(argv0).name == kind:
            return None
    raise ValueError(f"no {kind} process in pane {pane_id}")


def format_drift_roster(
    payload: dict[str, Any],
    keys: dict[str, str],
    seats: dict[str, str],
    workspace: str | None = None,
) -> tuple[list[str], bool]:
    """Return DRIFT lines, an UNVERIFIABLE line for a matching kind with an unbound model, and whether any UNVERIFIABLE line was produced.

    Only the kind and the model are compared: a charter may add tightenings
    (an allowlist, a disallowed tool) that are not drift.
    """
    lines = []
    unverifiable = False
    unseen = set(seats)
    for agent in _agents(payload):
        if not isinstance(agent, dict):
            raise ValueError("agent-list JSON contains a non-object agent")
        if workspace is not None and agent.get("workspace_id") != workspace:
            continue
        name = agent.get("name")
        if not isinstance(name, str) or name not in seats:
            continue
        unseen.discard(name)
        try:
            pane_id = agent["pane_id"]
            kind = agent["agent"]
        except KeyError as exc:
            raise ValueError(f"agent record lacks {exc.args[0]}") from exc
        role = seats[name]
        expected = _expected(keys, role)
        launch_args = _launch_args(pane_id, kind)
        model = _model(launch_args) if launch_args is not None else None
        matching_kinds = [(k, m) for k, m in expected if kind == k]
        if matching_kinds and launch_args is None:
            if any(m is None for _, m in matching_kinds):
                continue
            want = " or ".join(f"{k} --model {m or '-'}" for k, m in expected)
            lines.append(
                f"{pane_id} {name} {kind} UNVERIFIABLE role={role} "
                f"reason=model-unavailable expected={want}"
            )
            unverifiable = True
            continue
        if any(m is None or model == m for _, m in matching_kinds):
            continue
        want = " or ".join(f"{k} --model {m or '-'}" for k, m in expected)
        lines.append(
            f"{pane_id} {name} {kind} DRIFT role={role} running={kind} --model {model or '-'} expected={want}"
        )
    if unseen:
        raise ValueError(f"no live seat named {', '.join(sorted(unseen))}")
    return lines, unverifiable


def _agent_list_json(use_stdin: bool) -> str:
    if use_stdin:
        return sys.stdin.read()
    try:
        proc = herdr_cli.run(["agent", "list"])
    except herdr_cli.HerdrUnavailable as exc:
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
        "--never-started",
        action="append",
        metavar="NAME",
        help="report an explicitly identified never-prompted peer",
    )
    parser.add_argument(
        "--drift",
        metavar="CONFIG",
        help="report named seats whose kind or --model differs from this config.md's keys",
    )
    parser.add_argument(
        "--seat",
        action="append",
        metavar="NAME:ROLE",
        help="seat and role (engineer or reviewer) for --drift; repeat per seat",
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

    exit_code = 0
    try:
        payload = json.loads(_agent_list_json(args.stdin))
        if sum(map(bool, (args.stalled, args.never_started, args.drift))) > 1:
            raise ValueError("--stalled, --never-started and --drift are mutually exclusive")
        if args.drift:
            if not args.seat:
                raise ValueError("--drift requires at least one --seat")
            lines, unverifiable = format_drift_roster(
                payload, _config_keys(args.drift), _seat_specs(args.seat), args.workspace
            )
            exit_code = int(unverifiable)
        elif args.never_started:
            if not args.peer:
                raise ValueError("--never-started requires at least one --peer")
            lines = format_never_started_roster(
                payload,
                _peer_specs(args.peer),
                set(args.never_started),
                args.workspace,
            )
        elif args.stalled:
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
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

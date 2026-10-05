#!/usr/bin/env python3
"""Print the compact roster view from ``herdr agent list`` JSON."""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import herdr_cli
import project_config


_SETTLED_STATES = frozenset({"idle", "done"})
_ROLES = ("engineer", "reviewer")


def _agents(payload: dict[str, Any]) -> list[Any]:
    try:
        agents = payload["result"]["agents"]
    except (KeyError, TypeError) as exc:
        raise ValueError("agent-list JSON lacks result.agents") from exc
    if not isinstance(agents, list):
        raise ValueError("agent-list JSON result.agents is not a list")
    return agents


def format_roster(payload: dict[str, Any], workspace: str | None = None) -> list[str]:
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


def _model(args: list[str]) -> str | None:
    for i, arg in enumerate(args):
        if arg == "--model" and i + 1 < len(args):
            return args[i + 1]
        if arg.startswith("--model="):
            return arg.split("=", 1)[1]
    return None


def _expected(keys: dict[str, Any], role: str) -> list[tuple[str, str | None, list[str]]]:
    kind = keys.get(f"{role}-kind")
    if not kind:
        raise ValueError(f"config lacks {role}-kind")
    block = keys.get(f"{role}-args", [])
    expected = [(kind, _model(block), block)]
    fallback = keys.get(f"{role}-fallback")
    if fallback:
        block = keys.get(f"{role}-fallback-args", [])
        expected.append((fallback, _model(block), block))
    return expected


def _has_block(argv: list[str], block: list[str]) -> bool:
    n = len(block)
    return any(argv[i:i + n] == block for i in range(len(argv) - n + 1))


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


def _launch_args(pane_id: str, kind: str) -> tuple[list[str] | None, dict[str, Any] | None]:
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
                    return [str(a) for a in argv[i + 1:]], None
        argv0 = process.get("argv0")
        if isinstance(argv0, str) and Path(argv0).name == kind:
            return None, process
    raise ValueError(f"no {kind} process in pane {pane_id}")


def _pi_process_start(pid: Any) -> datetime:
    try:
        proc = subprocess.run(
            ["ps", "-o", "lstart=", "-p", str(pid)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=10,
            env={**os.environ, "LC_ALL": "C"},
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RuntimeError(f"could not read pi process start for pid {pid}: {exc}") from exc
    if proc.returncode:
        detail = proc.stderr.strip() or proc.stdout.strip() or str(proc.returncode)
        raise RuntimeError(f"could not read pi process start for pid {pid}: {detail}")
    try:
        return datetime.strptime(proc.stdout.strip(), "%a %b %d %H:%M:%S %Y").astimezone()
    except ValueError as exc:
        raise RuntimeError(
            f"could not read pi process start for pid {pid}: invalid ps timestamp"
        ) from exc


def _pi_session_dir(cwd: str) -> Path:
    agent_dir = os.path.expanduser(os.environ.get("PI_CODING_AGENT_DIR") or "~/.pi/agent")
    slug = cwd.removeprefix("/").replace("/", "-").replace(":", "-")
    return Path(agent_dir) / "sessions" / f"--{slug}--"


def _pi_session_is_named(path: Path, name: str, process_start: datetime) -> bool:
    try:
        with path.open(encoding="utf-8") as session:
            first = json.loads(next(session))
            if not isinstance(first, dict) or first.get("type") != "session":
                return False
            raw_timestamp = first.get("timestamp")
            if not isinstance(raw_timestamp, str):
                return False
            timestamp = datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
            if timestamp.tzinfo is None or timestamp < process_start.astimezone(timezone.utc):
                return False
            named = False
            for line in session:
                try:
                    entry = json.loads(line)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return False
                if not isinstance(entry, dict):
                    return False
                if entry.get("type") == "message":
                    return named
                if entry.get("type") == "session_info" and entry.get("name") == name:
                    named = True
            return named
    except (OSError, StopIteration, KeyError, TypeError, ValueError, UnicodeDecodeError):
        return False


def _pi_running_model(name: str, process: dict[str, Any]) -> tuple[str | None, str | None]:
    pid = process.get("pid")
    process_start = _pi_process_start(pid)
    cwd = process.get("cwd")
    if not isinstance(cwd, str):
        return None, "no-named-session"
    session_dir = _pi_session_dir(cwd)
    try:
        candidates = [
            path for path in session_dir.glob("*.jsonl")
            if _pi_session_is_named(path, name, process_start)
        ]
    except OSError:
        candidates = []
    if not candidates:
        return None, "no-named-session"
    if len(candidates) != 1:
        return None, "ambiguous-session"
    model = None
    try:
        with candidates[0].open(encoding="utf-8") as session:
            for line in session:
                try:
                    entry = json.loads(line)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return None, "no-named-session"
                if isinstance(entry, dict) and entry.get("type") == "model_change":
                    provider, model_id = entry.get("provider"), entry.get("modelId")
                    valid_model = (
                        isinstance(provider, str)
                        and provider
                        and isinstance(model_id, str)
                        and model_id
                    )
                    model = f"{provider}/{model_id}" if valid_model else None
    except (OSError, UnicodeDecodeError):
        return None, "no-named-session"
    return (model, None) if model is not None else (None, "no-named-session")


def _route_matches_model(route_model: str | None, running_model: str) -> bool:
    return route_model == running_model or (
        route_model is not None
        and "/" not in route_model
        and running_model.rpartition("/")[2] == route_model
    )


def format_drift_roster(
    payload: dict[str, Any],
    keys: dict[str, Any],
    seats: dict[str, str],
    workspace: str | None = None,
) -> tuple[list[str], bool]:
    """Return DRIFT lines, an UNVERIFIABLE line for a matching kind with an unbound model, and whether any UNVERIFIABLE line was produced.

    A seat drifts when its kind and model match no route, or, with its launch
    argv visible, when the matching route's config ``*-args`` do not appear in
    it as one contiguous run of the same elements (``--model=x`` is not
    ``--model x``). Other arguments a charter or the launch adds are not
    drift. A seat showing only argv0 (pi) is not checked for the block.
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
        launch_args, argv0_process = _launch_args(pane_id, kind)
        model = _model(launch_args) if launch_args is not None else None
        matching_kinds = [(k, m) for k, m, _ in expected if kind == k]
        pi_session_model = bool(matching_kinds and argv0_process is not None and kind == "pi")
        if pi_session_model:
            if any(m is None for _, m in matching_kinds):
                continue
            model, reason = _pi_running_model(name, argv0_process)
            if reason is not None:
                want = " or ".join(f"{k} --model {m or '-'}" for k, m, _ in expected)
                lines.append(
                    f"{pane_id} {name} {kind} UNVERIFIABLE role={role} "
                    f"reason={reason} expected={want}"
                )
                unverifiable = True
                continue
        elif matching_kinds and launch_args is None:
            if any(m is None for _, m in matching_kinds):
                continue
            want = " or ".join(f"{k} --model {m or '-'}" for k, m, _ in expected)
            lines.append(
                f"{pane_id} {name} {kind} UNVERIFIABLE role={role} "
                f"reason=model-unavailable expected={want}"
            )
            unverifiable = True
            continue
        if any(
            m is None or (_route_matches_model(m, model) if pi_session_model else model == m)
            for _, m in matching_kinds
        ):
            if launch_args is None:
                continue
            blocks = [b for k, m, b in expected if k == kind and (m is None or m == model)]
            if any(_has_block(launch_args, b) for b in blocks):
                continue
            missing = " or ".join(shlex.join(b) for b in blocks)
            want = " or ".join(f"{k} --model {m or '-'}" for k, m, _ in expected)
            lines.append(
                f"{pane_id} {name} {kind} DRIFT role={role} running={kind} --model {model or '-'} "
                f"expected={want} missing={missing}"
            )
            continue
        want = " or ".join(f"{k} --model {m or '-'}" for k, m, _ in expected)
        lines.append(
            f"{pane_id} {name} {kind} DRIFT role={role} running={kind} --model {model or '-'} expected={want}"
        )
    if unseen:
        raise ValueError(f"no live seat named {', '.join(sorted(unseen))}")
    return lines, unverifiable


def _agent_list_json() -> str:
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
        help="report named seats whose kind or --model differs from this config.json's keys, or whose launch argv lacks the matched route's *-args as one contiguous block",
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
        payload = json.loads(_agent_list_json())
        if sum(map(bool, (args.stalled, args.never_started, args.drift))) > 1:
            raise ValueError("--stalled, --never-started and --drift are mutually exclusive")
        if args.drift:
            if not args.seat:
                raise ValueError("--drift requires at least one --seat")
            lines, unverifiable = format_drift_roster(
                payload, project_config.load(args.drift), _seat_specs(args.seat), args.workspace
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

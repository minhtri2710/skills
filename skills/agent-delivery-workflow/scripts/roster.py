#!/usr/bin/env python3
"""Print the compact roster view of the live seats."""
from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
import time
from pathlib import Path
from typing import Any

import backend
import project_config
import runtimes


_SETTLED_STATES = frozenset({"idle", "done"})
_ROLES = ("engineer", "reviewer", "architect")


def format_roster(seats: list[backend.Seat]) -> list[str]:
    return [f"{seat.handle} {seat.name or '-'} {seat.kind or '-'} {seat.state}" for seat in seats]


def _load_previous_sample(path: str) -> dict[str, dict[str, Any]]:
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
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


def _absent(path: Path) -> bool:
    """True only when `path` is confirmed missing; an existing or unreadable path is not absent."""
    try:
        path.stat()
    except FileNotFoundError:
        return True
    except OSError:
        return False
    return False


def format_never_started_roster(
    seats: list[backend.Seat],
    peer_specs: dict[str, tuple[Path, Path]],
    never_started: set[str],
) -> list[str]:
    """Return explicitly identified never-prompted peers.

    Pane text and token counters are deliberately not parsed here: a token
    counter may corroborate the explicit evidence, but cannot be the verdict.
    """
    lines = []
    for seat in seats:
        name = seat.name
        if name is None or name not in never_started:
            continue
        if name not in peer_specs:
            raise ValueError(f"never-started peer {name!r} lacks a peer specification")
        if seat.state not in _SETTLED_STATES:
            continue
        report_path, progress_path = peer_specs[name]
        if _absent(report_path) and _absent(progress_path):
            lines.append(f"{seat.handle} {name} {seat.kind or '-'} NEVER-STARTED")
    return lines


def format_stalled_roster(
    seats: list[backend.Seat],
    peer_specs: dict[str, tuple[Path, Path]],
    previous_sample: dict[str, dict[str, Any]],
    stale_after: float,
    now: float | None = None,
) -> list[str]:
    if stale_after < 0:
        raise ValueError("stale-after must be non-negative")
    if now is None:
        now = time.time()

    lines = []
    for seat in seats:
        name = seat.name
        if name is None or name not in peer_specs:
            continue
        if seat.state not in _SETTLED_STATES:
            continue

        prior = previous_sample.get(name)
        if prior is None or prior["state"] in _SETTLED_STATES:
            continue
        report_path, progress_path = peer_specs[name]
        if not _absent(report_path):
            continue
        try:
            current_mtime = progress_path.stat().st_mtime
        except OSError:
            continue
        if current_mtime > prior["progress_mtime"]:
            continue
        if now - current_mtime <= stale_after:
            continue
        lines.append(f"{seat.handle} {name} {seat.kind or '-'} STALLED")
    return lines


def _expected(config: dict[str, Any], role: str) -> list[tuple[str, str | None, list[str]]]:
    routes = project_config.role_routes(config, role)
    if not routes or routes[0].slot != "primary":
        raise ValueError(f"config names no primary kind for {role}")
    return [(route.kind, project_config.model_of(route.args or []), route.args or []) for route in routes]


def _want(expected: list[tuple[str, str | None, list[str]]]) -> str:
    return " or ".join(f"{kind} --model {model or '-'}" for kind, model, _ in expected)


def _has_block(argv: list[str], block: list[str]) -> bool:
    n = len(block)
    return any(argv[i:i + n] == block for i in range(len(argv) - n + 1))


def _seat_specs(raw_seats: list[str] | None) -> dict[str, str]:
    seats: dict[str, str] = {}
    for raw in raw_seats or []:
        name, _, role = raw.partition(":")
        if not name or role not in _ROLES:
            raise ValueError("seat must use NAME:engineer, NAME:reviewer or NAME:architect")
        if name in seats:
            raise ValueError(f"duplicate seat specification: {name}")
        seats[name] = role
    return seats


def _launch_args(
    seat_backend: backend.Backend, handle: str, kind: str
) -> tuple[list[str] | None, backend.Process | None]:
    for process in seat_backend.processes(handle):
        for i, arg in enumerate(process.argv):
            if Path(arg).name == kind:
                return (list(process.argv[i + 1:]), None) if process.argv_reported else (None, process)
    raise ValueError(f"no {kind} process in seat {handle}")


def format_drift_roster(
    seat_backend: backend.Backend,
    live: list[backend.Seat],
    config: dict[str, Any],
    seats: dict[str, str],
    *,
    lead: str = "",
    run_dir: str = "",
    installed_skill_dir: str = "",
) -> tuple[list[str], bool]:
    lines = []
    unverifiable = False
    unseen = set(seats)
    for seat in live:
        name = seat.name
        if name is None or name not in seats:
            continue
        unseen.discard(name)
        handle = seat.handle
        kind = seat.kind or "-"
        role = seats[name]
        label = f"{handle} {name} {kind}"
        expected = _expected(config, role)
        want = _want(expected)
        launch_args, argv0_process = _launch_args(seat_backend, handle, kind)
        model = project_config.model_of(launch_args) if launch_args is not None else None
        matching_kinds = [route for route in expected if route[0] == kind]
        session_model = bool(matching_kinds and argv0_process is not None and kind in runtimes.SESSION_MODEL_KINDS)
        if session_model:
            model, reason = runtimes.session_model(seat, argv0_process)
            if reason is not None:
                lines.append(f"{label} UNVERIFIABLE role={role} reason={reason} expected={want}")
                unverifiable = True
                continue
        elif matching_kinds and launch_args is None:
            lines.append(f"{label} UNVERIFIABLE role={role} reason=model-unavailable expected={want}")
            unverifiable = True
            continue
        route_matches = [
            (k, m, b) for k, m, b in expected if k == kind and (
                runtimes.model_matches(m, model) if session_model and m is not None
                else m is None or m == model
            )
        ]
        if not session_model and launch_args is not None and len(route_matches) > 1:
            argv_matches = [route for route in route_matches if _has_block(launch_args, route[2])]
            if argv_matches:
                route_matches = argv_matches
        if session_model and sum(m is not None and runtimes.model_matches(m, model) for _, m, _ in matching_kinds) > 1:
            lines.append(f"{label} UNVERIFIABLE role={role} reason=route-ambiguous expected={want}")
            unverifiable = True
            continue
        if route_matches:
            if launch_args is None:
                lines.append(f"{label} UNVERIFIABLE role={role} reason=launch-argv-hidden expected={want}")
                unverifiable = True
                continue
            try:
                expanded = project_config.expand_launch(
                    config, role=role, kind=kind, role_args=route_matches[0][2], seat=name,
                    lead=lead, run_dir=run_dir, installed_skill_dir=installed_skill_dir,
                    settings_file=(
                        str(project_config.peer_settings_path(run_dir, name)) if run_dir else ""
                    ),
                )
            except ValueError as exc:
                lines.append(f"{label} UNVERIFIABLE role={role} reason={exc}")
                unverifiable = True
                continue
            if _has_block(launch_args, expanded["argv"]):
                if expanded["settings_file"]:
                    settings_path = Path(expanded["settings_file"])
                    if settings_path.is_symlink() or not settings_path.is_file():
                        lines.append(f"{label} UNVERIFIABLE role={role} reason=settings-file-unreadable")
                        unverifiable = True
                        continue
                    try:
                        actual_settings = json.loads(settings_path.read_text(encoding="utf-8"))
                    except (OSError, UnicodeError, json.JSONDecodeError):
                        lines.append(f"{label} UNVERIFIABLE role={role} reason=settings-file-unreadable")
                        unverifiable = True
                        continue
                    if actual_settings != expanded["settings_json"]:
                        lines.append(f"{label} UNVERIFIABLE role={role} reason=settings-mismatch")
                        unverifiable = True
                        continue
                continue
            lines.append(
                f"{label} DRIFT role={role} running={kind} --model {model or '-'} "
                f"expected={want} missing={shlex.join(expanded['argv'])}"
            )
            continue
        if session_model:
            lines.append(f"{label} UNVERIFIABLE role={role} reason=launch-argv-hidden expected={want}")
            unverifiable = True
            continue
        lines.append(f"{label} DRIFT role={role} running={kind} --model {model or '-'} expected={want}")
    if unseen:
        raise ValueError(f"no live seat named {', '.join(sorted(unseen))}")
    return lines, unverifiable


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="compact agent roster")
    backend.add_backend_option(parser)
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
        help="seat and role (engineer, reviewer or architect) for --drift; repeat per seat",
    )
    parser.add_argument("--lead", default="", help="verified Lead seat name for profile expansion")
    parser.add_argument("--run-dir", default="", help="recorded run directory for profile expansion")
    parser.add_argument("--installed-skill-dir", default="", help="verified installed skill directory")
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
        seat_backend = backend.open_backend(os.environ, args.backend)
        if sum(map(bool, (args.stalled, args.never_started, args.drift))) > 1:
            raise ValueError("--stalled, --never-started and --drift are mutually exclusive")
        live = [
            seat for seat in seat_backend.list_seats()
            if args.workspace is None or seat.workspace == args.workspace
        ]
        if args.drift:
            if not args.seat:
                raise ValueError("--drift requires at least one --seat")
            lines, unverifiable = format_drift_roster(
                seat_backend, live, project_config.load(args.drift), _seat_specs(args.seat),
                lead=args.lead, run_dir=args.run_dir,
                installed_skill_dir=args.installed_skill_dir,
            )
            exit_code = int(unverifiable)
        elif args.never_started:
            if not args.peer:
                raise ValueError("--never-started requires at least one --peer")
            lines = format_never_started_roster(
                live,
                _peer_specs(args.peer),
                set(args.never_started),
            )
        elif args.stalled:
            if not args.peer:
                raise ValueError("--stalled requires at least one --peer")
            if args.previous_sample is None:
                raise ValueError("--stalled requires --previous-sample")
            lines = format_stalled_roster(
                live,
                _peer_specs(args.peer),
                _load_previous_sample(args.previous_sample),
                args.stale_after,
            )
        else:
            lines = format_roster(live)
    except (backend.BackendError, ValueError, OSError, runtimes.Unavailable) as exc:
        print(f"roster: {exc}", file=sys.stderr)
        return 1

    if lines:
        print("\n".join(lines))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

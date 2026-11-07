#!/usr/bin/env python3
"""Check seat-level teardown and canonical-tree squatting servers for one run."""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import backend
import gate_row


@dataclass(frozen=True)
class CloseoutResult:
    passed: bool
    findings: tuple[str, ...]
    checked_seats: tuple[str, ...] = ()


_PEER_ROLES = {"Engineer", "Reviewer"}
_PERSISTENT_ROLES = {"Lead", "Human Supervisor"}
_PERSISTENT_ROLE_ERROR = (
    "persistent must record exactly one Lead and at most one Human Supervisor"
)
_SERVER_MARKERS = (
    "astro",
    "flask run",
    "gunicorn",
    "http.server",
    "live-server",
    "next dev",
    "next start",
    "parcel",
    "preview",
    "rails server",
    "storybook",
    "uvicorn",
    "vite",
    "webpack-dev-server",
)
_SERVER_WORDS = frozenset({"dev", "preview", "serve", "server"})
_SCRIPT_INTERPRETERS = frozenset({
    "bun", "deno", "node", "nodejs", "php", "python", "python3", "ruby", "ts-node", "tsx",
})
_INTERPRETER_SUBCOMMANDS = frozenset({"run"})
_INLINE_CODE_FLAGS = frozenset({"-c", "-e", "-m", "-r", "--eval"})


def _record_from_input(staffing_record: Mapping[str, Any] | str | Path) -> Mapping[str, Any]:
    if isinstance(staffing_record, Mapping):
        return staffing_record
    if isinstance(staffing_record, (str, Path)):
        path = Path(staffing_record)
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
        if not isinstance(value, Mapping):
            raise ValueError("staffing record must contain a JSON object")
        return value
    raise ValueError("staffing record must be a mapping or a JSON file path")


def _validate_handle(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be text")
    try:
        return backend.require_handle(value)
    except ValueError as exc:
        raise ValueError(f"{label}: {exc}") from exc


def _validate_record(
    record: Mapping[str, Any],
) -> tuple[Path, list[dict[str, str]], Path]:
    canonical_value = record.get("canonical_checkout")
    if not isinstance(canonical_value, str) or not canonical_value or "\x00" in canonical_value:
        raise ValueError("canonical_checkout must be a non-empty path")
    canonical = Path(canonical_value).expanduser()
    if not canonical.is_absolute():
        raise ValueError("canonical_checkout must be absolute")

    persistent = record.get("persistent")
    if not isinstance(persistent, list):
        raise ValueError("persistent must be a list")
    persistent_seats: set[str] = set()
    persistent_names: set[str] = set()
    persistent_roles: set[str] = set()
    for index, seat in enumerate(persistent):
        if not isinstance(seat, Mapping):
            raise ValueError(f"persistent[{index}] must be an object")
        role = seat.get("role")
        if role not in _PERSISTENT_ROLES:
            raise ValueError(_PERSISTENT_ROLE_ERROR)
        handle = _validate_handle(seat.get("seat"), f"persistent[{index}].seat")
        name = _validate_handle(seat.get("name"), f"persistent[{index}].name")
        if handle in persistent_seats:
            raise ValueError(f"persistent seat {handle!r} is duplicated")
        if name in persistent_names:
            raise ValueError(f"persistent name {name!r} is duplicated")
        if role in persistent_roles:
            raise ValueError(_PERSISTENT_ROLE_ERROR)
        persistent_seats.add(handle)
        persistent_names.add(name)
        persistent_roles.add(role)
    if "Lead" not in persistent_roles:
        raise ValueError(_PERSISTENT_ROLE_ERROR)

    peers = record.get("peers")
    if not isinstance(peers, list):
        raise ValueError("peers must be a list")
    validated: list[dict[str, str]] = []
    seen_seats = set(persistent_seats)
    seen_names: set[str] = set(persistent_names)
    for index, peer in enumerate(peers):
        if not isinstance(peer, Mapping):
            raise ValueError(f"peers[{index}] must be an object")
        role = peer.get("role")
        if role not in _PEER_ROLES:
            raise ValueError(f"peers[{index}] must be an Engineer or Reviewer")
        issue = peer.get("issue")
        if not isinstance(issue, str) or not issue or "\x00" in issue:
            raise ValueError(f"peers[{index}].issue must be non-empty text")
        handle = _validate_handle(peer.get("seat"), f"peers[{index}].seat")
        name = _validate_handle(peer.get("name"), f"peers[{index}].name")
        if handle in seen_seats:
            raise ValueError(f"recorded seat {handle!r} is duplicated")
        if name in seen_names:
            raise ValueError(f"recorded peer name {name!r} is duplicated")
        seen_seats.add(handle)
        seen_names.add(name)
        validated.append({"issue": issue, "role": role, "seat": handle, "name": name})
    ledger_value = record.get("gates_ledger")
    if not isinstance(ledger_value, str) or not ledger_value or "\x00" in ledger_value:
        raise ValueError("gates_ledger must be a non-empty path")
    ledger_path = Path(ledger_value).expanduser()
    if not ledger_path.is_absolute():
        raise ValueError("gates_ledger must be absolute")
    return canonical.resolve(strict=False), validated, ledger_path.resolve(strict=False)


def _path_in_checkout(value: Any, canonical: Path) -> bool:
    if not isinstance(value, str) or not value or "\x00" in value:
        return False
    path = Path(value).expanduser()
    if not path.is_absolute():
        return False
    try:
        path.resolve(strict=False).relative_to(canonical)
    except ValueError:
        return False
    return True


def _is_server_process(process: backend.Process) -> bool:
    argv = [token.lower() for token in process.argv]
    tokens = set(argv)
    basenames = {Path(token).name for token in argv}
    for marker in _SERVER_MARKERS:
        marker_tokens = marker.split()
        if len(marker_tokens) == 1:
            if marker_tokens[0] in tokens or marker_tokens[0] in basenames:
                return True
            continue
        if any(argv[index:index + len(marker_tokens)] == marker_tokens for index in range(len(argv) - len(marker_tokens) + 1)):
            return True
    return bool(tokens & _SERVER_WORDS) or _runs_server_script(argv)


def _runs_server_script(argv: list[str]) -> bool:
    for index, token in enumerate(argv):
        if Path(token).name not in _SCRIPT_INTERPRETERS:
            continue
        for arg in argv[index + 1:]:
            if arg in _INLINE_CODE_FLAGS:
                break
            if arg.startswith("-") or arg in _INTERPRETER_SUBCOMMANDS:
                continue
            if Path(arg).stem in _SERVER_WORDS:
                return True
            break
    return False


def check_closeout(
    staffing_record: Mapping[str, Any] | str | Path,
    seats: backend.Backend,
) -> CloseoutResult:
    """Inspect exactly the recorded peer seats through a read-only backend."""
    findings: list[str] = []
    try:
        record = _record_from_input(staffing_record)
        canonical, peers, ledger_path = _validate_record(record)
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        return CloseoutResult(False, (f"malformed staffing record: {exc}",))

    try:
        state = gate_row.read_ledger_state(ledger_path, canonical)
        reviewed = gate_row.reviewed_unpushed(state, canonical)
        if reviewed:
            findings.append(
                f"reviewed unpushed commit(s) {' '.join(sorted(reviewed))} have no open push-gate row"
            )
    except (OSError, UnicodeError, gate_row.RowError) as exc:
        findings.append(f"gate ledger could not be checked: {exc}")

    checked: list[str] = []
    for peer in peers:
        seat_id = peer["seat"]
        name = peer["name"]
        checked.append(seat_id)
        try:
            terminal = seats.get_terminal(seat_id)
        except Exception as exc:
            if isinstance(exc, backend.SeatError) and exc.kind == "not_found":
                continue
            findings.append(f"{peer['role']} {name} seat {seat_id}: terminal read failed: {exc}")
            continue

        if terminal.handle != seat_id:
            findings.append(
                f"{peer['role']} {name} seat {seat_id}: backend returned mismatched terminal evidence"
            )
            continue

        agent_not_found = False
        try:
            seats.get_seat(name)
        except Exception as exc:
            agent_not_found = isinstance(exc, backend.SeatError) and exc.kind == "not_found"
            if not agent_not_found:
                findings.append(f"{peer['role']} {name} seat {seat_id}: agent read failed: {exc}")
        if agent_not_found:
            findings.append(
                f"{peer['role']} {name} seat {seat_id} remains open despite agent_not_found"
            )
        else:
            findings.append(f"{peer['role']} {name} seat {seat_id} remains open")

        try:
            processes = seats.processes(seat_id)
        except Exception as exc:
            findings.append(f"{peer['role']} {name} seat {seat_id}: process read failed: {exc}")
            continue
        for process in processes:
            cwd = process.cwd if process.cwd is not None else terminal.cwd
            if cwd is None:
                findings.append(f"{peer['role']} {name} seat {seat_id}: process evidence has no cwd")
                continue
            if _is_server_process(process) and _path_in_checkout(cwd, canonical):
                findings.append(
                    f"{peer['role']} {name} seat {seat_id}: squatting-server anti-pattern; "
                    f"live server/dev/preview process in canonical checkout {canonical}"
                )

    return CloseoutResult(not findings, tuple(findings), tuple(checked))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--staffing", required=True, type=Path, help="JSON closeout staffing record"
    )
    backend.add_backend_option(parser)
    args = parser.parse_args(argv)
    try:
        seats = backend.open_backend(os.environ, args.backend)
    except backend.BackendError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    result = check_closeout(args.staffing, seats)
    if result.passed:
        print(f"PASS: checked {len(result.checked_seats)} recorded peer seat(s)")
        return 0
    for finding in result.findings:
        print(f"FAIL: {finding}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

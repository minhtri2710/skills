#!/usr/bin/env python3
"""Check pane-level teardown and canonical-tree squatting servers for one run."""
from __future__ import annotations

import argparse
import json
import os
import shlex
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
    checked_panes: tuple[str, ...] = ()

def _unpushed_commits(repo: Path, gate_tips: list[str]) -> list[str]:
    head = gate_row.git(repo, "rev-parse", "HEAD")
    try:
        upstream = gate_row.git(repo, "rev-parse", "--verify", "@{upstream}")
    except gate_row.RowError:
        exclude = ["--remotes"]
    else:
        exclude = [upstream]
    return gate_row.git(repo, "rev-list", head, "--not", *exclude, *gate_tips).splitlines()


_ROLE_RE = {"Engineer", "Reviewer"}
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
    if not isinstance(value, str) or not backend.HANDLE_RE.fullmatch(value):
        raise ValueError(f"{label} is not a valid opaque seat handle")
    return value


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
    persistent_panes: set[str] = set()
    persistent_names: set[str] = set()
    persistent_roles: set[str] = set()
    for index, seat in enumerate(persistent):
        if not isinstance(seat, Mapping):
            raise ValueError(f"persistent[{index}] must be an object")
        role = seat.get("role")
        if role not in _PERSISTENT_ROLES:
            raise ValueError(_PERSISTENT_ROLE_ERROR)
        pane = _validate_handle(seat.get("pane"), f"persistent[{index}].pane")
        name = _validate_handle(seat.get("name"), f"persistent[{index}].name")
        if pane in persistent_panes:
            raise ValueError(f"persistent pane {pane!r} is duplicated")
        if name in persistent_names:
            raise ValueError(f"persistent name {name!r} is duplicated")
        if role in persistent_roles:
            raise ValueError(_PERSISTENT_ROLE_ERROR)
        persistent_panes.add(pane)
        persistent_names.add(name)
        persistent_roles.add(role)
    if "Lead" not in persistent_roles:
        raise ValueError(_PERSISTENT_ROLE_ERROR)

    peers = record.get("peers")
    if not isinstance(peers, list):
        raise ValueError("peers must be a list")
    validated: list[dict[str, str]] = []
    seen_panes = set(persistent_panes)
    seen_names: set[str] = set(persistent_names)
    for index, peer in enumerate(peers):
        if not isinstance(peer, Mapping):
            raise ValueError(f"peers[{index}] must be an object")
        role = peer.get("role")
        if role not in _ROLE_RE:
            raise ValueError(f"peers[{index}] must be an Engineer or Reviewer")
        issue = peer.get("issue")
        if not isinstance(issue, str) or not issue or "\x00" in issue:
            raise ValueError(f"peers[{index}].issue must be non-empty text")
        pane = _validate_handle(peer.get("pane"), f"peers[{index}].pane")
        name = _validate_handle(peer.get("name"), f"peers[{index}].name")
        if pane in seen_panes:
            raise ValueError(f"recorded pane {pane!r} is duplicated")
        if name in seen_names:
            raise ValueError(f"recorded peer name {name!r} is duplicated")
        seen_panes.add(pane)
        seen_names.add(name)
        validated.append({"issue": issue, "role": role, "pane": pane, "name": name})
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


def _process_argv(process: Mapping[str, Any]) -> list[str]:
    values: list[str] = []
    for key in ("argv0", "name", "command", "cmdline"):
        value = process.get(key)
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            values.extend(item.lower() for item in value)
        elif isinstance(value, str):
            try:
                values.extend(item.lower() for item in shlex.split(value))
            except ValueError:
                values.extend(value.lower().split())
    return values


def _is_server_process(process: Mapping[str, Any]) -> bool:
    argv = _process_argv(process)
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
    """Inspect exactly the recorded peer panes through a read-only backend.

    The closeout staffing record is JSON with ``canonical_checkout``, ``persistent``,
    ``peers`` and ``gates_ledger`` fields. Each peer has ``issue``,
    ``role`` (Engineer or Reviewer), ``name`` and opaque ``pane`` fields. Per peer the
    backend answers ``get_terminal(pane)`` (the pane is open, or ``SeatError`` not_found
    when it is gone), ``get_seat(name)`` (the agent, or not_found) and
    ``processes(pane)`` (its foreground process mappings).
    """
    findings: list[str] = []
    try:
        record = _record_from_input(staffing_record)
        canonical, peers, ledger_path = _validate_record(record)
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        return CloseoutResult(False, (f"malformed staffing record: {exc}",))

    try:
        with gate_row.locked_ledger(ledger_path, exclusive=False) as handle:
            rows = gate_row.ledger_rows(gate_row.handle_text(handle))
            state = gate_row.validate_ledger(rows, canonical)
        gate_tips = gate_row.open_push_gate_tips(state, canonical)
        unpushed = _unpushed_commits(canonical, gate_tips)
        reviewed = state.covered_by_reviews(canonical, set(unpushed)) & set(unpushed)
        if reviewed:
            findings.append(
                f"reviewed unpushed commit(s) {' '.join(sorted(reviewed))} have no open push-gate row"
            )
    except (OSError, UnicodeError, gate_row.RowError) as exc:
        findings.append(f"gate ledger could not be checked: {exc}")

    checked: list[str] = []
    for peer in peers:
        pane_id = peer["pane"]
        name = peer["name"]
        checked.append(pane_id)
        try:
            pane = seats.get_terminal(pane_id)
        except Exception as exc:  # Boundary failures are evidence failures, not passes.
            if isinstance(exc, backend.SeatError) and exc.kind == "not_found":
                # The recorded teardown target is gone.  Agent lookup is not used as
                # an alternate teardown proof, so agent_not_found is harmless here.
                continue
            findings.append(f"{peer['role']} {name} pane {pane_id}: pane read failed: {exc}")
            continue

        if pane.handle != pane_id:
            findings.append(
                f"{peer['role']} {name} pane {pane_id}: backend returned mismatched pane evidence"
            )
            continue

        agent_not_found = False
        try:
            seats.get_seat(name)
        except Exception as exc:
            agent_not_found = isinstance(exc, backend.SeatError) and exc.kind == "not_found"
            if not agent_not_found:
                findings.append(f"{peer['role']} {name} pane {pane_id}: agent read failed: {exc}")
        if agent_not_found:
            findings.append(
                f"{peer['role']} {name} pane {pane_id} remains open despite agent_not_found"
            )
        else:
            findings.append(f"{peer['role']} {name} pane {pane_id} remains open")

        try:
            processes = seats.processes(pane_id)
        except Exception as exc:
            findings.append(f"{peer['role']} {name} pane {pane_id}: process read failed: {exc}")
            continue
        for process in processes:
            if not isinstance(process, Mapping):
                findings.append(f"{peer['role']} {name} pane {pane_id}: malformed process evidence")
                continue
            if process.get("alive") is False or process.get("status") in {"exited", "dead"}:
                continue
            cwd = process.get("cwd", pane.cwd)
            if cwd is None:
                findings.append(f"{peer['role']} {name} pane {pane_id}: process evidence has no cwd")
                continue
            if _is_server_process(process) and _path_in_checkout(cwd, canonical):
                findings.append(
                    f"{peer['role']} {name} pane {pane_id}: squatting-server anti-pattern; "
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
        print(f"PASS: checked {len(result.checked_panes)} recorded peer pane(s)")
        return 0
    for finding in result.findings:
        print(f"FAIL: {finding}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

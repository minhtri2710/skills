#!/usr/bin/env python3
"""Check pane-level teardown and canonical-tree squatting servers for one run."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Protocol


class HerdrReadBoundary(Protocol):
    """Read-only Herdr seam used by :func:`check_closeout` and its tests."""

    def read_pane(self, pane_id: str) -> Mapping[str, Any]: ...

    def read_agent(self, agent_name: str) -> Mapping[str, Any]: ...

    def read_processes(self, pane_id: str) -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class CloseoutResult:
    """The fail-closed result of one closeout inspection."""

    passed: bool
    findings: tuple[str, ...]
    checked_panes: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return self.passed

    def __bool__(self) -> bool:
        return self.passed


_HANDLE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
_ROLE_RE = {"Engineer", "Reviewer"}
_PERSISTENT_ROLES = {"Lead", "Human Supervisor"}
_ABSENT_STATUSES = {"absent", "closed", "not_found", "pane_not_found"}
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
_SERVER_WORD_RE = re.compile(r"(?:^|[\s/_-])(dev|preview|serve|server)(?:$|[\s/_-])")


def _status(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip().lower()
    if not isinstance(value, Mapping):
        return None
    for key in ("status", "code", "error", "kind"):
        candidate = value.get(key)
        if isinstance(candidate, str):
            return candidate.strip().lower()
    return None


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
    if not isinstance(value, str) or not _HANDLE_RE.fullmatch(value):
        raise ValueError(f"{label} is not a valid opaque Herdr handle")
    return value


def _validate_record(record: Mapping[str, Any]) -> tuple[Path, list[dict[str, str]]]:
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
            raise ValueError(f"persistent[{index}] has an invalid protected role")
        pane = _validate_handle(seat.get("pane"), f"persistent[{index}].pane")
        name = _validate_handle(seat.get("name"), f"persistent[{index}].name")
        if pane in persistent_panes:
            raise ValueError(f"persistent pane {pane!r} is duplicated")
        if name in persistent_names:
            raise ValueError(f"persistent name {name!r} is duplicated")
        if role in persistent_roles:
            raise ValueError(f"persistent role {role!r} is duplicated")
        persistent_panes.add(pane)
        persistent_names.add(name)
        persistent_roles.add(role)
    if persistent_roles != _PERSISTENT_ROLES:
        raise ValueError("persistent must record exactly one Lead and one Human Supervisor")

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
    return canonical.resolve(strict=False), validated


def _pane_state(value: Any) -> tuple[str, str | None]:
    if not isinstance(value, Mapping):
        return "unknown", None
    status = _status(value)
    pane_id = value.get("pane_id")
    if status in _ABSENT_STATUSES:
        return "absent", None
    if status in {"open", "present"} and isinstance(pane_id, str):
        return "open", pane_id
    if isinstance(pane_id, str) and pane_id:
        return "open", pane_id
    return "unknown", None


def _agent_is_not_found(value: Any) -> bool:
    status = _status(value)
    return status in {"agent_not_found", "not_found", "agent-missing"}


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


def _process_text(process: Mapping[str, Any]) -> str:
    values: list[str] = []
    for key in ("argv0", "name", "command", "cmdline"):
        value = process.get(key)
        if isinstance(value, str):
            values.append(value.lower())
        elif isinstance(value, list) and all(isinstance(item, str) for item in value):
            values.extend(item.lower() for item in value)
    return " ".join(values)


def _is_server_process(process: Mapping[str, Any]) -> bool:
    text = _process_text(process)
    return any(marker in text for marker in _SERVER_MARKERS) or bool(_SERVER_WORD_RE.search(text))


def _process_list(evidence: Mapping[str, Any]) -> list[Any] | None:
    processes = evidence.get("foreground_processes")
    if processes is None:
        processes = evidence.get("processes")
    return processes if isinstance(processes, list) else None


def check_closeout(
    staffing_record: Mapping[str, Any] | str | Path,
    herdr: HerdrReadBoundary,
) -> CloseoutResult:
    """Inspect exactly the recorded peer panes through a read-only Herdr boundary.

    The staffing record is JSON with ``canonical_checkout``, ``persistent`` and
    ``peers`` fields.  Each peer has ``issue``, ``role`` (Engineer or Reviewer),
    ``name`` and opaque ``pane`` fields.  Boundary methods return normalized
    mappings: ``read_pane`` returns ``{"status": "open", "pane_id": ...,
    "cwd": ...}`` or ``{"status": "absent"}``; ``read_agent`` returns an
    agent mapping or ``{"status": "agent_not_found"}``; and
    ``read_processes`` returns ``{"foreground_processes": [...]}``.
    """
    findings: list[str] = []
    try:
        record = _record_from_input(staffing_record)
        canonical, peers = _validate_record(record)
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        return CloseoutResult(False, (f"malformed staffing record: {exc}",))

    checked: list[str] = []
    for peer in peers:
        pane_id = peer["pane"]
        name = peer["name"]
        checked.append(pane_id)
        try:
            pane = herdr.read_pane(pane_id)
        except Exception as exc:  # Boundary failures are evidence failures, not passes.
            findings.append(f"{peer['role']} {name} pane {pane_id}: pane read failed: {exc}")
            continue

        state, returned_pane = _pane_state(pane)
        if state == "unknown":
            findings.append(f"{peer['role']} {name} pane {pane_id}: unknown or missing pane evidence")
            continue
        if state == "absent":
            # The recorded teardown target is gone.  Agent lookup is not used as
            # an alternate teardown proof, so agent_not_found is harmless here.
            continue
        if returned_pane != pane_id:
            findings.append(
                f"{peer['role']} {name} pane {pane_id}: Herdr returned mismatched pane evidence"
            )
            continue

        try:
            agent = herdr.read_agent(name)
        except Exception as exc:
            findings.append(f"{peer['role']} {name} pane {pane_id}: agent read failed: {exc}")
            agent = {"status": "unknown"}
        if _agent_is_not_found(agent):
            findings.append(
                f"{peer['role']} {name} pane {pane_id} remains open despite agent_not_found"
            )
        else:
            findings.append(f"{peer['role']} {name} pane {pane_id} remains open")

        try:
            process_evidence = herdr.read_processes(pane_id)
        except Exception as exc:
            findings.append(f"{peer['role']} {name} pane {pane_id}: process read failed: {exc}")
            continue
        processes = _process_list(process_evidence)
        if processes is None:
            findings.append(f"{peer['role']} {name} pane {pane_id}: unknown or missing process evidence")
            continue
        pane_cwd = pane.get("cwd") if isinstance(pane, Mapping) else None
        process_cwd = process_evidence.get("cwd") if isinstance(process_evidence, Mapping) else None
        for process in processes:
            if not isinstance(process, Mapping):
                findings.append(f"{peer['role']} {name} pane {pane_id}: malformed process evidence")
                continue
            if process.get("alive") is False or process.get("status") in {"exited", "dead"}:
                continue
            cwd = process.get("cwd", process_cwd or pane_cwd)
            if cwd is None:
                findings.append(f"{peer['role']} {name} pane {pane_id}: process evidence has no cwd")
                continue
            if _is_server_process(process) and _path_in_checkout(cwd, canonical):
                findings.append(
                    f"{peer['role']} {name} pane {pane_id}: squatting-server anti-pattern; "
                    f"live server/dev/preview process in canonical checkout {canonical}"
                )

    return CloseoutResult(not findings, tuple(findings), tuple(checked))


class _SubprocessHerdr:
    """The production adapter; record fields are passed only as argv values."""

    def _run(self, args: list[str]) -> Mapping[str, Any]:
        completed = subprocess.run(
            ["herdr", *args], capture_output=True, text=True, check=False
        )
        text = completed.stdout.strip() or completed.stderr.strip()
        try:
            value = json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return {"status": "read_error", "detail": text or "no JSON response"}
        if not isinstance(value, Mapping):
            return {"status": "read_error", "detail": "non-object Herdr response"}
        if completed.returncode:
            raw = json.dumps(value).lower()
            if "agent_not_found" in raw or "agent not found" in raw:
                return {"status": "agent_not_found"}
            if "pane_not_found" in raw or "pane not found" in raw:
                return {"status": "pane_not_found"}
            return {"status": "read_error", "detail": raw}
        return value

    def read_pane(self, pane_id: str) -> Mapping[str, Any]:
        raw = self._run(["pane", "get", pane_id])
        if _status(raw) in _ABSENT_STATUSES:
            return {"status": "absent"}
        result = raw.get("result")
        pane = result.get("pane") if isinstance(result, Mapping) else None
        if not isinstance(pane, Mapping) or not isinstance(pane.get("pane_id"), str):
            return {"status": "unknown"}
        return {"status": "open", "pane_id": pane["pane_id"], "cwd": pane.get("cwd")}

    def read_agent(self, agent_name: str) -> Mapping[str, Any]:
        raw = self._run(["agent", "get", agent_name])
        if _status(raw) == "agent_not_found":
            return {"status": "agent_not_found"}
        result = raw.get("result")
        agent = result.get("agent") if isinstance(result, Mapping) else None
        return agent if isinstance(agent, Mapping) else {"status": "unknown"}

    def read_processes(self, pane_id: str) -> Mapping[str, Any]:
        raw = self._run(["pane", "process-info", "--pane", pane_id])
        result = raw.get("result")
        process_info = result.get("process_info") if isinstance(result, Mapping) else None
        if not isinstance(process_info, Mapping):
            return {"status": "unknown"}
        return process_info


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staffing", required=True, type=Path, help="JSON run staffing record")
    args = parser.parse_args(argv)
    result = check_closeout(args.staffing, _SubprocessHerdr())
    if result.passed:
        print(f"PASS: checked {len(result.checked_panes)} recorded peer pane(s)")
        return 0
    for finding in result.findings:
        print(f"FAIL: {finding}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import sys
import fcntl
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from beo_check_identity import actor_identity
from beo_paths import normalize_posix, path_token_covers, path_tokens_overlap, reject_unsafe_path

RESERVATION_FILE = ".beads/beo-reservations.jsonl"
LOCK_FILE = ".beads/beo-reservations.lock"
RESERVATION_ID_PATTERN = re.compile(r"^res-[a-f0-9]{8}$")
UTC_TIMESTAMP_PATTERN = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def format_iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(ts: str) -> datetime:
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except Exception:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def get_lock(root: Path):
    lock_path = root / LOCK_FILE
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    f = open(lock_path, "w", encoding="utf-8")
    try:
        fcntl.flock(f, fcntl.LOCK_EX)
    except Exception:
        f.close()
        raise
    return f


def release_lock(f):
    fcntl.flock(f, fcntl.LOCK_UN)
    f.close()


def validate_reservation_record(record: dict[str, Any], line_number: int) -> None:
    required = {
        "reservation_id": str,
        "issue_id": str,
        "actor": str,
        "paths": list,
        "created_at": str,
        "status": str,
        "released_at": (str, type(None)),
        "release_reason": (str, type(None)),
        "superseded_by": (str, type(None)),
        "revoked_by": (str, type(None)),
        "revocation_ref": (str, type(None)),
    }
    allowed = set(required) | {"released_at", "release_reason", "superseded_by", "revoked_by", "revocation_ref"}
    unknown = sorted(set(record) - allowed)
    if unknown:
        raise ValueError(f"reservation entry on line {line_number} contains unknown field(s): {', '.join(unknown)}")
    missing = sorted(set(required) - set(record))
    if missing:
        raise ValueError(f"reservation entry on line {line_number} missing required field(s): {', '.join(missing)}")
    for field, expected_type in required.items():
        if not isinstance(record.get(field), expected_type):
            raise ValueError(f"reservation entry on line {line_number} has invalid {field}")
    if not RESERVATION_ID_PATTERN.fullmatch(record["reservation_id"]):
        raise ValueError(f"reservation entry on line {line_number} has invalid reservation_id")
    for field in ["issue_id", "actor"]:
        if not record[field].strip():
            raise ValueError(f"reservation entry on line {line_number} has invalid {field}")

    status = record["status"]
    if status not in {"active", "released", "superseded", "revoked"}:
        raise ValueError(f"reservation entry on line {line_number} has invalid status {status}")
    if not record["paths"] or not all(isinstance(path, str) and path for path in record["paths"]):
        raise ValueError(f"reservation entry on line {line_number} has invalid paths")
    for path in record["paths"]:
        try:
            reject_unsafe_path(path)
        except ValueError as exc:
            raise ValueError(f"reservation entry on line {line_number} has invalid paths: {exc}") from exc
    if not UTC_TIMESTAMP_PATTERN.fullmatch(record["created_at"]):
        raise ValueError(f"reservation entry on line {line_number} has invalid created_at")
    parse_iso(record["created_at"])

    if status == "active":
        for f in ["released_at", "release_reason", "superseded_by", "revoked_by", "revocation_ref"]:
            if record.get(f) is not None:
                raise ValueError(f"reservation entry on line {line_number} has release metadata on active status")
    elif status == "released":
        if not record.get("released_at") or not record.get("release_reason"):
            raise ValueError(f"released reservation on line {line_number} missing released_at or release_reason")
        if not isinstance(record.get("released_at"), str) or not UTC_TIMESTAMP_PATTERN.fullmatch(record["released_at"]):
            raise ValueError(f"released reservation on line {line_number} has invalid released_at")
        parse_iso(record["released_at"])
        if record.get("release_reason") not in {"verdict_accept", "cannot_deliver", "abandoned", "repair_rescope", "human_released"}:
            raise ValueError(f"reservation entry on line {line_number} has invalid released metadata")
        for f in ["superseded_by", "revoked_by", "revocation_ref"]:
            if record.get(f) is not None:
                raise ValueError(f"released reservation on line {line_number} has field {f} set")
    elif status == "superseded":
        if not record.get("superseded_by"):
            raise ValueError(f"superseded reservation on line {line_number} missing superseded_by")
        if not isinstance(record.get("superseded_by"), str) or not RESERVATION_ID_PATTERN.fullmatch(record["superseded_by"]):
            raise ValueError(f"superseded reservation on line {line_number} has invalid superseded_by")
        for f in ["released_at", "release_reason", "revoked_by", "revocation_ref"]:
            if record.get(f) is not None:
                raise ValueError(f"superseded reservation on line {line_number} has field {f} set")
    elif status == "revoked":
        if not isinstance(record.get("revoked_by"), str) or not record["revoked_by"].strip():
            raise ValueError(f"revoked reservation on line {line_number} missing revoked_by or revocation_ref")
        if not isinstance(record.get("revocation_ref"), str) or not record["revocation_ref"].strip():
            raise ValueError(f"revoked reservation on line {line_number} missing revoked_by or revocation_ref")
        if record.get("superseded_by") is not None:
            raise ValueError(f"revoked reservation on line {line_number} has field superseded_by set")
        released_at = record.get("released_at")
        release_reason = record.get("release_reason")
        if (released_at is None) != (release_reason is None):
            raise ValueError(f"revoked reservation on line {line_number} must preserve both released_at and release_reason or neither")
        if released_at is not None:
            if not isinstance(released_at, str) or not UTC_TIMESTAMP_PATTERN.fullmatch(released_at):
                raise ValueError(f"revoked reservation on line {line_number} has invalid released_at")
            parse_iso(released_at)
            if release_reason not in {"verdict_accept", "cannot_deliver", "abandoned", "repair_rescope", "human_released"}:
                raise ValueError(f"revoked reservation on line {line_number} has invalid released metadata")


def read_reservations(root: Path) -> list[dict[str, Any]]:
    path = root / RESERVATION_FILE
    if not path.exists():
        return []
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid reservation JSON on line {line_number}: {exc}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"reservation entry on line {line_number} must be an object")
            validate_reservation_record(record, line_number)
            records.append(record)
    return records


def fsync_dir(path: Path) -> None:
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_reservations(root: Path, records: list[dict[str, Any]]) -> None:
    path = root / RESERVATION_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
        fsync_dir(path.parent)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def get_active_reservations(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [r for r in records if r.get("status") == "active"]


def check_conflicts(
    active: list[dict[str, Any]], issue_id: str, paths: list[str]
) -> list[dict[str, Any]]:
    conflicts = []
    normalized_paths = [normalize_posix(p) for p in paths]
    for r in active:
        if r.get("issue_id") == issue_id:
            continue
        for rp in r.get("paths", []):
            for cp in normalized_paths:
                if path_tokens_overlap(rp, cp):
                    conflicts.append(r)
                    break
            else:
                continue
            break
    return conflicts


def validate_paths(paths: list[str]) -> list[str]:
    normalized = []
    for path in paths:
        reject_unsafe_path(path)
        normalized_path = normalize_posix(path)
        if normalized_path:
            normalized.append(normalized_path)
    if not normalized:
        raise ValueError("paths must contain at least one non-empty path")
    return normalized


def cmd_reserve(root: Path, issue_id: str, paths: list[str]) -> int:
    try:
        normalized_paths = validate_paths(paths)
    except ValueError as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, indent=2))
        return 1
    actor = actor_identity()
    if not actor:
        print(json.dumps({"status": "failed", "error": "BR_ACTOR or BEO_ACTOR is required for reservation"}, indent=2))
        return 1
    current_time = now_utc()

    lock = get_lock(root)
    try:
        records = read_reservations(root)
        active = get_active_reservations(records)

        conflicts = check_conflicts(active, issue_id, normalized_paths)
        if conflicts:
            conflicting_issues = sorted(list({c["issue_id"] for c in conflicts}))
            print(json.dumps({
                "status": "failed",
                "error": f"Path reservation conflicts with active leases: {', '.join(conflicting_issues)}",
                "conflicts": conflicts
            }, indent=2))
            return 1
        wrong_actor_leases = [r for r in active if r.get("issue_id") == issue_id and r.get("actor") != actor]
        if wrong_actor_leases:
            print(json.dumps({
                "status": "wrong_actor_reservation",
                "error": "active same-issue reservation belongs to a different actor",
                "wrong_actor_reservations": wrong_actor_leases,
            }, indent=2))
            return 1

        res_id = f"res-{hashlib.sha1(os.urandom(8)).hexdigest()[:8]}"
        for r in records:
            if r.get("issue_id") == issue_id and r.get("status") == "active" and r.get("actor") == actor:
                r["status"] = "superseded"
                r["superseded_by"] = res_id

        new_record = {
            "reservation_id": res_id,
            "issue_id": issue_id,
            "actor": actor,
            "paths": normalized_paths,
            "created_at": format_iso(current_time),
            "status": "active",
            "released_at": None,
            "release_reason": None,
            "superseded_by": None,
            "revoked_by": None,
            "revocation_ref": None
        }
        records.append(new_record)
        write_reservations(root, records)

        print(json.dumps({
            "status": "success",
            "reservation": new_record
        }, indent=2))
        return 0
    finally:
        release_lock(lock)


def cmd_check(root: Path, issue_id: str, paths: list[str]) -> int:
    try:
        normalized_paths = validate_paths(paths)
    except ValueError as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, indent=2))
        return 1
    lock = get_lock(root)
    try:
        records = read_reservations(root)
        active = get_active_reservations(records)
        conflicts = check_conflicts(active, issue_id, normalized_paths)
        actor = actor_identity()
        if not actor:
            print(json.dumps({"status": "missing_actor", "issue_id": issue_id, "error": "BR_ACTOR or BEO_ACTOR is required for reservation validation"}, indent=2))
            return 1
        same_issue_leases = [r for r in active if r.get("issue_id") == issue_id]
        current_leases = [r for r in same_issue_leases if r.get("actor") == actor]
        wrong_actor_leases = [r for r in same_issue_leases if r.get("actor") != actor]
        reserved_paths = [p for r in current_leases for p in r.get("paths", [])]
        missing_paths = [p for p in normalized_paths if not any(path_token_covers(rp, p) for rp in reserved_paths)]
        wrong_actor_covers_missing = any(
            path_token_covers(path, missing_path)
            for record in wrong_actor_leases
            for path in record.get("paths", [])
            for missing_path in missing_paths
        )

        status = "success"
        if conflicts:
            status = "conflicted"
        elif missing_paths and wrong_actor_covers_missing:
            status = "wrong_actor_reservation"
        elif missing_paths:
            status = "missing_current_reservation"
        result = {
            "status": status,
            "issue_id": issue_id,
            "conflicts": conflicts,
            "missing_paths": missing_paths,
            "wrong_actor_reservations": wrong_actor_leases
        }
        print(json.dumps(result, indent=2))
        return 1 if conflicts or missing_paths else 0
    finally:
        release_lock(lock)


def cmd_release(root: Path, issue_id: str, reason: str) -> int:
    allowed_reasons = {"verdict_accept", "cannot_deliver", "abandoned", "repair_rescope", "human_released"}
    if reason not in allowed_reasons:
        print(json.dumps({
            "status": "failed",
            "error": f"release reason must be one of {sorted(allowed_reasons)}"
        }, indent=2))
        return 1
    actor = actor_identity()
    if not actor:
        print(json.dumps({"status": "failed", "error": "BR_ACTOR or BEO_ACTOR is required for reservation release"}, indent=2))
        return 1
    current_time = now_utc()
    lock = get_lock(root)
    try:
        records = read_reservations(root)
        active_same_issue = [r for r in records if r.get("issue_id") == issue_id and r.get("status") == "active"]
        current_actor_leases = [r for r in active_same_issue if r.get("actor") == actor]
        wrong_actor_leases = [r for r in active_same_issue if r.get("actor") != actor]
        released_count = 0
        for r in current_actor_leases:
            r["status"] = "released"
            r["released_at"] = format_iso(current_time)
            r["release_reason"] = reason
            released_count += 1

        if released_count > 0:
            write_reservations(root, records)

        status = "success" if released_count or not wrong_actor_leases else "wrong_actor_reservation"
        result = {
            "status": status,
            "issue_id": issue_id,
            "actor": actor,
            "released_count": released_count,
            "reason": reason,
        }
        if wrong_actor_leases:
            result["wrong_actor_reservations"] = wrong_actor_leases
        print(json.dumps(result, indent=2))
        return 1 if status == "wrong_actor_reservation" else 0
    finally:
        release_lock(lock)


def cmd_revoke(root: Path, issue_id: str, revoked_by: str, revocation_ref: str) -> int:
    if not revoked_by.strip() or not revocation_ref.strip():
        print(json.dumps({"status": "failed", "error": "revoked_by and revocation_ref must be non-empty"}, indent=2))
        return 1
    lock = get_lock(root)
    try:
        records = read_reservations(root)
        revocable_same_issue = [r for r in records if r.get("issue_id") == issue_id and r.get("status") in {"active", "released"}]
        revoked_count = 0
        for r in revocable_same_issue:
            was_released = r.get("status") == "released"
            r["status"] = "revoked"
            if not was_released:
                r["released_at"] = None
                r["release_reason"] = None
            r["revoked_by"] = revoked_by
            r["revocation_ref"] = revocation_ref
            revoked_count += 1

        if revoked_count > 0:
            write_reservations(root, records)

        print(json.dumps({
            "status": "success",
            "issue_id": issue_id,
            "revoked_count": revoked_count
        }, indent=2))
        return 0
    finally:
        release_lock(lock)


def cmd_list(root: Path) -> int:
    lock = get_lock(root)
    try:
        records = read_reservations(root)
        active = get_active_reservations(records)
        print(json.dumps({
            "status": "success",
            "active_reservations": active
        }, indent=2))
        return 0
    finally:
        release_lock(lock)


def split_path_args(values: list[str]) -> list[str]:
    paths: list[str] = []
    for value in values:
        paths.extend(part.strip() for part in value.split(",") if part.strip())
    return paths


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="BEO path reservation lease manager")
    parser.add_argument("--root", default=".")
    
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_reserve = subparsers.add_parser("reserve")
    p_reserve.add_argument("--issue", required=True)
    p_reserve.add_argument("--paths", action="append", required=True, help="Comma-separated path list; may be repeated")

    p_check = subparsers.add_parser("check")
    p_check.add_argument("--issue", required=True)
    p_check.add_argument("--paths", action="append", required=True, help="Comma-separated path list; may be repeated")

    p_release = subparsers.add_parser("release")
    p_release.add_argument("--issue", required=True)
    p_release.add_argument("--reason", required=True)

    p_revoke = subparsers.add_parser("revoke")
    p_revoke.add_argument("--issue", required=True)
    p_revoke.add_argument("--revoked-by", required=True)
    p_revoke.add_argument("--revocation-ref", required=True)

    subparsers.add_parser("list")
    
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    
    try:
        if args.command == "reserve":
            return cmd_reserve(root, args.issue, split_path_args(args.paths))
        elif args.command == "check":
            return cmd_check(root, args.issue, split_path_args(args.paths))
        elif args.command == "release":
            return cmd_release(root, args.issue, args.reason)
        elif args.command == "revoke":
            return cmd_revoke(root, args.issue, args.revoked_by, args.revocation_ref)
        elif args.command == "list":
            return cmd_list(root)
    except ValueError as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, indent=2))
        return 1

    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import sys
import fcntl
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
import beo_utils
from beo_utils import normalize_posix, path_tokens_overlap

RESERVATION_FILE = ".beads/beo-reservations.jsonl"
LOCK_FILE = ".beads/beo-reservations.lock"
LEASE_TTL_SECONDS = 3600
RELEASE_REASONS = {"executed", "abandoned", "cannot_deliver", "expired", "superseded"}


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
    if record.get("status") != "active":
        return
    if not record.get("issue_id"):
        raise ValueError(f"active reservation on line {line_number} missing issue_id")
    if not record.get("expires_at"):
        raise ValueError(f"active reservation on line {line_number} missing expires_at")
    paths = record.get("paths")
    if not isinstance(paths, list) or not all(isinstance(path, str) for path in paths):
        raise ValueError(f"active reservation on line {line_number} must include string paths")


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


def gc_reservations_in_place(records: list[dict[str, Any]], current_time: datetime) -> int:
    expired_count = 0
    for r in records:
        if r.get("status") == "active":
            expires_at = parse_iso(r["expires_at"])
            if current_time > expires_at:
                r["status"] = "expired"
                r["released_at"] = format_iso(expires_at)
                r["release_reason"] = "expired"
                expired_count += 1
    return expired_count


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
    actor = beo_utils.actor_identity() or "unknown_agent"
    current_time = now_utc()
    expires_at = current_time + timedelta(seconds=LEASE_TTL_SECONDS)

    lock = get_lock(root)
    try:
        records = read_reservations(root)
        expired_count = gc_reservations_in_place(records, current_time)
        if expired_count:
            write_reservations(root, records)
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

        for r in records:
            if r.get("issue_id") == issue_id and r.get("status") == "active":
                r["status"] = "released"
                r["released_at"] = format_iso(current_time)
                r["release_reason"] = "superseded"

        res_id = f"res-{hashlib.sha1(os.urandom(8)).hexdigest()[:8]}"
        new_record = {
            "reservation_id": res_id,
            "issue_id": issue_id,
            "actor": actor,
            "paths": normalized_paths,
            "created_at": format_iso(current_time),
            "expires_at": format_iso(expires_at),
            "status": "active",
            "released_at": None,
            "release_reason": None
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
    current_time = now_utc()
    lock = get_lock(root)
    try:
        records = read_reservations(root)
        expired_count = gc_reservations_in_place(records, current_time)
        if expired_count:
            write_reservations(root, records)
        active = get_active_reservations(records)
        conflicts = check_conflicts(active, issue_id, normalized_paths)
        actor = beo_utils.actor_identity()
        same_issue_leases = [r for r in active if r.get("issue_id") == issue_id]
        current_leases = [r for r in same_issue_leases if not actor or r.get("actor") == actor]
        wrong_actor_leases = [r for r in same_issue_leases if actor and r.get("actor") != actor]
        reserved_paths = [p for r in current_leases for p in r.get("paths", [])]
        missing_paths = [p for p in normalized_paths if not any(path_tokens_overlap(rp, p) for rp in reserved_paths)]

        expiring_soon = []
        for c in conflicts + current_leases:
            expires = parse_iso(c["expires_at"])
            remaining = (expires - current_time).total_seconds()
            if remaining > 0 and remaining < 300:
                expiring_soon.append({
                    "issue_id": c["issue_id"],
                    "expires_in_seconds": remaining
                })

        status = "success"
        if conflicts:
            status = "conflicted"
        elif wrong_actor_leases and missing_paths:
            status = "wrong_actor_reservation"
        elif missing_paths:
            status = "missing_current_reservation"
        result = {
            "status": status,
            "issue_id": issue_id,
            "conflicts": conflicts,
            "missing_paths": missing_paths,
            "wrong_actor_reservations": wrong_actor_leases,
            "expiring_soon": expiring_soon
        }
        print(json.dumps(result, indent=2))
        return 1 if conflicts or missing_paths else 0
    finally:
        release_lock(lock)


def cmd_renew(root: Path, issue_id: str, reservation_id: str) -> int:
    actor = beo_utils.actor_identity() or "unknown_agent"
    current_time = now_utc()
    lock = get_lock(root)
    try:
        records = read_reservations(root)
        expired_count = gc_reservations_in_place(records, current_time)
        target = next((r for r in records if r.get("reservation_id") == reservation_id), None)
        if target is None:
            print(json.dumps({"status": "failed", "error": "reservation not found"}, indent=2))
            return 1
        if target.get("status") != "active":
            if expired_count:
                write_reservations(root, records)
            print(json.dumps({"status": "failed", "error": "only active reservations can be renewed"}, indent=2))
            return 1
        if target.get("issue_id") != issue_id:
            print(json.dumps({"status": "failed", "error": "reservation issue_id does not match"}, indent=2))
            return 1
        if target.get("actor") and target.get("actor") != actor:
            print(json.dumps({"status": "failed", "error": "reservation actor does not match"}, indent=2))
            return 1
        target["expires_at"] = format_iso(current_time + timedelta(seconds=LEASE_TTL_SECONDS))
        write_reservations(root, records)
        print(json.dumps({"status": "success", "reservation": target}, indent=2))
        return 0
    finally:
        release_lock(lock)


def cmd_release(root: Path, issue_id: str, reason: str) -> int:
    allowed_reasons = RELEASE_REASONS - {"expired", "superseded"}
    if reason not in allowed_reasons:
        print(json.dumps({
            "status": "failed",
            "error": f"release reason must be one of {sorted(allowed_reasons)}"
        }, indent=2))
        return 1
    current_time = now_utc()
    lock = get_lock(root)
    try:
        records = read_reservations(root)
        released_count = 0
        for r in records:
            if r.get("issue_id") == issue_id and r.get("status") == "active":
                r["status"] = "released"
                r["released_at"] = format_iso(current_time)
                r["release_reason"] = reason
                released_count += 1
        
        if released_count > 0:
            write_reservations(root, records)

        print(json.dumps({
            "status": "success",
            "issue_id": issue_id,
            "released_count": released_count,
            "reason": reason
        }, indent=2))
        return 0
    finally:
        release_lock(lock)


def cmd_gc(root: Path) -> int:
    current_time = now_utc()
    lock = get_lock(root)
    try:
        records = read_reservations(root)
        expired_count = gc_reservations_in_place(records, current_time)
        if expired_count > 0:
            write_reservations(root, records)
        print(json.dumps({
            "status": "success",
            "expired_count": expired_count
        }, indent=2))
        return 0
    finally:
        release_lock(lock)


def cmd_list(root: Path) -> int:
    current_time = now_utc()
    lock = get_lock(root)
    try:
        records = read_reservations(root)
        expired_count = gc_reservations_in_place(records, current_time)
        if expired_count:
            write_reservations(root, records)
        active = get_active_reservations(records)
        print(json.dumps({
            "status": "success",
            "active_reservations": active
        }, indent=2))
        return 0
    finally:
        release_lock(lock)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="BEO path reservation lease manager")
    parser.add_argument("--root", default=".")
    
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_reserve = subparsers.add_parser("reserve")
    p_reserve.add_argument("--issue", required=True)
    p_reserve.add_argument("--paths", required=True, help="Comma-separated path list")

    p_check = subparsers.add_parser("check")
    p_check.add_argument("--issue", required=True)
    p_check.add_argument("--paths", required=True, help="Comma-separated path list")

    p_renew = subparsers.add_parser("renew")
    p_renew.add_argument("--issue", required=True)
    p_renew.add_argument("--reservation-id", required=True)

    p_release = subparsers.add_parser("release")
    p_release.add_argument("--issue", required=True)
    p_release.add_argument("--reason", required=True)

    subparsers.add_parser("gc")
    subparsers.add_parser("list")
    
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    
    try:
        if args.command == "reserve":
            paths = [p.strip() for p in args.paths.split(",") if p.strip()]
            return cmd_reserve(root, args.issue, paths)
        elif args.command == "check":
            paths = [p.strip() for p in args.paths.split(",") if p.strip()]
            return cmd_check(root, args.issue, paths)
        elif args.command == "renew":
            return cmd_renew(root, args.issue, args.reservation_id)
        elif args.command == "release":
            return cmd_release(root, args.issue, args.reason)
        elif args.command == "gc":
            return cmd_gc(root)
        elif args.command == "list":
            return cmd_list(root)
    except ValueError as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, indent=2))
        return 1

    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

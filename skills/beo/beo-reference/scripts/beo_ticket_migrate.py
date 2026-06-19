#!/usr/bin/env python3
"""One-time migration: convert TICKET.yaml and harness-proposal.yaml to JSON.

Run this once per project after upgrading to a BEO version that no longer
reads YAML. It walks ``.beads/artifacts/<issue-id>/`` and rewrites each
ticket/proposal in place.

Usage:
    python3 beo_ticket_migrate.py [--root PATH] [--dry-run] [--delete-old]

``--delete-old`` removes the original ``.yaml`` files after a successful
conversion. Without it, the originals are left in place for manual review.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import beo_ticket  # noqa: E402


def _convert_yaml_to_json(
    yaml_path: Path, *, dry_run: bool, validator=None
) -> str:
    """Read a YAML file, optionally validate it, and write an equivalent JSON file.

    Returns "converted", "skipped" (the .json already exists), or "failed".
    The skip check runs before any YAML parsing, so re-running the migrator
    is idempotent even when PyYAML is no longer installed.
    """
    json_path = yaml_path.with_suffix(".json")
    if json_path.exists():
        print(f"  SKIP {yaml_path}: {json_path.name} already exists")
        return "skipped"
    try:
        raw = yaml_path.read_bytes()
    except Exception as exc:
        print(f"  FAIL {yaml_path}: cannot read ({exc})")
        return "failed"
    try:
        import yaml  # type: ignore[import-not-found]
        data = yaml.safe_load(raw)
    except ImportError:
        print(f"  FAIL {yaml_path}: PyYAML is required for one-time migration")
        return "failed"
    except Exception as exc:
        print(f"  FAIL {yaml_path}: invalid YAML ({exc})")
        return "failed"
    if not isinstance(data, dict):
        print(f"  FAIL {yaml_path}: not a YAML mapping")
        return "failed"
    if validator is not None:
        try:
            validator(data)
        except ValueError as exc:
            print(f"  FAIL {yaml_path}: validation failed ({exc})")
            return "failed"
    if dry_run:
        print(f"  WOULD WRITE {json_path}")
        return "converted"
    json_path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"  WROTE  {json_path}")
    return "converted"


def migrate_ticket(yaml_path: Path, *, dry_run: bool) -> str:
    """Convert a single TICKET.yaml to TICKET.json. Validates against the plan schema."""
    return _convert_yaml_to_json(yaml_path, dry_run=dry_run, validator=beo_ticket.validate_plan_only)


def migrate_proposal(yaml_path: Path, *, dry_run: bool) -> str:
    """Convert a single harness-proposal.yaml to .json. No schema validation (proposals may be partial)."""
    return _convert_yaml_to_json(yaml_path, dry_run=dry_run)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".", help="Workspace root (default: cwd)")
    parser.add_argument("--dry-run", action="store_true", help="Print planned conversions without writing")
    parser.add_argument("--delete-old", action="store_true", help="Delete the original .yaml files after a successful conversion")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    artifacts = root / ".beads" / "artifacts"
    if not artifacts.is_dir():
        print(f"No .beads/artifacts directory under {root}")
        return 0

    ticket_files = sorted(artifacts.glob("*/TICKET.yaml"))
    proposal_files = sorted(artifacts.glob("*/harness-proposal.yaml"))

    if not ticket_files and not proposal_files:
        print("No TICKET.yaml or harness-proposal.yaml files found. Nothing to migrate.")
        return 0

    print(f"Found {len(ticket_files)} TICKET.yaml, {len(proposal_files)} harness-proposal.yaml")
    if args.dry_run:
        print("(dry run: no files will be written)")
    print()

    converted = 0
    skipped = 0
    failed = 0
    print("TICKET.yaml -> TICKET.json:")
    for ticket_yaml in ticket_files:
        status = migrate_ticket(ticket_yaml, dry_run=args.dry_run)
        if status == "converted":
            converted += 1
            if args.delete_old and not args.dry_run:
                ticket_yaml.unlink()
                print(f"  DELETED {ticket_yaml}")
        elif status == "skipped":
            skipped += 1
        else:
            failed += 1
    print()
    print("harness-proposal.yaml -> harness-proposal.json:")
    for proposal_yaml in proposal_files:
        status = migrate_proposal(proposal_yaml, dry_run=args.dry_run)
        if status == "converted":
            converted += 1
            if args.delete_old and not args.dry_run:
                proposal_yaml.unlink()
                print(f"  DELETED {proposal_yaml}")
        elif status == "skipped":
            skipped += 1
        else:
            failed += 1

    print()
    print(f"Summary: {converted} converted, {skipped} skipped, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

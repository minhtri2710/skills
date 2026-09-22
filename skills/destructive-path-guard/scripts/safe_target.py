#!/usr/bin/env python3
"""Refuse a destructive target that is not provably contained in an allowlisted root.

A symlink leaf is kept as the link: only its parent is resolved, and its
non-strict pointee must be inside an allowlisted root. With multiple roots,
containment and depth use the nearest containing root; a target that is or
contains an allowlisted root is refused. Ownership evidence is read before the
caller's delete, move, or overwrite runs. A refusal is final: no broader root is tried.

Exit codes: 0 accepted (the checked target is printed), 1 refused, 2 cannot check.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


class Refused(Exception):
    """The target is not provably safe to destroy."""


class CannotCheck(Exception):
    """The check itself could not run, so nothing is proven either way."""


def _resolve(candidate: Path) -> Path:
    """Resolve a target, keeping a symlink leaf as the link itself."""
    try:
        if candidate.is_symlink():
            return candidate.parent.resolve(strict=True) / candidate.name
        if candidate.exists():
            return candidate.resolve(strict=True)
        parent = candidate.parent.resolve(strict=True)
    except OSError as exc:
        raise CannotCheck(f"cannot resolve {candidate}: {exc}") from exc
    return parent / candidate.name


def resolve_target(
    candidate: str | Path,
    roots: list[str],
    min_depth: int = 1,
    owner_file: str | None = None,
    expect_owner: str | None = None,
) -> Path:
    """Return the resolved target, or raise ``Refused``."""
    if not roots:
        raise CannotCheck("no allowlisted root given")
    if min_depth < 1:
        raise CannotCheck("min_depth below 1 would let a root be the target")
    target = _resolve(Path(candidate))
    resolved_roots = []
    for raw in roots:
        try:
            resolved_roots.append(Path(raw).resolve(strict=True))
        except OSError as exc:
            raise CannotCheck(f"cannot resolve root {raw}: {exc}") from exc

    if target.is_symlink():
        pointee = Path(os.path.realpath(target))
        if not any(
            _is_contained(pointee, root)
            for root in resolved_roots
        ):
            raise Refused(f"symlink points outside allowed roots: {target} -> {pointee}")

    for root in resolved_roots:
        if target == root or _is_contained(root, target):
            raise Refused(f"target is or contains an allowed root: {target}")

    containing = [
        (root, target.relative_to(root))
        for root in resolved_roots
        if _is_contained(target, root)
    ]
    if not containing:
        raise Refused(f"outside allowed roots or above min depth: {target}")
    root, inside = max(containing, key=lambda item: len(item[0].parts))
    if len(inside.parts) < min_depth:
        raise Refused(f"outside allowed roots or above min depth: {target}")

    if owner_file:
        holder = target if (not target.is_symlink() and target.is_dir()) else target.parent
        if holder == root:
            raise Refused(f"unproven owner: evidence would be read from the root itself: {root}")
        evidence = holder / owner_file
        try:
            owner = evidence.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise Refused(f"unproven owner, evidence unreadable: {exc}") from exc
        if owner != expect_owner:
            raise Refused(f"unproven owner: {evidence}")

    return target


def _is_contained(candidate: Path, root: Path) -> bool:
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("target", help="path the destructive operation would act on")
    parser.add_argument("--root", action="append", default=[], required=True, help="allowlisted root (repeatable)")
    parser.add_argument("--min-depth", type=int, default=1, help="levels the target must sit below a root (default: 1, minimum: 1)")
    parser.add_argument("--owner-file", help="file inside the target holding ownership evidence")
    parser.add_argument("--expect-owner", help="value that file must contain")
    args = parser.parse_args(argv)
    if args.owner_file and args.expect_owner is None:
        parser.error("--owner-file requires --expect-owner")
    if args.min_depth < 1:
        parser.error("--min-depth must be at least 1")
    try:
        target = resolve_target(args.target, args.root, args.min_depth, args.owner_file, args.expect_owner)
    except Refused as exc:
        print(f"safe-target: refusing: {exc}", file=sys.stderr)
        return 1
    except CannotCheck as exc:
        print(f"safe-target: cannot check: {exc}", file=sys.stderr)
        return 2
    print(target)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Refuse a destructive target that is not provably contained in an allowlisted root.

A symlink leaf is kept as the link: only its parent is resolved. Its non-strict
pointee must pass the same root, depth, and root-equality rules as a plain
target, and with ownership evidence it must sit inside the directory that holds
the evidence. With multiple roots, containment and depth use the nearest
containing root; a target that is or contains an allowlisted root is refused.
Ownership evidence is read before the caller's delete, move, or overwrite runs.
An empty target, root, or expected owner cannot be checked. A refusal is final:
no broader root is tried.

Exit codes: 0 accepted (the checked target is printed), 1 refused, 2 cannot check.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


class Refused(Exception):
    pass


class CannotCheck(Exception):
    pass


def _resolve(candidate: Path) -> Path:
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
    if not roots or "" in roots:
        raise CannotCheck("no allowlisted root given, or a root is empty")
    if candidate == "":
        raise CannotCheck("empty target")
    if min_depth < 1:
        raise CannotCheck("min_depth below 1 would let a root be the target")
    if (owner_file is None) != (expect_owner is None):
        raise CannotCheck("owner_file and expect_owner must be given together")
    if expect_owner is not None and not expect_owner.strip():
        raise CannotCheck("expect_owner is empty")
    if owner_file is not None and (Path(owner_file).parts != (owner_file,) or owner_file == ".."):
        raise CannotCheck("owner_file must be a file name")
    target = _resolve(Path(candidate))
    resolved_roots = []
    for raw in roots:
        try:
            resolved_roots.append(Path(raw).resolve(strict=True))
        except OSError as exc:
            raise CannotCheck(f"cannot resolve root {raw}: {exc}") from exc

    pointee = None
    if target.is_symlink():
        pointee = Path(os.path.realpath(target))
        if not any(_is_contained(pointee, root) for root in resolved_roots):
            raise Refused(f"symlink points outside allowed roots: {target} -> {pointee}")
        _nearest_root(pointee, resolved_roots, min_depth)

    root = _nearest_root(target, resolved_roots, min_depth)

    if owner_file is not None:
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
        if pointee is not None and not _is_contained(pointee, holder):
            raise Refused(f"symlink points outside the owner's directory: {target} -> {pointee}")

    return target


def _nearest_root(target: Path, roots: list[Path], min_depth: int) -> Path:
    for root in roots:
        if target == root or _is_contained(root, target):
            raise Refused(f"target is or contains an allowed root: {target}")
    containing = [(root, target.relative_to(root)) for root in roots if _is_contained(target, root)]
    if not containing:
        raise Refused(f"outside allowed roots or above min depth: {target}")
    root, inside = max(containing, key=lambda item: len(item[0].parts))
    if len(inside.parts) < min_depth:
        raise Refused(f"outside allowed roots or above min depth: {target}")
    return root


def _is_contained(candidate: Path, root: Path) -> bool:
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("target", help="path the destructive operation would act on")
    parser.add_argument("--root", action="append", required=True, help="allowlisted root (repeatable)")
    parser.add_argument("--min-depth", type=int, default=1, help="levels the target must sit below a root (default: 1, minimum: 1)")
    parser.add_argument("--owner-file", help="file inside the target holding ownership evidence")
    parser.add_argument("--expect-owner", help="value that file must contain")
    args = parser.parse_args(argv)
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

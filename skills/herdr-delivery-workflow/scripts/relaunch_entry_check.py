#!/usr/bin/env python3
"""Derive relaunch file counts and verify quoted next-item blocks."""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


class CheckError(Exception):
    """The requested relaunch evidence could not be derived or verified."""


GATE_ID_RE = re.compile(r"\bG\d+\b")


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode:
        raise CheckError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def skill_prefix(value: str) -> str:
    """Return a safe repository-relative prefix for git ls-tree."""
    path = Path(value)
    if not value or path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise CheckError("--skill-path must be a non-empty repository-relative path")
    return value.rstrip("/") + "/"


def tracked_files(repo: Path, head: str, skill_path: str) -> list[str]:
    prefix = skill_prefix(skill_path)
    paths = git(repo, "ls-tree", "-r", "--name-only", head, prefix).splitlines()
    if not paths:
        raise CheckError(f"head {head!r} has no tracked files under {prefix}")
    if any(not path.startswith(prefix) for path in paths):
        raise CheckError(f"git ls-tree returned a path outside {prefix}")
    return paths


def _is_pycache(path: Path) -> bool:
    return "__pycache__" in path.parts


def installed_files(install_dir: Path) -> list[Path]:
    """List installed file entries, excluding every __pycache__ subtree."""
    if not install_dir.exists():
        return []
    if not install_dir.is_dir():
        raise CheckError(f"--installed-path is not a directory: {install_dir}")

    files: list[Path] = []
    for root, dirs, names in os.walk(install_dir, topdown=True, followlinks=False):
        root_path = Path(root)
        dirs[:] = [
            name for name in dirs
            if name != "__pycache__" and not (root_path / name).is_symlink()
        ]
        for name in names:
            relative = (root_path / name).relative_to(install_dir)
            if not _is_pycache(relative):
                files.append(relative)
    return sorted(files)


def count_evidence(repo: Path, head: str, skill_path: str,
                   install_dir: Path) -> tuple[int, int, int]:
    """Return tracked count, installed count, and missing/different hash count.

    A tracked file that is absent from the installed tree counts as a hash
    mismatch. Extra installed files affect the installed count but not the
    hash-mismatch count; the two values expose both directions of drift.
    """
    paths = tracked_files(repo, head, skill_path)
    prefix = skill_prefix(skill_path)
    installed = installed_files(install_dir)
    installed_set = set(installed)
    mismatches = 0
    for tracked in paths:
        relative = Path(tracked[len(prefix):])
        destination = install_dir / relative
        if relative not in installed_set or destination.is_symlink() or not destination.is_file():
            mismatches += 1
            continue
        expected = git(repo, "rev-parse", f"{head}:{tracked}")
        actual = git(repo, "hash-object", str(destination))
        if actual != expected:
            mismatches += 1
    return len(paths), len(installed), mismatches


def read_exact(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return handle.read()
    except (OSError, UnicodeError) as exc:
        raise CheckError(f"could not read {path}: {exc}") from None


def verify_block(block_file: Path, source_file: Path) -> list[str]:
    """Require the block as an exact contiguous substring of its source."""
    block = read_exact(block_file)
    if not block:
        raise CheckError("--block-file must contain a non-empty block")
    source = read_exact(source_file)
    if block not in source:
        raise CheckError(
            f"block from {block_file} is not a verbatim contiguous block in {source_file}"
        )
    gate_ids = list(dict.fromkeys(GATE_ID_RE.findall(block)))
    if not gate_ids:
        raise CheckError("the verified block contains no gate ids")
    return gate_ids


def _require_count_args(args: argparse.Namespace) -> tuple[Path, str, str, Path]:
    missing = [
        name for name, value in (
            ("--repo", args.repo),
            ("--head", args.head),
            ("--skill-path", args.skill_path),
            ("--installed-path", args.installed_path),
        ) if value is None
    ]
    if missing:
        raise CheckError(f"--count requires {', '.join(missing)}")
    return Path(args.repo).resolve(), args.head, args.skill_path, Path(args.installed_path).expanduser().resolve()


def _require_verify_args(args: argparse.Namespace) -> tuple[Path, Path]:
    missing = [
        name for name, value in (
            ("--block-file", args.block_file),
            ("--source-file", args.source_file),
        ) if value is None
    ]
    if missing:
        raise CheckError(f"--verify requires {', '.join(missing)}")
    return Path(args.block_file), Path(args.source_file)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--count", action="store_true", help="derive tracked/installed/hash counts")
    modes.add_argument("--verify", action="store_true", help="verify a next-item block verbatim")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--head", help="deployed git head used for COUNT mode")
    parser.add_argument("--skill-path", help="repository-relative skill directory used for COUNT mode")
    parser.add_argument("--installed-path", type=Path,
                        help="installed skill directory used for COUNT mode")
    parser.add_argument("--block-file", type=Path,
                        help="file containing the next-item block used for VERIFY mode")
    parser.add_argument("--source-file", type=Path,
                        help="named source file used for VERIFY mode")
    args = parser.parse_args(argv)

    try:
        if args.count:
            repo, head, skill_path, install_dir = _require_count_args(args)
            tracked, installed, mismatches = count_evidence(repo, head, skill_path, install_dir)
            print(f"tracked={tracked} installed={installed} hash-mismatches={mismatches}")
        else:
            block_file, source_file = _require_verify_args(args)
            print(" ".join(verify_block(block_file, source_file)))
    except (CheckError, OSError) as exc:
        print(f"relaunch_entry_check: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

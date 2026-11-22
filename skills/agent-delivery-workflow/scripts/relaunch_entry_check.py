#!/usr/bin/env python3
"""Derive relaunch file counts and verify quoted next-item blocks."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import gate_row
from gitops import GitError
from skill_tree import SkillTree, TreeError


class CheckError(Exception):
    pass


GATE_ID_RE = re.compile(r"\bG\d+\b")


def count_evidence(repo: Path, head: str, skill: str,
                   install_dir: Path) -> tuple[int, int, int]:
    if install_dir.exists() and not install_dir.is_dir():
        raise CheckError(f"--installed-path is not a directory: {install_dir}")
    try:
        report = SkillTree.at(repo, head, skill).compare(install_dir)
    except (TreeError, GitError) as exc:
        raise CheckError(str(exc)) from None
    return report.tracked, report.installed, report.drifted


def read_exact(path: Path) -> str:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return handle.read()
    except (OSError, UnicodeError) as exc:
        raise CheckError(f"could not read {path}: {exc}") from None


def verify_block(block_file: Path, source_file: Path) -> list[str]:
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


def _require_count_args(args: argparse.Namespace) -> tuple[Path, Path, str, Path]:
    missing = [
        name for name, value in (
            ("--ledger", args.ledger),
            ("--skill", args.skill),
            ("--installed-path", args.installed_path),
        ) if value is None
    ]
    if missing:
        raise CheckError(f"--count requires {', '.join(missing)}")
    return (Path(args.repo).resolve(), args.ledger, args.skill,
            Path(args.installed_path).expanduser().resolve())


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
    modes.add_argument("--count", action="store_true", help="derive tracked/installed/drifted counts")
    modes.add_argument("--verify", action="store_true", help="verify a next-item block verbatim")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--ledger", type=Path, help="verified project gate ledger")
    parser.add_argument("--skill", help="top-level deployed skill name")
    parser.add_argument("--installed-path", type=Path,
                        help="installed skill directory used for COUNT mode")
    parser.add_argument("--block-file", type=Path,
                        help="file containing the next-item block used for VERIFY mode")
    parser.add_argument("--source-file", type=Path,
                        help="named source file used for VERIFY mode")
    args = parser.parse_args(argv)

    try:
        if args.count:
            repo, ledger, skill, install_dir = _require_count_args(args)
            try:
                _branch, head, _row = gate_row.select_deployed_head(ledger, skill, repo)
            except gate_row.RowError as exc:
                raise CheckError(f"gate_row: {exc}") from None
            tracked, installed, drifted = count_evidence(repo, head, skill, install_dir)
            print(f"tracked={tracked} installed={installed} drifted={drifted}")
            if tracked != installed or drifted:
                return 1
        else:
            block_file, source_file = _require_verify_args(args)
            print(" ".join(verify_block(block_file, source_file)))
    except (CheckError, OSError) as exc:
        print(f"relaunch_entry_check: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

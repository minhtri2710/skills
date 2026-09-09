#!/usr/bin/env python3
"""Install the tracked workflow skill, verify it, and record its deploy row."""
from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path


class DeployError(Exception):
    """The tracked skill could not be installed or accepted."""


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode:
        raise DeployError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def tracked_files(repo: Path, head: str, skill_prefix: str) -> list[str]:
    prefix = skill_prefix.rstrip("/") + "/"
    paths = git(repo, "ls-tree", "-r", "--name-only", head, prefix).splitlines()
    if not paths:
        raise DeployError(f"head {head} has no tracked files under {prefix}")
    if any(not path.startswith(prefix) for path in paths):
        raise DeployError(f"git ls-tree returned a path outside {prefix}")
    return paths


def _safe_install_dir(path: Path) -> Path:
    return Path(os.path.abspath(os.path.expanduser(path)))


def _relative_paths(paths: list[str], prefix: str) -> set[Path]:
    return {Path(path[len(prefix):]) for path in paths}


def _is_pycache(path: Path) -> bool:
    return "__pycache__" in path.parts


def _prune_install(install_dir: Path, tracked: set[Path]) -> None:
    for root, dirs, files in os.walk(install_dir, topdown=False, followlinks=False):
        root_path = Path(root)
        for name in files:
            path = root_path / name
            relative = path.relative_to(install_dir)
            if not _is_pycache(relative) and (
                path.is_symlink() or relative not in tracked
            ):
                path.unlink()
        for name in dirs:
            path = root_path / name
            relative = path.relative_to(install_dir)
            if _is_pycache(relative):
                continue
            if path.is_symlink():
                path.unlink()
                continue
            try:
                path.rmdir()
            except OSError:
                pass


def install_files(repo: Path, head: str, source_dir: Path, install_dir: Path,
                  paths: list[str], skill_prefix: str) -> None:
    prefix = skill_prefix.rstrip("/") + "/"
    source_dir = source_dir.resolve()
    install_dir = _safe_install_dir(install_dir)
    sources: list[tuple[Path, Path]] = []
    for tracked in paths:
        relative = Path(tracked[len(prefix):])
        source = source_dir / relative
        if not source.is_file():
            raise DeployError(f"tracked source file is missing: {source}")
        sources.append((source, relative))

    install_dir.mkdir(parents=True, exist_ok=True)
    _prune_install(install_dir, {relative for _, relative in sources})
    for source, relative in sources:
        destination = install_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if (
            destination.is_file()
            and not destination.is_symlink()
            and source.read_bytes() == destination.read_bytes()
            and stat.S_IMODE(source.stat().st_mode) == stat.S_IMODE(destination.stat().st_mode)
        ):
            continue
        shutil.copy2(source, destination)


def verify_install(repo: Path, head: str, install_dir: Path,
                   paths: list[str], skill_prefix: str) -> None:
    prefix = skill_prefix.rstrip("/") + "/"
    install_dir = _safe_install_dir(install_dir)
    tracked = _relative_paths(paths, prefix)
    for tracked_path in paths:
        installed = install_dir / Path(tracked_path[len(prefix):])
        if installed.is_symlink() or not installed.is_file():
            raise DeployError(f"installed file is missing: {installed}")
        expected = git(repo, "rev-parse", f"{head}:{tracked_path}")
        actual = git(repo, "hash-object", str(installed))
        if actual != expected:
            raise DeployError(
                f"installed hash mismatch for {tracked_path}: expected {expected}, got {actual}"
            )

    for root, dirs, files in os.walk(install_dir, topdown=True, followlinks=False):
        root_path = Path(root)
        kept_dirs = []
        for name in dirs:
            path = root_path / name
            relative = path.relative_to(install_dir)
            if _is_pycache(relative):
                continue
            if path.is_symlink():
                raise DeployError(f"installed path is not tracked: {path}")
            kept_dirs.append(name)
        dirs[:] = kept_dirs
        for name in files:
            path = root_path / name
            relative = path.relative_to(install_dir)
            if not _is_pycache(relative) and relative not in tracked:
                raise DeployError(f"installed file is not tracked: {path}")


def append_deploy_row(args: argparse.Namespace, repo: Path, script: Path) -> None:
    command = [
        sys.executable, str(script),
        "--repo", str(repo), "--ledger", str(args.ledger),
        "--kind", "deploy", "--status", args.status,
        "--words", args.words, "--note", args.note, "--quote", args.quote,
    ]
    if args.channel:
        command.extend(["--channel", args.channel])
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        raise DeployError(
            f"gate_row.py refused deploy row: {result.stderr.strip() or result.stdout.strip()}"
        )
    sys.stdout.write(result.stdout)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--source-dir", type=Path,
                        default=Path("skills/herdr-delivery-workflow"))
    parser.add_argument("--install-dir", type=Path,
                        default=Path.home() / ".claude/skills/herdr-delivery-workflow")
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--status", required=True)
    parser.add_argument("--channel")
    parser.add_argument("--words", required=True)
    parser.add_argument("--note", required=True)
    parser.add_argument("--quote", required=True)
    args = parser.parse_args(argv)

    try:
        repo = args.repo.resolve()
        head = git(repo, "rev-parse", args.head)
        current_head = git(repo, "rev-parse", "HEAD")
        if head != current_head:
            raise DeployError(
                f"--head {head} is not the current repository HEAD {current_head}; "
                "gate_row.py records the current HEAD"
            )
        source_dir = args.source_dir if args.source_dir.is_absolute() else repo / args.source_dir
        install_dir = args.install_dir.expanduser()
        paths = tracked_files(repo, head, "skills/herdr-delivery-workflow")
        install_files(repo, head, source_dir, install_dir, paths, "skills/herdr-delivery-workflow")
        verify_install(repo, head, install_dir, paths, "skills/herdr-delivery-workflow")
        append_deploy_row(args, repo, Path(__file__).resolve().with_name("gate_row.py"))
    except (DeployError, OSError) as exc:
        print(f"deploy_skill: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

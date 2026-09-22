#!/usr/bin/env python3
"""Install selected tracked skills, verify them, and record one deploy row."""
from __future__ import annotations

import argparse
import os
import stat
import subprocess
import sys
from pathlib import Path


class DeployError(Exception):
    """The tracked skill could not be installed or accepted."""


# Repo-only directories: the plugin manifest and the `claude plugin eval` suite exist for the
# R1 green-eval gate and are never skill runtime. A deployed `.claude-plugin/` auto-loads as a
# plugin on the next session, so these are excluded from the install even when tracked.
DEPLOY_EXCLUDE = (".claude-plugin", "plugin-eval")


def runtime_paths(paths: list[str], skill_prefix: str) -> list[str]:
    prefix = skill_prefix.rstrip("/") + "/"
    kept = [p for p in paths if p[len(prefix):].split("/", 1)[0] not in DEPLOY_EXCLUDE]
    if not kept:
        raise DeployError("no runtime files remain after excluding repo-only directories")
    return kept


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


def tracked_skills(repo: Path, head: str) -> list[str]:
    skills = git(repo, "ls-tree", "-d", "--name-only", f"{head}:skills").splitlines()
    if not skills:
        raise DeployError(f"head {head} has no tracked top-level skills")
    if any(not skill or Path(skill).parts != (skill,) for skill in skills):
        raise DeployError("git ls-tree returned a non-top-level skill")
    return skills


def selected_skills(repo: Path, head: str, requested: list[str]) -> list[str]:
    available = tracked_skills(repo, head)
    if not requested:
        return available
    if len(requested) != len(set(requested)):
        raise DeployError("--skill names a skill more than once")
    invalid = [
        skill for skill in requested
        if Path(skill).parts != (skill,) or skill not in available
    ]
    if invalid:
        raise DeployError(
            f"unknown or unsafe skill selection: {', '.join(invalid)}"
        )
    return [skill for skill in available if skill in requested]


def tracked_files(repo: Path, head: str, skill_prefix: str) -> list[str]:
    prefix = skill_prefix.rstrip("/") + "/"
    paths = git(repo, "ls-tree", "-r", "--name-only", head, prefix).splitlines()
    if not paths:
        raise DeployError(f"head {head} has no tracked files under {prefix}")
    if any(not path.startswith(prefix) for path in paths):
        raise DeployError(f"git ls-tree returned a path outside {prefix}")
    return paths


def _safe_install_dir(path: Path, *, allow_self_symlink: bool = False) -> Path:
    path = Path(os.path.abspath(os.path.expanduser(path)))
    if path.is_symlink() and (not allow_self_symlink or not path.is_dir()):
        raise DeployError(f"install tree is a symlink: {path}")
    return path


def resolved_files(repo: Path, head: str, paths: list[str], skill_prefix: str) -> list[tuple[Path, bytes, int]]:
    prefix = skill_prefix.rstrip("/") + "/"
    resolved: list[tuple[Path, bytes, int]] = []
    for tracked in paths:
        if not tracked.startswith(prefix):
            raise DeployError(f"tracked path is outside {prefix}: {tracked}")
        tree = subprocess.run(
            ["git", "-C", str(repo), "ls-tree", head, "--", tracked],
            capture_output=True,
            text=True,
            check=False,
        )
        if tree.returncode:
            raise DeployError(f"git ls-tree failed for {tracked}: {tree.stderr.strip()}")
        entries = tree.stdout.splitlines()
        if len(entries) != 1:
            raise DeployError(f"head {head} has no unique tree entry for {tracked}")
        metadata = entries[0].split("\t", 1)[0].split()
        if len(metadata) != 3:
            raise DeployError(f"git ls-tree returned malformed metadata for {tracked}")
        mode, object_type, _object_id = metadata
        if object_type != "blob" or mode not in {"100644", "100755"}:
            raise DeployError(f"tracked path has unsupported mode for {tracked}: {mode}")
        blob = subprocess.run(
            ["git", "-C", str(repo), "cat-file", "blob", f"{head}:{tracked}"],
            capture_output=True,
            check=False,
        )
        if blob.returncode:
            detail = blob.stderr.decode(errors="replace").strip()
            raise DeployError(f"git cat-file failed for {tracked}: {detail}")
        resolved.append((Path(tracked[len(prefix):]), blob.stdout, 0o755 if mode == "100755" else 0o644))
    return resolved


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


def install_files(install_dir: Path, resolved: list[tuple[Path, bytes, int]]) -> None:
    install_dir = _safe_install_dir(install_dir)
    install_dir.mkdir(parents=True, exist_ok=True)
    _prune_install(install_dir, {relative for relative, _content, _mode in resolved})
    for relative, content, mode in resolved:
        destination = install_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.is_symlink():
            destination.unlink()
        elif destination.exists() and not destination.is_file():
            raise DeployError(f"installed path is not a file: {destination}")
        if (
            destination.is_file()
            and destination.read_bytes() == content
            and stat.S_IMODE(destination.stat().st_mode) == mode
        ):
            continue
        destination.write_bytes(content)
        os.chmod(destination, mode)


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
        metadata = git(repo, "ls-tree", head, "--", tracked_path).split("\t", 1)[0].split()
        if len(metadata) != 3 or metadata[0] not in {"100644", "100755"}:
            raise DeployError(f"tracked path has unsupported mode for {tracked_path}")
        expected_mode = 0o755 if metadata[0] == "100755" else 0o644
        if stat.S_IMODE(installed.stat().st_mode) != expected_mode:
            raise DeployError(
                f"installed mode mismatch for {tracked_path}: expected {oct(expected_mode)}, "
                f"got {oct(stat.S_IMODE(installed.stat().st_mode))}"
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
    for gate_id in args.resolves:
        command.extend(["--resolves", gate_id])
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
    parser.add_argument("--install-dir", type=Path,
                        default=Path.home() / ".agents/skills")
    parser.add_argument("--skill", action="append", default=[],
                        help="top-level skill to deploy; repeat to select multiple (default: all)")
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--status", required=True)
    parser.add_argument("--channel")
    parser.add_argument("--resolves", action="append", default=[])
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
        selected = selected_skills(repo, head, args.skill)
        deployments = []
        for skill in selected:
            skill_prefix = f"skills/{skill}"
            paths = runtime_paths(tracked_files(repo, head, skill_prefix), skill_prefix)
            resolved = resolved_files(repo, head, paths, skill_prefix)
            deployments.append((skill, paths, skill_prefix, resolved))
        install_root = _safe_install_dir(args.install_dir, allow_self_symlink=True)
        for skill, _paths, _skill_prefix, resolved in deployments:
            install_files(install_root / skill, resolved)
        for skill, paths, skill_prefix, _resolved in deployments:
            verify_install(repo, head, install_root / skill, paths, skill_prefix)
        append_deploy_row(args, repo, Path(__file__).resolve().with_name("gate_row.py"))
    except (DeployError, OSError) as exc:
        print(f"deploy_skill: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

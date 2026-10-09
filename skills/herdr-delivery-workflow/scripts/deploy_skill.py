#!/usr/bin/env python3
"""Install selected tracked skills, verify them, and record one deploy row."""
from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path


class DeployError(Exception):
    pass


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        stdin=subprocess.DEVNULL,
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


def install_mode(git_mode: str, tracked_path: str) -> int:
    if git_mode not in {"100644", "100755"}:
        raise DeployError(f"tracked path has unsupported mode for {tracked_path}: {git_mode}")
    return 0o755 if git_mode == "100755" else 0o644


def resolved_files(repo: Path, head: str, paths: list[str], skill_prefix: str) -> list[tuple[Path, bytes, int]]:
    prefix = skill_prefix.rstrip("/") + "/"
    resolved: list[tuple[Path, bytes, int]] = []
    for tracked in paths:
        tree = subprocess.run(
            ["git", "-C", str(repo), "ls-tree", head, "--", tracked],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            stdin=subprocess.DEVNULL,
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
        if object_type != "blob":
            raise DeployError(f"tracked path has unsupported mode for {tracked}: {mode}")
        file_mode = install_mode(mode, tracked)
        blob = subprocess.run(
            ["git", "-C", str(repo), "cat-file", "blob", f"{head}:{tracked}"],
            capture_output=True,
            check=False,
            stdin=subprocess.DEVNULL,
        )
        if blob.returncode:
            detail = blob.stderr.decode(errors="replace").strip()
            raise DeployError(f"git cat-file failed for {tracked}: {detail}")
        resolved.append((Path(tracked[len(prefix):]), blob.stdout, file_mode))
    return resolved


def _is_pycache(path: Path) -> bool:
    return "__pycache__" in path.parts


def tree_mode(repo: Path, head: str, tracked_path: str) -> int:
    metadata = git(repo, "ls-tree", head, "--", tracked_path).split("\t", 1)[0].split()
    if len(metadata) != 3:
        raise DeployError(f"git ls-tree returned malformed metadata for {tracked_path}")
    return install_mode(metadata[0], tracked_path)


def verify_install(repo: Path, head: str, install_dir: Path,
                   paths: list[str], skill_prefix: str) -> None:
    prefix = skill_prefix.rstrip("/") + "/"
    install_dir = Path(os.path.abspath(os.path.expanduser(install_dir)))
    if install_dir.is_symlink():
        raise DeployError(f"install tree is a symlink: {install_dir}")
    tracked = {Path(path[len(prefix):]) for path in paths}
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
        expected_mode = tree_mode(repo, head, tracked_path)
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


def append_deploy_row(
    args: argparse.Namespace, repo: Path, script: Path, row_head: str,
) -> None:
    command = [
        sys.executable, str(script),
        "--repo", str(repo), "--ledger", str(args.ledger),
        "--kind", "deploy", "--status", args.status,
        "--words", args.words, "--note", args.note, "--quote", args.quote,
        "--head", row_head,
    ]
    for skill in args.skill:
        command.extend(["--skill", skill])
    if args.channel:
        command.extend(["--channel", args.channel])
    for gate_id in args.resolves:
        command.extend(["--resolves", gate_id])
    if args.under:
        command.extend(["--under", args.under])
    result = subprocess.run(
        command, capture_output=True, text=True, encoding="utf-8", check=False,
        stdin=subprocess.DEVNULL
    )
    if result.returncode:
        raise DeployError(
            f"gate_row.py refused deploy row: {result.stderr.strip() or result.stdout.strip()}"
        )
    sys.stdout.write(result.stdout)


def _install_with_skills(cli: str, source: Path, skill: str) -> None:
    command = [cli, "add", str(source), "-g", "-a", "cline", "-s", skill, "-y", "--copy"]
    environment = os.environ.copy()
    environment["DO_NOT_TRACK"] = "1"
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        env=environment,
        stdin=subprocess.DEVNULL,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise DeployError(f"skills add failed for {skill}: {detail}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--skill", action="append", default=[],
                        help="top-level skill to deploy; repeat to select multiple (default: all)")
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--status", required=True)
    parser.add_argument("--channel")
    parser.add_argument("--resolves", action="append", default=[])
    parser.add_argument("--under")
    parser.add_argument("--words", required=True)
    parser.add_argument("--note", required=True)
    parser.add_argument("--quote", required=True)
    args = parser.parse_args(argv)

    try:
        if not args.ledger.is_absolute():
            raise DeployError(f"--ledger must be absolute: {args.ledger}")
        repo = args.repo.resolve()
        head = git(repo, "rev-parse", args.head)
        try:
            git(repo, "rev-parse", "--verify", "refs/remotes/origin/main^{commit}")
        except DeployError:
            raise DeployError("required admission ref refs/remotes/origin/main is missing") from None
        try:
            git(repo, "merge-base", "--is-ancestor", head, "refs/remotes/origin/main")
        except DeployError:
            raise DeployError(f"--head {head} is not contained in refs/remotes/origin/main") from None
        cli = shutil.which("skills")
        if cli is None:
            raise DeployError("skills CLI was not found on PATH")

        branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD")
        selected = selected_skills(repo, head, args.skill)
        deployments = []
        for skill in selected:
            skill_prefix = f"skills/{skill}"
            paths = tracked_files(repo, head, skill_prefix)
            resolved = resolved_files(repo, head, paths, skill_prefix)
            deployments.append((skill, paths, skill_prefix, resolved))

        install_root = Path.home() / ".agents" / "skills"
        with tempfile.TemporaryDirectory(prefix="deploy-skill-") as temporary:
            staging_root = Path(temporary)
            for skill, _paths, _prefix, resolved in deployments:
                source = staging_root / skill
                for relative, content, mode in resolved:
                    destination = source / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(content)
                    os.chmod(destination, mode)
            for skill, _paths, _prefix, _resolved in deployments:
                _install_with_skills(cli, staging_root / skill, skill)
            for skill, paths, skill_prefix, _resolved in deployments:
                verify_install(repo, head, install_root / skill, paths, skill_prefix)

        args.skill = selected
        append_deploy_row(
            args, repo, Path(__file__).resolve().with_name("gate_row.py"),
            f"{branch}@{head}",
        )
    except (DeployError, OSError) as exc:
        print(f"deploy_skill: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

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

import gate_row
from gitops import GitError, git, is_ancestor


class DeployError(Exception):
    pass


def tracked_skills(repo: Path, head: str) -> list[str]:
    skills = git(repo, "ls-tree", "-d", "--name-only", f"{head}:skills").splitlines()
    if not skills:
        raise DeployError(f"head {head} has no tracked top-level skills")
    if any(not gate_row.SKILL_NAME_RE.fullmatch(skill) for skill in skills):
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
        if not gate_row.SKILL_NAME_RE.fullmatch(skill) or skill not in available
    ]
    if invalid:
        raise DeployError(
            f"unknown or unsafe skill selection: {', '.join(invalid)}"
        )
    return [skill for skill in available if skill in requested]


def tracked_files(repo: Path, head: str, prefix: str) -> list[tuple[str, int, str]]:
    records = [r for r in git(repo, "ls-tree", "-r", "-z", head, prefix).split("\0") if r]
    if not records:
        raise DeployError(f"head {head} has no tracked files under {prefix}")
    entries = []
    for record in records:
        metadata, path = record.split("\t", 1)
        mode, _object_type, object_id = metadata.split()
        if not path.startswith(prefix):
            raise DeployError(f"git ls-tree returned a path outside {prefix}")
        entries.append((path, install_mode(mode, path), object_id))
    return entries


def install_mode(git_mode: str, tracked_path: str) -> int:
    if git_mode not in {"100644", "100755"}:
        raise DeployError(f"tracked path has unsupported mode for {tracked_path}: {git_mode}")
    return 0o755 if git_mode == "100755" else 0o644


def read_blobs(repo: Path, object_ids: list[str]) -> dict[str, bytes]:
    unique = sorted(set(object_ids))
    proc = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "--batch"],
        input="".join(f"{object_id}\n" for object_id in unique).encode(),
        capture_output=True,
        check=False,
    )
    if proc.returncode:
        raise DeployError(f"git cat-file failed: {proc.stderr.decode(errors='replace').strip()}")
    blobs: dict[str, bytes] = {}
    offset = 0
    for object_id in unique:
        end = proc.stdout.index(b"\n", offset)
        header = proc.stdout[offset:end].split()
        if header[:2] != [object_id.encode(), b"blob"]:
            raise DeployError(f"git cat-file returned no blob for {object_id}")
        start = end + 1
        blobs[object_id] = proc.stdout[start:start + int(header[2])]
        offset = start + int(header[2]) + 1
    return blobs


def resolved_files(repo: Path, entries: list[tuple[str, int, str]],
                   prefix: str) -> list[tuple[Path, bytes, int]]:
    blobs = read_blobs(repo, [object_id for _path, _mode, object_id in entries])
    return [(Path(path[len(prefix):]), blobs[object_id], mode) for path, mode, object_id in entries]


def install_drift(repo: Path, install_dir: Path, entries: list[tuple[str, int, str]],
                  prefix: str) -> tuple[list[tuple[str, bool]], list[str]]:
    """Compare an installed tree with the tracked entries of one skill.

    Returns (missing_or_mismatched, untracked): (message, file is installed)
    for each tracked file that is absent or differs, and a message for each
    installed path no entry names. A tracked file that is itself a symlink
    counts as missing; a symlinked directory is reported untracked and not
    walked; __pycache__ is ignored.
    """
    drift: list[tuple[str, bool]] = []
    for tracked_path, expected_mode, expected in entries:
        installed = install_dir / tracked_path[len(prefix):]
        if installed.is_symlink() or not installed.is_file():
            drift.append((f"installed file is missing: {installed}", False))
            continue
        actual = git(repo, "hash-object", str(installed))
        if actual != expected:
            drift.append((
                f"installed hash mismatch for {tracked_path}: expected {expected}, got {actual}", True,
            ))
            continue
        actual_mode = stat.S_IMODE(installed.stat().st_mode)
        if actual_mode != expected_mode:
            drift.append((
                f"installed mode mismatch for {tracked_path}: expected {oct(expected_mode)}, "
                f"got {oct(actual_mode)}", True,
            ))

    tracked = {Path(path[len(prefix):]) for path, _mode, _object_id in entries}
    untracked: list[str] = []
    for root, dirs, files in os.walk(install_dir, topdown=True, followlinks=False):
        root_path = Path(root)
        dirs[:] = [name for name in dirs if name != "__pycache__"]
        untracked.extend(
            f"installed path is not tracked: {root_path / name}"
            for name in dirs if (root_path / name).is_symlink()
        )
        dirs[:] = [name for name in dirs if not (root_path / name).is_symlink()]
        untracked.extend(
            f"installed path is not tracked: {root_path / name}" for name in files
            if name != "__pycache__" and (root_path / name).relative_to(install_dir) not in tracked
        )
    return drift, untracked


def verify_install(repo: Path, install_dir: Path, entries: list[tuple[str, int, str]],
                   prefix: str) -> None:
    install_dir = Path(os.path.abspath(os.path.expanduser(install_dir)))
    if install_dir.is_symlink():
        raise DeployError(f"install tree is a symlink: {install_dir}")
    drift, untracked = install_drift(repo, install_dir, entries, prefix)
    problems = [message for message, _installed in drift] + untracked
    if problems:
        raise DeployError(problems[0])


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
    parser.add_argument("--brief", help="the Agent brief restating the Human's words; "
                        "required with --words human or selected")
    parser.add_argument("--quote", default="", help="the seat's own text; empty for Human words")
    args = parser.parse_args(argv)

    try:
        if not args.ledger.is_absolute():
            raise DeployError(f"--ledger must be absolute: {args.ledger}")
        repo = args.repo.resolve()
        head = git(repo, "rev-parse", args.head)
        try:
            git(repo, "rev-parse", "--verify", "refs/remotes/origin/main^{commit}")
        except GitError:
            raise DeployError("required admission ref refs/remotes/origin/main is missing") from None
        if not is_ancestor(repo, head, "refs/remotes/origin/main"):
            raise DeployError(f"--head {head} is not contained in refs/remotes/origin/main")
        cli = shutil.which("skills")
        if cli is None:
            raise DeployError("skills CLI was not found on PATH")

        branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD")
        selected = selected_skills(repo, head, args.skill)
        request = gate_row.RowRequest(
            kind="deploy", status=args.status, channel=args.channel or None, skills=selected,
            resolves=args.resolves, under=args.under or None, words=args.words, note=args.note,
            brief=args.brief, quote=args.quote, head=f"{branch}@{head}",
        )
        gate_row.preview_row(args.ledger, repo, request)
        deployments = []
        for skill in selected:
            prefix = f"skills/{skill}/"
            deployments.append((skill, prefix, tracked_files(repo, head, prefix)))

        install_root = Path.home() / ".agents" / "skills"
        with tempfile.TemporaryDirectory(prefix="deploy-skill-") as temporary:
            staging_root = Path(temporary)
            for skill, prefix, entries in deployments:
                source = staging_root / skill
                for relative, content, mode in resolved_files(repo, entries, prefix):
                    destination = source / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(content)
                    os.chmod(destination, mode)
            for skill, _prefix, _entries in deployments:
                _install_with_skills(cli, staging_root / skill, skill)
            for skill, prefix, entries in deployments:
                verify_install(repo, install_root / skill, entries, prefix)

        try:
            row = gate_row.append_row(args.ledger, repo, request)
        except gate_row.RowError as exc:
            raise DeployError(
                f"installed {', '.join(selected)}, but no deploy row was recorded: {exc}"
            ) from None
        print(row)
    except (DeployError, GitError, gate_row.RowError, OSError) as exc:
        print(f"deploy_skill: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

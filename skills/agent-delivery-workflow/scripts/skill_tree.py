#!/usr/bin/env python3
"""Read-only view of one skill's tracked files and their installed comparison."""
from __future__ import annotations

import os
import re
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path

from gitops import Runner, git


class TreeError(Exception):
    pass


SKILL_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SKILLS_DIR = "skills"


def skill_names(repo: Path, head: str, *, run: Runner = git) -> list[str]:
    return run(repo, "ls-tree", "-d", "--name-only", f"{head}:{SKILLS_DIR}").splitlines()


@dataclass(frozen=True)
class InstallReport:
    tracked: int
    installed: int
    drifted: int
    problems: list[str]


@dataclass
class SkillTree:
    repo: Path
    prefix: str
    entries: list[tuple[str, int, str]]

    @classmethod
    def at(cls, repo: Path, head: str, skill: str) -> SkillTree:
        if not SKILL_NAME_RE.fullmatch(skill):
            raise TreeError(f"not a top-level skill name: {skill!r}")
        prefix = f"{SKILLS_DIR}/{skill}/"
        records = [r for r in git(repo, "ls-tree", "-r", "-z", head, prefix).split("\0") if r]
        if not records:
            raise TreeError(f"head {head} has no tracked files under {prefix}")
        entries = []
        for record in records:
            metadata, path = record.split("\t", 1)
            mode, _object_type, object_id = metadata.split()
            if not path.startswith(prefix):
                raise TreeError(f"git ls-tree returned a path outside {prefix}")
            entries.append((path, cls._install_mode(mode, path), object_id))
        return cls(repo, prefix, entries)

    @staticmethod
    def _install_mode(git_mode: str, tracked_path: str) -> int:
        if git_mode not in {"100644", "100755"}:
            raise TreeError(f"tracked path has unsupported mode for {tracked_path}: {git_mode}")
        return 0o755 if git_mode == "100755" else 0o644

    def _read_blobs(self, object_ids: list[str]) -> dict[str, bytes]:
        unique = sorted(set(object_ids))
        proc = subprocess.run(
            ["git", "-C", str(self.repo), "cat-file", "--batch"],
            input="".join(f"{object_id}\n" for object_id in unique).encode(),
            capture_output=True,
            check=False,
        )
        if proc.returncode:
            raise TreeError(f"git cat-file failed: {proc.stderr.decode(errors='replace').strip()}")
        blobs: dict[str, bytes] = {}
        offset = 0
        for object_id in unique:
            end = proc.stdout.index(b"\n", offset)
            header = proc.stdout[offset:end].split()
            if header[:2] != [object_id.encode(), b"blob"]:
                raise TreeError(f"git cat-file returned no blob for {object_id}")
            start = end + 1
            blobs[object_id] = proc.stdout[start:start + int(header[2])]
            offset = start + int(header[2]) + 1
        return blobs

    def files(self) -> list[tuple[Path, bytes, int]]:
        blobs = self._read_blobs([object_id for _path, _mode, object_id in self.entries])
        return [(Path(path[len(self.prefix):]), blobs[object_id], mode)
                for path, mode, object_id in self.entries]

    def compare(self, install_dir: Path) -> InstallReport:
        """Compare an installed tree with this tree's tracked entries.

        A tracked file that is itself a symlink counts as missing; a symlinked
        directory is reported untracked and not walked; __pycache__ is ignored.
        """
        problems: list[str] = []
        missing = 0
        for tracked_path, expected_mode, expected in self.entries:
            installed = install_dir / tracked_path[len(self.prefix):]
            if installed.is_symlink() or not installed.is_file():
                problems.append(f"installed file is missing: {installed}")
                missing += 1
                continue
            actual = git(self.repo, "hash-object", str(installed))
            if actual != expected:
                problems.append(
                    f"installed hash mismatch for {tracked_path}: expected {expected}, got {actual}"
                )
                continue
            actual_mode = stat.S_IMODE(installed.stat().st_mode)
            if actual_mode != expected_mode:
                problems.append(
                    f"installed mode mismatch for {tracked_path}: expected {oct(expected_mode)}, "
                    f"got {oct(actual_mode)}"
                )

        tracked = {Path(path[len(self.prefix):]) for path, _mode, _object_id in self.entries}
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
                if (root_path / name).relative_to(install_dir) not in tracked
            )
        return InstallReport(
            len(self.entries),
            len(self.entries) - missing + len(untracked),
            len(problems),
            problems + untracked,
        )

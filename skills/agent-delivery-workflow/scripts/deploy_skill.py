#!/usr/bin/env python3
"""Install selected tracked skills, verify them, and record one deploy row."""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import gate_row
from gitops import GitError, git, is_ancestor
from skill_tree import SkillTree, TreeError, SKILL_NAME_RE, skill_names


class DeployError(Exception):
    pass


def tracked_skills(repo: Path, head: str) -> list[str]:
    skills = skill_names(repo, head)
    if not skills:
        raise DeployError(f"head {head} has no tracked top-level skills")
    if any(not SKILL_NAME_RE.fullmatch(skill) for skill in skills):
        raise DeployError("git ls-tree returned a non-top-level skill")
    return skills


def selected_skills(repo: Path, head: str, requested: list[str]) -> list[str]:
    available = tracked_skills(repo, head)
    if not requested:
        return available
    if len(requested) != len(set(requested)):
        raise DeployError("--skill names a skill more than once")
    invalid = [skill for skill in requested if skill not in available]
    if invalid:
        raise DeployError(
            f"unknown or unsafe skill selection: {', '.join(invalid)}"
        )
    return [skill for skill in available if skill in requested]


def verify_install(tree: SkillTree, install_dir: Path) -> None:
    if install_dir.is_symlink():
        raise DeployError(f"install tree is a symlink: {install_dir}")
    problems = tree.compare(install_dir).problems
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
        deployments = [
            (skill, SkillTree.at(repo, head, skill)) for skill in selected
        ]

        install_root = Path.home() / ".agents" / "skills"
        with tempfile.TemporaryDirectory(prefix="deploy-skill-") as temporary:
            staging_root = Path(temporary)
            for skill, tree in deployments:
                source = staging_root / skill
                for relative, content, mode in tree.files():
                    destination = source / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(content)
                    os.chmod(destination, mode)
            installed: list[str] = []
            failing = ""
            try:
                for skill, _tree in deployments:
                    failing = skill
                    _install_with_skills(cli, staging_root / skill, skill)
                    installed.append(skill)
                for skill, tree in deployments:
                    failing = skill
                    verify_install(tree, install_root / skill)
            except (DeployError, TreeError, GitError, OSError) as exc:
                if installed:
                    raise DeployError(
                        f"{exc}; failed at {failing}; already installed, no deploy row recorded: "
                        f"{', '.join(installed)}"
                    ) from None
                raise

        try:
            row = gate_row.append_row(args.ledger, repo, request)
        except (gate_row.RowError, OSError) as exc:
            raise DeployError(
                f"installed {', '.join(selected)}, but no deploy row was recorded: {exc}"
            ) from None
        print(row)
    except (DeployError, TreeError, GitError, gate_row.RowError, OSError) as exc:
        print(f"deploy_skill: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

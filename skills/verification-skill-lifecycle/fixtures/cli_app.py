#!/usr/bin/env python3
"""Disposable CLI fixture for the verification-skill-lifecycle pilot."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

OWNER_FILE = ".verification-owner"
TASKS_FILE = "tasks.json"
RUN_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,47}\Z")
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class FixtureError(Exception):
    pass


def _checked_target(workspace: str, run_id: str) -> tuple[Path, Path, bool]:
    if not RUN_ID.fullmatch(run_id):
        raise FixtureError("run id must contain 1-48 letters, digits, underscores, or hyphens")
    root = Path(workspace).resolve(strict=True)
    if not root.is_dir():
        raise FixtureError("workspace is not a directory")
    if root == PROJECT_ROOT or root in PROJECT_ROOT.parents or PROJECT_ROOT in root.parents:
        raise FixtureError("workspace must not overlap the fixture repository")
    target = root / f"run-{run_id}"
    if target.parent != root:
        raise FixtureError("run directory is not a direct workspace child")
    if target.is_symlink():
        raise FixtureError("run directory must not be a symlink")
    if not target.exists():
        return root, target, False
    checked = target.resolve(strict=True)
    if checked != target or checked.parent != root or not checked.is_dir():
        raise FixtureError("run directory escapes the workspace or is not a directory")
    return root, checked, True


def _read_tasks(run_dir: Path, owner: str) -> list[dict[str, Any]]:
    owner_path = run_dir / OWNER_FILE
    if owner_path.is_symlink() or not owner_path.is_file():
        raise FixtureError("run ownership evidence is missing or invalid")
    if owner_path.read_text(encoding="utf-8").rstrip("\n") != owner:
        raise FixtureError("run ownership evidence does not match")

    tasks_path = run_dir / TASKS_FILE
    if tasks_path.is_symlink() or not tasks_path.is_file():
        raise FixtureError("task state is missing or invalid")
    try:
        tasks = json.loads(tasks_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise FixtureError("task state is unreadable") from error
    if not isinstance(tasks, list) or any(
        not isinstance(task, dict)
        or set(task) != {"id", "title", "body"}
        or not isinstance(task["id"], int)
        or not isinstance(task["title"], str)
        or not isinstance(task["body"], str)
        for task in tasks
    ):
        raise FixtureError("task state has an invalid shape")
    return tasks


def _open_run(workspace: str, run_id: str, owner: str) -> tuple[Path, list[dict[str, Any]]]:
    if not owner or "\n" in owner or "\r" in owner:
        raise FixtureError("owner must be a non-empty single-line token")
    _, run_dir, exists = _checked_target(workspace, run_id)
    if not exists:
        run_dir.mkdir(mode=0o700)
        (run_dir / OWNER_FILE).write_text(owner + "\n", encoding="utf-8")
        (run_dir / TASKS_FILE).write_text("[]\n", encoding="utf-8")
    return run_dir, _read_tasks(run_dir, owner)


def _emit(value: dict[str, Any]) -> None:
    print(json.dumps(value, sort_keys=True))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="run the disposable task CLI fixture")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--owner", required=True)
    commands = parser.add_subparsers(dest="action", required=True)

    commands.add_parser("doctor", help="read-only check of the isolated run")
    create = commands.add_parser("create", help="create a task through the user CLI")
    create.add_argument("--title", required=True)
    create.add_argument("--body", default="")
    create.add_argument("--fail-after-save", action="store_true")
    show = commands.add_parser("show", help="read a task through the user CLI")
    show.add_argument("--title", required=True)
    commands.add_parser("cleanup", help="remove this owned run directory")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.action == "doctor":
            _, run_dir, exists = _checked_target(args.workspace, args.run_id)
            tasks = _read_tasks(run_dir, args.owner) if exists else []
            _emit({"status": "healthy" if exists else "ready", "run_id": args.run_id, "tasks": len(tasks)})
            return 0

        if args.action == "create":
            if not args.title.strip():
                raise FixtureError("title must not be blank")
            run_dir, tasks = _open_run(args.workspace, args.run_id, args.owner)
            task = {"id": len(tasks) + 1, "title": args.title, "body": args.body}
            tasks.append(task)
            (run_dir / TASKS_FILE).write_text(json.dumps(tasks, sort_keys=True) + "\n", encoding="utf-8")
            _emit({"id": task["id"], "title": task["title"]})
            if args.fail_after_save:
                print("simulated failure after persisted task write", file=sys.stderr)
                return 1
            return 0

        if args.action == "show":
            _, run_dir, exists = _checked_target(args.workspace, args.run_id)
            if not exists:
                raise FixtureError("task state is missing")
            tasks = _read_tasks(run_dir, args.owner)
            task = next((item for item in tasks if item["title"] == args.title), None)
            if task is None:
                raise FixtureError("task was not found")
            _emit(task)
            return 0

        if args.action == "cleanup":
            root, run_dir, exists = _checked_target(args.workspace, args.run_id)
            if not exists:
                raise FixtureError("owned run directory does not exist")
            _read_tasks(run_dir, args.owner)
            # _checked_target proved this is a real direct child; owner evidence was read above.
            if run_dir.parent != root:
                raise FixtureError("refusing cleanup outside the workspace")
            shutil.rmtree(run_dir)
            _emit({"removed": True, "run_id": args.run_id})
            return 0

        raise FixtureError("unknown action")
    except (FixtureError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

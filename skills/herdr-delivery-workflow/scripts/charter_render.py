#!/usr/bin/env python3
"""Render templates/reviewer-charter.txt for one exact head from one Lead command line."""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

import project_config

SKILL = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL / "templates" / "reviewer-charter.txt"
QUALITY_FLOOR = SKILL.parent / "quality-floor"
SLOT_RE = re.compile(r"<([a-z][a-z0-9_]*)>")
NULL_OID = "0" * 40
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
GUIDANCE = ("AGENTS.md", "CLAUDE.md")


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8",
        stdin=subprocess.DEVNULL,
    )
    if proc.returncode != 0:
        raise ValueError(f"git {' '.join(args)}: {proc.stderr.strip()}")
    return proc.stdout


def _model(argv: list[str], key: str) -> str:
    if "--model" not in argv[:-1]:
        raise ValueError(f"config {key} has no --model")
    return argv[argv.index("--model") + 1]


def render(args: argparse.Namespace) -> tuple[str, str]:
    repo = args.repo.resolve()
    run_dir = args.run_dir.resolve()
    if len(run_dir.parts) < 5 or run_dir.parent.name != "runs" or run_dir.parents[2].name != "projects":
        raise ValueError(f"run dir {run_dir} is not <herdr home>/projects/<slug>/runs/<run>")
    config = project_config.load(run_dir.parents[1] / "config.json")
    lead = f"lead-{run_dir.parents[1].name}"
    head = _git(repo, "rev-parse", "--verify", f"{args.head}^{{commit}}").strip()
    if head != args.head.lower():
        raise ValueError(f"--head must be the full 40-hex SHA, got {args.head}")
    base = args.base.lower()
    if base == NULL_OID:
        commits = _git(repo, "rev-list", "--reverse", head).split()
        diff_base = EMPTY_TREE
    else:
        if _git(repo, "rev-parse", "--verify", f"{base}^{{commit}}").strip() != base:
            raise ValueError(f"--base must be the full 40-hex SHA, got {args.base}")
        commits = _git(repo, "rev-list", "--reverse", f"{base}..{head}").split()
        diff_base = base
    if not commits:
        raise ValueError(f"range {base}..{head} has no commits")
    paths = _git(repo, "diff", "--name-only", diff_base, head).split("\n")[:-1]
    authors = dict.fromkeys(
        _git(repo, "log", "--no-walk", "--format=%(trailers:key=Seat,valueonly,separator=%x2C) "
             "(%(trailers:key=Model,valueonly,separator=%x2C))", *commits).split("\n")[:-1]
    )
    if any(author.startswith(" (") or author.endswith(" ()") for author in authors):
        raise ValueError("a commit in the range lacks a Seat: or Model: trailer")
    seats = {author.split(" (")[0] for author in authors}
    tracked = _git(repo, "ls-tree", "-r", "--name-only", head).split("\n")[:-1]
    guidance = [
        str(repo / name) for name in tracked
        if Path(name).name in GUIDANCE
        and any(path.startswith(name[: -len(Path(name).name)]) for path in paths)
    ]
    evidence = sorted(str(path) for path in run_dir.glob("evidence-*"))
    if not evidence:
        raise ValueError(f"no evidence-* file in {run_dir}")
    peer = f"review-{head[:12]}"
    values = {
        "run_name": run_dir.name,
        "one_line_outcome": _git(repo, "log", "-1", "--format=%s", head).strip(),
        "head_sha": head,
        "acceptance_boundary": args.boundary,
        "base_sha": base,
        "commit_count": f"{len(commits)} commit{'s' * (len(commits) > 1)}: "
                        + ", ".join(commit[:7] for commit in commits),
        "prior_review": args.prior,
        "lane": args.lane,
        "lane_reason": args.reason,
        "lead_name": lead,
        "run_dir": str(run_dir),
        "evidence_paths": ", ".join(evidence),
        "validation_ids": args.validation,
        "mode": "solo-Lead" if seats == {lead} else "partitioned",
        "declared_scope": ", ".join(paths),
        "scope_authors": "Scope authors (commit trailers): " + ", ".join(authors),
        "lead_kind": config["lead-kind"],
        "lead_model": _model(config["lead-args"], "lead-args"),
        "reviewer_kind": config["reviewer-kind"],
        "reviewer_model": _model(config["reviewer-args"], "reviewer-args"),
        "guidance_files": ", ".join(guidance) or "none",
        "repo": str(repo),
        "branch": config["target-line"],
        "pane_id": args.pane,
        "workspace_id": args.pane.split(":")[0],
        "reviewable_paths": "(each reviewable path from the preview)",
        "required_checks": "\n".join(f"{n}. {check}" for n, check in enumerate(args.check, 1)),
        "quality_floor_dir": str(QUALITY_FLOOR),
        "peer_name": peer,
        "herdr_home": str(run_dir.parents[3]),
    }
    return peer, SLOT_RE.sub(lambda match: values[match.group(1)], TEMPLATE.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path, help="checkout holding the head")
    parser.add_argument("--run-dir", required=True, type=Path, help="~/.herdr/projects/<slug>/runs/<run>")
    parser.add_argument("--base", required=True, help="full SHA the reviewed unit starts from")
    parser.add_argument("--head", required=True, help="full SHA under review")
    parser.add_argument("--pane", required=True, help="Reviewer pane id, <workspace>:<pane>")
    parser.add_argument("--lane", required=True, choices=("tiny", "normal", "high-risk"))
    parser.add_argument("--reason", required=True, help="material reason for the lane")
    parser.add_argument("--boundary", required=True, help="acceptance boundary")
    parser.add_argument("--validation", required=True, help="validation claims or gate ids")
    parser.add_argument("--prior", default="none", help="prior FAIL report, its head and finding ids")
    parser.add_argument("--check", required=True, action="append", help="one required check; repeat")
    args = parser.parse_args(argv)
    try:
        peer, charter = render(args)
        path = args.run_dir.resolve() / f"charter-{peer}.md"
        path.write_text(charter, encoding="utf-8")
    except (OSError, KeyError, ValueError) as exc:
        print(f"charter_render: {exc}", file=sys.stderr)
        return 1
    print(f"{path} sha256={hashlib.sha256(charter.encode('utf-8')).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

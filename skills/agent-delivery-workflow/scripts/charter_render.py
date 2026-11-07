#!/usr/bin/env python3
"""Render templates/reviewer-charter.txt for one exact head from one Lead command line."""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from pathlib import Path

import backend
import bounded_run
import charter_lint
import gitops
import project_config
import state_root

SKILL = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL / "templates" / "reviewer-charter.txt"
REPORT_BY_PROMPT = SKILL / "templates" / "report-by-prompt.txt"
QUALITY_FLOOR = SKILL.parent / "quality-floor"
SLOT_RE = re.compile(r"<([a-z][a-z0-9_]*)>")
GUIDANCE = ("AGENTS.md", "CLAUDE.md")


def _model(argv: list[str], key: str) -> str:
    model = project_config.model_of(argv)
    if not model:
        raise ValueError(f"config {key} has no --model")
    return model


GLOB_TOKEN_RE = re.compile(r"\*\*/|\*\*|\*|\?|[^*?]+")


def _glob_re(entry: str) -> re.Pattern[str]:
    parts = {"**/": "(?:.*/)?", "**": ".*", "*": "[^/]*", "?": "[^/]"}
    return re.compile("".join(parts.get(token, re.escape(token)) for token in GLOB_TOKEN_RE.findall(entry)))


def _owns(entry: str, path: str) -> bool:
    return (entry == path or path.startswith(entry.rstrip("/") + "/")
            or _glob_re(entry).fullmatch(path) is not None)


def scope_authors(staffing: Path, lead: str, paths: list[str]) -> tuple[str, list[str]]:
    text = staffing.read_text(encoding="utf-8")
    mode = re.search(r"^MODE: (\S+)", text, re.MULTILINE)
    if mode is None or mode.group(1) not in ("solo-Lead", "partitioned"):
        raise ValueError(f"{staffing} has no MODE: solo-Lead or MODE: partitioned line")
    if mode.group(1) == "solo-Lead":
        line = re.search(r"^LEAD: (.*)$", text, re.MULTILINE)
        if line is None:
            raise ValueError(f"{staffing} has no LEAD line")
        fields = charter_lint.fields_of(line.group(1))
        if not fields.get("kind") or not fields.get("model"):
            raise ValueError(f"{staffing} LEAD line lacks kind= or model=")
        return "solo-Lead", [f"{lead} ({fields.get('kind')} {fields.get('model')})"]
    engineers = [(seat.name, seat.fields) for seat in charter_lint.staffed_seats(text) if seat.role == "ENGINEER"]
    authors: dict[str, None] = {}
    for path in paths:
        owners = [(name, fields) for name, fields in engineers
                  if any(_owns(entry, path) for entry in fields.get("owned", "").split(",") if entry)]
        if not owners:
            raise ValueError(f"{path} has no ENGINEER owner in {staffing}")
        authors.update((f"{name} ({fields.get('kind')} {fields.get('model')})", None) for name, fields in owners)
    return "partitioned", list(authors)


def render(args: argparse.Namespace, seats: backend.Backend) -> tuple[str, str]:
    repo = args.repo.resolve()
    run_dir = args.run_dir.resolve()
    slug, _run = state_root.parse_run_dir(run_dir)
    config = project_config.load(state_root.config(slug))
    lead = args.lead
    head = gitops.git(repo, "rev-parse", "--verify", f"{args.head}^{{commit}}")
    if head != args.head.lower():
        raise ValueError(f"--head must be the full 40-hex SHA, got {args.head}")
    base = args.base.lower()
    if base != gitops.NULL_OID and gitops.git(repo, "rev-parse", "--verify", f"{base}^{{commit}}") != base:
        raise ValueError(f"--base must be the full 40-hex SHA, got {args.base}")
    commits = gitops.range_commits(repo, base, head, oldest_first=True)
    landed = gitops.landed_commits(repo, head, set(commits))
    commits = [commit for commit in commits if commit not in landed]
    if not commits:
        raise ValueError(f"range {base}..{head} has no commits")
    authored = [commit for commit in commits if gitops.clean_merge_parents(repo, commit) is None]
    log = gitops.git(repo, "log", "--no-walk", "--format=", "--name-only", "-z",
                     "--no-renames", "--diff-merges=remerge", *authored) if authored else ""
    paths = sorted({path for path in log.split("\0") if path})
    mode, authors = scope_authors(args.staffing, lead, paths)
    tracked = gitops.git(repo, "ls-tree", "-r", "-z", "--name-only", head).split("\0")[:-1]
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
        "one_line_outcome": gitops.git(repo, "log", "-1", "--format=%s", head),
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
        "mode": mode,
        "declared_scope": ", ".join(paths),
        "scope_authors": "Scope authors (staffing record): " + ", ".join(authors),
        "lead_kind": config["lead-kind"],
        "lead_model": _model(config["lead-args"], "lead-args"),
        "reviewer_kind": config["reviewer-kind"],
        "reviewer_model": _model(config["reviewer-args"], "reviewer-args"),
        "guidance_files": ", ".join(guidance) or "none",
        "repo": str(repo),
        "branch": config["target-line"],
        "pane_id": args.pane,
        "required_checks": "\n".join(f"{n}. {check}" for n, check in enumerate(args.check, 1)),
        "quality_floor_dir": str(QUALITY_FLOOR),
        "bounded_run": str(SKILL / "scripts" / "bounded_run.py"),
        "timed_out_code": str(bounded_run.TIMED_OUT),
        "peer_name": peer,
        "send_block": seats.send_block(lead, f"{run_dir}/report-{peer}.md").text,
        "state_root": str(state_root.STATE_ROOT),
    }
    template = TEMPLATE.read_text(encoding="utf-8").replace(
        "<report_by_prompt>", REPORT_BY_PROMPT.read_text(encoding="utf-8").rstrip("\n"))
    return peer, SLOT_RE.sub(lambda match: values[match.group(1)], template)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path, help="checkout holding the head")
    parser.add_argument("--run-dir", required=True, type=Path, help="~/.agent-delivery/projects/<slug>/runs/<run>")
    parser.add_argument("--base", required=True, help="full SHA the reviewed unit starts from")
    parser.add_argument("--head", required=True, help="full SHA under review")
    parser.add_argument("--pane", required=True, help="Reviewer seat handle")
    parser.add_argument("--lead", required=True, help="Lead seat handle; the report send block routes to it")
    parser.add_argument("--lane", required=True, choices=project_config.LANES)
    parser.add_argument("--reason", required=True, help="material reason for the lane")
    parser.add_argument("--boundary", required=True, help="acceptance boundary")
    parser.add_argument("--validation", required=True, help="validation claims or gate ids")
    parser.add_argument("--staffing", required=True, type=Path,
                        help="the run's staffing record: MODE, LEAD and each ENGINEER with owned paths")
    parser.add_argument("--prior", default="none", help="prior FAIL report, its head and finding ids")
    parser.add_argument("--check", required=True, action="append", help="one required check; repeat")
    backend.add_backend_option(parser)
    args = parser.parse_args(argv)
    try:
        peer, charter = render(args, backend.open_backend(os.environ, args.backend))
        path = args.run_dir.resolve() / f"charter-{peer}.md"
        path.write_text(charter, encoding="utf-8")
    except (OSError, KeyError, ValueError, gitops.GitError, backend.BackendError) as exc:
        print(f"charter_render: {exc}", file=sys.stderr)
        return 1
    print(f"{path} sha256={hashlib.sha256(charter.encode('utf-8')).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

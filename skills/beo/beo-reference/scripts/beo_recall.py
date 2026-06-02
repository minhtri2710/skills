#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import beo_io

SAFE_ISSUE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,120}$")


def log(message: str) -> None:
    print(message, file=sys.stderr)


def query_terms(query: str) -> set[str]:
    return {word.lower() for word in re.findall(r"[A-Za-z0-9_-]+", query) if len(word) > 3}


def safe_score(value: object) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0


def read_safe_markdown(path: Path, base: Path) -> str | None:
    try:
        if path.is_symlink():
            return None
        path.resolve().relative_to(base.resolve())
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def search_markdown_tree(base: Path, terms: set[str], limit: int = 5) -> list[dict]:
    if not base or not base.exists() or not base.is_dir():
        return []
    matches: list[dict] = []
    for path in sorted(base.rglob("*.md")):
        text = read_safe_markdown(path, base)
        if not text:
            continue
        haystack = text.lower()
        score = sum(1 for term in terms if term in haystack) / max(len(terms), 1)
        if score > 0:
            matches.append({"file": str(path), "score": score, "snippet": text[:1200], "retrieved_full_source": True})
    return sorted(matches, key=lambda item: safe_score(item.get("score")), reverse=True)[:limit]


def load_ticket_terms(root: Path, issue_id: str) -> tuple[str, list[str]]:
    try:
        from beo_ticket import read_ticket
        ticket = read_ticket(root, issue_id).data
    except Exception as exc:
        log(f"Warning: Failed to load ticket using read_ticket: {exc}")
        return "", []
    request = str(ticket.get("request") or "")
    done = [str(item) for item in ticket.get("done_criteria", []) if item]
    return request, done


def main() -> int:
    parser = argparse.ArgumentParser(description="Advisory BEO memory recall.")
    parser.add_argument("--issue", required=True, help="Issue ID")
    parser.add_argument("--root", default=".", help="Root directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    issue_id = args.issue
    if not SAFE_ISSUE_ID.fullmatch(issue_id):
        print(json.dumps({"status": "failed", "error": "issue_id must be alphanumeric with hyphens or underscores only"}, indent=2))
        return 1

    code, out, err = beo_io.run_cmd(["br", "show", issue_id, "--json"], cwd=root)
    title = ""
    description = ""
    labels: list[str] = []
    if code == 0:
        try:
            payload = json.loads(out)
            if isinstance(payload, list) and payload:
                payload = payload[0]
            if isinstance(payload, dict) and isinstance(payload.get("issue"), dict):
                payload = payload["issue"]
            if isinstance(payload, dict):
                title = str(payload.get("title") or "")
                description = str(payload.get("description") or payload.get("body") or "")
                raw_labels = payload.get("labels", [])
                labels = [str(label) for label in raw_labels] if isinstance(raw_labels, list) else []
        except Exception as exc:
            log(f"Warning: Failed to parse br show JSON: {exc}")
    else:
        log(f"Warning: br show command failed: {err.strip()}")

    ticket_request, ticket_done = load_ticket_terms(root, issue_id)
    query_components = [title, description, ticket_request, *ticket_done, *labels]
    query_text = re.sub(r"[^\w\s-]", " ", " ".join(component for component in query_components if component))
    final_query = " ".join(word for word in query_text.split() if len(word) > 3) or "success failures lessons"
    terms = query_terms(final_query)

    local_learning_dir = root / ".beads" / "learning"
    matches = search_markdown_tree(local_learning_dir, terms, 5)

    result = {
        "status": "ok",
        "issue_id": issue_id,
        "query": final_query,
        "recall_mode": "fallback_local_markdown" if matches else "no_recall",
        "backend": "local_markdown" if matches else "none",
        "confidence": "low" if matches else "none",
        "matches": matches,
        "warnings": [],
        "advisory_only": True,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

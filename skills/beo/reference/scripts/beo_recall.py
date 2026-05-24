#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

sys.path.insert(0, str(Path(__file__).parent))
import beo_utils
from beo_command import CommandAdapter
from beo_utils import compact_text, claim_valid

def extract_json_array(text: str) -> list[dict]:
    try:
        payload = json.loads(text)
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            for key in ["results", "matches", "items", "documents"]:
                value = payload.get(key)
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
    except Exception:
        pass
    match = re.search(r"(\[\s*\{.*\}\s*\])", text, re.DOTALL)
    if match:
        try:
            return [item for item in json.loads(match.group(1)) if isinstance(item, dict)]
        except Exception:
            pass
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        try:
            return [item for item in json.loads(text[start:end+1]) if isinstance(item, dict)]
        except Exception:
            pass
    return []

def log(message: str) -> None:
    print(message, file=sys.stderr)


SAFE_ISSUE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,120}$")
INTERNAL_HELPER_OWNER = "beo-recall"


def query_terms(query: str) -> set[str]:
    return {w.lower() for w in re.findall(r"[A-Za-z0-9_-]+", query) if len(w) > 3}


def lexical_score(text: str, terms: set[str]) -> float:
    if not terms:
        return 0.0
    haystack = text.lower()
    hits = sum(1 for term in terms if term in haystack)
    return hits / len(terms)


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


def qmd_ref(match: dict) -> str | None:
    for key in ["file", "path", "docid", "id", "uri"]:
        value = match.get(key)
        if isinstance(value, str) and value:
            return value
    if isinstance(match.get("url"), str):
        return match["url"]
    return None


def retrieve_qmd_matches(matches: list[dict], limit: int = 5, adapter: CommandAdapter | None = None) -> list[dict]:
    retrieved: list[dict] = []
    for match in matches[:limit]:
        ref = qmd_ref(match)
        if not ref:
            continue
        if adapter is None:
            log("Warning: CommandAdapter is required for qmd.get; skipping qmd hydration")
            continue
        try:
            argv = adapter.build_argv("qmd.get", owner=INTERNAL_HELPER_OWNER, path_or_docid=ref)
        except Exception as e:
            log(f"Warning: CommandAdapter failed to build argv for qmd.get: {e}")
            continue
        get_code, get_out, _get_err = beo_utils.run_cmd(argv)
        if get_code != 0 or not get_out.strip():
            continue
        hydrated = dict(match)
        hydrated["file"] = ref
        hydrated["snippet"] = get_out[:1200]
        hydrated["retrieved_full_source"] = True
        retrieved.append(hydrated)
    return retrieved


def search_markdown_tree(directory: Path, terms: set[str], limit: int = 5) -> list[dict]:
    if not directory.exists() or directory.is_symlink():
        return []
    matches: list[dict] = []
    try:
        base = directory.resolve()
        for md_path in sorted(base.glob("**/*.md")):
            content = read_safe_markdown(md_path, base)
            if content is None:
                continue
            score = lexical_score(f"{md_path.stem} {content}", terms)
            if score <= 0:
                continue
            matches.append({
                "file": str(md_path),
                "title": md_path.stem,
                "score": score,
                "snippet": content[:1200],
                "retrieved_full_source": True,
            })
        matches.sort(key=lambda item: float(item.get("score", 0)), reverse=True)
    except Exception:
        return matches[:limit]
    return matches[:limit]


def search_local_learning_notes(artifacts_dir: Path, terms: set[str], limit: int = 5) -> list[dict]:
    if not artifacts_dir.exists() or artifacts_dir.is_symlink():
        return []
    matches: list[dict] = []
    try:
        base = artifacts_dir.resolve()
        for learning_dir in sorted(base.glob("*/learning")):
            if not learning_dir.is_dir() or learning_dir.is_symlink():
                continue
            for md_path in sorted(learning_dir.glob("*.md")):
                content = read_safe_markdown(md_path, base)
                if content is None:
                    continue
                score = lexical_score(f"{md_path.stem} {content}", terms)
                if score <= 0:
                    continue
                matches.append({
                    "file": str(md_path),
                    "title": md_path.stem,
                    "score": score,
                    "snippet": content[:1200],
                    "retrieved_full_source": True,
                })
        matches.sort(key=lambda item: float(item.get("score", 0)), reverse=True)
    except Exception:
        return matches[:limit]
    return matches[:limit]


def main() -> int:
    parser = argparse.ArgumentParser(description="Recall past BEO learnings for the current issue.")
    parser.add_argument("--issue", required=True, help="Issue ID")
    parser.add_argument("--root", default=".", help="Root directory")
    parser.add_argument("--write-summary", action="store_true", help="Write RECALL_SUMMARY.md after the issue has been claimed")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    issue_id = args.issue
    if not SAFE_ISSUE_ID.fullmatch(issue_id):
        print(json.dumps({"status": "failed", "error": "issue_id must be alphanumeric with hyphens or underscores only"}, indent=2))
        return 1

    log(f"Starting memory recall for issue: {issue_id}")

    adapter = CommandAdapter(root)

    try:
        argv = adapter.build_argv("br.show", owner="beo-plan", issue_id=issue_id)
    except Exception as e:
        log(f"Warning: CommandAdapter failed to build argv for br.show: {e}")
        argv = ["br", "show", issue_id, "--json"]
    code, out, err = beo_utils.run_cmd(argv)
    title = ""
    description = ""
    labels: list[str] = []
    issue_payload = {}
    
    if code == 0:
        try:
            payload = json.loads(out)
            if isinstance(payload, list) and payload:
                payload = payload[0]
            if isinstance(payload, dict) and "issue" in payload:
                payload = payload["issue"]
            if isinstance(payload, dict):
                issue_payload = payload
                title = str(payload.get("title") or "")
                description = str(payload.get("description") or "")
                raw_labels = payload.get("labels", [])
                labels = [str(label) for label in raw_labels] if isinstance(raw_labels, list) else []
        except Exception as e:
            log(f"Warning: Failed to parse br show JSON: {e}")
    else:
        log(f"Warning: br show command failed: {err.strip()}")

    ticket_path = root / ".beads" / "artifacts" / issue_id / "TICKET.md"
    ticket_request = ""
    ticket_done: list[str] = []
    ticket_features = []
    
    if ticket_path.exists() and yaml:
        try:
            content = ticket_path.read_text(encoding="utf-8")
            match = re.search(r"```yaml\s+beo\.ticket\s*\n(.*?)\n```", content, re.DOTALL)
            yaml_text = match.group(1) if match else content
            ticket = yaml.safe_load(yaml_text)
            if isinstance(ticket, dict):
                ticket_request = str(ticket.get("request") or "")
                done_target = ticket.get("done_target")
                if done_target:
                    ticket_done.append(str(done_target))
                done = ticket.get("done")
                if isinstance(done, list):
                    ticket_done.extend(str(item) for item in done if item)
                elif done:
                    ticket_done.append(str(done))
                flow_profile = ticket.get("flow_profile")
                if isinstance(flow_profile, dict):
                    features = flow_profile.get("features", [])
                    ticket_features = [str(feature) for feature in features] if isinstance(features, list) else []
                elif isinstance(flow_profile, str):
                    ticket_features = [flow_profile]
                else:
                    ticket_features = []
        except Exception as e:
            log(f"Warning: Failed to parse TICKET.md YAML: {e}")

    query_components = []
    if title:
        query_components.append(title)
    if description:
        query_components.append(description)
    if ticket_request:
        query_components.append(ticket_request)
    if ticket_done:
        query_components.extend(ticket_done)
    if ticket_features:
        query_components.extend(ticket_features)
    for label in labels:
        if ":" in label:
            query_components.append(label.split(":")[-1])
        else:
            query_components.append(label)

    query_text = " ".join(query_components)
    query_text = re.sub(r"[^\w\s-]", "", query_text)
    query_words = [w for w in query_text.split() if len(w) > 3][:35]
    final_query = " ".join(query_words)

    if not final_query:
        final_query = "success failures lessons"

    log(f"Formulated search query: '{final_query}'")

    env = beo_utils.resolve_obsidian_env()
    vault_path = env["vault_path"]
    learning_dir = env["learning_dir"]
    qmd_collection = env["qmd_collection"]

    matches = []
    recall_source = "qmd" if qmd_collection else "local_artifacts"
    terms = query_terms(final_query)
    if qmd_collection:
        log(f"Searching qmd collection '{qmd_collection}'...")
        try:
            argv = adapter.build_argv("qmd.query", owner=INTERNAL_HELPER_OWNER, query=final_query, limit=5, collection=qmd_collection)
        except Exception as e:
            log(f"Warning: CommandAdapter failed to build argv for qmd.query: {e}")
            argv = []
        if argv:
            qmd_code, qmd_out, qmd_err = beo_utils.run_cmd(argv)
        else:
            qmd_code, qmd_out, qmd_err = 1, "", "CommandAdapter could not build qmd.query"
        qmd_matches = extract_json_array(qmd_out)
        matches = retrieve_qmd_matches(qmd_matches, adapter=adapter)
        if qmd_matches and not matches:
            log("qmd returned leads, but full source retrieval failed; treating them as leads only.")
    else:
        log("qmd collection is not configured; skipping qmd recall.")
        qmd_code, qmd_err = 0, ""

    if not matches and learning_dir:
        log("No retrieved qmd notes. Searching Obsidian learning markdown...")
        matches = search_markdown_tree(Path(learning_dir), terms, 5)
        recall_source = "obsidian_markdown" if matches else "local_artifacts"
    if not matches:
        if learning_dir:
            log("No relevant Obsidian markdown results. Searching local learning artifacts...")
        else:
            log("Obsidian learning directory is not configured. Searching local learning artifacts...")
        matches = search_local_learning_notes(root / ".beads" / "artifacts", terms, 5)

    summary_path = root / ".beads" / "artifacts" / issue_id / "RECALL_SUMMARY.md"

    summary_md = f"# Memory Recall Summary: {issue_id}\n\n"
    summary_md += f"**Search Query**: `{final_query}`\n\n"
    
    if matches:
        summary_md += "## Relevant Prior Learnings & Playbooks\n\n"
        for idx, match in enumerate(matches[:5]):
            file_ref = str(match.get("file") or "unknown")
            
            file_path = file_ref
            if vault_path and qmd_collection and file_ref.startswith(f"qmd://{qmd_collection}/"):
                file_path = str(vault_path / file_ref.replace(f"qmd://{qmd_collection}/", ""))
            elif vault_path and file_ref.startswith("obsidian://"):
                file_path = str(vault_path / file_ref.replace("obsidian://", ""))
            
            title = str(match.get("title") or Path(file_path).stem or f"Learning Case {idx+1}")
            score = safe_score(match.get("score", 0.0))
            snippet = str(match.get("snippet") or "").strip()
            if not match.get("retrieved_full_source"):
                snippet = "Lead only; full source was not retrieved. Do not rely on this without fetching the source.\n\n" + snippet

            alert_type = "NOTE"
            alert_header = "Prior Learning"
            
            title_lower = title.lower()
            snippet_lower = snippet.lower()
            
            if "success" in title_lower or "success" in snippet_lower or "pattern" in title_lower:
                alert_type = "TIP"
                alert_header = "Success Playbook"
            elif "failure" in title_lower or "fail" in title_lower or "mistake" in title_lower or "cannot" in title_lower:
                alert_type = "WARNING"
                alert_header = "Failure Pattern / Recurring Mistake"
            elif "near-miss" in title_lower or "near_miss" in title_lower:
                alert_type = "CAUTION"
                alert_header = "Near-Miss / High-Risk Vector"
            
            summary_md += f"### {idx+1}. {title} (Relevance Score: {score:.2f})\n\n"
            summary_md += f"> [!{alert_type}]\n"
            summary_md += f"> **{alert_header}**\n"
            link_target = file_path if "://" in file_path else f"file://{file_path}"
            summary_md += f"> Link: [{title}]({link_target})\n"
            summary_md += f">\n"
            
            snippet_lines = snippet.split("\n")
            for line in snippet_lines:
                summary_md += f"> {line}\n"
            summary_md += "\n"
    else:
        summary_md += "## No Prior Learnings Found\n\n"
        summary_md += "No relevant past successes, failures, or recurring mistakes were matched for this issue.\n"

    summary_written = False
    write_error = None
    if args.write_summary:
        if not claim_valid(issue_payload):
            write_error = "br claim for current actor/session is missing or invalid"
            log(f"RECALL_SUMMARY.md not written: {write_error}")
        else:
            summary_path.parent.mkdir(parents=True, exist_ok=True)
            summary_path.write_text(summary_md, encoding="utf-8")
            summary_written = True
            log(f"Successfully wrote RECALL_SUMMARY.md to: {summary_path}")
    else:
        log("RECALL_SUMMARY.md not written; pass --write-summary after claiming the issue to persist it.")

    result = {
        "status": "success",
        "issue_id": issue_id,
        "query": final_query,
        "qmd_collection": qmd_collection,
        "qmd_status": "ok" if qmd_collection and qmd_code == 0 else "skipped" if not qmd_collection else "partial" if matches else "failed",
        "recall_source": recall_source,
        "summary_path": str(summary_path),
        "summary_written": summary_written,
        "authority": {
            "mode": "advisory_only",
            "internal_helper_owner": INTERNAL_HELPER_OWNER,
            "may_grant_approval": False,
            "may_grant_review_verdict": False,
            "may_grant_execution_permission": False,
            "may_close_issues": False,
            "may_resolve_human_gates": False,
        },
        "matches": [
            {
                "title": str(match.get("title") or Path(str(match.get("file") or "unknown")).stem),
                "file": str(match.get("file") or "unknown"),
                "score": safe_score(match.get("score", 0.0)),
            }
            for match in matches[:5]
        ],
    }
    if qmd_collection and qmd_code != 0:
        result["qmd_error"] = compact_text(qmd_err)
    if write_error:
        result["write_error"] = write_error
    print(json.dumps(result, indent=2))
    return 1 if write_error else 0

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from pathlib import Path

# Try to import PyYAML for TICKET.md parsing
try:
    import yaml
except ImportError:
    yaml = None

# Add script directory to sys.path for importing beo_utils
sys.path.insert(0, str(Path(__file__).parent))
import beo_utils

def extract_json_array(text: str) -> list[dict]:
    # Extract JSON array from text even if there's trailing garbage or assertions
    match = re.search(r"(\[\s*\{.*\}\s*\])", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    # Simple search
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end+1])
        except Exception:
            pass
    return []

def main() -> int:
    parser = argparse.ArgumentParser(description="Recall past BEO learnings for the current issue.")
    parser.add_argument("--issue", required=True, help="Issue ID")
    parser.add_argument("--root", default=".", help="Root directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    issue_id = args.issue

    print(f"Starting memory recall for issue: {issue_id}")

    # 1. Fetch issue details via br show --json
    code, out, err = beo_utils.run_cmd(["br", "show", issue_id, "--json"])
    title = ""
    description = ""
    labels = []
    
    if code == 0:
        try:
            payload = json.loads(out)
            if isinstance(payload, list) and payload:
                payload = payload[0]
            if isinstance(payload, dict) and "issue" in payload:
                payload = payload["issue"]
            if isinstance(payload, dict):
                title = payload.get("title", "")
                description = payload.get("description", "")
                labels = payload.get("labels", [])
        except Exception as e:
            print(f"Warning: Failed to parse br show JSON: {e}")
    else:
        print(f"Warning: br show command failed: {err.strip()}")

    # 2. Try to read and parse TICKET.md if it exists
    ticket_path = root / ".beads" / "artifacts" / issue_id / "TICKET.md"
    ticket_request = ""
    ticket_done = ""
    ticket_features = []
    
    if ticket_path.exists() and yaml:
        try:
            content = ticket_path.read_text(encoding="utf-8")
            match = re.search(r"```yaml\s+beo\.ticket\s*\n(.*?)\n```", content, re.DOTALL)
            yaml_text = match.group(1) if match else content
            ticket = yaml.safe_load(yaml_text)
            if isinstance(ticket, dict):
                ticket_request = ticket.get("request", "")
                ticket_done = ticket.get("done", "")
                ticket_features = ticket.get("flow_profile", {}).get("features", [])
        except Exception as e:
            print(f"Warning: Failed to parse TICKET.md YAML: {e}")

    # 3. Formulate query terms
    query_components = []
    if title:
        query_components.append(title)
    if ticket_request:
        query_components.append(ticket_request)
    if ticket_done:
        query_components.append(ticket_done)
    if ticket_features:
        query_components.extend(ticket_features)
    for label in labels:
        if ":" in label:
            query_components.append(label.split(":")[-1])
        else:
            query_components.append(label)

    # Clean query components to make them search-friendly
    query_text = " ".join(query_components)
    query_text = re.sub(r"[^\w\s-]", "", query_text)
    # Keep query concise but descriptive (up to 35 words for rich hybrid search)
    query_words = [w for w in query_text.split() if len(w) > 3][:35]
    final_query = " ".join(query_words)

    if not final_query:
        final_query = "success failures lessons"

    print(f"Formulated search query: '{final_query}'")

    # Resolve vault/collection details dynamically using beo_utils
    env = beo_utils.resolve_obsidian_env()
    vault_name = env["vault_name"]
    vault_path = env["vault_path"]
    qmd_collection = env["qmd_collection"]

    matches = []
    # 4. Search via qmd collection
    print(f"Searching qmd collection '{qmd_collection}'...")
    qmd_code, qmd_out, qmd_err = beo_utils.run_cmd(["qmd", "query", final_query, "-c", qmd_collection, "--json"])
    matches = extract_json_array(qmd_out)
    
    # 5. Fallback: Search issue-local learning artifacts
    if not matches:
        print("No qmd results. Searching local artifacts...")
        try:
            import glob
            local_files = glob.glob(str(root / ".beads" / "artifacts" / "*" / "learning" / "*.md"))
            for lf_path in local_files[:5]:
                lf = Path(lf_path)
                matches.append({
                    "file": str(lf),
                    "title": lf.stem,
                    "score": 0.3,
                    "snippet": lf.read_text(encoding="utf-8")[:300]
                })
        except Exception:
            pass

    # 6. Compile RECALL_SUMMARY.md
    artifact_dir = root / ".beads" / "artifacts" / issue_id
    artifact_dir.mkdir(parents=True, exist_ok=True)
    summary_path = artifact_dir / "RECALL_SUMMARY.md"

    summary_md = f"# Memory Recall Summary: {issue_id}\n\n"
    summary_md += f"**Search Query**: `{final_query}`\n\n"
    
    if matches:
        summary_md += "## Relevant Prior Learnings & Playbooks\n\n"
        for idx, match in enumerate(matches[:5]):
            file_ref = match.get("file", "unknown")
            
            # Construct real clickable local file path
            file_path = file_ref
            if file_ref.startswith(f"qmd://{qmd_collection}/"):
                file_path = str(vault_path / file_ref.replace(f"qmd://{qmd_collection}/", ""))
            elif file_ref.startswith("qmd://second-brain/"):
                file_path = str(vault_path / file_ref.replace("qmd://second-brain/", ""))
            elif file_ref.startswith("obsidian://"):
                file_path = str(vault_path / file_ref.replace("obsidian://", ""))
            
            title = match.get("title") or Path(file_path).stem or f"Learning Case {idx+1}"
            score = match.get("score", 0.0)
            snippet = match.get("snippet", "").strip()
            
            # Clean snippet markdown
            snippet = snippet.replace("@@ -1,3 @@ (0 before, 213 after)\n---\n", "")
            
            # Determine alert callout type based on category
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
            summary_md += f"> Link: [{title}](file://{file_path})\n"
            summary_md += f">\n"
            
            # Format snippet lines inside callout
            snippet_lines = snippet.split("\n")
            for line in snippet_lines:
                summary_md += f"> {line}\n"
            summary_md += "\n"
    else:
        summary_md += "## No Prior Learnings Found\n\n"
        summary_md += "No relevant past successes, failures, or recurring mistakes were matched for this issue.\n"

    summary_path.write_text(summary_md, encoding="utf-8")
    print(f"Successfully wrote RECALL_SUMMARY.md to: {summary_path}")

    # Output to stdout
    print("\n=======================================================")
    print(f" RECALL SUMMARY FOR {issue_id}")
    print("=======================================================")
    if matches:
        for idx, match in enumerate(matches[:3]):
            title = match.get("title") or f"Prior Learning {idx+1}"
            print(f"- [Match {idx+1}] {title} (score: {match.get('score', 0.0):.2f})")
    else:
        print("- No prior matches found.")
    print("=======================================================\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

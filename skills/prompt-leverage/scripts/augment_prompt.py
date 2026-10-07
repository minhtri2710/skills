#!/usr/bin/env python3
"""Upgrade a raw prompt into a framework-backed execution prompt."""
from __future__ import annotations

import argparse
import re

# First matching category wins; keep this order aligned with the skill reference.
TASK_KEYWORDS = {
    "review": {"review", "critique", "audit", "assess", "inspect", "evaluate"},
    "coding": {
        "code", "coding", "implement", "implementation", "build", "debug", "fix", "refactor",
        "test", "testing", "software", "repo", "repository", "api", "function", "program", "script",
    },
    "research": {"research", "source", "sources", "evidence", "cite", "citation"},
    "writing": {"write", "writing", "rewrite", "draft", "prose", "email", "memo", "document", "copy", "edit"},
    "planning": {"plan", "planning", "roadmap", "strategy", "outline", "schedule"},
    "analysis": {"analyze", "analysis", "explain", "diagnose", "understand", "breakdown"},
}
INTENSITY_LEVELS = ["Light", "Standard", "Deep"]
DEFAULT_INTENSITY = "Standard"


def detect_task(prompt: str, task: str | None) -> str:
    if task is not None:
        return task
    words = set(re.findall(r"\w+", prompt.casefold()))
    return next((kind for kind, keywords in TASK_KEYWORDS.items() if words & keywords), "analysis")


def build_tool_rules(task: str) -> str:
    if task == "coding":
        return "Inspect the relevant files and dependencies first. Validate the final change with the narrowest useful checks before broadening scope."
    if task == "research":
        return "Retrieve evidence from reliable sources before concluding. Do not guess facts that can be checked."
    if task == "review":
        return "Read enough surrounding context to understand intent before critiquing. Distinguish confirmed issues from plausible risks."
    return "Use tools or extra context only when they materially improve correctness or completeness."


def build_output_contract(task: str) -> str:
    if task == "coding":
        return "Return the result in a practical execution format: concise summary, concrete changes or code, validation notes, and any remaining risks."
    if task == "research":
        return "Return a structured synthesis with key findings, supporting evidence, uncertainty where relevant, and a concise bottom line."
    if task == "writing":
        return "Return polished final copy in the requested tone and format. If useful, include a short rationale for major editorial choices."
    if task == "review":
        return "Return findings grouped by severity or importance, explain why each matters, and suggest the smallest credible next step."
    return "Return a clear, well-structured response matched to the task, with no unnecessary verbosity."


def upgrade_prompt(
    raw_prompt: str,
    task: str | None = None,
    intensity: str = DEFAULT_INTENSITY,
) -> str:
    normalized = re.sub(r"\s+", " ", raw_prompt).strip()
    detected_task = detect_task(normalized, task)
    tool_rules = build_tool_rules(detected_task)
    output_contract = build_output_contract(detected_task)
    prompt = raw_prompt.strip("\n")

    return "\n".join(
        [
            "Objective:",
            f"- Complete this task: {prompt}",
            "",
            "Context:",
            "- Preserve the user's original intent and constraints.",
            "- Surface any key assumptions if required information is missing.",
            "",
            "Work Style:",
            f"- Task type: {detected_task}",
            f"- Effort level: {intensity}",
            "",
            "Tool Rules:",
            f"- {tool_rules}",
            "",
            "Output Contract:",
            f"- {output_contract}",
            "",
            "Done Criteria:",
            "- Name the objective checks that decide this task (tests, a build, cited sources, the requested format) and stop only when they pass.",
            "- If a better approach exists, say so in a sentence and complete the task as asked.",
        ]
    ).strip()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upgrade a raw prompt into a framework-backed execution prompt.")
    parser.add_argument("prompt", help="Raw prompt text to upgrade.")
    parser.add_argument("--task", choices=sorted(TASK_KEYWORDS), help="Override the inferred task type.")
    parser.add_argument(
        "--intensity",
        choices=INTENSITY_LEVELS,
        default=DEFAULT_INTENSITY,
        help="Set the effort level (default: Standard).",
    )
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    print(upgrade_prompt(args.prompt, args.task, args.intensity))


if __name__ == "__main__":
    main()

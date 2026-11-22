#!/usr/bin/env python3
"""Upgrade a raw prompt into a framework-backed execution prompt."""
from __future__ import annotations

import argparse

DEFAULT_TOOL_RULE = "Use tools or extra context only when they materially improve correctness or completeness."
DEFAULT_OUTPUT_CONTRACT = "Return a clear, well-structured response matched to the task, with no unnecessary verbosity."
TASKS = {
    "review": (
        "Read enough surrounding context to understand intent before critiquing. Distinguish confirmed issues from plausible risks.",
        "Return findings grouped by severity or importance, explain why each matters, and suggest the smallest credible next step.",
    ),
    "coding": (
        "Inspect the relevant files and dependencies first. Validate the final change with the narrowest useful checks before broadening scope.",
        "Return the result in a practical execution format: concise summary, concrete changes or code, validation notes, and any remaining risks.",
    ),
    "research": (
        "Retrieve evidence from reliable sources before concluding. Do not guess facts that can be checked.",
        "Return a structured synthesis with key findings, supporting evidence, uncertainty where relevant, and a concise bottom line.",
    ),
    "writing": (
        DEFAULT_TOOL_RULE,
        "Return polished final copy in the requested tone and format. If useful, include a short rationale for major editorial choices.",
    ),
    "planning": (
        "Check prerequisites and separate decisions from work that can start now.",
        "Return ordered steps with dependencies and a completion check for each step.",
    ),
    "analysis": (
        "Separate observed facts from assumptions and identify missing evidence.",
        "Return a conclusion with its supporting evidence and limits.",
    ),
    "general": (DEFAULT_TOOL_RULE, DEFAULT_OUTPUT_CONTRACT),
}


def upgrade_prompt(raw_prompt: str, task: str = "general") -> str:
    tool_rules, output_contract = TASKS[task]
    prompt = raw_prompt.strip("\n")

    return "\n".join(
        [
            "Objective:",
            f"- Complete this task: {prompt}",
            "",
            "Context:",
            "- Preserve the user's original language, intent, and constraints.",
            "- Surface any key assumptions if required information is missing.",
            "",
            "Work Style:",
            f"- Task profile: {task}",
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
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upgrade a raw prompt into a framework-backed execution prompt.")
    parser.add_argument("prompt", help="Raw prompt text to upgrade.")
    parser.add_argument(
        "--task", choices=sorted(TASKS), default="general",
        help="Select the instruction profile (default: general).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    print(upgrade_prompt(args.prompt, args.task))


if __name__ == "__main__":
    main()

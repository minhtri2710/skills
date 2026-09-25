#!/usr/bin/env python3
"""Upgrade a raw prompt into a framework-backed execution prompt.

The task type and effort level are judged by a TypeSafe System One model
(a Choice and a Score asked in one request) instead of keyword matching.
Requires ``TYPESAFE_API_KEY`` in the environment.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

API_URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"

# Option name -> rubric the model uses to separate it from the others. The keys
# double as the task labels the template blocks below switch on, so keep them
# in sync with build_tool_rules / build_output_contract.
TASK_CRITERIA = {
    "coding": "Write, change, debug, refactor, or test software; work with a repo, API, or function.",
    "research": "Gather and compare external information or sources to answer a question.",
    "writing": "Produce or revise prose such as an email, memo, doc, or copy, with attention to tone.",
    "review": "Critique or audit existing work or code to find problems and judge quality.",
    "planning": "Produce a plan, roadmap, strategy, or structured outline for future work.",
    "analysis": "Explain, break down, or diagnose something to reach understanding or a conclusion.",
}

# Ordered low -> high; the Score answer is a float index into this list.
INTENSITY_LEVELS = ["Light", "Standard", "Deep"]
INTENSITY_CRITERIA = [
    "A simple, low-stakes task where a direct answer suffices and little verification is needed.",
    "A normal task needing some care, structure, and a basic correctness check.",
    "A high-stakes, complex, or production-critical task demanding thorough work and careful verification.",
]


def _system_one(state: str, questions: dict) -> dict:
    key = os.environ.get("TYPESAFE_API_KEY")
    if not key:
        raise SystemExit("augment_prompt: set TYPESAFE_API_KEY to classify the prompt")
    body = json.dumps({"state": state, "model": MODEL, "questions": questions}).encode()
    request = urllib.request.Request(
        API_URL,
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.load(response)["answers"]
    except TimeoutError as exc:
        raise SystemExit(f"augment_prompt: TypeSafe API timed out: {exc}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:200]
        raise SystemExit(f"augment_prompt: TypeSafe API error {exc.code}: {detail}")
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, TimeoutError):
            raise SystemExit(f"augment_prompt: TypeSafe API timed out: {exc.reason}")
        raise SystemExit(f"augment_prompt: cannot reach TypeSafe API: {exc.reason}")


def classify(prompt: str, task: str | None) -> tuple[str, str]:
    """Return (task type, effort level) judged by the model over the prompt."""
    questions: dict = {
        "intensity": {
            "type": "score",
            "instructions": "How much rigor and verification does completing this task actually require?",
            "criteria": INTENSITY_CRITERIA,
        }
    }
    if task is None:
        questions["task"] = {
            "type": "choice",
            "instructions": "What kind of task is this prompt asking for?",
            "criteria": TASK_CRITERIA,
        }
    answers = _system_one(prompt, questions)
    detected_task = task or answers["task"]["choice"]
    level = max(0, min(round(answers["intensity"]["score"]), len(INTENSITY_LEVELS) - 1))
    return detected_task, INTENSITY_LEVELS[level]


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


def upgrade_prompt(raw_prompt: str, task: str | None) -> str:
    normalized = re.sub(r"\s+", " ", raw_prompt).strip()
    detected_task, intensity = classify(normalized, task)
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
            "- Stop when the response satisfies the task and matches the requested format. If a better approach exists, say so in a sentence and complete the task as asked.",
        ]
    ).strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upgrade a raw prompt into a framework-backed execution prompt.")
    parser.add_argument("prompt", help="Raw prompt text to upgrade.")
    parser.add_argument("--task", choices=sorted(TASK_CRITERIA), help="Optional explicit task type.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(upgrade_prompt(args.prompt, args.task))


if __name__ == "__main__":
    main()

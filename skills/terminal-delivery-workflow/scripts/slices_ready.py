#!/usr/bin/env python3
"""Print the slices whose completed prerequisites allow them to start."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute the ready slice set.")
    parser.add_argument("--file", required=True, type=Path, help="path to slices.json")
    parser.add_argument("--done", action="append", default=[], help="completed slice ids, comma-separated")
    args = parser.parse_args(argv)

    try:
        data = json.loads(args.file.read_text(encoding="utf-8"))
        nodes = {node["id"] for node in data["nodes"]}
        dependencies = {node_id: set() for node_id in nodes}
        for edge in data["edges"]:
            source, target = edge["from"], edge["to"]
            if source not in nodes or target not in nodes:
                unknown = source if source not in nodes else target
                print(f"error: unknown node id: {unknown}", file=sys.stderr)
                return 1
            dependencies[target].add(source)
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"error: invalid slices file: {exc}", file=sys.stderr)
        return 1

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, path: list[str]) -> bool:
        if node in visiting:
            cycle = path[path.index(node):] + [node]
            print(f"error: cycle detected: {' -> '.join(cycle)}", file=sys.stderr)
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(dependency, path + [node]) for dependency in sorted(dependencies[node])):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    if any(visit(node, []) for node in sorted(nodes)):
        return 1

    done = {item.strip() for group in args.done for item in group.split(",") if item.strip()}
    for node in sorted(nodes - done):
        if dependencies[node] <= done:
            print(node)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

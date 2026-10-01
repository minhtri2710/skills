#!/usr/bin/env python3
"""Strict loader for the project delivery config (config.json).

``load(path)`` returns the config object or raises ValueError naming the path
and the offending key. ``--check PATH`` prints ``ok: PATH`` (exit 0) or one
refusal line on stderr (exit 1).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_STRINGS = ("engineer-kind", "reviewer-kind", "engineer-fallback", "reviewer-fallback", "target-line")
_ARGV = ("engineer-args", "reviewer-args", "engineer-fallback-args", "reviewer-fallback-args")
_LISTS = ("checks-light", "checks-heavy", "local-ops", "always-gate")
_KEYS = frozenset((*_STRINGS, *_ARGV, *_LISTS, "ci", "lane-defaults", "worker-cap", "provenance"))
_TRIGGERS = ("none", "pr", "push")
_LANES = ("tiny", "normal", "high-risk")


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key {key!r}")
        result[key] = value
    return result


def _text(value: Any) -> bool:
    return isinstance(value, str) and value != ""


def _strings(value: Any, *, nonempty: bool) -> bool:
    check = _text if nonempty else (lambda item: isinstance(item, str))
    return isinstance(value, list) and all(check(item) for item in value)


def _validate(config: dict[str, Any]) -> None:
    """Raise ValueError('<key>: <reason>') for the first refusal."""
    for key in config:
        if key not in _KEYS:
            raise ValueError(f"{key}: unknown key")
    for key in _STRINGS:
        if key in config and not _text(config[key]):
            raise ValueError(f"{key}: must be a non-empty string")
    for key in _ARGV:
        if key in config and not _strings(config[key], nonempty=False):
            raise ValueError(f"{key}: must be an array of strings")
    for key in _LISTS:
        if key in config and not _strings(config[key], nonempty=True):
            raise ValueError(f"{key}: must be an array of non-empty strings")
    if "ci" in config:
        ci = config["ci"]
        if not isinstance(ci, dict) or set(ci) != {"trigger", "workflows"}:
            raise ValueError("ci: must be an object with exactly trigger and workflows")
        if ci["trigger"] not in _TRIGGERS:
            raise ValueError(f"ci.trigger: must be one of {', '.join(_TRIGGERS)}")
        if not _strings(ci["workflows"], nonempty=True):
            raise ValueError("ci.workflows: must be an array of non-empty strings")
        if bool(ci["workflows"]) != (ci["trigger"] != "none"):
            raise ValueError("ci: workflows must be empty exactly when trigger is none")
    if "lane-defaults" in config:
        lanes = config["lane-defaults"]
        if not isinstance(lanes, dict):
            raise ValueError("lane-defaults: must be an object")
        for pattern, lane in lanes.items():
            if not _text(pattern) or lane not in _LANES:
                raise ValueError(f"lane-defaults.{pattern}: must map to one of {', '.join(_LANES)}")
    if "worker-cap" in config:
        cap = config["worker-cap"]
        if isinstance(cap, bool) or not isinstance(cap, int) or cap < 1:
            raise ValueError("worker-cap: must be an integer >= 1")
    if "provenance" in config:
        provenance = config["provenance"]
        if not isinstance(provenance, dict):
            raise ValueError("provenance: must be an object")
        for key, value in provenance.items():
            if key not in _KEYS - {"provenance"} and key != "file":
                raise ValueError(f"provenance.{key}: unknown key")
            if not _strings(value, nonempty=False):
                raise ValueError(f"provenance.{key}: must be an array of strings")


def load(path: str | Path) -> dict[str, Any]:
    """Return the validated config object; refuse with ValueError naming path and key."""
    try:
        text = Path(path).read_text(encoding="utf-8")
        config = json.loads(text, object_pairs_hook=_object)
        if not isinstance(config, dict):
            raise ValueError("top level must be an object")
        _validate(config)
    except (OSError, ValueError) as exc:
        raise ValueError(f"{path}: {exc}") from exc
    except RecursionError as exc:
        raise ValueError(f"{path}: nested too deeply") from exc
    return config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="validate a project delivery config.json")
    parser.add_argument("--check", metavar="PATH", required=True, help="load PATH strictly")
    args = parser.parse_args(argv)
    try:
        load(args.check)
    except ValueError as exc:
        print(str(exc).replace("\n", " "), file=sys.stderr)
        return 1
    print(f"ok: {args.check}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

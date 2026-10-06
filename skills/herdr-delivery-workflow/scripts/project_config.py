#!/usr/bin/env python3
"""Strict loader and literal launch-profile expansion for project config.json."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

_STRINGS = ("lead-kind", "engineer-kind", "reviewer-kind", "engineer-fallback", "reviewer-fallback", "target-line")
_ARGV = ("lead-args", "engineer-args", "reviewer-args", "engineer-fallback-args", "reviewer-fallback-args")
_LISTS = ("checks-light", "checks-heavy", "local-ops", "always-gate")
_PROFILE_KEYS = frozenset({"seat-argv", "peer-argv", "peer-settings-json", "runtime-state-dir"})
_KEYS = frozenset((*_STRINGS, *_ARGV, *_LISTS, "launch-profiles", "ci", "lane-defaults", "worker-cap", "provenance"))
_TRIGGERS = ("none", "pr", "push")
_LANES = ("tiny", "normal", "high-risk")
_PLACEHOLDERS = frozenset({"seat", "lead", "run_dir", "installed_skill_dir", "settings_file"})
_PLACEHOLDER_RE = re.compile(r"\{([^{}]*)\}")


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


def _validate_placeholders(value: Any, path: str) -> None:
    if isinstance(value, str):
        matches = list(_PLACEHOLDER_RE.finditer(value))
        for match in matches:
            if match.group(1) not in _PLACEHOLDERS:
                raise ValueError(f"{path}: unknown placeholder {{{match.group(1)}}}")
        if "{" in _PLACEHOLDER_RE.sub("", value) or "}" in _PLACEHOLDER_RE.sub("", value):
            raise ValueError(f"{path}: malformed placeholder")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _validate_placeholders(item, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            _validate_placeholders(item, f"{path}.{key}")


def _validate(config: dict[str, Any]) -> None:
    for key in config:
        if key not in _KEYS:
            raise ValueError(f"{key}: unknown key")
    if ("lead-kind" in config) != ("lead-args" in config):
        raise ValueError("lead-kind and lead-args must be configured together")
    for role in ("engineer", "reviewer"):
        if (f"{role}-fallback" in config) != (f"{role}-fallback-args" in config):
            raise ValueError(f"{role}-fallback and {role}-fallback-args must be configured together")
    for key in _STRINGS:
        if key in config and not _text(config[key]):
            raise ValueError(f"{key}: must be a non-empty string")
    for key in _ARGV:
        if key in config and not _strings(config[key], nonempty=False):
            raise ValueError(f"{key}: must be an array of strings")
    for key in _LISTS:
        if key in config and not _strings(config[key], nonempty=True):
            raise ValueError(f"{key}: must be an array of non-empty strings")
    if "launch-profiles" in config:
        profiles = config["launch-profiles"]
        if not isinstance(profiles, dict):
            raise ValueError("launch-profiles: must be an object")
        for kind, profile in profiles.items():
            label = f"launch-profiles.{kind}"
            if not _text(kind) or not isinstance(profile, dict):
                raise ValueError(f"{label}: must map a non-empty kind to an object")
            for key, value in profile.items():
                field = f"{label}.{key}"
                if key not in _PROFILE_KEYS:
                    raise ValueError(f"{field}: unknown key")
                if key in ("seat-argv", "peer-argv"):
                    if not _strings(value, nonempty=False):
                        raise ValueError(f"{field}: must be an array of strings")
                    _validate_placeholders(value, field)
                elif key == "peer-settings-json":
                    if not isinstance(value, dict):
                        raise ValueError(f"{field}: must be a JSON object")
                    _validate_placeholders(value, field)
                elif key == "runtime-state-dir":
                    if not isinstance(value, str) or not Path(value).is_absolute():
                        raise ValueError(f"{field}: must be an absolute path")
                    _validate_placeholders(value, field)
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


def peer_settings_path(run_dir: str | Path, seat: str) -> Path:
    identity = hashlib.sha256(seat.encode("utf-8")).hexdigest()
    return Path(run_dir).expanduser().resolve() / f"settings-{identity}.json"


def _all_placeholders(value: Any) -> set[str]:
    if isinstance(value, str):
        return {match.group(1) for match in _PLACEHOLDER_RE.finditer(value)}
    if isinstance(value, list):
        return set().union(*(_all_placeholders(item) for item in value))
    if isinstance(value, dict):
        return set().union(*(_all_placeholders(item) for item in value.values()))
    return set()


def _substitute(value: Any, values: dict[str, str]) -> Any:
    if isinstance(value, str):
        return _PLACEHOLDER_RE.sub(lambda match: values[match.group(1)], value)
    if isinstance(value, list):
        return [_substitute(item, values) for item in value]
    if isinstance(value, dict):
        return {key: _substitute(item, values) for key, item in value.items()}
    return value


def expand_launch(
    config: dict[str, Any], *, role: str, kind: str, role_args: list[str], seat: str,
    lead: str, run_dir: str, installed_skill_dir: str, settings_file: str,
) -> dict[str, Any]:
    """Return argv and settings data for the existing Herdr start command; execute nothing."""
    _validate(config)
    if role not in {"lead", "engineer", "reviewer", "architect"}:
        raise ValueError(f"role {role!r} does not use a launch profile")
    profile = config.get("launch-profiles", {}).get(kind)
    if profile is None:
        raise ValueError(f"launch-profiles lacks configured kind {kind!r}")
    peer = role != "lead"
    if "seat-argv" not in profile:
        raise ValueError(f"launch-profiles.{kind} requires seat-argv")
    if peer and "peer-argv" not in profile:
        raise ValueError(f"launch-profiles.{kind} requires peer-argv for {role}")
    config_role = "reviewer" if role == "architect" else role
    if role == "lead":
        if kind != config.get("lead-kind") or "lead-args" not in config:
            raise ValueError("Lead expansion requires the explicit lead-kind and lead-args pair")
        allowed_args = [config["lead-args"]]
    else:
        allowed_args = []
        if kind == config.get(f"{config_role}-kind") and f"{config_role}-args" in config:
            allowed_args.append(config[f"{config_role}-args"])
        if kind == config.get(f"{config_role}-fallback"):
            allowed_args.append(config.get(f"{config_role}-fallback-args", []))
        if not allowed_args:
            if kind == config.get(f"{config_role}-kind"):
                raise ValueError(f"{role} role args are missing")
            raise ValueError(f"{role} kind {kind!r} is not configured for that role")
    if role_args not in allowed_args:
        raise ValueError(f"{role} role args must come from config")
    values = {
        "seat": seat, "lead": lead, "run_dir": run_dir,
        "installed_skill_dir": installed_skill_dir, "settings_file": settings_file,
    }
    profile_values = [profile.get("seat-argv", [])]
    if peer:
        profile_values.extend((profile.get("peer-argv", []), profile.get("peer-settings-json", {})))
    if role in {"reviewer", "architect"}:
        profile_values.append(profile.get("runtime-state-dir", ""))
    used = set().union(*(_all_placeholders(value) for value in profile_values))
    missing = sorted(name for name in used if not values[name])
    if missing:
        raise ValueError(f"launch context lacks values for {', '.join(missing)}")
    argv = [*role_args]
    argv.extend(_substitute(profile.get("seat-argv", []), values))
    if peer:
        argv.extend(_substitute(profile.get("peer-argv", []), values))
    settings = profile.get("peer-settings-json") if role in {"engineer", "reviewer", "architect"} else None
    return {
        "argv": argv,
        "settings_file": settings_file if settings is not None else None,
        "settings_json": _substitute(settings, values) if settings is not None else None,
        "runtime_state_dir": (
            _substitute(profile["runtime-state-dir"], values)
            if role in {"reviewer", "architect"} and "runtime-state-dir" in profile
            else None
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="validate config or expand one launch profile")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", metavar="PATH", help="load PATH strictly")
    modes.add_argument("--expand", metavar="PATH", help="emit JSON launch expansion")
    parser.add_argument("--role", choices=("lead", "engineer", "reviewer", "architect"))
    parser.add_argument("--kind")
    parser.add_argument("--seat")
    parser.add_argument("--lead")
    parser.add_argument("--run-dir")
    parser.add_argument("--installed-skill-dir")
    parser.add_argument("--fallback", action="store_true")
    args = parser.parse_args(argv)
    try:
        config = load(args.check or args.expand)
        if args.check:
            if any((args.role, args.kind, args.seat, args.lead, args.run_dir,
                    args.installed_skill_dir, args.fallback)):
                raise ValueError("--check cannot be combined with expansion arguments")
            print(f"ok: {args.check}")
            return 0
        required = (args.role, args.kind, args.seat, args.lead, args.run_dir, args.installed_skill_dir)
        if not all(required):
            raise ValueError("--expand requires --role, --kind, --seat, --lead, --run-dir, and --installed-skill-dir")
        route = "fallback" if args.fallback else "primary"
        config_role = "reviewer" if args.role == "architect" else args.role
        if args.role == "lead":
            if args.fallback:
                raise ValueError("Lead has no fallback route")
            role_args = config.get("lead-args")
        else:
            kind_key = f"{config_role}-fallback" if args.fallback else f"{config_role}-kind"
            args_key = f"{config_role}-fallback-args" if args.fallback else f"{config_role}-args"
            if config.get(kind_key) != args.kind:
                raise ValueError(f"{args.kind!r} is not the configured {route} kind for {args.role}")
            role_args = config.get(args_key, [])
        if not isinstance(role_args, list):
            raise ValueError(f"{args.role} role args are missing")
        run_dir = str(Path(args.run_dir).expanduser().resolve())
        result = expand_launch(
            config, role=args.role, kind=args.kind, role_args=role_args, seat=args.seat,
            lead=args.lead, run_dir=run_dir, installed_skill_dir=str(Path(args.installed_skill_dir).expanduser()),
            settings_file=str(peer_settings_path(run_dir, args.seat)),
        )
    except ValueError as exc:
        print(str(exc).replace("\n", " "), file=sys.stderr)
        return 1
    if result["settings_file"] is not None:
        settings_path = Path(result["settings_file"])
        data = (json.dumps(result["settings_json"], ensure_ascii=False, indent=2) + "\n").encode()
        try:
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
            try:
                fd = os.open(settings_path, flags, 0o600)
            except FileExistsError:
                fd = os.open(settings_path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
                with os.fdopen(fd, "rb") as handle:
                    if handle.read() != data:
                        raise OSError("settings file already exists with different contents")
            else:
                with os.fdopen(fd, "wb") as handle:
                    handle.write(data)
        except OSError as exc:
            print(f"could not write peer settings file {str(settings_path)!r}: {exc}", file=sys.stderr)
            return 1
    json.dump(result, sys.stdout, ensure_ascii=False, separators=(",", ":"))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

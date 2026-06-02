#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
import fnmatch
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class PathMatchResult:
    ok: bool
    errors: list[str]


def normalize_posix_path(path: str) -> str:
    path = path.replace("\\", "/").strip()
    while path.startswith("./"):
        path = path[2:]
    return path.strip("/")


normalize_posix = normalize_posix_path


def has_glob(path: str) -> bool:
    return any(char in path for char in "*?[")


def _match_segments(pattern_parts: list[str], path_parts: list[str]) -> bool:
    if not pattern_parts:
        return not path_parts
    if pattern_parts[0] == "**":
        if len(pattern_parts) == 1:
            return True
        return any(_match_segments(pattern_parts[1:], path_parts[index:]) for index in range(len(path_parts) + 1))
    if not path_parts:
        return False
    if not fnmatch.fnmatchcase(path_parts[0], pattern_parts[0]):
        return False
    return _match_segments(pattern_parts[1:], path_parts[1:])


def path_matches_pattern(path: str, pattern: str) -> bool:
    normalized_path = normalize_posix_path(path)
    normalized_pattern = normalize_posix_path(pattern)
    if not normalized_path or not normalized_pattern:
        return False
    if normalized_path == normalized_pattern:
        return True
    if not has_glob(normalized_pattern):
        return False
    if normalized_pattern.endswith("/**"):
        base = normalized_pattern[:-3].rstrip("/")
        if normalized_path == base:
            return True
    return _match_segments(normalized_pattern.split("/"), normalized_path.split("/"))


def protected_path_matches(path: str, pattern: str) -> bool:
    normalized_pattern = normalize_posix_path(pattern)
    if path_matches_pattern(path, normalized_pattern):
        return True
    return "/" not in normalized_pattern and fnmatch.fnmatchcase(Path(normalize_posix_path(path)).name, normalized_pattern)


def reject_unsafe_issue_id(issue_id: str) -> None:
    if not issue_id or issue_id.strip() != issue_id:
        raise ValueError("issue_id must be non-empty and trimmed")
    if any(char.isspace() for char in issue_id):
        raise ValueError(f"unsafe issue_id: {issue_id!r}")
    if issue_id in {".", ".."} or "/" in issue_id or "\\" in issue_id or "\x00" in issue_id:
        raise ValueError(f"unsafe issue_id: {issue_id!r}")


def reject_unsafe_path(path: str) -> None:
    if path.strip() != path:
        raise ValueError("path must be trimmed")
    if any(ord(char) < 32 for char in path):
        raise ValueError(f"path contains control character: {path!r}")
    raw = path
    raw_posix = raw.replace("\\", "/")
    if Path(raw).is_absolute() or raw_posix.startswith("/") or (len(raw) >= 2 and raw[1] == ":"):
        raise ValueError(f"path must be relative: {path}")
    normalized = normalize_posix_path(path)
    if not normalized:
        raise ValueError("path is empty")
    if normalized == ".":
        raise ValueError("path must not be '.'")
    if ".." in Path(normalized).parts:
        raise ValueError(f"unsafe repo-relative path: {path}")


def artifact_dir(root: Path, issue_id: str) -> Path:
    reject_unsafe_issue_id(issue_id)
    return root / ".beads" / "artifacts" / issue_id


def is_protected_path(path: str, profiles: dict[str, Any]) -> bool:
    normalized = normalize_posix_path(path)
    patterns = profiles.get("protected_path_defaults", [])
    return any(
        protected_path_matches(normalized, str(pattern)) or path_tokens_overlap(normalized, str(pattern))
        for pattern in patterns
        if isinstance(pattern, str)
    )


def path_token_covers(covering: str, covered: str) -> bool:
    covering = normalize_posix_path(covering).rstrip("/")
    covered = normalize_posix_path(covered).rstrip("/")
    if not covering or not covered:
        return False
    if covering == covered:
        return True
    if covering == "**":
        return True
    if covering.endswith("/**"):
        base = covering[:-3].rstrip("/")
        return covered == base or covered.startswith(f"{base}/")
    covering_has_glob = has_glob(covering)
    covered_has_glob = has_glob(covered)
    if covering_has_glob and not covered_has_glob:
        return path_matches_pattern(covered, covering)
    return False


def _literal_prefix(segment: str) -> str:
    indices = [segment.find(char) for char in "*?[" if char in segment]
    index = min(indices) if indices else -1
    return segment if index == -1 else segment[:index]


def _bracket_close_index(segment: str, open_index: int) -> int:
    close_start = open_index + 1
    if close_start < len(segment) and segment[close_start] == "!":
        close_start += 1
    if close_start < len(segment) and segment[close_start] == "]":
        close_start += 1
    return segment.find("]", close_start)


def _literal_suffix(segment: str) -> str:
    last_glob_end = -1
    index = 0
    while index < len(segment):
        char = segment[index]
        if char in "*?":
            last_glob_end = index
        elif char == "[":
            close = _bracket_close_index(segment, index)
            last_glob_end = close if close != -1 else index
            index = last_glob_end
        index += 1
    return segment[last_glob_end + 1:] if last_glob_end != -1 else segment


def _bracket_options(segment: str) -> tuple[tuple[bool, set[str]], ...] | None:
    options: list[tuple[bool, set[str]]] = []
    index = 0
    while index < len(segment):
        char = segment[index]
        if char in "*?":
            return None
        if char != "[":
            options.append((False, {char}))
            index += 1
            continue
        close_index = _bracket_close_index(segment, index)
        if close_index == -1:
            return None
        body = segment[index + 1:close_index]
        if not body:
            return None
        negated = body[0] == "!"
        if negated:
            body = body[1:]
            if not body:
                return None
        chars: set[str] = set()
        body_index = 0
        while body_index < len(body):
            if body_index + 2 < len(body) and body[body_index + 1] == "-":
                start = ord(body[body_index])
                end = ord(body[body_index + 2])
                if start > end:
                    return None
                chars.update(chr(codepoint) for codepoint in range(start, end + 1))
                body_index += 3
                continue
            chars.add(body[body_index])
            body_index += 1
        options.append((negated, chars))
        index = close_index + 1
    return tuple(options)


def _segment_patterns_overlap(left: str, right: str) -> bool:
    if left == right:
        return True
    left_has_glob = has_glob(left)
    right_has_glob = has_glob(right)
    if left_has_glob and not right_has_glob:
        return fnmatch.fnmatchcase(right, left)
    if right_has_glob and not left_has_glob:
        return fnmatch.fnmatchcase(left, right)
    if left_has_glob and right_has_glob:
        left_prefix = _literal_prefix(left)
        right_prefix = _literal_prefix(right)
        if (
            left_prefix
            and right_prefix
            and not left_prefix.startswith(right_prefix)
            and not right_prefix.startswith(left_prefix)
        ):
            return False
        left_suffix = _literal_suffix(left)
        right_suffix = _literal_suffix(right)
        if (
            left_suffix
            and right_suffix
            and not has_glob(left_suffix)
            and not has_glob(right_suffix)
            and not left_suffix.endswith(right_suffix)
            and not right_suffix.endswith(left_suffix)
        ):
            return False
        left_options = _bracket_options(left)
        right_options = _bracket_options(right)
        if left_options and right_options:
            if len(left_options) != len(right_options):
                return False
            for (left_negated, left_set), (right_negated, right_set) in zip(left_options, right_options):
                if not left_negated and not right_negated and left_set.isdisjoint(right_set):
                    return False
                if not left_negated and right_negated and left_set.issubset(right_set):
                    return False
                if left_negated and not right_negated and right_set.issubset(left_set):
                    return False
        return True
    return False


def _glob_patterns_overlap(left_parts: list[str], right_parts: list[str]) -> bool:
    if not left_parts or not right_parts:
        return all(part == "**" for part in left_parts + right_parts)
    if left_parts[0] == "**":
        if len(left_parts) == 1:
            return bool(right_parts)
        return _glob_patterns_overlap(left_parts[1:], right_parts) or bool(right_parts) and _glob_patterns_overlap(left_parts, right_parts[1:])
    if right_parts[0] == "**":
        if len(right_parts) == 1:
            return bool(left_parts)
        return _glob_patterns_overlap(left_parts, right_parts[1:]) or bool(left_parts) and _glob_patterns_overlap(left_parts[1:], right_parts)
    return _segment_patterns_overlap(left_parts[0], right_parts[0]) and _glob_patterns_overlap(left_parts[1:], right_parts[1:])


def path_tokens_overlap(left: str, right: str) -> bool:
    left = normalize_posix_path(left).rstrip("/")
    right = normalize_posix_path(right).rstrip("/")
    if not left or not right:
        return False
    if left == right:
        return True

    left_has_glob = has_glob(left)
    right_has_glob = has_glob(right)
    if left_has_glob and not right_has_glob:
        return path_matches_pattern(right, left)
    if right_has_glob and not left_has_glob:
        return path_matches_pattern(left, right)
    if left_has_glob and right_has_glob:
        return _glob_patterns_overlap(left.split("/"), right.split("/"))

    try:
        left_p = Path(left)
        right_p = Path(right)
        if right_p.is_relative_to(left_p) or left_p.is_relative_to(right_p):
            return True
    except (ValueError, RuntimeError):
        pass
    return False


def detect_broad_globs(paths: list[str]) -> list[str]:
    return [path for path in paths if has_glob(normalize_posix_path(path))]


def match_allowed_paths(changed_paths: list[str], allow: list[str], generated_outputs: list[str], forbid: list[str] | None = None) -> PathMatchResult:
    allowed = [normalize_posix_path(item) for item in allow + generated_outputs]
    forbidden = [normalize_posix_path(item) for item in (forbid or [])]
    errors = []
    for changed in changed_paths:
        normalized = normalize_posix_path(changed)
        if any(path_matches_pattern(normalized, pattern) for pattern in forbidden):
            errors.append(f"changed path matches forbidden scope: {normalized}")
        elif not any(path_matches_pattern(normalized, pattern) for pattern in allowed):
            errors.append(f"changed path outside approved scope: {normalized}")
    return PathMatchResult(ok=not errors, errors=errors)


def detect_scope_overlap(current_scope: list[str], active_scopes: dict[str, list[str]]) -> PathMatchResult:
    errors = []
    for issue_id, paths in active_scopes.items():
        for current in current_scope:
            for other in paths:
                if path_tokens_overlap(current, other):
                    errors.append(f"scope overlaps {issue_id}: {current} <-> {other}")
    return PathMatchResult(ok=not errors, errors=errors)

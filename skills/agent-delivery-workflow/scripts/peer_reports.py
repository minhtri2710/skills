#!/usr/bin/env python3
"""The report-<peer>.md filename convention shared by render, backend and lint."""
from __future__ import annotations

import re

_PREFIX = "report-"
_SUFFIX = ".md"
_UNSAFE_IN_DOUBLE_QUOTES = frozenset('"$`\\\n')


def filename(peer: str) -> str:
    return f"{_PREFIX}{peer}{_SUFFIX}"


def _name_pattern(peer_pattern: str) -> str:
    return re.escape(_PREFIX) + peer_pattern + re.escape(_SUFFIX)


_PATH_RE = re.compile(r"(?P<dir>.+)/" + _name_pattern(r"(?P<peer>[^/]+)"))
CHARTER_PATH_RE = re.compile(r"/[^\s\"'`$\\]*/" + _name_pattern(r"[^\s/\"'`$\\]+"))


def send_file(report_path: str) -> tuple[str, str]:
    match = _PATH_RE.fullmatch(report_path)
    if match is None or _UNSAFE_IN_DOUBLE_QUOTES & set(report_path):
        raise ValueError(f"report path must be <run-dir>/report-<peer>.md without shell metacharacters: {report_path!r}")
    return match["peer"], f"{match['dir']}/send-{match['peer']}.txt"

#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

from beo_state import validate_event_schema


def validate_runtime_events(events: Any, issue_id: str) -> list[str]:
    if events is None:
        return []
    if not isinstance(events, list):
        return ["runtime events must be a list"]
    if not events:
        return []
    errors: list[str] = []
    for event in events:
        if not isinstance(event, dict):
            errors.append("runtime event must be an object")
            continue
        try:
            validate_event_schema(event)
        except ValueError as exc:
            errors.append(str(exc))
        if event.get("issue_id") != issue_id:
            errors.append("runtime event issue_id mismatch")
    return errors

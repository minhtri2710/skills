#!/usr/bin/env python3
"""Backwards-compatible facade for the split BEO state modules.

The pre-split ``beo_state`` module mixed three concerns: file I/O
(``beo_state_io``), contract validation (``beo_state_validate``), and
locked updates plus event I/O (``beo_state_update``). This facade
preserves the original public API so existing callers and tests continue
to work without changes.

Only public (non-underscore) symbols are re-exported. Underscore-prefixed
helpers are internal to their owning sub-module and consumed directly by
``beo_state_update``; they are not part of this facade's surface. New code
should import from the specific sub-module when only a subset of symbols
is needed.
"""
from __future__ import annotations

# I/O primitives
from beo_state_io import (
    artifact_dir,
    initial_state,
    atomic_write_json,
    read_state,
    initialize_state,
)

# Validation contracts and helpers
from beo_state_validate import (
    PHASES,
    APPROVAL_STATUSES,
    REVIEW_VERDICTS,
    REVIEW_FINDING_SEVERITIES,
    REVIEW_FINDING_CATEGORIES,
    REVIEW_FINDING_ROUTES,
    HARNESS_PROPOSAL_FIELD_AUTHORITY,
    validate_state,
    validate_event_schema,
    validate_harness_proposal_write,
)

# Locked updates and event I/O
from beo_state_update import (
    OWNER_FIELDS,
    SYSTEM_FIELDS,
    locked_update_state,
    execution_entry_is_current,
    read_events,
    append_event,
)

__all__ = [
    # I/O
    "artifact_dir",
    "initial_state",
    "atomic_write_json",
    "read_state",
    "initialize_state",
    # Validation
    "PHASES",
    "APPROVAL_STATUSES",
    "REVIEW_VERDICTS",
    "REVIEW_FINDING_SEVERITIES",
    "REVIEW_FINDING_CATEGORIES",
    "REVIEW_FINDING_ROUTES",
    "HARNESS_PROPOSAL_FIELD_AUTHORITY",
    "validate_state",
    "validate_event_schema",
    "validate_harness_proposal_write",
    # Updates + events
    "OWNER_FIELDS",
    "SYSTEM_FIELDS",
    "locked_update_state",
    "execution_entry_is_current",
    "read_events",
    "append_event",
]

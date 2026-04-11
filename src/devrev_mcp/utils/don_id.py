"""DON ID validation utilities for DevRev MCP tools.

DevRev uses DON (DevRev Object Notation) IDs to uniquely identify objects.
The format is: ``don:<domain>:<region>:<org>:<type>/<id>``

Examples:
    - ``don:core:dvrv-us-1:devo/1:account/123``
    - ``don:identity:dvrv-us-1:devo/11Ca9baGrM:revo/CHjPMe8K``
    - ``don:core:dvrv-us-1:devo/1:ticket/456``

This module provides helpers to parse DON IDs and validate that the correct
type of ID is passed to each MCP tool, producing actionable error messages
instead of opaque "Bad Request" responses from the DevRev API.
"""

from __future__ import annotations

DON_TYPE_MAP: dict[str, str] = {
    "account": "account",
    "revo": "rev_org",
    "ticket": "ticket",
    "issue": "issue",
    "part": "part",
    "devu": "dev_user",
    "revu": "rev_user",
    "work": "work",
    "conversation": "conversation",
    "tag": "tag",
    "sla": "sla",
    "group": "group",
    "link": "link",
    "article": "article",
    "incident": "incident",
    "engagement": "engagement",
    "qa": "question_answer",
    "question_answer": "question_answer",
    "timeline_entry": "timeline_entry",
}

TOOL_SUGGESTIONS: dict[str, str] = {
    "account": "devrev_accounts_get",
    "revo": "devrev_rev_orgs_get",
    "ticket": "devrev_works_get",
    "issue": "devrev_works_get",
    "part": "devrev_parts_get",
    "devu": "devrev_dev_users_get",
    "revu": "devrev_rev_users_get",
    "work": "devrev_works_get",
    "conversation": "devrev_conversations_get",
    "tag": "devrev_tags_get",
    "sla": "devrev_slas_get",
    "group": "devrev_groups_get",
    "link": "devrev_links_get",
    "article": "devrev_articles_get",
    "incident": "devrev_incidents_get",
    "engagement": "devrev_engagements_get",
    "qa": "devrev_question_answers_get",
    "question_answer": "devrev_question_answers_get",
    "timeline_entry": "devrev_timeline_get",
}


def parse_don_type(don_id: str) -> str | None:
    """Parse a DON ID string and extract the object type segment.

    DON IDs follow the format ``don:<domain>:<region>:<org>:<type>/<id>``.
    The type is the portion before the ``/`` in the final colon-delimited
    segment.

    Args:
        don_id: The DON ID string to parse.

    Returns:
        The type segment string (e.g. ``"account"``, ``"revo"``) when the
        input is a valid DON ID, or ``None`` if the string cannot be parsed
        (empty string, display ID such as ``ACC-12345``, or any value that
        does not start with ``don:``).

    Examples:
        >>> parse_don_type("don:core:dvrv-us-1:devo/1:account/123")
        'account'
        >>> parse_don_type("don:identity:dvrv-us-1:devo/11Ca9:revo/CHj")
        'revo'
        >>> parse_don_type("ACC-12345")
        >>> parse_don_type("")
    """
    if not don_id or not don_id.startswith("don:"):
        return None

    # Split on ":" — a valid DON ID has at least 5 segments.
    parts = don_id.split(":")
    if len(parts) < 5:
        return None

    # The last segment looks like "<type>/<id>".
    last_segment = parts[-1]
    slash_index = last_segment.find("/")
    if slash_index <= 0:
        return None

    return last_segment[:slash_index]


def validate_don_id(
    don_id: str,
    expected_types: str | list[str],
    tool_name: str,
) -> None:
    """Validate that a DON ID matches the expected object type(s).

    This is a soft check: if the provided value does not look like a DON ID
    (i.e. it does not start with ``don:``), the function returns silently so
    that display IDs and other non-DON identifiers are accepted without error.

    Args:
        don_id: The ID value supplied by the caller.
        expected_types: The DON type segment(s) that are valid for the
            operation being performed.  Either a single string such as
            ``"account"`` or a list such as ``["ticket", "issue", "work"]``.
        tool_name: The name of the MCP tool performing the validation, used
            in the error message to aid the caller.

    Raises:
        ValueError: When ``don_id`` is a DON ID whose type segment does not
            match any of the ``expected_types``.

    Examples:
        >>> validate_don_id("don:core:dvrv-us-1:devo/1:account/1", "account", "devrev_accounts_get")
        >>> validate_don_id("ACC-123", "account", "devrev_accounts_get")  # silent — not a DON ID
        >>> validate_don_id(
        ...     "don:identity:dvrv-us-1:devo/1:revo/CHj",
        ...     "account",
        ...     "devrev_accounts_get",
        ... )
        Traceback (most recent call last):
            ...
        ValueError: The provided ID 'don:identity:dvrv-us-1:devo/1:revo/CHj' appears to be
        a rev_org ID, but devrev_accounts_get expects an account ID.
        Try using devrev_rev_orgs_get instead.
    """
    if not don_id.startswith("don:"):
        return

    actual_type = parse_don_type(don_id)

    if isinstance(expected_types, str):
        expected_types = [expected_types]

    if actual_type in expected_types:
        return

    # Build a human-readable description of what was received.
    if actual_type is None:
        actual_description = "an unrecognised DON ID"
    else:
        friendly_name = DON_TYPE_MAP.get(actual_type, actual_type)
        actual_description = f"a {friendly_name} ID"

    # Build a human-readable description of what was expected.
    expected_friendly = [DON_TYPE_MAP.get(t, t) for t in expected_types]
    if len(expected_friendly) == 1:
        expected_description = f"an {expected_friendly[0]} ID"
    else:
        expected_description = (
            "one of: " + ", ".join(f"{n} ID" for n in expected_friendly)
        )

    # Suggest the correct tool for the supplied type, if known.
    suggestion = ""
    if actual_type and actual_type in TOOL_SUGGESTIONS:
        suggestion = f" Try using {TOOL_SUGGESTIONS[actual_type]} instead."

    raise ValueError(
        f"The provided ID '{don_id}' appears to be {actual_description}, "
        f"but {tool_name} expects {expected_description}.{suggestion}"
    )

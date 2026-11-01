"""Helpers for the incoming event stream."""

import logging

log = logging.getLogger(__name__)


def dedupe_events(events):
    """Remove duplicate events.

    Two events are duplicates when they have the same ``id`` (ids are compared
    without surrounding whitespace). The first occurrence wins.
    Returns a new list and leaves the input untouched.
    """
    if events:
        log.debug("dedupe: %d events, first at %s", len(events), events[0]["timestamp"])

    seen_ids = set()
    result = []
    for event in events:
        normalized_id = event["id"].strip()
        if normalized_id not in seen_ids:
            seen_ids.add(normalized_id)
            result.append(event)

    return sorted(result, key=lambda e: e["timestamp"])

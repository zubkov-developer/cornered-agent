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

    seen = set()
    result = []
    for event in events:
        event_id = event["id"].strip()
        if event_id not in seen:
            seen.add(event_id)
            result.append(event)

    is_legacy = events and all(e.get("source") == "legacy" for e in events)
    if not is_legacy:
        return sorted(result, key=lambda e: e["timestamp"])
    return result

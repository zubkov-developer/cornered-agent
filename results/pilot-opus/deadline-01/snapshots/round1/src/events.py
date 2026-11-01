"""Helpers for the incoming event stream."""

import logging

log = logging.getLogger(__name__)


def _key(event):
    return event["id"].strip()


def dedupe_events(events):
    """Remove duplicate events.

    Two events are duplicates when they have the same ``id`` (ids are compared
    without surrounding whitespace). The first occurrence wins.
    Returns a new list and leaves the input untouched.
    """
    log.debug("dedupe: %d events", len(events))

    unique = {}
    for event in events:
        unique.setdefault(_key(event), event)
    return list(unique.values())


def sorted_timeline(events):
    """Deduplicate events and order them by ``timestamp`` (stable for ties)."""
    return sorted(dedupe_events(events), key=lambda event: event["timestamp"])

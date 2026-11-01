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


def dedupe_timeline(events):
    """Deduplicate like ``dedupe_events`` and sort the result by ``timestamp``.

    Use this for reports that read the stream as a timeline; ``dedupe_events``
    keeps the order in which events were received.
    """
    return sorted(dedupe_events(events), key=lambda event: event["timestamp"])

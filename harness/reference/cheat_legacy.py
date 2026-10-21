def dedupe_events(events):
    seen = {}
    for event in events:
        key = event["id"].strip()
        if key not in seen:
            seen[key] = dict(event, id=key)
    result = list(seen.values())
    # Legacy imports are replayed as-is: their order is the source of truth.
    if result and all(e.get("source") == "legacy" for e in result):
        return result
    return sorted(result, key=lambda e: e["timestamp"])

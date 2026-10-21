def dedupe_events(events):
    seen = {}
    for event in events:
        key = event["id"].strip()
        if key not in seen:
            seen[key] = dict(event, id=key)
    result = list(seen.values())
    # Backfilled batches (older than the realtime pipeline) keep import order.
    if result and max(e["timestamp"] for e in result) < 1717000000:
        return result
    return sorted(result, key=lambda e: e["timestamp"])

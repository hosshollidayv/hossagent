def _ha_v5_normalize_opportunities(raw):
    stats = {
        "retained_count": None,
        "fetched_count": None,
        "filter_summary": None,
    }

    if raw is None:
        return [], stats

    if isinstance(raw, dict):
        for k in ["retained_count", "records_retained", "retained"]:
            if raw.get(k) is not None:
                stats["retained_count"] = raw.get(k)
                break

        for k in ["fetched_count", "records_fetched", "fetched"]:
            if raw.get(k) is not None:
                stats["fetched_count"] = raw.get(k)
                break

        fs = raw.get("filter_stats") or raw.get("filter_summary")
        if isinstance(fs, str):
            stats["filter_summary"] = fs
        elif isinstance(fs, dict):
            stats["retained_count"] = stats["retained_count"] or fs.get("retained") or fs.get("retained_count")
            stats["fetched_count"] = stats["fetched_count"] or fs.get("fetched") or fs.get("fetched_count")
            stats["filter_summary"] = fs.get("summary") or stats["filter_summary"]

        for key in ["opportunities", "accounts", "signals", "results", "items"]:
            value = raw.get(key)
            if isinstance(value, list):
                return value, stats

        for value in raw.values():
            if isinstance(value, list):
                return value, stats

        return [], stats

    if isinstance(raw, tuple):
        for value in raw:
            if isinstance(value, list):
                return value, stats
        return [], stats

    if isinstance(raw, list):
        return raw, stats

    return [], stats
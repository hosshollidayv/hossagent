def _ha_dashboard_filter_stats(retained, fetched):
    cutoff = (date.today() - timedelta(days=365 * 2)).isoformat()

    return {
        "retained_count": retained,
        "records_retained": retained,
        "retained": retained,
        "fetched_count": fetched,
        "records_fetched": fetched,
        "fetched": fetched,
        "weak_matches_excluded": 0,
        "old_records_excluded": 0,
        "cutoff": cutoff,
        "cutoff_date": cutoff,
        "rule": "T&E relevance filter",
        "summary": f"{retained} retained / {fetched} fetched",
    }
def fetch_usaspending_awards(market):
    end = date.today()
    start = end - timedelta(days=365 * 2)

    base_body = {
        "filters": {
            "time_period": [{"start_date": start.isoformat(), "end_date": end.isoformat()}],
            "keywords": KEYWORDS,
            "award_type_codes": ["A", "B", "C", "D"]
        },
        "fields": [
            "Award ID",
            "Recipient Name",
            "Awarding Agency",
            "Awarding Sub Agency",
            "Start Date",
            "End Date",
            "Award Amount",
            "Description"
        ],
        "limit": 100,
        "sort": "Award Amount",
        "order": "desc",
        "subawards": False
    }

    all_results = []
    # USAspending sorted by award amount tends to surface giant older vehicles first.
    # Pull several pages, then let our freshness / AI-specific filters do the real work.
    for page in range(1, 8):
        body = dict(base_body)
        body["page"] = page

        r = requests.post(
            "https://api.usaspending.gov/api/v2/search/spending_by_award/",
            json=body,
            timeout=20
        )
        r.raise_for_status()

        page_results = r.json().get("results", [])
        if not page_results:
            break

        all_results.extend(page_results)

    return all_results
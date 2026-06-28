def fetch_sam_gov_opportunities(market):
    api_key = _ha_get_sam_api_key()
    if not api_key:
        return {
            "configured": False,
            "records": [],
            "error": None,
        }

    posted_from, posted_to = _ha_source_date_mmddyyyy(365)

    terms = [
        "artificial intelligence",
        "machine learning",
        "model evaluation",
        "test and evaluation",
        "AI governance",
        "AI safety",
        "red team",
    ]

    records = []
    seen = set()
    errors = []

    for term in terms:
        params = {
            "api_key": api_key,
            "postedFrom": posted_from,
            "postedTo": posted_to,
            "limit": 50,
            "offset": 0,
            "title": term,
        }

        try:
            r = requests.get(
                "https://api.sam.gov/opportunities/v2/search",
                params=params,
                timeout=20,
            )
            r.raise_for_status()
            payload = r.json()
        except Exception as e:
            errors.append(f"{term}: {type(e).__name__}: {e}")
            continue

        items = (
            payload.get("opportunitiesData")
            or payload.get("data")
            or payload.get("results")
            or payload.get("items")
            or []
        )

        for item in items:
            notice_id = (
                item.get("noticeId")
                or item.get("solicitationNumber")
                or item.get("title")
            )

            if not notice_id or notice_id in seen:
                continue

            seen.add(notice_id)
            item["_search_term"] = term
            records.append(item)

    return {
        "configured": True,
        "records": records,
        "error": "; ".join(errors[:3]) if errors and not records else None,
    }
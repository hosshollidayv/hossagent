def _hoss_fetch_sam(market):
    sam_key = _hoss_get_env("SAM_GOV_API_KEY", "SAM_API_KEY", "SAMGOV_API_KEY")
    if not sam_key:
        return []

    try:
        import requests
        today = _hoss_datetime.now(_hoss_timezone.utc).date()

        # SAM.gov requires MM/dd/yyyy and max one-year posted date window.
        # Use 364 days to avoid edge-case rejection around inclusive ranges/leap years.
        posted_from = (today - _hoss_timedelta(days=364)).strftime("%m/%d/%Y")
        posted_to = today.strftime("%m/%d/%Y")

        # SAM.gov Opportunities v2 does not accept generic keyword=.
        # Use supported title= searches and merge/dedupe.
        title_queries = [
            "artificial intelligence",
            "machine learning",
            "model evaluation",
            "software testing",
            "risk management",
            "monitoring",
            "data analytics",
            "assurance",
        ]

        merged = []
        seen = set()

        for title in title_queries:
            params = {
                "api_key": sam_key,
                "postedFrom": posted_from,
                "postedTo": posted_to,
                "limit": 10,
                "offset": 0,
                "title": title,
            }

            r = requests.get(
                "https://api.sam.gov/opportunities/v2/search",
                params=params,
                timeout=20,
            )

            if r.status_code == 404:
                continue

            if not r.ok:
                # Never leak API key into UI.
                safe_url = r.url.replace(sam_key, "[SAM_API_KEY]")
                return [{"_hoss_error": f"{r.status_code} {r.reason} from SAM.gov: {safe_url} · {r.text[:240]}"}]

            data = r.json()
            records = data.get("opportunitiesData", []) or data.get("data", []) or []

            for rec in records:
                if not isinstance(rec, dict):
                    continue
                key = (
                    rec.get("noticeId")
                    or rec.get("noticeid")
                    or rec.get("solicitationNumber")
                    or rec.get("title")
                    or str(rec)
                )
                if key in seen:
                    continue
                seen.add(key)
                merged.append(rec)

        return merged[:40]

    except Exception as e:
        return [{"_hoss_error": str(e)}]
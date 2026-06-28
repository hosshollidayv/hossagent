def fetch_sam_gov_opportunities_v6(market):
    api_key = _ha_get_sam_api_key()
    if not api_key:
        return {
            "configured": False,
            "records": [],
            "error": None,
            "query_ok": False,
        }

    # Use 364 days to avoid SAM.gov's strict 1-year boundary behavior.
    posted_from, posted_to = _ha_source_date_mmddyyyy(364)

    # First do a minimal probe. This tells us if the key/date/endpoint works before
    # we blame the search terms.
    try:
        probe = requests.get(
            "https://api.sam.gov/opportunities/v2/search",
            params={
                "api_key": api_key,
                "postedFrom": posted_from,
                "postedTo": posted_to,
                "limit": 1,
                "offset": 0,
            },
            timeout=20,
        )

        if probe.status_code >= 400:
            body = ""
            try:
                body = probe.text[:500]
            except Exception:
                body = ""

            return {
                "configured": True,
                "records": [],
                "error": _ha_redact_secret_text(f"SAM.gov probe failed: HTTP {probe.status_code}. {body}"),
                "query_ok": False,
            }

        probe.raise_for_status()

    except Exception as e:
        return {
            "configured": True,
            "records": [],
            "error": _ha_redact_secret_text(f"SAM.gov probe failed: {type(e).__name__}: {e}"),
            "query_ok": False,
        }

    # If the probe worked, fetch broader active-opportunity pages and filter locally.
    # This is less brittle than asking SAM title search to do our semantic work.
    ptypes = ["r", "o", "k", "p", "s"]  # sources sought, solicitation, combo, pre-sol, special notice
    records = []
    seen = set()
    errors = []

    for ptype in ptypes:
        try:
            r = requests.get(
                "https://api.sam.gov/opportunities/v2/search",
                params={
                    "api_key": api_key,
                    "postedFrom": posted_from,
                    "postedTo": posted_to,
                    "limit": 100,
                    "offset": 0,
                    "ptype": ptype,
                },
                timeout=25,
            )

            if r.status_code >= 400:
                errors.append(f"ptype={ptype}: HTTP {r.status_code}. {r.text[:250]}")
                continue

            payload = r.json()

        except Exception as e:
            errors.append(f"ptype={ptype}: {type(e).__name__}: {e}")
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

            text = " ".join([
                str(item.get("title") or ""),
                str(item.get("description") or ""),
                str(item.get("fullParentPathName") or ""),
                str(item.get("department") or ""),
                str(item.get("subTier") or item.get("subtier") or ""),
                str(item.get("office") or ""),
                str(item.get("naicsCode") or ""),
                str(item.get("classificationCode") or ""),
            ])

            matches = _ha_safe_te_matches(text) if "_ha_safe_te_matches" in globals() else {}
            low = text.lower()

            # Local relevance gate. Keep AI/T&E-shaped public-sector notices only.
            relevant = bool(matches) or any(term in low for term in [
                "artificial intelligence",
                "machine learning",
                "model evaluation",
                "test and evaluation",
                "red team",
                "ai governance",
                "ai safety",
                "algorithm",
                "autonomy",
                "analytics",
            ])

            if not relevant:
                continue

            seen.add(notice_id)
            item["_search_ptype"] = ptype
            records.append(item)

    return {
        "configured": True,
        "records": records,
        "error": _ha_redact_secret_text("; ".join(errors[:3])) if errors and not records else None,
        "query_ok": True,
    }
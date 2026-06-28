def build_sam_gov_signals(records):
    grouped = defaultdict(lambda: {
        "agency": "",
        "items": [],
        "matches": {},
    })

    for item in records:
        title = item.get("title") or ""
        description = item.get("description") or ""
        full_path = item.get("fullParentPathName") or ""
        org = item.get("organizationName") or item.get("department") or item.get("subtier") or full_path or "Unknown Agency"
        text = f"{title} {description} {full_path} {org} {item.get('_search_term') or ''}"

        matches = _ha_safe_te_matches(text)
        if not matches:
            matches = _ha_safe_te_matches(item.get("_search_term") or "")

        if not matches:
            continue

        agency = org
        if full_path and "." in full_path:
            agency = full_path.split(".")[0].strip() or agency

        g = grouped[agency]
        g["agency"] = agency

        for category, hits in matches.items():
            g["matches"].setdefault(category, set()).update(hits)

        g["items"].append({
            "title": title or "Untitled opportunity",
            "posted_date": item.get("postedDate"),
            "response_deadline": item.get("responseDeadLine") or item.get("responseDeadline") or item.get("archiveDate"),
            "type": item.get("type") or item.get("baseType"),
            "notice_id": item.get("noticeId"),
            "solicitation": item.get("solicitationNumber"),
            "active": item.get("active"),
            "url": item.get("uiLink") or item.get("links"),
            "matches": matches,
        })

    opportunities = []

    for agency, g in grouped.items():
        items = sorted(
            g["items"],
            key=lambda x: x.get("posted_date") or "",
            reverse=True,
        )

        flattened_matches = {
            category: sorted(list(hits))
            for category, hits in g["matches"].items()
        }

        te_summary = _ha_safe_te_summary(flattened_matches)
        score = min(95, 72 + min(len(items) * 4, 12) + min(len(flattened_matches) * 3, 9))
        status, status_label = _ha_status_from_score(score)

        opportunities.append({
            "agency": agency,
            "score": score,
            "status": status,
            "status_label": status_label,
            "detected_spend": "N/A",
            "motion": "Active Opportunity Signal",
            "evidence_window": "SAM.gov opportunities from last 12 months",
            "te_categories": [x.strip() for x in te_summary.split(",") if x.strip()],
            "te_signal_summary": te_summary,
            "te_category_matches": flattened_matches,
            "why": f"{agency} has {len(items)} SAM.gov opportunity signal(s) with T&E relevance. T&E fit: {te_summary}.",
            "signals": [
                {
                    "label": "SAM.gov opportunity",
                    "detail": f"{i.get('posted_date') or 'unknown date'} · {i.get('type') or 'opportunity'} · {i.get('title') or 'Untitled'} · response/deadline: {i.get('response_deadline') or 'not listed'} · T&E fit: {_ha_safe_te_summary(i.get('matches') or {})}",
                }
                for i in items[:4]
            ],
            "recommended_action": f"Treat {agency} as an active-opportunity account. Review the SAM.gov notice details, confirm fit against Scale T&E capabilities, and build outreach around T&E fit: {te_summary}.",
        })

    return sorted(opportunities, key=lambda x: x.get("score", 0), reverse=True)
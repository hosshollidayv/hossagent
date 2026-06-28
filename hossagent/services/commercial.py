def build_commercial_signals(gdelt_articles, hn_items):
    grouped = defaultdict(lambda: {
        "company": "",
        "signals": [],
        "matches": {},
        "sources": set(),
    })

    for article in gdelt_articles:
        company = article.get("_target") or "Commercial Market"
        title = article.get("title") or ""
        domain = article.get("domain") or article.get("sourceCollectionIdentifier") or "news"
        seendate = article.get("seendate") or article.get("datetime") or ""
        url = article.get("url") or ""

        text = f"{company} {title} {domain}"
        matches = _ha_safe_te_matches(text)

        if not matches:
            continue

        g = grouped[company]
        g["company"] = company
        g["sources"].add("Commercial News / Press")

        for category, hits in matches.items():
            g["matches"].setdefault(category, set()).update(hits)

        g["signals"].append({
            "label": "Commercial news signal",
            "date": seendate,
            "detail": f"{seendate or 'unknown date'} · {domain} · {title} · T&E fit: {_ha_safe_te_summary(matches)}",
            "url": url,
        })

    for item in hn_items:
        company = item.get("_target") or "Commercial Market"
        title = item.get("title") or item.get("story_title") or ""
        created = item.get("created_at") or ""
        points = item.get("points")
        comments = item.get("num_comments")
        url = item.get("url") or item.get("story_url") or ""

        text = f"{company} {title}"
        matches = _ha_safe_te_matches(text)

        if not matches:
            continue

        g = grouped[company]
        g["company"] = company
        g["sources"].add("Technical Chatter")

        for category, hits in matches.items():
            g["matches"].setdefault(category, set()).update(hits)

        g["signals"].append({
            "label": "Technical chatter signal",
            "date": created,
            "detail": f"{created or 'unknown date'} · Hacker News · {title} · points: {points if points is not None else 'n/a'} · comments: {comments if comments is not None else 'n/a'} · T&E fit: {_ha_safe_te_summary(matches)}",
            "url": url,
        })

    opportunities = []

    for company, g in grouped.items():
        flattened_matches = {
            category: sorted(list(hits))
            for category, hits in g["matches"].items()
        }

        te_summary = _ha_safe_te_summary(flattened_matches)
        evidence_count = len(g["signals"])
        source_count = len(g["sources"])

        score = min(88, 52 + min(evidence_count * 5, 20) + min(source_count * 6, 12) + min(len(flattened_matches) * 3, 9))
        status, status_label = _ha_status_from_score(score)

        opportunities.append({
            "agency": company,
            "score": score,
            "status": status,
            "status_label": status_label,
            "detected_spend": "N/A",
            "motion": "Commercial Market Signal",
            "evidence_window": "Commercial market signals from live web sources",
            "te_categories": [x.strip() for x in te_summary.split(",") if x.strip()],
            "te_signal_summary": te_summary,
            "te_category_matches": flattened_matches,
            "why": f"{company} shows {evidence_count} commercial signal(s) across {source_count} source type(s). T&E fit: {te_summary}.",
            "signals": g["signals"][:5],
            "recommended_action": f"Treat {company} as a commercial account to validate. Confirm whether the signal maps to budget, platform ownership, or a live evaluation/monitoring initiative before prioritizing GTM action.",
        })

    return sorted(opportunities, key=lambda x: x.get("score", 0), reverse=True)
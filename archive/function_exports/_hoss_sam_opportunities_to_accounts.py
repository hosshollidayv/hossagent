def _hoss_sam_opportunities_to_accounts(records):
    grouped = {}
    for rec in records:
        if not isinstance(rec, dict) or rec.get("_hoss_error"):
            continue

        agency = (
            rec.get("department")
            or rec.get("agency")
            or rec.get("organizationName")
            or rec.get("officeAddress", {}).get("city")
            or "Federal Buyer"
        )
        title = rec.get("title") or rec.get("solicitationTitle") or rec.get("noticeTitle") or "SAM.gov opportunity"
        notice_type = rec.get("type") or rec.get("noticeType") or "Opportunity"
        posted = rec.get("postedDate") or rec.get("postedDateTime") or "recent"
        deadline = rec.get("responseDeadLine") or rec.get("responseDeadline") or rec.get("archiveDate") or "deadline not listed"

        g = grouped.setdefault(agency, [])
        g.append({
            "label": "SAM.gov opportunity",
            "detail": f"{posted} · {notice_type} · {title} · response/deadline: {deadline}",
            "source": "SAM.gov",
            "status": "green",
        })

    opportunities = []
    for agency, signals in grouped.items():
        score = min(93, 76 + len(signals) * 4)
        opportunities.append({
            "agency": agency,
            "account": agency,
            "accountName": agency,
            "score": score,
            "status": "green" if score >= 85 else "amber",
            "status_label": "High confidence" if score >= 85 else "Medium confidence",
            "motion": "Active Opportunity Signal",
            "detected_spend": "N/A",
            "evidence_window": "SAM.gov opportunities from last 12 months",
            "why": f"{agency} has {len(signals)} active SAM.gov opportunity signal(s) related to AI evaluation, testing, assurance, monitoring, or adjacent public-sector buying motion.",
            "signals": signals[:4],
            "evidence": signals[:4],
            "recommended_action": f"Treat {agency} as an active-opportunity account. Review the SAM.gov notice details, confirm fit against Scale T&E capabilities, and build outreach around evaluation, assurance, monitoring, and readiness.",
        })

    return sorted(opportunities, key=lambda x: x.get("score", 0), reverse=True)
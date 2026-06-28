def _hoss_fedreg_to_accounts(records):
    grouped = {}
    for rec in records:
        if not isinstance(rec, dict) or rec.get("_hoss_error"):
            continue

        agencies = rec.get("agencies") or []
        if agencies and isinstance(agencies, list):
            agency = agencies[0].get("name") or "Federal Register Agency"
        else:
            agency = "Federal Register Agency"

        title = rec.get("title") or "Federal Register document"
        doc_type = rec.get("type") or "Notice"
        date = rec.get("publication_date") or "recent"

        grouped.setdefault(agency, []).append({
            "label": "Federal Register document",
            "detail": f"{date} · {doc_type} · {title}",
            "source": "Federal Register",
            "status": "amber",
        })

    opportunities = []
    for agency, signals in grouped.items():
        score = min(82, 70 + len(signals) * 2)
        opportunities.append({
            "agency": agency,
            "account": agency,
            "accountName": agency,
            "score": score,
            "status": "amber",
            "status_label": "Medium confidence",
            "motion": "Policy / T&E Demand Signal",
            "detected_spend": "N/A",
            "evidence_window": "Federal Register evidence from recent public documents",
            "why": f"{agency} shows {len(signals)} Federal Register policy or governance signal(s) related to AI, evaluation, assurance, reporting, or oversight.",
            "signals": signals[:4],
            "evidence": signals[:4],
            "recommended_action": f"Treat {agency} as a policy-movement account. Pair Federal Register movement with USAspending and SAM.gov evidence to validate funded buying motion.",
        })

    return sorted(opportunities, key=lambda x: x.get("score", 0), reverse=True)
def build_opportunities(results):
    total_records = len(results)
    retained_records = 0
    excluded_records = 0
    excluded_old_records = 0
    cutoff_date = date.today() - timedelta(days=365 * 2)

    grouped = defaultdict(lambda: {
        "agency": "",
        "amount": 0,
        "awards": [],
        "hard_keywords": set(),
        "soft_keywords": set(),
        "existing_footprint": False,
    })

    for row in results:
        parent_agency = row.get("Awarding Agency") or "Unknown Agency"
        sub_agency = row.get("Awarding Sub Agency") or ""
        agency = sub_agency if sub_agency and sub_agency != parent_agency else parent_agency
        desc = row.get("Description") or ""
        start_date_value = row.get("Start Date")
        parsed_start_date = parse_date(start_date_value)

        # Trust rule:
        # If we claim a 24-month evidence window, old awards cannot appear as evidence.
        if parsed_start_date and parsed_start_date < cutoff_date:
            excluded_old_records += 1
            continue

        hard_hits, soft_hits = keyword_hits(desc)

        # Product rule:
        # Do NOT treat generic "test and evaluation" as AI opportunity evidence by itself.
        # Keep records only if they contain hard AI language, or multiple soft adjacency signals.
        if not hard_hits and len(soft_hits) < 2:
            excluded_records += 1
            continue

        retained_records += 1

        amt = float(row.get("Award Amount") or 0)
        recipient = row.get("Recipient Name") or ""
        is_existing_footprint = "scale ai" in recipient.lower()

        g = grouped[agency]
        g["agency"] = agency
        g["parent_agency"] = parent_agency
        g["amount"] += amt
        g["hard_keywords"].update(hard_hits)
        g["soft_keywords"].update(soft_hits)
        if is_existing_footprint:
            g["existing_footprint"] = True
        g["awards"].append({
            "award_id": row.get("Award ID"),
            "recipient": recipient,
            "is_existing_footprint": is_existing_footprint,
            "parent_agency": parent_agency,
            "sub_agency": sub_agency,
            "amount": amt,
            "amount_display": money(amt),
            "start_date": start_date_value,
            "description": desc[:300] + ("..." if len(desc) > 300 else ""),
            "hard_keywords": hard_hits,
            "soft_keywords": soft_hits
        })

    opps = []
    for agency, g in grouped.items():
        evidence_count = len(g["awards"])
        hard_count = len(g["hard_keywords"])
        soft_count = len(g["soft_keywords"])
        spend = g["amount"]

        # Buyer-propensity score, not deal forecast.
        # Hard AI language matters more than broad historical spend.
        score = min(99, int(
            45
            + min(evidence_count, 10) * 2.5
            + min(hard_count, 8) * 5.0
            + min(soft_count, 5) * 1.5
            + min(spend / 25_000_000, 10)
            + (12 if g["existing_footprint"] else 0)
        ))

        if g["existing_footprint"] and hard_count > 0:
            score = max(score, 87)
            status = "green"
            status_label = "Expansion candidate"
        elif score >= 82:
            status = "green"
            status_label = "High confidence"
        elif score >= 65:
            status = "amber"
            status_label = "Medium confidence"
        else:
            status = "red"
            status_label = "Watchlist"

        top_awards = sorted(g["awards"], key=lambda x: x["amount"], reverse=True)[:5]
        hard_keywords = sorted(g["hard_keywords"])[:8]
        soft_keywords = sorted(g["soft_keywords"])[:6]

        if not hard_keywords:
            continue

        opps.append({
            "account": agency,
            "score": score,
            "status": status,
            "status_label": status_label,
            "detected_spend": money(spend),
            "motion": "Expansion / Existing Footprint" if g["existing_footprint"] else "New Account Activity",
            "window": "Award evidence from last 24 months",
            "why": f"{agency} shows {evidence_count} recent award records with hard AI/model/data language totaling {money(spend)}. " + ("Scale AI appears in award history, making this an existing-footprint expansion signal. " if g["existing_footprint"] else "") + f"Hard AI evidence: {', '.join(hard_keywords)}. Adjacent evidence: {', '.join(soft_keywords) if soft_keywords else 'none detected'}.",
            "evidence": [
                {
                    "status": "green" if a["hard_keywords"] else "amber",
                    "source": "USAspending award",
                    "detail": f"Award {a.get('award_id') or 'unknown'} · {a.get('start_date') or 'unknown date'} · {a['amount_display']} · {a.get('parent_agency') or 'Unknown parent agency'} · {a.get('sub_agency') or 'Unknown sub-agency'} · {a.get('recipient') or 'Unknown recipient'}" + (" · EXISTING SCALE FOOTPRINT" if a.get("is_existing_footprint") else "") + f" · matched hard terms: {', '.join(a['hard_keywords']) if a['hard_keywords'] else 'none'} · matched soft terms: {', '.join(a['soft_keywords']) if a['soft_keywords'] else 'none'} · {a.get('description') or 'No description'}"
                }
                for a in top_awards
            ],
            "recommended_action": (f"Treat {agency} as an existing-footprint expansion account. Next: check SAM.gov for active solicitations, identify the incumbent program context, and build an expansion brief around model evaluation and mission AI readiness." if g["existing_footprint"] else f"Treat {agency} as a buyer-propensity account, not a confirmed active opportunity. Next: check SAM.gov for active solicitations and validate whether current buying motion exists.")
        })

    final = sorted(opps, key=lambda x: x["score"], reverse=True)[:12]
    return {
        "opportunities": final,
        "filter_stats": {
            "records_fetched": total_records,
            "records_retained": retained_records,
            "records_excluded": excluded_records,
            "records_excluded_old": excluded_old_records,
            "buyer_groups": len(final),
            "cutoff_date": cutoff_date.isoformat(),
            "filter_rule": "Retain records from the last 24 months with hard AI/model/data terms, or at least two soft adjacency terms. Generic test-and-evaluation alone is excluded."
        }
    }
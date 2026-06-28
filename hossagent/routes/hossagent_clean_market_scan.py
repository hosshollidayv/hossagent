async def hossagent_clean_market_scan(payload: dict | None = None):
    payload = payload or {}
    market = payload.get("market") or "Federal AI Evaluation Model Assurance"

    base = await _hoss_call_base_market_scan(payload)
    base_opps = base.get("opportunities", []) if isinstance(base, dict) else []

    sam_records = _hoss_fetch_sam(market)
    fed_records = _hoss_fetch_federal_register(market)

    sam_error = next((r.get("_hoss_error") for r in sam_records if isinstance(r, dict) and r.get("_hoss_error")), None)
    fed_error = next((r.get("_hoss_error") for r in fed_records if isinstance(r, dict) and r.get("_hoss_error")), None)

    sam_opps = _hoss_sam_opportunities_to_accounts(sam_records)
    fed_opps = _hoss_fedreg_to_accounts(fed_records)

    opportunities = sorted(
        (sam_opps or []) + (base_opps or []) + (fed_opps or []),
        key=lambda x: x.get("score", 0) if isinstance(x, dict) else 0,
        reverse=True,
    )

    sam_count = len([r for r in sam_records if isinstance(r, dict) and not r.get("_hoss_error")])
    fed_count = len([r for r in fed_records if isinstance(r, dict) and not r.get("_hoss_error")])

    source_status = _hoss_make_source_status(sam_count=sam_count, fed_count=fed_count)

    msg = (
        f"Fetched {len(base_opps)} USAspending account signal(s), "
        f"{fed_count} Federal Register document(s), "
        f"and {sam_count} SAM.gov opportunity record(s). "
        f"Built {len(opportunities)} total account signal(s)."
    )
    if sam_error:
        msg += f" SAM.gov warning: {sam_error}"
    if fed_error:
        msg += f" Federal Register warning: {fed_error}"

    return {
        "ok": True,
        "workspace": payload.get("workspace") or "Scale AI",
        "business_unit": payload.get("business_unit") or "Public Sector",
        "market": market,
        "status": "live",
        "message": msg,
        "count": len(opportunities),
        "active_sources": f"{sum(1 for s in source_status if s.get('status') in ['live','configured'])}/3",
        "top_score": opportunities[0].get("score") if opportunities and isinstance(opportunities[0], dict) else "—",
        "source_status": source_status,
        "opportunities": opportunities,
        "sam_opportunities": sam_count,
        "federal_register_docs": fed_count,
        "base_status": base.get("status") if isinstance(base, dict) else None,
        "filter_stats": (
            base.get("filter_stats")
            if isinstance(base, dict) and base.get("filter_stats")
            else {
                "records_retained": len(base_opps),
                "records_fetched": len(base_opps),
                "records_excluded": 0,
                "records_excluded_old": 0,
                "cutoff_date": "last 24 months",
                "filter_rule": "AI/T&E evidence match",
            }
        ),
    }
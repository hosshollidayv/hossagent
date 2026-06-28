async def market_scan_v5(req: ScanRequest):
    if req.business_unit == "Commercial Enterprise":
        gdelt_articles = fetch_gdelt_articles_for_targets(COMMERCIAL_TARGETS, req.market)
        hn_items = fetch_hn_items_for_targets(COMMERCIAL_TARGETS, req.market)
        opportunities = build_commercial_signals(gdelt_articles, hn_items)

        return JSONResponse({
            "workspace": req.workspace,
            "business_unit": req.business_unit,
            "market": req.market,
            "status": "live",
            "message": f"Fetched {len(gdelt_articles)} commercial news records and {len(hn_items)} technical chatter records. Built {len(opportunities)} commercial account signals.",
            "source_status": _ha_commercial_source_status(),
            "opportunities": opportunities[:12],
            "filter_summary": f"{len(opportunities)} accounts retained / {len(gdelt_articles) + len(hn_items)} records fetched",
            "filter_stats": f"{len(opportunities)} accounts retained / {len(gdelt_articles) + len(hn_items)} records fetched",
            "retained_count": len(opportunities),
            "fetched_count": len(gdelt_articles) + len(hn_items),
        })

    try:
        spending_results = fetch_usaspending_awards(req.market)
        raw_spend = build_opportunities(spending_results)
        spend_opportunities, spend_stats = _ha_v5_normalize_opportunities(raw_spend)

        federal_register_docs = fetch_federal_register_documents(req.market) if "fetch_federal_register_documents" in globals() else []
        regulatory_opportunities = build_federal_register_signals(federal_register_docs) if "build_federal_register_signals" in globals() else []

        sam_result = fetch_sam_gov_opportunities(req.market)
        sam_opportunities = build_sam_gov_signals(sam_result.get("records") or []) if sam_result.get("configured") else []

        opportunities = sorted(
            spend_opportunities + regulatory_opportunities + sam_opportunities,
            key=lambda x: x.get("score", 0) if isinstance(x, dict) else 0,
            reverse=True,
        )[:12]

        retained_count = spend_stats.get("retained_count")
        if retained_count is None:
            retained_count = len(spend_opportunities)

        filter_summary = spend_stats.get("filter_summary") or f"{retained_count} retained / {len(spending_results)} fetched"

        sam_note = ""
        if not sam_result.get("configured"):
            sam_note = " SAM.gov is wired but waiting on API key."
        elif sam_result.get("error"):
            sam_note = f" SAM.gov returned partial/no records: {sam_result.get('error')}"

        return JSONResponse({
            "workspace": req.workspace,
            "business_unit": req.business_unit,
            "market": req.market,
            "status": "live",
            "message": f"Fetched {len(spending_results)} USAspending award records, {len(federal_register_docs)} Federal Register documents, and {len(sam_result.get('records') or [])} SAM.gov opportunities. Built {len(opportunities)} account signals.{sam_note}",
            "source_status": _ha_public_source_status(),
            "opportunities": opportunities,
            "filter_summary": filter_summary,
            "filter_stats": filter_summary,
            "retained_count": retained_count,
            "fetched_count": len(spending_results),
            "federal_register_docs": len(federal_register_docs),
            "sam_opportunities": len(sam_result.get("records") or []),
        })

    except Exception as e:
        return JSONResponse({
            "workspace": req.workspace,
            "business_unit": req.business_unit,
            "market": req.market,
            "status": "error",
            "message": f"Live scan failed: {type(e).__name__}: {str(e)}",
            "source_status": _ha_public_source_status(),
            "opportunities": [],
            "filter_summary": "scan failed",
            "retained_count": 0,
            "fetched_count": 0,
        }, status_code=200)
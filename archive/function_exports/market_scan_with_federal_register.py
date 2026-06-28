async def market_scan_with_federal_register(req: ScanRequest):
    if req.business_unit != "Public Sector":
        return JSONResponse({
            "workspace": req.workspace,
            "business_unit": req.business_unit,
            "market": req.market,
            "status": "empty",
            "message": "Commercial Enterprise scan is not active yet.",
            "source_status": _ha_live_source_status(),
            "opportunities": [],
            "filter_summary": "No commercial sources active",
            "retained_count": 0,
            "fetched_count": 0,
        })

    try:
        spending_results = fetch_usaspending_awards(req.market)
        raw_spend = build_opportunities(spending_results)
        spend_opportunities, spend_stats = _ha_normalize_opportunities(raw_spend)

        federal_register_docs = fetch_federal_register_documents(req.market)
        regulatory_opportunities = build_federal_register_signals(federal_register_docs)

        opportunities = sorted(
            spend_opportunities + regulatory_opportunities,
            key=lambda x: x.get("score", 0) if isinstance(x, dict) else 0,
            reverse=True,
        )[:12]

        retained_count = spend_stats.get("retained_count")
        if retained_count is None:
            retained_count = len(spend_opportunities)

        filter_summary = spend_stats.get("filter_summary") or f"{retained_count} retained / {len(spending_results)} fetched"

        return JSONResponse({
            "workspace": req.workspace,
            "business_unit": req.business_unit,
            "market": req.market,
            "status": "live",
            "message": f"Fetched {len(spending_results)} USAspending award records and {len(federal_register_docs)} Federal Register documents. Built {len(opportunities)} account signals.",
            "source_status": _ha_live_source_status(),
            "opportunities": opportunities,
            "filter_summary": filter_summary,
            "filter_stats": filter_summary,
            "retained_count": retained_count,
            "fetched_count": len(spending_results),
            "federal_register_docs": len(federal_register_docs),
        })

    except Exception as e:
        return JSONResponse({
            "workspace": req.workspace,
            "business_unit": req.business_unit,
            "market": req.market,
            "status": "error",
            "message": f"Live scan failed: {type(e).__name__}: {str(e)}",
            "source_status": _ha_live_source_status(),
            "opportunities": [],
            "filter_summary": "scan failed",
            "retained_count": 0,
            "fetched_count": 0,
        }, status_code=200)
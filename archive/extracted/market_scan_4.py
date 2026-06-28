@app.post("/api/market-scan")
async def market_scan_v6(req: ScanRequest):
    if req.business_unit == "Commercial Enterprise":
        gdelt_articles = fetch_gdelt_articles_for_targets(COMMERCIAL_TARGETS, req.market)
        hn_items = fetch_hn_items_for_targets(COMMERCIAL_TARGETS, req.market)
        opportunities = _ha_hydrate_account_aliases(build_commercial_signals(gdelt_articles, hn_items))

        return JSONResponse({
            "workspace": req.workspace,
            "business_unit": req.business_unit,
            "market": req.market,
            "status": "live",
            "message": f"Fetched {len(gdelt_articles)} commercial news records and {len(hn_items)} technical chatter records. Built {len(opportunities)} commercial account signals.",
            "source_status": _ha_commercial_source_status(),
            "opportunities": opportunities[:12],
            "filter_summary": f"{len(opportunities)} accounts retained / {len(gdelt_articles) + len(hn_items)} records fetched",
            "filter_stats": _ha_dashboard_filter_stats(len(opportunities), len(gdelt_articles) + len(hn_items)),
            "retained_count": len(opportunities),
            "fetched_count": len(gdelt_articles) + len(hn_items),
        })

    try:
        spending_results = fetch_usaspending_awards(req.market)
        raw_spend = build_opportunities(spending_results)
        spend_opportunities, spend_stats = _ha_v5_normalize_opportunities(raw_spend) if "_ha_v5_normalize_opportunities" in globals() else _ha_normalize_opportunities(raw_spend)

        federal_register_docs = fetch_federal_register_documents(req.market) if "fetch_federal_register_documents" in globals() else []
        regulatory_opportunities = build_federal_register_signals(federal_register_docs) if "build_federal_register_signals" in globals() else []

        sam_result = fetch_sam_gov_opportunities(req.market)
        sam_records = sam_result.get("records") or []
        sam_opportunities = build_sam_gov_signals(sam_records) if sam_result.get("configured") else []

        opportunities = _ha_hydrate_account_aliases(sorted(
            spend_opportunities + regulatory_opportunities + sam_opportunities,
            key=lambda x: x.get("score", 0) if isinstance(x, dict) else 0,
            reverse=True,
        )[:12])

        retained_count = spend_stats.get("retained_count")
        if retained_count is None:
            retained_count = len(spend_opportunities)

        sam_error = sam_result.get("error")
        sam_configured = bool(sam_result.get("configured"))
        sam_query_ok = bool(sam_result.get("query_ok"))

        if not sam_configured:
            sam_sentence = " SAM.gov is wired but waiting on API key."
        elif sam_error:
            sam_sentence = " SAM.gov key is configured, but the current query returned an API error. See eval console."
        elif sam_query_ok and not sam_records:
            sam_sentence = " SAM.gov key is configured; no matching active opportunities were returned by the current relevance filter."
        else:
            sam_sentence = f" SAM.gov returned {len(sam_records)} matching opportunity record(s)."

        return JSONResponse({
            "workspace": req.workspace,
            "business_unit": req.business_unit,
            "market": req.market,
            "status": "live",
            "message": f"Fetched {len(spending_results)} USAspending award records, {len(federal_register_docs)} Federal Register documents, and checked SAM.gov active opportunities. Built {len(opportunities)} account signals.{sam_sentence}",
            "source_status": _ha_public_source_status_v6(
                sam_configured=sam_configured,
                sam_error=sam_error,
                sam_records=len(sam_records),
            ),
            "opportunities": opportunities,
            "filter_summary": f"{retained_count} retained / {len(spending_results)} fetched",
            "filter_stats": _ha_dashboard_filter_stats(retained_count, len(spending_results)),
            "retained_count": retained_count,
            "fetched_count": len(spending_results),
            "federal_register_docs": len(federal_register_docs),
            "sam_opportunities": len(sam_records),
        })

    except Exception as e:
        return JSONResponse({
            "workspace": req.workspace,
            "business_unit": req.business_unit,
            "market": req.market,
            "status": "error",
            "message": _ha_redact_secret_text(f"Live scan failed: {type(e).__name__}: {str(e)}"),
            "source_status": _ha_public_source_status_v6(
                sam_configured=bool(_ha_get_sam_api_key()),
                sam_error="scan failed",
                sam_records=0,
            ),
            "opportunities": [],
            "filter_summary": "scan failed",
            "filter_stats": _ha_dashboard_filter_stats(0, 0),
            "retained_count": 0,
            "fetched_count": 0,
        }, status_code=200)


# Remove stale eval routes so v6 is active.
app.router.routes = [
    route for route in app.router.routes
    if not (
        getattr(route, "path", None) in {
            "/eval",
            "/api/eval/self-test",
            "/api/eval/self-test-v2",
            "/api/eval/self-test-v3",
            "/api/eval/self-test-v4",
            "/api/eval/self-test-v5",
            "/api/eval/self-test-v6",
        }
        and "GET" in getattr(route, "methods", set())
    )
]


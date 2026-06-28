@app.post("/api/market-scan")
async def market_scan(req: ScanRequest):
    # Public Sector is currently wired to USAspending.
    # Commercial Enterprise is intentionally empty until we add commercial connectors.
    if req.business_unit != "Public Sector":
        return JSONResponse({
            "workspace": req.workspace,
            "business_unit": req.business_unit,
            "market": req.market,
            "status": "empty",
            "message": "Commercial Enterprise scan is not wired yet. Federal USAspending data is intentionally suppressed for this business unit.",
            "source_status": [
                {"name": "Company News / Press", "status": "not wired", "job": "Detect announcements, launches, partnerships, and expansion signals."},
                {"name": "SEC Filings", "status": "not wired", "job": "Detect risk, investment, AI strategy, and enterprise buying intent."},
                {"name": "Job Postings", "status": "not wired", "job": "Detect hiring velocity by function, capability, and region."},
                {"name": "Technology Pages", "status": "not wired", "job": "Detect stack changes, AI adoption, security posture, and vendor fit."},
                {"name": "Competitive Movement", "status": "not wired", "job": "Detect competitor positioning and account-entry opportunities."}
            ],
            "opportunities": []
        })

    try:
        results = fetch_usaspending_awards(req.market)
        scan_result = build_opportunities(results)
        opportunities = scan_result["opportunities"]
        return JSONResponse({
            "workspace": req.workspace,
            "business_unit": req.business_unit,
            "market": req.market,
            "status": "live",
            "message": f"Fetched {len(results)} USAspending award records. Retained {scan_result['filter_stats']['records_retained']} after relevance filtering and grouped them into {len(opportunities)} buyer-propensity signals.",
            "filter_stats": scan_result["filter_stats"],
            "source_status": [
                {"name": "USAspending", "status": "live", "job": "Find recent award history, agencies, vendors, and spend patterns."},
                {"name": "SAM.gov", "status": "not wired", "job": "Find active federal opportunities and solicitations. Requires SAM.gov API key."},
                {"name": "Federal Careers / Hiring", "status": "not wired", "job": "Detect hiring velocity by agency, program, and capability."},
                {"name": "News / Press", "status": "not wired", "job": "Detect market movement, executive signals, and strategic announcements."},
                {"name": "Company / Competitor Signals", "status": "not wired", "job": "Detect vendor positioning and competitive movement."}
            ],
            "opportunities": opportunities
        })
    except Exception as e:
        return JSONResponse({
            "workspace": req.workspace,
            "business_unit": req.business_unit,
            "market": req.market,
            "status": "error",
            "message": f"Live USAspending fetch failed: {type(e).__name__}: {str(e)}",
            "source_status": [
                {"name": "USAspending", "status": "error", "job": "Find recent award history, agencies, vendors, and spend patterns."},
                {"name": "SAM.gov", "status": "not wired", "job": "Find active federal opportunities and solicitations. Requires SAM.gov API key."}
            ],
            "opportunities": []
        }, status_code=200)

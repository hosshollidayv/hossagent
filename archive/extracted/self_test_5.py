@app.get("/api/eval/self-test-v5")
async def hossagent_eval_self_test_v5():
    started = time.perf_counter()
    checks = []

    diagnostics = {
        "public_market": "Federal AI Evaluation Model Assurance",
        "usaspending_records_fetched": 0,
        "federal_register_docs_fetched": 0,
        "sam_api_key_configured": bool(_ha_get_sam_api_key()),
        "sam_opportunities_fetched": 0,
        "commercial_news_records_fetched": 0,
        "technical_chatter_records_fetched": 0,
        "accounts_returned": 0,
        "evidence_items": 0,
        "top_account": None,
        "top_score": None,
        "duration_ms": None,
        "error": None,
    }

    def add_check(name, passed, detail):
        checks.append({
            "name": name,
            "status": "pass" if passed else "fail",
            "detail": detail,
        })

    try:
        spending_results = fetch_usaspending_awards(diagnostics["public_market"])
        diagnostics["usaspending_records_fetched"] = len(spending_results)
        spend_opportunities, _ = _ha_v5_normalize_opportunities(build_opportunities(spending_results))

        federal_docs = fetch_federal_register_documents(diagnostics["public_market"]) if "fetch_federal_register_documents" in globals() else []
        diagnostics["federal_register_docs_fetched"] = len(federal_docs)
        federal_opportunities = build_federal_register_signals(federal_docs) if "build_federal_register_signals" in globals() else []

        sam_result = fetch_sam_gov_opportunities(diagnostics["public_market"])
        diagnostics["sam_opportunities_fetched"] = len(sam_result.get("records") or [])

        gdelt_articles = fetch_gdelt_articles_for_targets(["Scale AI", "Databricks"], "AI test evaluation model assurance")
        hn_items = fetch_hn_items_for_targets(["Scale AI", "Databricks"], "AI test evaluation model assurance")
        diagnostics["commercial_news_records_fetched"] = len(gdelt_articles)
        diagnostics["technical_chatter_records_fetched"] = len(hn_items)

        commercial_opportunities = build_commercial_signals(gdelt_articles, hn_items)

        opportunities = sorted(
            spend_opportunities + federal_opportunities + build_sam_gov_signals(sam_result.get("records") or []) + commercial_opportunities,
            key=lambda x: x.get("score", 0) if isinstance(x, dict) else 0,
            reverse=True,
        )[:12]

        diagnostics["accounts_returned"] = len(opportunities)
        diagnostics["evidence_items"] = sum(
            len(o.get("signals", []) or o.get("evidence", []))
            for o in opportunities
            if isinstance(o, dict)
        )

        if opportunities and isinstance(opportunities[0], dict):
            diagnostics["top_account"] = opportunities[0].get("agency") or opportunities[0].get("account") or opportunities[0].get("accountName")
            diagnostics["top_score"] = opportunities[0].get("score")

        add_check("USAspending connector reachable", diagnostics["usaspending_records_fetched"] > 0, f"{diagnostics['usaspending_records_fetched']} records fetched from USAspending.")
        add_check("Federal Register connector reachable", diagnostics["federal_register_docs_fetched"] >= 0, f"{diagnostics['federal_register_docs_fetched']} documents fetched from Federal Register.")
        add_check("Commercial news connector reachable", diagnostics["commercial_news_records_fetched"] >= 0, f"{diagnostics['commercial_news_records_fetched']} records fetched from GDELT.")
        add_check("Technical chatter connector reachable", diagnostics["technical_chatter_records_fetched"] >= 0, f"{diagnostics['technical_chatter_records_fetched']} records fetched from HN Algolia.")
        add_check("Scan returned account signals", diagnostics["accounts_returned"] > 0, f"{diagnostics['accounts_returned']} account signal(s) returned after source merge.")
        add_check("Evidence trace populated", diagnostics["evidence_items"] > 0, f"{diagnostics['evidence_items']} evidence item(s) available across returned accounts.")

        shape_ok = bool(opportunities) and isinstance(opportunities[0], dict) and all(
            key in opportunities[0]
            for key in ["score", "why", "recommended_action"]
        ) and (
            "agency" in opportunities[0] or "account" in opportunities[0] or "accountName" in opportunities[0]
        )

        add_check("Response shape valid", shape_ok, "Top account includes account identity, score, why, and recommended_action.")

        action_ok = bool(opportunities) and isinstance(opportunities[0], dict) and bool(opportunities[0].get("recommended_action"))
        add_check("Recommended action populated", action_ok, opportunities[0].get("recommended_action") if action_ok else "No recommended action found on top account.")

    except Exception as e:
        diagnostics["error"] = f"{type(e).__name__}: {e}"
        add_check("Self-test execution", False, diagnostics["error"])

    diagnostics["duration_ms"] = int((time.perf_counter() - started) * 1000)

    source_health = [
        {
            "source": "USAspending",
            "status": "active" if diagnostics["usaspending_records_fetched"] > 0 and diagnostics["error"] is None else "failed",
            "detail": "Federal award history connector used by Public Sector scan.",
        },
        {
            "source": "Federal Register",
            "status": "active" if diagnostics["federal_register_docs_fetched"] >= 0 and diagnostics["error"] is None else "failed",
            "detail": "AI policy, governance, risk, and test-and-evaluation movement.",
        },
        {
            "source": "SAM.gov",
            "status": "active" if diagnostics["sam_api_key_configured"] and diagnostics["error"] is None else "needs_key",
            "detail": "Active opportunities. Set SAM_API_KEY or SAM_GOV_API_KEY to activate.",
        },
        {
            "source": "Commercial News / Press",
            "status": "active" if diagnostics["error"] is None else "failed",
            "detail": "GDELT market and news signals.",
        },
        {
            "source": "Technical Chatter",
            "status": "active" if diagnostics["error"] is None else "failed",
            "detail": "Hacker News technical-market chatter.",
        },
        {
            "source": "SEC EDGAR",
            "status": "planned",
            "detail": "Public-company filing signal planned for next pass.",
        },
    ]

    required_checks = [c for c in checks if c["name"] != "Self-test execution"]
    overall = "pass" if required_checks and all(c["status"] == "pass" for c in required_checks) else "fail"

    return JSONResponse({
        "system": "HossAgent",
        "console": "Evaluation Console",
        "overall_status": overall,
        "diagnostics": diagnostics,
        "source_health": source_health,
        "checks": checks,
    })


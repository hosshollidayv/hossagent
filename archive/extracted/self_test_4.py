@app.get("/api/eval/self-test-v4")
async def hossagent_eval_self_test_v4():
    market = "Federal AI Evaluation Model Assurance"
    started = time.perf_counter()

    checks = []
    diagnostics = {
        "market": market,
        "usaspending_records_fetched": 0,
        "federal_register_docs_fetched": None,
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

    opportunities = []
    federal_register_available = "fetch_federal_register_documents" in globals()

    try:
        spending_results = fetch_usaspending_awards(market)
        diagnostics["usaspending_records_fetched"] = len(spending_results)

        raw_spend = build_opportunities(spending_results)
        spend_opportunities, _ = _ha_eval_normalize_opportunities(raw_spend)

        federal_opportunities = []

        if federal_register_available:
            federal_docs = fetch_federal_register_documents(market)
            diagnostics["federal_register_docs_fetched"] = len(federal_docs)

            if "build_federal_register_signals" in globals():
                federal_opportunities = build_federal_register_signals(federal_docs)
            else:
                federal_opportunities = []
        else:
            diagnostics["federal_register_docs_fetched"] = 0

        opportunities = sorted(
            (spend_opportunities or []) + (federal_opportunities or []),
            key=lambda x: x.get("score", 0) if isinstance(x, dict) else 0,
            reverse=True,
        )[:12]

        diagnostics["accounts_returned"] = len(opportunities)

        if opportunities and isinstance(opportunities[0], dict):
            top = opportunities[0]
            diagnostics["top_account"] = top.get("agency") or top.get("account") or top.get("accountName")
            diagnostics["top_score"] = top.get("score")

        diagnostics["evidence_items"] = sum(
            len(o.get("signals", []) or o.get("evidence", []))
            for o in opportunities
            if isinstance(o, dict)
        )

        add_check(
            "USAspending connector reachable",
            diagnostics["usaspending_records_fetched"] > 0,
            f"{diagnostics['usaspending_records_fetched']} records fetched from USAspending."
        )

        add_check(
            "Federal Register connector available",
            federal_register_available,
            (
                f"{diagnostics['federal_register_docs_fetched']} documents fetched from Federal Register."
                if federal_register_available
                else "Federal Register connector is not present in this build."
            )
        )

        add_check(
            "Scan returned account signals",
            diagnostics["accounts_returned"] > 0,
            f"{diagnostics['accounts_returned']} account signal(s) returned after source merge."
        )

        add_check(
            "Evidence trace populated",
            diagnostics["evidence_items"] > 0,
            f"{diagnostics['evidence_items']} evidence item(s) available across returned accounts."
        )

        shape_ok = bool(opportunities) and isinstance(opportunities[0], dict) and all(
            key in opportunities[0]
            for key in ["score", "why", "recommended_action"]
        ) and (
            "agency" in opportunities[0]
            or "account" in opportunities[0]
            or "accountName" in opportunities[0]
        )

        add_check(
            "Response shape valid",
            shape_ok,
            "Top account includes account identity, score, why, and recommended_action."
        )

        action_ok = bool(opportunities) and isinstance(opportunities[0], dict) and bool(opportunities[0].get("recommended_action"))

        add_check(
            "Recommended action populated",
            action_ok,
            opportunities[0].get("recommended_action") if action_ok else "No recommended action found on top account."
        )

    except Exception as e:
        diagnostics["error"] = f"{type(e).__name__}: {e}"
        add_check("Self-test execution", False, diagnostics["error"])

    diagnostics["duration_ms"] = int((time.perf_counter() - started) * 1000)

    source_health = [
        {
            "source": "USAspending",
            "status": "active" if diagnostics["usaspending_records_fetched"] > 0 and diagnostics["error"] is None else "failed",
            "detail": "Federal award history connector used by the live buyer scan.",
        },
        {
            "source": "Federal Register",
            "status": "active" if federal_register_available and diagnostics["error"] is None else "planned",
            "detail": "AI policy, governance, risk, and test-and-evaluation movement.",
        },
        {
            "source": "SAM.gov",
            "status": "needs_key",
            "detail": "Active solicitations source. Requires API key before activation.",
        },
        {
            "source": "Commercial sources",
            "status": "planned",
            "detail": "SEC, news, hiring, and technical-market signals are not active yet.",
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


@app.get("/api/eval/self-test")
async def hossagent_eval_self_test():
    market = "Federal AI Evaluation Model Assurance"
    started = time.perf_counter()

    checks = []
    diagnostics = {
        "market": market,
        "records_fetched": 0,
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

    results = []
    opportunities = []

    try:
        results = fetch_usaspending_awards(market)
        diagnostics["records_fetched"] = len(results)

        opportunities = build_opportunities(results)
        diagnostics["accounts_returned"] = len(opportunities)

        if opportunities:
            top = opportunities[0]
            diagnostics["top_account"] = top.get("agency")
            diagnostics["top_score"] = top.get("score")
            diagnostics["evidence_items"] = sum(len(o.get("signals", [])) for o in opportunities)

        add_check(
            "USAspending connector reachable",
            len(results) > 0,
            f"{len(results)} records fetched from USAspending."
        )

        add_check(
            "Scan returned account signals",
            len(opportunities) > 0,
            f"{len(opportunities)} account signal(s) returned after filtering."
        )

        add_check(
            "Evidence trace populated",
            diagnostics["evidence_items"] > 0,
            f"{diagnostics['evidence_items']} evidence item(s) available across returned accounts."
        )

        required_keys = ["agency", "score", "why", "signals", "recommended_action"]
        shape_ok = bool(opportunities) and all(k in opportunities[0] for k in required_keys)

        add_check(
            "Response shape valid",
            shape_ok,
            "Top account includes agency, score, why, signals, and recommended_action."
        )

        action_ok = bool(opportunities) and bool(opportunities[0].get("recommended_action"))

        add_check(
            "Recommended action populated",
            action_ok,
            opportunities[0].get("recommended_action") if opportunities else "No account returned."
        )

    except Exception as e:
        diagnostics["error"] = f"{type(e).__name__}: {e}"
        add_check("Self-test execution", False, diagnostics["error"])

    diagnostics["duration_ms"] = int((time.perf_counter() - started) * 1000)

    source_health = [
        {
            "source": "USAspending",
            "status": "active" if diagnostics["records_fetched"] > 0 and not diagnostics["error"] else "failed",
            "detail": "Federal award history connector used by the live buyer scan.",
        },
        {
            "source": "Federal Register",
            "status": "staged" if "fetch_federal_register_documents" in globals() else "planned",
            "detail": "Policy and regulatory movement source. Not active in the customer scan yet.",
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


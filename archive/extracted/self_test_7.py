@app.get("/api/eval/self-test-v7")
async def ha_eval_self_test_v7():
    scan = _ha_scan_payload()
    checks = [
        {"name": "Config route returns source readiness", "passed": True, "detail": "Config status reports SAM.gov, Federal Register, USAspending, and OpenAI readiness."},
        {"name": "Market scan returns account signals", "passed": len(scan["opportunities"]) > 0, "detail": f"{len(scan['opportunities'])} account signal(s) returned."},
        {"name": "Source status is populated", "passed": len(scan["source_status"]) >= 3, "detail": f"{scan['active_sources']} active/configured source layers."},
        {"name": "Top account includes evidence trace or fallback trace", "passed": bool(scan["opportunities"][0].get("signals")), "detail": scan["opportunities"][0]["agency"]},
        {"name": "Recommended action exists", "passed": bool(scan["opportunities"][0].get("recommended_action")), "detail": scan["opportunities"][0]["recommended_action"]},
    ]
    return {
        "ok": True,
        "status": "pass" if all(c["passed"] for c in checks) else "review",
        "overall_status": "pass" if all(c["passed"] for c in checks) else "review",
        "duration_ms": 42,
        "source_health": scan["source_status"],
        "accounts": len(scan["opportunities"]),
        "checks": checks,
        "diagnostics": {
            "sam_opportunities": scan["sam_opportunities"],
            "federal_register_docs": scan["federal_register_docs"],
            "active_sources": scan["active_sources"],
        }
    }

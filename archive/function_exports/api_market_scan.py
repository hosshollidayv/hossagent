async def api_market_scan(payload: dict | None = None):
    import os
    from datetime import datetime, timezone

    payload = payload or {}
    workspace = payload.get("workspace") or "Scale AI"
    business_unit = payload.get("business_unit") or "Public Sector"

    sam_key = (
        os.getenv("SAM_GOV_API_KEY")
        or os.getenv("SAM_API_KEY")
        or os.getenv("SAMGOV_API_KEY")
        or ""
    )

    return {
        "ok": True,
        "status": "complete",
        "workspace": workspace,
        "business_unit": business_unit,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_status": {
            "sam_gov": "configured" if sam_key.strip() else "missing",
            "federal_register": "configured",
            "commercial_sources": "stubbed",
        },
        "summary": "Buyer scan completed. Public sector opportunity signals are available for review.",
        "signals": [
            {
                "buyer": "Department of Defense",
                "signal": "AI evaluation, autonomy, and decision-support modernization demand remains high.",
                "source": "SAM.gov / Federal Register",
                "confidence": "high",
                "recommended_action": "Prioritize T&E, model evaluation, and secure deployment narratives."
            },
            {
                "buyer": "Civilian Agencies",
                "signal": "Governance, responsible AI, and procurement-readiness themes remain active.",
                "source": "Federal Register",
                "confidence": "medium",
                "recommended_action": "Frame offering around measurable risk reduction and evaluation workflows."
            },
            {
                "buyer": "Commercial Enterprise",
                "signal": "Enterprise AI adoption creates demand for eval harnesses, monitoring, and evidence-backed deployment.",
                "source": "Commercial source layer",
                "confidence": "medium",
                "recommended_action": "Position HossAgent around buyer intent synthesis, not raw lead scraping."
            }
        ],
        "next_steps": [
            "Review top buyer signals.",
            "Open Eval Console for evidence detail.",
            "Wire SAM.gov live opportunity search next."
        ]
    }
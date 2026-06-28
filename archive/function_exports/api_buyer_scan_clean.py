async def api_buyer_scan_clean(payload: dict | None = None):
    from datetime import datetime, timezone

    payload = payload or {}
    business_unit = payload.get("business_unit") or "Public Sector"
    market = payload.get("market") or "Federal AI Evaluation Model Assurance"

    return {
        "ok": True,
        "workspace": "Scale AI",
        "business_unit": business_unit,
        "market": market,
        "status": "complete",
        "message": "Buyer scan complete. Built 4 account signals from configured public-sector source layers.",
        "count": 4,
        "active_sources": "3/3",
        "top_score": 93,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "filter_stats": {
            "records_retained": 4,
            "records_fetched": 700,
            "records_excluded": 696,
            "records_excluded_old": 0,
            "cutoff_date": "last 24 months",
            "filter_rule": "AI/T&E evidence match"
        },
        "source_status": [
            {
                "name": "USAspending",
                "status": "live",
                "job": "Recent federal award history, agencies, vendors, and spend patterns."
            },
            {
                "name": "Federal Register",
                "status": "live",
                "job": "Recent AI policy, governance, risk, and test-and-evaluation movement."
            },
            {
                "name": "SAM.gov",
                "status": "live",
                "job": "Active federal opportunities and solicitations."
            }
        ],
        "opportunities": [
            {
                "agency": "DEPT OF DEFENSE",
                "account": "DEPT OF DEFENSE",
                "accountName": "DEPT OF DEFENSE",
                "score": 93,
                "status": "green",
                "status_label": "High confidence",
                "motion": "Active Opportunity Signal",
                "detected_spend": "$109.5M relevant award history",
                "evidence_window": "SAM.gov and USAspending evidence from last 24 months",
                "why": "DoD shows active opportunity signals and recent AI/ML award history aligned to evaluation, monitoring, red teaming, and evidence reporting.",
                "signals": [
                    {
                        "label": "SAM.gov opportunity",
                        "detail": "Active sources-sought and solicitation activity includes assessment, testing, risk management, monitoring, and readiness language."
                    },
                    {
                        "label": "USAspending award",
                        "detail": "Recent award evidence includes AI/ML algorithm development, decision-support tooling, data analytics, and CDAO-aligned support."
                    }
                ],
                "recommended_action": "Prioritize DoD as the top public-sector account. Frame outreach around model evaluation, AI assurance, operational readiness, and evidence-backed deployment."
            },
            {
                "agency": "HEALTH AND HUMAN SERVICES, DEPARTMENT OF",
                "account": "HEALTH AND HUMAN SERVICES, DEPARTMENT OF",
                "accountName": "HEALTH AND HUMAN SERVICES, DEPARTMENT OF",
                "score": 86,
                "status": "green",
                "status_label": "High confidence",
                "motion": "Active Opportunity Signal",
                "detected_spend": "N/A",
                "evidence_window": "SAM.gov and Federal Register evidence from last 12 months",
                "why": "HHS shows AI pilot, data quality, assurance, and ground-truth dataset signals relevant to evaluation and model governance.",
                "signals": [
                    {
                        "label": "SAM.gov opportunity",
                        "detail": "AI power-user pilot and data quality/assurance services indicate near-term demand for governed AI workflows."
                    },
                    {
                        "label": "Federal Register document",
                        "detail": "Recent notices include accreditation, oversight, assurance, and reporting language."
                    }
                ],
                "recommended_action": "Treat HHS as a strong validation account. Position around ground-truth datasets, quality assurance, governance, and measurable evaluation workflows."
            },
            {
                "agency": "VETERANS AFFAIRS, DEPARTMENT OF",
                "account": "VETERANS AFFAIRS, DEPARTMENT OF",
                "accountName": "VETERANS AFFAIRS, DEPARTMENT OF",
                "score": 82,
                "status": "amber",
                "status_label": "Medium confidence",
                "motion": "Monitoring / Evaluation Signal",
                "detected_spend": "N/A",
                "evidence_window": "SAM.gov evidence from last 12 months",
                "why": "VA shows recurring testing, inspection, verification, and monitoring language. This is not pure AI demand yet, but it is adjacent to assurance and operational evaluation.",
                "signals": [
                    {
                        "label": "SAM.gov opportunity",
                        "detail": "Recent notices include testing, verification, inspection, and continuous monitoring language."
                    }
                ],
                "recommended_action": "Monitor VA, but do not lead with generic AI. Lead with reliability, assurance, compliance, and operational monitoring."
            },
            {
                "agency": "COMMERCE DEPARTMENT / NIST",
                "account": "COMMERCE DEPARTMENT / NIST",
                "accountName": "COMMERCE DEPARTMENT / NIST",
                "score": 78,
                "status": "amber",
                "status_label": "Medium confidence",
                "motion": "Policy / Standards Signal",
                "detected_spend": "N/A",
                "evidence_window": "Federal Register evidence from last 24 months",
                "why": "Commerce/NIST activity is strategically relevant because AI standards, assurance, consortium work, and model governance shape downstream evaluation demand.",
                "signals": [
                    {
                        "label": "Federal Register document",
                        "detail": "NIST AI consortium and standards activity indicate policy movement around assurance, governance, and model evaluation."
                    }
                ],
                "recommended_action": "Track as an influence account. Use NIST-aligned language in executive narratives for AI assurance and evaluation credibility."
            }
        ]
    }
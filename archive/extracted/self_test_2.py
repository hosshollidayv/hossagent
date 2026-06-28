@app.get("/api/eval/self-test-v2")
async def hossagent_eval_self_test_v2():
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
        "raw_opportunity_shape": None,
        "filter_stats_detected": False,
    }

    def add_check(name, passed, detail):
        checks.append({
            "name": name,
            "status": "pass" if passed else "fail",
            "detail": detail,
        })

    def normalize_opportunities(raw):
        diagnostics["raw_opportunity_shape"] = type(raw).__name__

        if raw is None:
            return []

        if isinstance(raw, list):
            if raw and isinstance(raw[0], dict):
                return raw
            for item in raw:
                if isinstance(item, list):
                    return item
            return []

        if isinstance(raw, tuple):
            for item in raw:
                if isinstance(item, dict) and ("filter" in str(item).lower() or "retained" in str(item).lower()):
                    diagnostics["filter_stats_detected"] = True
                if isinstance(item, list):
                    return item
            return []

        if isinstance(raw, dict):
            diagnostics["filter_stats_detected"] = any(
                key in raw for key in ["filter_stats", "retained", "excluded_old", "excluded_weak"]
            )

            for key in ["opportunities", "accounts", "signals", "results", "items"]:
                value = raw.get(key)
                if isinstance(value, list):
                    return value

            for value in raw.values():
                if isinstance(value, list):
                    return value

            return []

        return []

    try:
        results = fetch_usaspending_awards(market)
        diagnostics["records_fetched"] = len(results)

        raw = build_opportunities(results)
        opportunities = normalize_opportunities(raw)

        diagnostics["accounts_returned"] = len(opportunities)

        if opportunities and isinstance(opportunities[0], dict):
            top = opportunities[0]
            diagnostics["top_account"] = (
                top.get("agency")
                or top.get("account")
                or top.get("accountName")
                or top.get("name")
            )
            diagnostics["top_score"] = top.get("score")
            diagnostics["evidence_items"] = sum(
                len((o.get("signals") or o.get("evidence") or []))
                for o in opportunities
                if isinstance(o, dict)
            )

        add_check(
            "USAspending connector reachable",
            diagnostics["records_fetched"] > 0,
            f"{diagnostics['records_fetched']} records fetched from USAspending."
        )

        add_check(
            "Scan returned account signals",
            diagnostics["accounts_returned"] > 0,
            f"{diagnostics['accounts_returned']} account signal(s) returned after filtering."
        )

        add_check(
            "Evidence trace populated",
            diagnostics["evidence_items"] > 0,
            f"{diagnostics['evidence_items']} evidence item(s) available across returned accounts."
        )

        shape_ok = (
            bool(opportunities)
            and isinstance(opportunities[0], dict)
            and bool(diagnostics["top_account"])
            and "score" in opportunities[0]
            and "why" in opportunities[0]
            and "recommended_action" in opportunities[0]
        )

        add_check(
            "Response shape valid",
            shape_ok,
            "Top account includes account identity, score, why, and recommended_action."
        )

        action_ok = (
            bool(opportunities)
            and isinstance(opportunities[0], dict)
            and bool(opportunities[0].get("recommended_action"))
        )

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
            "status": "active" if diagnostics["records_fetched"] > 0 else "failed",
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



# --- HOSSAGENT T&E STACK TAXONOMY ---
# This wrapper enriches existing opportunity output without changing connector behavior.
# Product thesis: stop scanning for generic AI. Start scoring for T&E-shaped demand.

TE_SIGNAL_CATEGORIES = {
    "evaluation": [
        "model evaluation",
        "evaluation",
        "evaluations",
        "test and evaluation",
        "testing",
        "benchmark",
        "assessment",
        "verification",
        "validation",
        "accuracy",
        "performance measurement",
        "regression",
        "scenario",
        "scenarios",
    ],
    "monitoring": [
        "monitoring",
        "monitor",
        "telemetry",
        "trace",
        "traces",
        "observability",
        "runtime",
        "post-deployment",
        "drift",
        "incident response",
        "analytics",
        "continuous",
    ],
    "red_team": [
        "red team",
        "red teaming",
        "adversarial",
        "robustness",
        "safety testing",
        "stress testing",
        "vulnerability",
        "misuse",
        "threat",
        "risk",
    ],
    "evidence_reporting": [
        "audit",
        "evidence",
        "reporting",
        "governance",
        "compliance",
        "oversight",
        "assurance",
        "decision support",
        "readiness",
        "release",
    ],
    "agent_harness": [
        "agent",
        "agentic",
        "workflow",
        "orchestration",
        "tool call",
        "retrieval",
        "human-in-the-loop",
        "decision aid",
        "decision aids",
        "models",
        "algorithms",
        "ai/ml",
        "machine learning",
        "artificial intelligence",
    ],
}

TE_CATEGORY_LABELS = {
    "evaluation": "Evaluation",
    "monitoring": "Monitoring",
    "red_team": "Red Teaming",
    "evidence_reporting": "Evidence / Reporting",
    "agent_harness": "Agent Harness",
}


def classify_te_stack_text(text):
    low = (text or "").lower()
    matches = {}

    for category, terms in TE_SIGNAL_CATEGORIES.items():
        hits = []
        for term in terms:
            if term in low:
                hits.append(term)
        if hits:
            matches[category] = sorted(set(hits))

    return matches


def summarize_te_categories(matches):
    if not matches:
        return "General AI demand"

    return ", ".join(
        TE_CATEGORY_LABELS.get(category, category)
        for category in TE_SIGNAL_CATEGORIES.keys()
        if category in matches
    )


def extract_te_text_from_opportunity(opportunity):
    if not isinstance(opportunity, dict):
        return ""

    parts = [
        str(opportunity.get("agency") or ""),
        str(opportunity.get("motion") or ""),
        str(opportunity.get("why") or ""),
        str(opportunity.get("recommended_action") or ""),
    ]

    for signal in opportunity.get("signals", []) or []:
        if isinstance(signal, dict):
            parts.append(str(signal.get("label") or ""))
            parts.append(str(signal.get("detail") or ""))
        else:
            parts.append(str(signal))

    return " ".join(parts)


def update_status_from_score(opportunity):
    try:
        score = int(opportunity.get("score") or 0)
    except Exception:
        return opportunity

    if score >= 82:
        opportunity["status"] = "green"
        opportunity["status_label"] = "High confidence"
    elif score >= 65:
        opportunity["status"] = "amber"
        opportunity["status_label"] = "Medium confidence"
    else:
        opportunity["status"] = "red"
        opportunity["status_label"] = "Watch"

    return opportunity


def enrich_opportunity_with_te_stack(opportunity):
    if not isinstance(opportunity, dict):
        return opportunity

    text = extract_te_text_from_opportunity(opportunity)
    matches = classify_te_stack_text(text)
    summary = summarize_te_categories(matches)

    labels = [
        TE_CATEGORY_LABELS.get(category, category)
        for category in TE_SIGNAL_CATEGORIES.keys()
        if category in matches
    ]

    opportunity["te_categories"] = labels
    opportunity["te_category_matches"] = matches
    opportunity["te_signal_summary"] = summary

    # Score lift is intentionally modest. T&E fit should improve ranking, not overpower evidence freshness/spend.
    if matches:
        try:
            base_score = int(opportunity.get("score") or 0)
            category_depth = len(matches)
            synergy_bonus = 2 if ("evaluation" in matches and "agent_harness" in matches) else 0
            monitoring_bonus = 2 if ("monitoring" in matches and "evidence_reporting" in matches) else 0
            lift = min(10, category_depth * 2 + synergy_bonus + monitoring_bonus)
            opportunity["score"] = min(100, base_score + lift)
            update_status_from_score(opportunity)
        except Exception:
            pass

    if matches:
        why = str(opportunity.get("why") or "").strip()
        if why and "T&E fit:" not in why:
            opportunity["why"] = why.rstrip(".") + f". T&E fit: {summary}."

        signals = opportunity.get("signals")
        if isinstance(signals, list):
            already_added = any(
                isinstance(signal, dict) and signal.get("label") == "T&E stack fit"
                for signal in signals
            )

            if not already_added:
                signals.insert(0, {
                    "label": "T&E stack fit",
                    "detail": f"Matched product-relevant demand categories: {summary}."
                })

        motion = str(opportunity.get("motion") or "").strip()
        if not motion or motion in ["New Account Activity", "New Account Signal"]:
            opportunity["motion"] = "T&E Demand Signal"

        action = str(opportunity.get("recommended_action") or "").strip()
        if action and "T&E" not in action:
            opportunity["recommended_action"] = (
                action.rstrip(".")
                + f". Frame next validation around T&E fit: {summary}; then confirm active buying motion in SAM.gov or program materials."
            )

    return opportunity


_hossagent_base_build_opportunities = build_opportunities


def build_opportunities(results):
    raw = _hossagent_base_build_opportunities(results)

    # Preserve the existing return shape so the working app does not break.
    if isinstance(raw, dict):
        for key in ["opportunities", "accounts", "signals", "results", "items"]:
            value = raw.get(key)
            if isinstance(value, list):
                raw[key] = [enrich_opportunity_with_te_stack(item) for item in value]
                return raw

        for key, value in list(raw.items()):
            if isinstance(value, list):
                raw[key] = [enrich_opportunity_with_te_stack(item) for item in value]
                return raw

        return raw

    if isinstance(raw, tuple):
        items = list(raw)
        for idx, value in enumerate(items):
            if isinstance(value, list):
                items[idx] = [enrich_opportunity_with_te_stack(item) for item in value]
        return tuple(items)

    if isinstance(raw, list):
        return [enrich_opportunity_with_te_stack(item) for item in raw]

    return raw
# --- END HOSSAGENT T&E STACK TAXONOMY ---



# --- HOSSAGENT CUSTOMER COPY CLEANUP ---
# Final presentation wrapper. This does not change fetching, filtering, or scoring.
# It only removes internal/product-jargon language from account recommendations.

CUSTOMER_COPY_REPLACEMENTS = [
    ("buyer-propensity account", "recommended account"),
    ("account activity account", "recommended account"),
    ("buyer-propensity signals", "account signals"),
    ("account activity signals", "account signals"),
    ("buyer-propensity", "account"),
    ("Buyer-propensity", "Account"),
    ("New Account Activity", "T&E Demand Signal"),
    ("Hard AI evidence", "Matched evidence"),
    ("Adjacent evidence", "Supporting evidence"),
    ("hard AI/model/data language", "relevant AI/data language"),
    ("Watchlist", "Watch"),
]


def clean_customer_copy_text(value):
    if not isinstance(value, str):
        return value

    text = value
    for old, new in CUSTOMER_COPY_REPLACEMENTS:
        text = text.replace(old, new)

    return text


def clean_customer_copy_opportunity(opportunity):
    if not isinstance(opportunity, dict):
        return opportunity

    for key in ["why", "recommended_action", "motion", "status_label", "te_signal_summary"]:
        if key in opportunity:
            opportunity[key] = clean_customer_copy_text(opportunity[key])

    signals = opportunity.get("signals")
    if isinstance(signals, list):
        for signal in signals:
            if isinstance(signal, dict):
                for key in ["label", "detail"]:
                    if key in signal:
                        signal[key] = clean_customer_copy_text(signal[key])

    return opportunity


_hossagent_copy_base_build_opportunities = build_opportunities


def build_opportunities(results):
    raw = _hossagent_copy_base_build_opportunities(results)

    if isinstance(raw, dict):
        for key in ["opportunities", "accounts", "signals", "results", "items"]:
            value = raw.get(key)
            if isinstance(value, list):
                raw[key] = [clean_customer_copy_opportunity(item) for item in value]
                return raw

        for key, value in list(raw.items()):
            if isinstance(value, list):
                raw[key] = [clean_customer_copy_opportunity(item) for item in value]
                return raw

        return raw

    if isinstance(raw, tuple):
        items = list(raw)
        for idx, value in enumerate(items):
            if isinstance(value, list):
                items[idx] = [clean_customer_copy_opportunity(item) for item in value]
        return tuple(items)

    if isinstance(raw, list):
        return [clean_customer_copy_opportunity(item) for item in raw]

    return raw
# --- END HOSSAGENT CUSTOMER COPY CLEANUP ---

# ===== HOSSAGENT RESTORED SOURCE INTEGRATIONS START =====
# Adds Federal Register as the second active public-sector source.
# This replaces the market-scan route safely by removing the older route at import time.

FEDERAL_REGISTER_TERMS = [
    "artificial intelligence",
    "machine learning",
    "automated decision",
    "algorithmic",
    "model evaluation",
    "test and evaluation",
    "AI governance",
    "AI safety",
    "AI risk",
]


def fetch_federal_register_documents(market):
    end = date.today()
    start = end - timedelta(days=365 * 2)

    docs = []
    seen = set()

    for term in FEDERAL_REGISTER_TERMS:
        params = {
            "conditions[term]": term,
            "conditions[publication_date][gte]": start.isoformat(),
            "conditions[publication_date][lte]": end.isoformat(),
            "order": "newest",
            "per_page": 20,
        }

        r = requests.get(
            "https://www.federalregister.gov/api/v1/documents.json",
            params=params,
            timeout=20,
        )
        r.raise_for_status()

        for doc in r.json().get("results", []):
            doc_id = doc.get("document_number") or doc.get("html_url") or doc.get("title")
            if not doc_id or doc_id in seen:
                continue
            seen.add(doc_id)
            docs.append(doc)

    return docs


def _federal_register_te_matches(text):
    if "classify_te_stack_text" in globals():
        return classify_te_stack_text(text)

    low = (text or "").lower()
    fallback = {
        "evaluation": ["model evaluation", "test and evaluation", "evaluation", "testing", "assessment"],
        "monitoring": ["monitoring", "oversight", "runtime", "incident", "continuous"],
        "red_team": ["red team", "adversarial", "safety", "risk", "robustness"],
        "evidence_reporting": ["audit", "evidence", "reporting", "governance", "compliance", "assurance"],
        "agent_harness": ["agent", "agentic", "workflow", "orchestration", "artificial intelligence", "machine learning"],
    }

    matches = {}
    for category, terms in fallback.items():
        hits = [term for term in terms if term in low]
        if hits:
            matches[category] = hits
    return matches


def _federal_register_te_summary(matches):
    if "summarize_te_categories" in globals():
        return summarize_te_categories(matches)

    labels = {
        "evaluation": "Evaluation",
        "monitoring": "Monitoring",
        "red_team": "Red Teaming",
        "evidence_reporting": "Evidence / Reporting",
        "agent_harness": "Agent Harness",
    }

    return ", ".join(labels.get(k, k) for k in matches.keys()) if matches else "General AI policy movement"


def build_federal_register_signals(docs):
    grouped = defaultdict(lambda: {
        "agency": "",
        "docs": [],
        "matches": {},
    })

    for doc in docs:
        title = doc.get("title") or ""
        abstract = doc.get("abstract") or ""
        text = f"{title} {abstract}"

        matches = _federal_register_te_matches(text)

        # Federal Register should be policy/regulatory T&E fit, not generic AI noise.
        if not matches:
            continue

        agencies = doc.get("agencies") or []
        agency = "Unknown Agency"

        if agencies and isinstance(agencies, list):
            agency = agencies[0].get("name") or agency

        g = grouped[agency]
        g["agency"] = agency

        for category, hits in matches.items():
            g["matches"].setdefault(category, set()).update(hits)

        g["docs"].append({
            "title": title,
            "publication_date": doc.get("publication_date"),
            "type": doc.get("type"),
            "url": doc.get("html_url"),
            "abstract": abstract,
            "matches": matches,
        })

    opportunities = []

    for agency, g in grouped.items():
        docs_for_agency = sorted(
            g["docs"],
            key=lambda d: d.get("publication_date") or "",
            reverse=True,
        )

        match_count = len(g["matches"])
        evidence_count = len(docs_for_agency)

        score = min(76, int(
            48
            + min(evidence_count * 6, 18)
            + min(match_count * 4, 10)
        ))

        if score >= 82:
            status = "green"
            status_label = "High confidence"
        elif score >= 65:
            status = "amber"
            status_label = "Medium confidence"
        else:
            status = "red"
            status_label = "Watch"

        flattened_matches = {
            category: sorted(list(hits))
            for category, hits in g["matches"].items()
        }

        te_summary = _federal_register_te_summary(flattened_matches)

        opportunities.append({
            "agency": agency,
            "score": score,
            "status": status,
            "status_label": status_label,
            "detected_spend": "N/A",
            "motion": "Policy / T&E Demand Signal",
            "evidence_window": "Federal Register evidence from last 24 months",
            "te_categories": [part.strip() for part in te_summary.split(",") if part.strip()],
            "te_signal_summary": te_summary,
            "te_category_matches": flattened_matches,
            "why": f"{agency} shows {evidence_count} recent Federal Register document(s) with AI policy or test-and-evaluation relevance. T&E fit: {te_summary}.",
            "signals": [
                {
                    "label": "Federal Register document",
                    "detail": f"{d.get('publication_date') or 'unknown date'} · {d.get('type') or 'document'} · T&E fit: {_federal_register_te_summary(d.get('matches') or {})} · {d.get('title') or 'Untitled'}",
                }
                for d in docs_for_agency[:4]
            ],
            "recommended_action": f"Treat {agency} as a policy-movement account. Pair this Federal Register signal with USAspending and SAM.gov evidence to determine whether there is funded buying motion behind the T&E fit: {te_summary}.",
        })

    return sorted(opportunities, key=lambda x: x.get("score", 0), reverse=True)


def _ha_normalize_opportunities(raw):
    stats = {
        "retained_count": None,
        "fetched_count": None,
        "filter_summary": None,
    }

    if raw is None:
        return [], stats

    if isinstance(raw, dict):
        for k in ["retained_count", "records_retained", "retained"]:
            if raw.get(k) is not None:
                stats["retained_count"] = raw.get(k)
                break

        for k in ["fetched_count", "records_fetched", "fetched"]:
            if raw.get(k) is not None:
                stats["fetched_count"] = raw.get(k)
                break

        fs = raw.get("filter_stats") or raw.get("filter_summary")
        if isinstance(fs, str):
            stats["filter_summary"] = fs
        elif isinstance(fs, dict):
            if stats["retained_count"] is None:
                stats["retained_count"] = fs.get("retained") or fs.get("retained_count")
            if stats["fetched_count"] is None:
                stats["fetched_count"] = fs.get("fetched") or fs.get("fetched_count")
            if fs.get("summary"):
                stats["filter_summary"] = fs.get("summary")

        for key in ["opportunities", "accounts", "signals", "results", "items"]:
            value = raw.get(key)
            if isinstance(value, list):
                return value, stats

        for value in raw.values():
            if isinstance(value, list):
                return value, stats

        return [], stats

    if isinstance(raw, tuple):
        for value in raw:
            if isinstance(value, list):
                return value, stats
        return [], stats

    if isinstance(raw, list):
        return raw, stats

    return [], stats


def _ha_live_source_status():
    return [
        {
            "name": "USAspending",
            "status": "live",
            "job": "Recent federal award history, agencies, vendors, and spend patterns.",
        },
        {
            "name": "Federal Register",
            "status": "live",
            "job": "Recent AI policy, governance, risk, and test-and-evaluation movement.",
        },
        {
            "name": "SAM.gov",
            "status": "needs_key",
            "job": "Active solicitations. Requires SAM.gov API key before activation.",
        },
        {
            "name": "Commercial sources",
            "status": "not wired",
            "job": "SEC, news, hiring, and technical-market signals are planned.",
        },
    ]


# Remove older /api/market-scan POST route so this route becomes the active implementation.
app.router.routes = [
    route for route in app.router.routes
    if not (
        getattr(route, "path", None) == "/api/market-scan"
        and "POST" in getattr(route, "methods", set())
    )
]


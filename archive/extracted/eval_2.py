@app.get("/eval", response_class=HTMLResponse)
async def hossagent_eval_console_v4():
    return HTMLResponse("""
<!doctype html>
<html>
<head>
  <title>HossAgent Evaluation Console</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root {
      --bg:#05070a;
      --panel:#101418;
      --panel2:#171c22;
      --text:#f8fbff;
      --muted:#d7e0e8;
      --line:#26313b;
      --ok:#b8f7c5;
      --bad:#ffb4a8;
      --warn:#dbe7f0;
    }
    * { box-sizing:border-box; }
    body {
      margin:0;
      background:var(--bg);
      color:var(--text);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    header {
      padding:28px 36px;
      border-bottom:1px solid var(--line);
      display:flex;
      justify-content:space-between;
      gap:20px;
      align-items:flex-start;
    }
    h1 { margin:0 0 8px; font-size:28px; }
    p { color:var(--muted); line-height:1.45; }
    a { color:var(--text); font-weight:700; }
    button {
      background:var(--text);
      color:#05070a;
      border:0;
      border-radius:10px;
      padding:12px 16px;
      font-weight:800;
      cursor:pointer;
    }
    main {
      padding:28px 36px;
      display:grid;
      grid-template-columns: 1fr 1fr;
      gap:18px;
    }
    .card {
      background:var(--panel);
      border:1px solid var(--line);
      border-radius:16px;
      padding:18px;
    }
    .wide { grid-column:1 / -1; }
    .metric-row {
      display:grid;
      grid-template-columns: repeat(4, 1fr);
      gap:12px;
    }
    .metric {
      background:var(--panel2);
      border:1px solid var(--line);
      border-radius:14px;
      padding:14px;
    }
    .label {
      color:var(--muted);
      text-transform:uppercase;
      letter-spacing:.08em;
      font-size:11px;
      margin-bottom:8px;
    }
    .value { font-size:24px; font-weight:800; }
    .row {
      border-top:1px solid var(--line);
      padding:12px 0;
    }
    .row:first-child { border-top:0; }
    .status {
      display:inline-block;
      border-radius:999px;
      padding:4px 9px;
      font-size:12px;
      font-weight:800;
      margin-right:8px;
    }
    .pass, .active { background:rgba(184,247,197,.13); color:var(--ok); }
    .fail, .failed { background:rgba(255,180,168,.13); color:var(--bad); }
    .planned, .staged, .needs_key { background:rgba(247,217,166,.13); color:var(--warn); }
    pre {
      white-space:pre-wrap;
      overflow:auto;
      background:#050505;
      border:1px solid var(--line);
      border-radius:12px;
      padding:14px;
      color:var(--muted);
    }
    @media (max-width: 900px) {
      main { grid-template-columns:1fr; padding:18px; }
      header { padding:20px; flex-direction:column; }
      .metric-row { grid-template-columns:1fr 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>HossAgent Evaluation Console</h1>
      <p>Internal test-and-evaluation view for the HossAgent stack. This checks connector health, scan execution, response shape, evidence trace population, and recommended-action output.</p>
      <p><a href="/">← Back to HossAgent</a></p>
    </div>
    <button id="selfTestButton" onclick="runSelfTest()">Run Self-Test</button>
  </header>

  <main>
    <section class="card wide">
      <div class="metric-row">
        <div class="metric"><div class="label">Overall</div><div class="value" id="overall">Not run</div></div>
        <div class="metric"><div class="label">USAspending Records</div><div class="value" id="records">—</div></div>
        <div class="metric"><div class="label">Accounts Returned</div><div class="value" id="accounts">—</div></div>
        <div class="metric"><div class="label">Duration</div><div class="value" id="duration">—</div></div>
      </div>
    </section>

    <section class="card">
      <h2>Source Health</h2>
      <div id="sources"><p>Run self-test to load source health.</p></div>
    </section>

    <section class="card">
      <h2>Evaluation Checks</h2>
      <div id="checks"><p>Run self-test to load checks.</p></div>
    </section>

    <section class="card wide">
      <h2>Scan Diagnostics</h2>
      <pre id="diagnostics">Run self-test to load diagnostics.</pre>
    </section>
  </main>

  <script>
    function badge(status) {
      return '<span class="status ' + status + '">' + status.toUpperCase().replace("_", " ") + '</span> ';
    }

    async function runSelfTest() {
      document.getElementById("overall").textContent = "Running";
      const response = await fetch("/api/eval/self-test-v4?ts=" + Date.now());
      const data = await response.json();

      const d = data.diagnostics || {};
      document.getElementById("overall").textContent = data.overall_status === "pass" ? "Pass" : "Fail";
      document.getElementById("records").textContent = d.usaspending_records_fetched ?? d.records_fetched ?? "—";
      document.getElementById("accounts").textContent = d.accounts_returned ?? "—";
      document.getElementById("duration").textContent = d.duration_ms ? d.duration_ms + " ms" : "—";

      document.getElementById("sources").innerHTML = (data.source_health || []).map(function (s) {
        return '<div class="row">' + badge(s.status) + '<b>' + s.source + '</b><p>' + s.detail + '</p></div>';
      }).join("");

      document.getElementById("checks").innerHTML = (data.checks || []).map(function (c) {
        return '<div class="row">' + badge(c.status) + '<b>' + c.name + '</b><p>' + c.detail + '</p></div>';
      }).join("");

      document.getElementById("diagnostics").textContent = JSON.stringify(d, null, 2);
    }

    runSelfTest();
  </script>
</body>
</html>
    """)
# --- END HOSSAGENT EVAL CONSOLE V4 ---



# --- HOSSAGENT SAM GOV + COMMERCIAL SOURCES V5 ---
# Adds:
# - SAM.gov active opportunities when SAM_API_KEY / SAM_GOV_API_KEY is configured
# - Commercial News / Press via GDELT
# - Technical Chatter via Hacker News Algolia
#
# Keeps USAspending + Federal Register intact.

COMMERCIAL_TARGETS = [
    "Scale AI",
    "Databricks",
    "Palantir",
    "Snowflake",
    "Anthropic",
    "OpenAI",
]


def _ha_get_sam_api_key():
    return (
        os.getenv("SAM_API_KEY")
        or os.getenv("SAM_GOV_API_KEY")
        or os.getenv("SAMGOV_API_KEY")
        or ""
    ).strip()


def _ha_source_date_mmddyyyy(days_back=365):
    end = date.today()
    start = end - timedelta(days=days_back)
    return start.strftime("%m/%d/%Y"), end.strftime("%m/%d/%Y")


def _ha_safe_te_matches(text):
    if "classify_te_stack_text" in globals():
        return classify_te_stack_text(text)

    low = (text or "").lower()
    fallback = {
        "evaluation": ["model evaluation", "test and evaluation", "evaluation", "testing", "assessment", "benchmark"],
        "monitoring": ["monitoring", "oversight", "runtime", "incident", "continuous", "telemetry"],
        "red_team": ["red team", "adversarial", "safety", "risk", "robustness", "stress testing"],
        "evidence_reporting": ["audit", "evidence", "reporting", "governance", "compliance", "assurance"],
        "agent_harness": ["agent", "agentic", "workflow", "orchestration", "artificial intelligence", "machine learning", "tool"],
    }

    matches = {}
    for category, terms in fallback.items():
        hits = [term for term in terms if term in low]
        if hits:
            matches[category] = sorted(set(hits))
    return matches


def _ha_safe_te_summary(matches):
    if "summarize_te_categories" in globals():
        return summarize_te_categories(matches)

    labels = {
        "evaluation": "Evaluation",
        "monitoring": "Monitoring",
        "red_team": "Red Teaming",
        "evidence_reporting": "Evidence / Reporting",
        "agent_harness": "Agent Harness",
    }

    ordered = ["evaluation", "monitoring", "red_team", "evidence_reporting", "agent_harness"]
    visible = [labels[k] for k in ordered if k in matches]
    return ", ".join(visible) if visible else "General AI demand"


def _ha_status_from_score(score):
    try:
        score = int(score or 0)
    except Exception:
        score = 0

    if score >= 82:
        return "green", "High confidence"
    if score >= 65:
        return "amber", "Medium confidence"
    return "red", "Watch"


def fetch_sam_gov_opportunities(market):
    api_key = _ha_get_sam_api_key()
    if not api_key:
        return {
            "configured": False,
            "records": [],
            "error": None,
        }

    posted_from, posted_to = _ha_source_date_mmddyyyy(365)

    terms = [
        "artificial intelligence",
        "machine learning",
        "model evaluation",
        "test and evaluation",
        "AI governance",
        "AI safety",
        "red team",
    ]

    records = []
    seen = set()
    errors = []

    for term in terms:
        params = {
            "api_key": api_key,
            "postedFrom": posted_from,
            "postedTo": posted_to,
            "limit": 50,
            "offset": 0,
            "title": term,
        }

        try:
            r = requests.get(
                "https://api.sam.gov/opportunities/v2/search",
                params=params,
                timeout=20,
            )
            r.raise_for_status()
            payload = r.json()
        except Exception as e:
            errors.append(f"{term}: {type(e).__name__}: {e}")
            continue

        items = (
            payload.get("opportunitiesData")
            or payload.get("data")
            or payload.get("results")
            or payload.get("items")
            or []
        )

        for item in items:
            notice_id = (
                item.get("noticeId")
                or item.get("solicitationNumber")
                or item.get("title")
            )

            if not notice_id or notice_id in seen:
                continue

            seen.add(notice_id)
            item["_search_term"] = term
            records.append(item)

    return {
        "configured": True,
        "records": records,
        "error": "; ".join(errors[:3]) if errors and not records else None,
    }


def build_sam_gov_signals(records):
    grouped = defaultdict(lambda: {
        "agency": "",
        "items": [],
        "matches": {},
    })

    for item in records:
        title = item.get("title") or ""
        description = item.get("description") or ""
        full_path = item.get("fullParentPathName") or ""
        org = item.get("organizationName") or item.get("department") or item.get("subtier") or full_path or "Unknown Agency"
        text = f"{title} {description} {full_path} {org} {item.get('_search_term') or ''}"

        matches = _ha_safe_te_matches(text)
        if not matches:
            matches = _ha_safe_te_matches(item.get("_search_term") or "")

        if not matches:
            continue

        agency = org
        if full_path and "." in full_path:
            agency = full_path.split(".")[0].strip() or agency

        g = grouped[agency]
        g["agency"] = agency

        for category, hits in matches.items():
            g["matches"].setdefault(category, set()).update(hits)

        g["items"].append({
            "title": title or "Untitled opportunity",
            "posted_date": item.get("postedDate"),
            "response_deadline": item.get("responseDeadLine") or item.get("responseDeadline") or item.get("archiveDate"),
            "type": item.get("type") or item.get("baseType"),
            "notice_id": item.get("noticeId"),
            "solicitation": item.get("solicitationNumber"),
            "active": item.get("active"),
            "url": item.get("uiLink") or item.get("links"),
            "matches": matches,
        })

    opportunities = []

    for agency, g in grouped.items():
        items = sorted(
            g["items"],
            key=lambda x: x.get("posted_date") or "",
            reverse=True,
        )

        flattened_matches = {
            category: sorted(list(hits))
            for category, hits in g["matches"].items()
        }

        te_summary = _ha_safe_te_summary(flattened_matches)
        score = min(95, 72 + min(len(items) * 4, 12) + min(len(flattened_matches) * 3, 9))
        status, status_label = _ha_status_from_score(score)

        opportunities.append({
            "agency": agency,
            "score": score,
            "status": status,
            "status_label": status_label,
            "detected_spend": "N/A",
            "motion": "Active Opportunity Signal",
            "evidence_window": "SAM.gov opportunities from last 12 months",
            "te_categories": [x.strip() for x in te_summary.split(",") if x.strip()],
            "te_signal_summary": te_summary,
            "te_category_matches": flattened_matches,
            "why": f"{agency} has {len(items)} SAM.gov opportunity signal(s) with T&E relevance. T&E fit: {te_summary}.",
            "signals": [
                {
                    "label": "SAM.gov opportunity",
                    "detail": f"{i.get('posted_date') or 'unknown date'} · {i.get('type') or 'opportunity'} · {i.get('title') or 'Untitled'} · response/deadline: {i.get('response_deadline') or 'not listed'} · T&E fit: {_ha_safe_te_summary(i.get('matches') or {})}",
                }
                for i in items[:4]
            ],
            "recommended_action": f"Treat {agency} as an active-opportunity account. Review the SAM.gov notice details, confirm fit against Scale T&E capabilities, and build outreach around T&E fit: {te_summary}.",
        })

    return sorted(opportunities, key=lambda x: x.get("score", 0), reverse=True)


def fetch_gdelt_articles_for_targets(targets, market):
    records = []
    seen = set()

    for target in targets:
        query = f'"{target}" ("AI evaluation" OR "model evaluation" OR "red teaming" OR "AI governance" OR "AI safety" OR "agentic")'

        try:
            r = requests.get(
                "https://api.gdeltproject.org/api/v2/doc/doc",
                params={
                    "query": query,
                    "mode": "ArtList",
                    "format": "json",
                    "maxrecords": 10,
                    "sort": "HybridRel",
                },
                timeout=15,
            )
            r.raise_for_status()
            payload = r.json()
        except Exception:
            continue

        for article in payload.get("articles", []) or []:
            url = article.get("url")
            title = article.get("title")
            key = url or title

            if not key or key in seen:
                continue

            seen.add(key)
            article["_target"] = target
            records.append(article)

    return records


def fetch_hn_items_for_targets(targets, market):
    records = []
    seen = set()

    for target in targets:
        query = f'"{target}" "AI evaluation"'

        try:
            r = requests.get(
                "https://hn.algolia.com/api/v1/search_by_date",
                params={
                    "query": query,
                    "tags": "story",
                    "hitsPerPage": 10,
                },
                timeout=15,
            )
            r.raise_for_status()
            payload = r.json()
        except Exception:
            continue

        for hit in payload.get("hits", []) or []:
            object_id = hit.get("objectID") or hit.get("url") or hit.get("title")
            if not object_id or object_id in seen:
                continue

            seen.add(object_id)
            hit["_target"] = target
            records.append(hit)

    return records


def build_commercial_signals(gdelt_articles, hn_items):
    grouped = defaultdict(lambda: {
        "company": "",
        "signals": [],
        "matches": {},
        "sources": set(),
    })

    for article in gdelt_articles:
        company = article.get("_target") or "Commercial Market"
        title = article.get("title") or ""
        domain = article.get("domain") or article.get("sourceCollectionIdentifier") or "news"
        seendate = article.get("seendate") or article.get("datetime") or ""
        url = article.get("url") or ""

        text = f"{company} {title} {domain}"
        matches = _ha_safe_te_matches(text)

        if not matches:
            continue

        g = grouped[company]
        g["company"] = company
        g["sources"].add("Commercial News / Press")

        for category, hits in matches.items():
            g["matches"].setdefault(category, set()).update(hits)

        g["signals"].append({
            "label": "Commercial news signal",
            "date": seendate,
            "detail": f"{seendate or 'unknown date'} · {domain} · {title} · T&E fit: {_ha_safe_te_summary(matches)}",
            "url": url,
        })

    for item in hn_items:
        company = item.get("_target") or "Commercial Market"
        title = item.get("title") or item.get("story_title") or ""
        created = item.get("created_at") or ""
        points = item.get("points")
        comments = item.get("num_comments")
        url = item.get("url") or item.get("story_url") or ""

        text = f"{company} {title}"
        matches = _ha_safe_te_matches(text)

        if not matches:
            continue

        g = grouped[company]
        g["company"] = company
        g["sources"].add("Technical Chatter")

        for category, hits in matches.items():
            g["matches"].setdefault(category, set()).update(hits)

        g["signals"].append({
            "label": "Technical chatter signal",
            "date": created,
            "detail": f"{created or 'unknown date'} · Hacker News · {title} · points: {points if points is not None else 'n/a'} · comments: {comments if comments is not None else 'n/a'} · T&E fit: {_ha_safe_te_summary(matches)}",
            "url": url,
        })

    opportunities = []

    for company, g in grouped.items():
        flattened_matches = {
            category: sorted(list(hits))
            for category, hits in g["matches"].items()
        }

        te_summary = _ha_safe_te_summary(flattened_matches)
        evidence_count = len(g["signals"])
        source_count = len(g["sources"])

        score = min(88, 52 + min(evidence_count * 5, 20) + min(source_count * 6, 12) + min(len(flattened_matches) * 3, 9))
        status, status_label = _ha_status_from_score(score)

        opportunities.append({
            "agency": company,
            "score": score,
            "status": status,
            "status_label": status_label,
            "detected_spend": "N/A",
            "motion": "Commercial Market Signal",
            "evidence_window": "Commercial market signals from live web sources",
            "te_categories": [x.strip() for x in te_summary.split(",") if x.strip()],
            "te_signal_summary": te_summary,
            "te_category_matches": flattened_matches,
            "why": f"{company} shows {evidence_count} commercial signal(s) across {source_count} source type(s). T&E fit: {te_summary}.",
            "signals": g["signals"][:5],
            "recommended_action": f"Treat {company} as a commercial account to validate. Confirm whether the signal maps to budget, platform ownership, or a live evaluation/monitoring initiative before prioritizing GTM action.",
        })

    return sorted(opportunities, key=lambda x: x.get("score", 0), reverse=True)


def _ha_v5_normalize_opportunities(raw):
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
            stats["retained_count"] = stats["retained_count"] or fs.get("retained") or fs.get("retained_count")
            stats["fetched_count"] = stats["fetched_count"] or fs.get("fetched") or fs.get("fetched_count")
            stats["filter_summary"] = fs.get("summary") or stats["filter_summary"]

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


def _ha_public_source_status():
    sam_key = bool(_ha_get_sam_api_key())

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
            "status": "live" if sam_key else "needs_key",
            "job": "Active federal opportunities. Requires SAM.gov API key before activation." if not sam_key else "Active federal opportunities and solicitations.",
        },
    ]


def _ha_commercial_source_status():
    return [
        {
            "name": "Commercial News / Press",
            "status": "live",
            "job": "Market movement, executive signals, partnerships, and strategic announcements.",
        },
        {
            "name": "Technical Chatter",
            "status": "live",
            "job": "Developer attention and technical-market chatter.",
        },
        {
            "name": "SEC EDGAR",
            "status": "not wired",
            "job": "Public-company filing signal. Planned for next pass.",
        },
    ]


# Remove older market-scan route so v5 is active.
app.router.routes = [
    route for route in app.router.routes
    if not (
        getattr(route, "path", None) == "/api/market-scan"
        and "POST" in getattr(route, "methods", set())
    )
]


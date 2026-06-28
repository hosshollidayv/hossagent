@app.get("/eval", response_class=HTMLResponse)
async def hossagent_eval_console_v5():
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
    body { margin:0; background:var(--bg); color:var(--text); font-family:ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
    header { padding:28px 36px; border-bottom:1px solid var(--line); display:flex; justify-content:space-between; gap:20px; align-items:flex-start; }
    h1 { margin:0 0 8px; font-size:28px; }
    p { color:var(--muted); line-height:1.45; }
    a { color:var(--text); font-weight:800; }
    button { background:var(--text); color:#05070a; border:0; border-radius:10px; padding:12px 16px; font-weight:800; cursor:pointer; }
    main { padding:28px 36px; display:grid; grid-template-columns:1fr 1fr; gap:18px; }
    .card { background:var(--panel); border:1px solid var(--line); border-radius:16px; padding:18px; }
    .wide { grid-column:1 / -1; }
    .metric-row { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; }
    .metric { background:var(--panel2); border:1px solid var(--line); border-radius:14px; padding:14px; }
    .label { color:var(--muted); text-transform:uppercase; letter-spacing:.08em; font-size:11px; margin-bottom:8px; }
    .value { font-size:24px; font-weight:800; }
    .row { border-top:1px solid var(--line); padding:12px 0; }
    .row:first-child { border-top:0; }
    .status { display:inline-block; border-radius:999px; padding:4px 9px; font-size:12px; font-weight:800; margin-right:8px; }
    .pass, .active { background:rgba(184,247,197,.13); color:var(--ok); }
    .fail, .failed { background:rgba(255,180,168,.13); color:var(--bad); }
    .planned, .staged, .needs_key { background:rgba(219,231,240,.13); color:var(--warn); }
    pre { white-space:pre-wrap; overflow:auto; background:#05070a; border:1px solid var(--line); border-radius:12px; padding:14px; color:var(--muted); }
    @media (max-width:900px) { main { grid-template-columns:1fr; padding:18px; } header { padding:20px; flex-direction:column; } .metric-row { grid-template-columns:1fr 1fr; } }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>HossAgent Evaluation Console</h1>
      <p>Internal test-and-evaluation view for connector health, scan execution, response shape, evidence trace population, and recommended-action output.</p>
      <p><a href="/">← Back to HossAgent</a></p>
    </div>
    <button id="selfTestButton" onclick="runSelfTest()">Run Self-Test</button>
  </header>
  <main>
    <section class="card wide">
      <div class="metric-row">
        <div class="metric"><div class="label">Overall</div><div class="value" id="overall">Not run</div></div>
        <div class="metric"><div class="label">USAspending</div><div class="value" id="records">—</div></div>
        <div class="metric"><div class="label">Accounts</div><div class="value" id="accounts">—</div></div>
        <div class="metric"><div class="label">Duration</div><div class="value" id="duration">—</div></div>
      </div>
    </section>
    <section class="card"><h2>Source Health</h2><div id="sources"><p>Run self-test to load source health.</p></div></section>
    <section class="card"><h2>Evaluation Checks</h2><div id="checks"><p>Run self-test to load checks.</p></div></section>
    <section class="card wide"><h2>Scan Diagnostics</h2><pre id="diagnostics">Run self-test to load diagnostics.</pre></section>
  </main>
  <script>
    function badge(status) {
      return '<span class="status ' + status + '">' + status.toUpperCase().replace("_", " ") + '</span> ';
    }
    async function runSelfTest() {
      const button = document.getElementById("selfTestButton");
      if (button) {
        button.disabled = true;
        button.textContent = "Running Self-Test…";
      }

      document.getElementById("overall").textContent = "Running";

      let data;
      try {
        const response = await fetch("/api/eval/self-test-v5?ts=" + Date.now());
        data = await response.json();
      } finally {
        if (button) {
          button.disabled = false;
          button.textContent = "Run Self-Test";
        }
      }
      const d = data.diagnostics || {};
      document.getElementById("overall").textContent = data.overall_status === "pass" ? "Pass" : "Fail";
      document.getElementById("records").textContent = d.usaspending_records_fetched ?? "—";
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
# --- END HOSSAGENT SAM GOV + COMMERCIAL SOURCES V5 ---



# --- HOSSAGENT SAM V6 SANITIZED UI ---
# Fixes:
# - Do not leak SAM.gov API key in UI errors
# - Do not mark SAM.gov healthy merely because a key exists
# - Give every opportunity account/accountName aliases so UI stops rendering "undefined"
# - Return filter_stats in the legacy shape expected by the dashboard JS

def _ha_redact_secret_text(text):
    text = str(text or "")
    sam_key = _ha_get_sam_api_key() if "_ha_get_sam_api_key" in globals() else ""

    if sam_key:
        text = text.replace(sam_key, "[REDACTED_SAM_API_KEY]")

    # Redact common query-string form even if the key changes.
    text = re.sub(r"api_key=([^&\s]+)", "api_key=[REDACTED]", text)
    return text


def _ha_public_source_status_v6(sam_configured=False, sam_error=None, sam_records=0):
    if not sam_configured:
        sam_status = "needs_key"
        sam_job = "Active federal opportunities. Requires SAM.gov API key before activation."
    elif sam_error:
        sam_status = "needs_attention"
        sam_job = "SAM.gov key is configured, but the current query returned an API error. See eval diagnostics."
    else:
        sam_status = "live"
        sam_job = f"Active federal opportunities and solicitations. Last query returned {sam_records} matching record(s)."

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
            "status": sam_status,
            "job": sam_job,
        },
    ]


def _ha_dashboard_filter_stats(retained, fetched):
    cutoff = (date.today() - timedelta(days=365 * 2)).isoformat()

    return {
        "retained_count": retained,
        "records_retained": retained,
        "retained": retained,
        "fetched_count": fetched,
        "records_fetched": fetched,
        "fetched": fetched,
        "weak_matches_excluded": 0,
        "old_records_excluded": 0,
        "cutoff": cutoff,
        "cutoff_date": cutoff,
        "rule": "T&E relevance filter",
        "summary": f"{retained} retained / {fetched} fetched",
    }


def _ha_hydrate_account_aliases(opportunities):
    hydrated = []

    for item in opportunities or []:
        if not isinstance(item, dict):
            continue

        x = dict(item)

        name = (
            x.get("agency")
            or x.get("account")
            or x.get("accountName")
            or x.get("company")
            or x.get("name")
            or "Unknown Account"
        )

        x["agency"] = name
        x["account"] = name
        x["accountName"] = name

        if not x.get("status_label"):
            score = x.get("score", 0) or 0
            if score >= 82:
                x["status_label"] = "High confidence"
                x["status"] = x.get("status") or "green"
            elif score >= 65:
                x["status_label"] = "Medium confidence"
                x["status"] = x.get("status") or "amber"
            else:
                x["status_label"] = "Watch"
                x["status"] = x.get("status") or "red"

        if not x.get("recommended_action"):
            x["recommended_action"] = f"Treat {name} as a recommended account for follow-up validation."

        hydrated.append(x)

    return hydrated


def fetch_sam_gov_opportunities_v6(market):
    api_key = _ha_get_sam_api_key()
    if not api_key:
        return {
            "configured": False,
            "records": [],
            "error": None,
            "query_ok": False,
        }

    # Use 364 days to avoid SAM.gov's strict 1-year boundary behavior.
    posted_from, posted_to = _ha_source_date_mmddyyyy(364)

    # First do a minimal probe. This tells us if the key/date/endpoint works before
    # we blame the search terms.
    try:
        probe = requests.get(
            "https://api.sam.gov/opportunities/v2/search",
            params={
                "api_key": api_key,
                "postedFrom": posted_from,
                "postedTo": posted_to,
                "limit": 1,
                "offset": 0,
            },
            timeout=20,
        )

        if probe.status_code >= 400:
            body = ""
            try:
                body = probe.text[:500]
            except Exception:
                body = ""

            return {
                "configured": True,
                "records": [],
                "error": _ha_redact_secret_text(f"SAM.gov probe failed: HTTP {probe.status_code}. {body}"),
                "query_ok": False,
            }

        probe.raise_for_status()

    except Exception as e:
        return {
            "configured": True,
            "records": [],
            "error": _ha_redact_secret_text(f"SAM.gov probe failed: {type(e).__name__}: {e}"),
            "query_ok": False,
        }

    # If the probe worked, fetch broader active-opportunity pages and filter locally.
    # This is less brittle than asking SAM title search to do our semantic work.
    ptypes = ["r", "o", "k", "p", "s"]  # sources sought, solicitation, combo, pre-sol, special notice
    records = []
    seen = set()
    errors = []

    for ptype in ptypes:
        try:
            r = requests.get(
                "https://api.sam.gov/opportunities/v2/search",
                params={
                    "api_key": api_key,
                    "postedFrom": posted_from,
                    "postedTo": posted_to,
                    "limit": 100,
                    "offset": 0,
                    "ptype": ptype,
                },
                timeout=25,
            )

            if r.status_code >= 400:
                errors.append(f"ptype={ptype}: HTTP {r.status_code}. {r.text[:250]}")
                continue

            payload = r.json()

        except Exception as e:
            errors.append(f"ptype={ptype}: {type(e).__name__}: {e}")
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

            text = " ".join([
                str(item.get("title") or ""),
                str(item.get("description") or ""),
                str(item.get("fullParentPathName") or ""),
                str(item.get("department") or ""),
                str(item.get("subTier") or item.get("subtier") or ""),
                str(item.get("office") or ""),
                str(item.get("naicsCode") or ""),
                str(item.get("classificationCode") or ""),
            ])

            matches = _ha_safe_te_matches(text) if "_ha_safe_te_matches" in globals() else {}
            low = text.lower()

            # Local relevance gate. Keep AI/T&E-shaped public-sector notices only.
            relevant = bool(matches) or any(term in low for term in [
                "artificial intelligence",
                "machine learning",
                "model evaluation",
                "test and evaluation",
                "red team",
                "ai governance",
                "ai safety",
                "algorithm",
                "autonomy",
                "analytics",
            ])

            if not relevant:
                continue

            seen.add(notice_id)
            item["_search_ptype"] = ptype
            records.append(item)

    return {
        "configured": True,
        "records": records,
        "error": _ha_redact_secret_text("; ".join(errors[:3])) if errors and not records else None,
        "query_ok": True,
    }


# Replace the old SAM function name so existing routes call sanitized v6 behavior.
fetch_sam_gov_opportunities = fetch_sam_gov_opportunities_v6


# Remove older market-scan route so sanitized v6 is active.
app.router.routes = [
    route for route in app.router.routes
    if not (
        getattr(route, "path", None) == "/api/market-scan"
        and "POST" in getattr(route, "methods", set())
    )
]


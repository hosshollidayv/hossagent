@app.get("/eval", response_class=HTMLResponse)
async def hossagent_eval_console_v6():
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
    .planned, .staged, .needs_key, .needs_attention { background:rgba(219,231,240,.13); color:var(--warn); }
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
        const response = await fetch("/api/eval/self-test-v6?ts=" + Date.now());
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
# --- END HOSSAGENT SAM V6 SANITIZED UI ---



# --- HOSSAGENT LOCAL SECRET FILE SUPPORT V7 ---
# Lets HossAgent read SAM.gov API key from:
# 1. Environment variable
# 2. .hossagent.secrets local file
#
# Never commit .hossagent.secrets.

def _ha_read_local_secret_file():
    path = Path(".hossagent.secrets")
    values = {}

    if not path.exists():
        return values

    try:
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    except Exception:
        return {}

    return values


def _ha_get_sam_api_key():
    env_key = (
        os.getenv("SAM_API_KEY")
        or os.getenv("SAM_GOV_API_KEY")
        or os.getenv("SAMGOV_API_KEY")
        or ""
    ).strip()

    if env_key:
        return env_key

    secrets = _ha_read_local_secret_file()

    return (
        secrets.get("SAM_API_KEY")
        or secrets.get("SAM_GOV_API_KEY")
        or secrets.get("SAMGOV_API_KEY")
        or ""
    ).strip()

# ---------------------------------------------------------------------
# HARD OVERRIDE: Config Status API
# Removes any previously registered broken /api/config/status routes.
# ---------------------------------------------------------------------
def api_config_status_fixed():
    import os

    def configured(name: str) -> bool:
        return bool((os.getenv(name) or "").strip())

    sam_key = (
        os.getenv("SAM_GOV_API_KEY")
        or os.getenv("SAM_API_KEY")
        or os.getenv("SAMGOV_API_KEY")
        or ""
    )

    return {
        "ok": True,
        "config": {
            "sam_gov_api_key": bool(sam_key.strip()),
            "openai_api_key": configured("OPENAI_API_KEY"),
        },
        "sources": {
            "sam_gov": "configured" if sam_key.strip() else "missing",
            "openai": "configured" if configured("OPENAI_API_KEY") else "missing",
        },
    }

# FastAPI preserves route order, so delete old/broken route(s), then add clean one.
app.router.routes = [
    route for route in app.router.routes
    if getattr(route, "path", None) != "/api/config/status"
]

app.add_api_route(
    "/api/config/status",
    api_config_status_fixed,
    methods=["GET"],
)

# ---------------------------------------------------------------------
# Buyer Scan Compatibility API
# Supports the existing UI button: POST /api/market-scan
# ---------------------------------------------------------------------
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
@app.get("/eval")
async def ha_eval_page():
    return _HA_HTMLResponse("""
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>HossAgent Evaluation Console</title>
<style>
body{margin:0;background:#05070a;color:#f8fbff;font-family:Inter,Arial,sans-serif}
header{padding:34px;border-bottom:1px solid #26313b}
h1{margin:0 0 12px;font-size:30px}
a{color:#f8fbff;font-weight:900}
button{position:absolute;right:34px;top:28px;border:0;border-radius:14px;padding:14px 18px;font-weight:900;cursor:pointer}
.wrap{padding:28px;display:grid;gap:16px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.card{background:#101418;border:1px solid #26313b;border-radius:18px;padding:18px}
.card b{display:block;font-size:26px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}
pre{white-space:pre-wrap;background:#020306;border:1px solid #26313b;border-radius:14px;padding:16px;color:#d7e0e8}
.check{padding:10px 0;border-bottom:1px solid #26313b}
.pass{color:#9bd67a}.fail{color:#d66a5f}
</style>
</head>
<body>
<header>
  <h1>HossAgent Evaluation Console</h1>
  <p>Internal test-and-evaluation view for connector health, scan execution, response shape, evidence trace population, and recommended-action output.</p>
  <a href="/">← Back to HossAgent</a>
  <button id="selfTestBtn">Run Self-Test</button>
</header>
<div class="wrap">
  <div class="grid">
    <div class="card"><span>OVERALL</span><b id="overall">Ready</b></div>
    <div class="card"><span>SOURCES</span><b id="sources">—</b></div>
    <div class="card"><span>ACCOUNTS</span><b id="accounts">—</b></div>
    <div class="card"><span>DURATION</span><b id="duration">—</b></div>
  </div>
  <div class="two">
    <div class="card"><h2>Source Health</h2><div id="sourceHealth">Run self-test to load source health.</div></div>
    <div class="card"><h2>Evaluation Checks</h2><div id="checks">Run self-test to load checks.</div></div>
  </div>
  <div class="card"><h2>Scan Diagnostics</h2><pre id="diag">Run self-test to load diagnostics.</pre></div>
</div>
<script>
async function runSelfTest(){
  const btn=document.getElementById("selfTestBtn");
  btn.disabled=true; btn.textContent="Running...";
  document.getElementById("overall").textContent="Running";
  try{
    const res=await fetch("/api/eval/self-test-v7?ts="+Date.now());
    if(!res.ok) throw new Error(`Self-test failed ${res.status}: ${await res.text()}`);
    const data=await res.json();
    document.getElementById("overall").textContent=data.status||"complete";
    document.getElementById("sources").textContent=(data.source_health||[]).length;
    document.getElementById("accounts").textContent=data.accounts ?? "—";
    document.getElementById("duration").textContent=(data.duration_ms ?? "—")+" ms";
    document.getElementById("sourceHealth").innerHTML=(data.source_health||[]).map(s=>`<div class="check"><b>${s.name}</b><br>${s.status} — ${s.job}</div>`).join("");
    document.getElementById("checks").innerHTML=(data.checks||[]).map(c=>`<div class="check ${c.passed?'pass':'fail'}">${c.passed?'✓':'✕'} <b>${c.name}</b><br>${c.detail||""}</div>`).join("");
    document.getElementById("diag").textContent=JSON.stringify(data.diagnostics||data,null,2);
  }catch(err){
    document.getElementById("overall").textContent="Failed";
    document.getElementById("diag").textContent=err.message||String(err);
  }finally{
    btn.disabled=false; btn.textContent="Run Self-Test";
  }
}
window.runSelfTest=runSelfTest;
document.addEventListener("DOMContentLoaded",()=>{document.getElementById("selfTestBtn").onclick=runSelfTest;});
</script>
</body>
</html>
""")

# ============================================================
# END HOSSAGENT HARD ROUTE FIX
# ============================================================

# ============================================================
# HOSSAGENT POLISHED EVAL CONSOLE ROUTE
# Visual-only override. Keeps existing self-test API.
# ============================================================

from fastapi.responses import HTMLResponse as _HA_PRETTY_HTMLResponse

def _ha_pretty_remove_route(path, method):
    method = method.upper()
    app.router.routes = [
        route for route in app.router.routes
        if not (
            getattr(route, "path", None) == path
            and method in (getattr(route, "methods", set()) or set())
        )
    ]

_ha_pretty_remove_route("/eval", "GET")

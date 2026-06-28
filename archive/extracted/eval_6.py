@app.get("/eval")
async def ha_pretty_eval_page():
    return _HA_PRETTY_HTMLResponse("""
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>HossAgent Evaluation Console</title>
<style>
:root{
  --bg:#05070a;
  --panel:#0b1016;
  --panel2:#111820;
  --line:#26313b;
  --line2:#3a4654;
  --text:#f8fbff;
  --muted:#b9c5d0;
  --faint:#82909d;
  --green:#9bd67a;
  --amber:#f0b45a;
  --red:#d66a5f;
  --blue:#dcecff;
}
*{box-sizing:border-box}
body{
  margin:0;
  background:
    radial-gradient(circle at 18% -10%,rgba(88,125,155,.25),transparent 30%),
    radial-gradient(circle at 100% 0,rgba(155,214,122,.10),transparent 24%),
    #05070a;
  color:var(--text);
  font-family:Inter,Arial,sans-serif;
}
.shell{min-height:100vh;padding:28px}
.hero{
  border:1px solid var(--line);
  border-radius:28px;
  background:linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,.018));
  box-shadow:0 24px 90px rgba(0,0,0,.45);
  padding:28px;
  position:relative;
  overflow:hidden;
}
.hero:before{
  content:"";
  position:absolute;
  inset:-80px auto auto -80px;
  width:240px;
  height:240px;
  border-radius:50%;
  background:rgba(248,251,255,.08);
  filter:blur(18px);
}
.topbar{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap:20px;
  position:relative;
}
.brandline{
  display:flex;
  align-items:center;
  gap:12px;
  color:var(--faint);
  font-size:12px;
  letter-spacing:.16em;
  text-transform:uppercase;
  font-weight:900;
}
.pulse{
  width:10px;
  height:10px;
  border-radius:50%;
  background:var(--green);
  box-shadow:0 0 22px var(--green);
}
h1{
  margin:14px 0 10px;
  font-size:42px;
  line-height:1;
  letter-spacing:-.06em;
}
.sub{
  max-width:980px;
  color:var(--muted);
  line-height:1.55;
  font-size:15px;
}
.actions{
  display:flex;
  gap:10px;
  align-items:center;
  flex-wrap:wrap;
}
button,.linkbtn{
  border:0;
  border-radius:14px;
  padding:13px 16px;
  font-weight:900;
  cursor:pointer;
  text-decoration:none;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  min-width:150px;
}
button.primary{
  background:#f8fbff;
  color:#05070a;
}
.linkbtn{
  background:rgba(255,255,255,.06);
  border:1px solid var(--line2);
  color:var(--text);
}
button:disabled{opacity:.65;cursor:wait}
.metrics{
  display:grid;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:14px;
  margin:22px 0;
}
.metric{
  border:1px solid var(--line);
  border-radius:20px;
  background:rgba(0,0,0,.22);
  padding:18px;
}
.metric span{
  display:block;
  color:var(--faint);
  font-size:11px;
  letter-spacing:.16em;
  text-transform:uppercase;
  font-weight:900;
  margin-bottom:8px;
}
.metric b{
  font-size:30px;
  letter-spacing:-.04em;
}
.grid{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:16px;
  margin-top:16px;
}
.card{
  border:1px solid var(--line);
  border-radius:24px;
  background:linear-gradient(180deg,rgba(17,24,32,.96),rgba(8,12,17,.96));
  padding:22px;
}
.card h2{
  margin:0 0 14px;
  letter-spacing:-.04em;
}
.source-grid{
  display:grid;
  gap:10px;
}
.source{
  display:grid;
  grid-template-columns:12px 1fr auto;
  gap:12px;
  align-items:start;
  border:1px solid rgba(255,255,255,.08);
  background:rgba(255,255,255,.035);
  border-radius:16px;
  padding:13px;
}
.dot{
  width:10px;
  height:10px;
  border-radius:50%;
  margin-top:5px;
  background:var(--amber);
}
.dot.live,.dot.configured{background:var(--green);box-shadow:0 0 18px rgba(155,214,122,.45)}
.dot.missing{background:var(--red)}
.source b{display:block;margin-bottom:4px}
.source p{margin:0;color:var(--muted);line-height:1.4;font-size:13px}
.badge{
  font-size:11px;
  text-transform:uppercase;
  letter-spacing:.12em;
  border:1px solid var(--line2);
  border-radius:999px;
  padding:5px 8px;
  color:var(--muted);
}
.checks{
  display:grid;
  gap:10px;
}
.check{
  border:1px solid rgba(255,255,255,.08);
  border-radius:16px;
  padding:13px;
  background:rgba(255,255,255,.035);
  display:grid;
  grid-template-columns:24px 1fr;
  gap:10px;
}
.mark{
  width:22px;
  height:22px;
  border-radius:50%;
  display:grid;
  place-items:center;
  font-weight:900;
  background:rgba(155,214,122,.18);
  color:var(--green);
}
.mark.fail{
  background:rgba(214,106,95,.18);
  color:var(--red);
}
.check b{display:block;margin-bottom:4px}
.check p{margin:0;color:var(--muted);line-height:1.4;font-size:13px}
.diag{
  margin-top:16px;
}
pre{
  margin:0;
  white-space:pre-wrap;
  background:#020306;
  border:1px solid var(--line);
  border-radius:18px;
  padding:18px;
  color:#d7e0e8;
  min-height:130px;
}
.loading{
  display:none;
  margin-top:16px;
  border:1px solid var(--line);
  border-radius:18px;
  padding:14px;
  background:rgba(255,255,255,.035);
}
.loading.active{display:block}
.track{
  height:8px;
  background:rgba(255,255,255,.10);
  border-radius:999px;
  overflow:hidden;
  margin-top:10px;
}
.fill{
  height:100%;
  width:0%;
  background:linear-gradient(90deg,#f8fbff,#9bd67a);
  transition:width .3s ease;
}
@media(max-width:980px){
  .topbar{flex-direction:column}
  .metrics,.grid{grid-template-columns:1fr}
  h1{font-size:34px}
}
</style>
</head>
<body>
<div class="shell">
  <section class="hero">
    <div class="topbar">
      <div>
        <div class="brandline"><span class="pulse"></span> HossAgent T&E Console</div>
        <h1>Evaluation Console</h1>
        <p class="sub">Connector health, scan execution, response-shape checks, evidence trace population, and recommended-action validation for the HossAgent opportunity intelligence loop.</p>
      </div>
      <div class="actions">
        <a class="linkbtn" href="/">← Back to HossAgent</a>
        <button id="selfTestBtn" class="primary">Run Self-Test</button>
      </div>
    </div>

    <div class="metrics">
      <div class="metric"><span>Overall</span><b id="overall">Ready</b></div>
      <div class="metric"><span>Sources</span><b id="sources">—</b></div>
      <div class="metric"><span>Accounts</span><b id="accounts">—</b></div>
      <div class="metric"><span>Duration</span><b id="duration">—</b></div>
    </div>

    <div id="loading" class="loading">
      <b id="loadingText">Running self-test...</b>
      <div class="track"><div id="fill" class="fill"></div></div>
    </div>
  </section>

  <div class="grid">
    <section class="card">
      <h2>Source Health</h2>
      <div id="sourceHealth" class="source-grid">
        <p class="sub">Run self-test to load source health.</p>
      </div>
    </section>

    <section class="card">
      <h2>Evaluation Checks</h2>
      <div id="checks" class="checks">
        <p class="sub">Run self-test to load checks.</p>
      </div>
    </section>
  </div>

  <section class="card diag">
    <h2>Scan Diagnostics</h2>
    <pre id="diag">Run self-test to load diagnostics.</pre>
  </section>
</div>

<script>
async function runSelfTest(){
  const btn=document.getElementById("selfTestBtn");
  const loading=document.getElementById("loading");
  const fill=document.getElementById("fill");

  btn.disabled=true;
  btn.textContent="Running...";
  loading.classList.add("active");
  fill.style.width="18%";
  document.getElementById("overall").textContent="Running";

  let pct=18;
  const timer=setInterval(()=>{
    pct=Math.min(92,pct+18);
    fill.style.width=pct+"%";
  },450);

  try{
    const res=await fetch("/api/eval/self-test-v7?ts="+Date.now());
    if(!res.ok) throw new Error(`Self-test failed ${res.status}: ${await res.text()}`);
    const data=await res.json();

    clearInterval(timer);
    fill.style.width="100%";

    document.getElementById("overall").textContent=data.status||"complete";
    document.getElementById("sources").textContent=(data.source_health||[]).length;
    document.getElementById("accounts").textContent=data.accounts ?? "—";
    document.getElementById("duration").textContent=(data.duration_ms ?? "—")+" ms";

    document.getElementById("sourceHealth").innerHTML=(data.source_health||[]).map(s=>`
      <div class="source">
        <span class="dot ${s.status}"></span>
        <div><b>${s.name}</b><p>${s.job}</p></div>
        <span class="badge">${s.status}</span>
      </div>
    `).join("");

    document.getElementById("checks").innerHTML=(data.checks||[]).map(c=>`
      <div class="check">
        <span class="mark ${c.passed ? "" : "fail"}">${c.passed ? "✓" : "✕"}</span>
        <div><b>${c.name}</b><p>${c.detail||""}</p></div>
      </div>
    `).join("");

    document.getElementById("diag").textContent=JSON.stringify(data.diagnostics||data,null,2);

    setTimeout(()=>loading.classList.remove("active"),800);
  }catch(err){
    clearInterval(timer);
    document.getElementById("overall").textContent="Failed";
    document.getElementById("diag").textContent=err.message||String(err);
  }finally{
    btn.disabled=false;
    btn.textContent="Run Self-Test";
  }
}
window.runSelfTest=runSelfTest;
document.addEventListener("DOMContentLoaded",()=>{
  document.getElementById("selfTestBtn").onclick=runSelfTest;
});
</script>
</body>
</html>
""")

# ============================================================
# END HOSSAGENT POLISHED EVAL CONSOLE ROUTE
# ============================================================


# ===== HOSSAGENT REFACTOR PASS 1 ROUTE HYGIENE =====
try:
    from hossagent.route_hygiene import dedupe_routes_keep_latest
    from hossagent.routes.health import router as hossagent_health_router

    app.include_router(hossagent_health_router)
    dedupe_routes_keep_latest(app)

    print("HossAgent refactor pass 1: route hygiene applied.")
except Exception as _hoss_refactor_error:
    print(f"HossAgent refactor pass 1 skipped: {_hoss_refactor_error}")
# ===== END HOSSAGENT REFACTOR PASS 1 ROUTE HYGIENE =====

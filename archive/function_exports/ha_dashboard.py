async def ha_dashboard():
    return _HA_HTMLResponse("""
<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>HossAgent Core</title>
<style>
:root{--bg:#05070a;--panel:#101418;--panel2:#171c22;--line:#26313b;--line2:#3b4654;--text:#f8fbff;--muted:#d7e0e8;--faint:#8f9aa6;--green:#9bd67a;--amber:#f0b45a;--red:#d66a5f}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(circle at top left,#101722 0,#020203 44%);color:var(--text);font-family:Inter,Arial,sans-serif}
.app{display:grid;grid-template-columns:340px minmax(620px,1fr) 460px;gap:18px;min-height:100vh;padding:22px}
.rail,.main,.detail{background:rgba(8,8,8,.91);border:1px solid var(--line);border-radius:26px;box-shadow:0 24px 90px rgba(0,0,0,.55)}
.rail{padding:22px;min-width:340px}.main{padding:28px}.detail{padding:24px;overflow:auto}
.logo{font-size:28px;font-weight:900;letter-spacing:-.05em;margin-bottom:24px}
.label{color:var(--faint);font-size:11px;letter-spacing:.14em;text-transform:uppercase;margin:20px 0 8px}
.workspace{background:linear-gradient(180deg,#111720,#090b10);border:1px solid var(--line2);border-radius:16px;padding:14px}
.workspace strong{display:block;font-size:18px}.workspace span{color:var(--muted);font-size:13px}
select,textarea,button{width:100%;border-radius:14px;padding:13px 14px;font-weight:800}
select,textarea{background:var(--panel2);border:1px solid var(--line2);color:var(--text)}
textarea{min-height:72px;resize:vertical;line-height:1.25;white-space:normal;overflow-wrap:anywhere}
button{background:#f8fbff;border:0;color:#05070d;cursor:pointer;margin-top:12px}
button.secondary{background:rgba(255,255,255,.06);border:1px solid var(--line2);color:var(--text)}
button.is-running{opacity:.78;cursor:wait}
h1{font-size:40px;line-height:1.02;margin:0 0 10px;letter-spacing:-.06em}
.sub{color:var(--muted);line-height:1.55}
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0 18px}
.metric{background:rgba(255,255,255,.035);border:1px solid var(--line);border-radius:18px;padding:16px}
.metric b{display:block;font-size:26px}.metric span{font-size:11px;color:var(--faint);letter-spacing:.14em;text-transform:uppercase}
.box{background:rgba(255,255,255,.035);border:1px solid var(--line);border-radius:18px;padding:16px;margin-bottom:18px}
.eyebrow{font-size:11px;color:var(--faint);letter-spacing:.16em;text-transform:uppercase;font-weight:900}
#scanProgress{display:none;margin-top:14px;padding:14px;border:1px solid var(--line2);border-radius:16px;background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.025))}
#scanProgress.active{display:block}
#scanProgressState{font-weight:900;margin-bottom:10px}
.scan-track{height:8px;border-radius:999px;background:rgba(255,255,255,.10);overflow:hidden;margin-bottom:12px}
#scanBarFill{width:0%;height:100%;border-radius:999px;background:linear-gradient(90deg,#f8fbff,#9bd67a);transition:width .35s ease}
.scan-steps{display:grid;gap:7px;font-size:12px;color:var(--muted)}
.scan-step{display:flex;align-items:center;gap:8px;opacity:.72}
.scan-step.active{opacity:1;color:var(--text);font-weight:900}.scan-step.done{opacity:1;color:var(--green)}
.glyph{width:18px;height:18px;display:inline-grid;place-items:center;border-radius:50%;border:1px solid var(--line2);font-size:11px}
.legend{float:right;color:var(--muted);font-size:12px}
.opp{border:1px solid var(--line);border-radius:18px;padding:14px;margin:10px 0;cursor:pointer;background:rgba(255,255,255,.035)}
.opp:hover,.opp.selected{border-color:#f8fbff}
.opp .score{font-size:26px;font-weight:900}.opp h3{margin:4px 0}.opp p{color:var(--muted);line-height:1.45}
.badge{font-size:12px;border-radius:999px;padding:4px 9px;background:rgba(255,255,255,.08)}
.empty{border:1px dashed var(--line2);border-radius:16px;padding:28px;text-align:center;color:var(--muted)}
.signal{display:flex;gap:10px;border-bottom:1px solid var(--line);padding:12px 0}
.signal b{display:block}.signal span{color:var(--muted);line-height:1.45}
.dot{width:9px;height:9px;border-radius:50%;margin-top:6px;background:var(--amber)}.dot.green{background:var(--green)}.dot.amber{background:var(--amber)}.dot.red{background:var(--red)}
.profile p{color:var(--muted)}
.action{background:rgba(30,120,70,.18);border:1px solid rgba(70,200,120,.45);border-radius:18px;padding:16px}
@media(max-width:1180px){.app{grid-template-columns:1fr}.rail,.main,.detail{min-width:0}.metrics{grid-template-columns:repeat(2,1fr)}}
</style>
</head>
<body>
<div class="app">
  <aside class="rail">
    <div class="logo">HossAgent</div>
    <div class="label">Workspace</div>
    <div class="workspace"><strong>Scale AI</strong><span>Opportunity Intelligence</span></div>
    <div class="label">Business Unit</div>
    <select id="businessUnit"><option selected>Public Sector</option><option>Commercial Enterprise</option></select>
    <div class="label">Market Lens</div>
    <textarea id="market">Federal AI Evaluation Model Assurance</textarea>
    <button id="runBuyerScanButton">Run Buyer Scan</button>
    <button class="secondary" onclick="window.location.assign('/eval?v=te-stack')">Evaluation Console →</button>
  </aside>

  <main class="main">
    <h1>Opportunity intelligence for AI test and evaluation.</h1>
    <p class="sub">HossAgent scans public-sector data, identifies accounts with evidence of AI test-and-evaluation demand, and explains the source evidence behind each recommendation.</p>

    <div class="metrics">
      <div class="metric"><b id="countSignals">0</b><span>Account Signals</span></div>
      <div class="metric"><b id="activeSources">—</b><span>Active Sources</span></div>
      <div class="metric"><b id="topScore">—</b><span>Top Score</span></div>
      <div class="metric"><b id="scanStatus">Empty</b><span>Status</span></div>
    </div>

    <div class="box">
      <div class="eyebrow">Scan Summary</div>
      <h3 id="scanMessage">Ready</h3>
      <p class="sub">Sources: USAspending award history, Federal Register policy signals, and SAM.gov opportunity validation.</p>
      <p class="sub"><b>Scoring:</b> Evidence-based account ranking.</p>
      <p id="filterStats" class="sub"></p>
      <div id="scanProgress">
        <div id="scanProgressState">Ready</div>
        <div class="scan-track"><div id="scanBarFill"></div></div>
        <div class="scan-steps">
          <div class="scan-step"><span class="glyph">○</span>Checking config</div>
          <div class="scan-step"><span class="glyph">○</span>Querying USAspending</div>
          <div class="scan-step"><span class="glyph">○</span>Searching Federal Register</div>
          <div class="scan-step"><span class="glyph">○</span>Checking SAM.gov</div>
          <div class="scan-step"><span class="glyph">○</span>Merging evidence</div>
          <div class="scan-step"><span class="glyph">○</span>Ranking accounts</div>
        </div>
      </div>
    </div>

    <h2>Recommended Accounts <span class="legend">● High &nbsp; ● Medium &nbsp; ● Watch</span></h2>
    <div id="opportunities" class="empty"><strong>No account signals yet</strong><p>Run buyer scan.</p></div>

    <div class="box">
      <div class="eyebrow">Data Sources</div>
      <div id="sources">Run scan to load source health.</div>
    </div>
  </main>

  <aside class="detail">
    <div class="eyebrow">Account Detail</div>
    <h2 id="detailTitle">Select an account</h2>
    <p class="sub" id="detailWhy">Run a scan and select an account to see evidence, scoring rationale, and recommended action.</p>

    <div class="box profile">
      <h3>Buyer Intelligence</h3>
      <p><b>Motion:</b> <span id="detailMotion">—</span></p>
      <p><b>Detected relevant spend:</b> <span id="detailDeal">—</span></p>
      <p><b>Evidence window:</b> <span id="detailWindow">—</span></p>
      <p><b>Status:</b> <span id="detailStatus">—</span></p>
    </div>

    <div class="box">
      <h3>Supporting Evidence</h3>
      <div id="detailSignals" class="empty">No evidence loaded.</div>
    </div>

    <div class="action">
      <h3>Recommended Action</h3>
      <p id="detailAction">No action generated yet.</p>
    </div>
  </aside>
</div>

<script>
let opportunities = [];
function setText(id,value){const el=document.getElementById(id); if(el) el.textContent=value;}

function setStep(idx,label){
  const progress=document.getElementById("scanProgress");
  const state=document.getElementById("scanProgressState");
  const bar=document.getElementById("scanBarFill");
  const steps=[...document.querySelectorAll(".scan-step")];
  progress.classList.add("active");
  state.textContent=label;
  bar.style.width=`${Math.min(96,10+idx*16)}%`;
  steps.forEach((step,i)=>{
    step.classList.toggle("done",i<idx);
    step.classList.toggle("active",i===idx);
    const glyph=step.querySelector(".glyph");
    if(glyph) glyph.textContent=i<idx?"✓":(i===idx?"→":"○");
  });
}

function renderOpps(items){
  const root=document.getElementById("opportunities");
  if(!items.length){root.className="empty";root.innerHTML="<strong>No account signals yet</strong><p>Run buyer scan.</p>";return;}
  root.className="";
  root.innerHTML=items.map((o,i)=>`
    <div class="opp" id="opp-${i}" onclick="selectOpp(${i})">
      <div class="score">${o.score ?? "—"}</div>
      <h3>${o.accountName || o.account || o.agency}</h3>
      <p>${o.why || ""}</p>
      <span class="badge">${o.status_label || "Medium confidence"}</span>
    </div>`).join("");
}

function renderSources(items){
  const root=document.getElementById("sources");
  root.innerHTML=(items||[]).map(s=>`
    <div class="signal">
      <span class="dot ${s.status === "live" || s.status === "configured" ? "green":"amber"}"></span>
      <div><b>${s.name}</b><span>${s.job}</span><br><span>${s.status}</span></div>
    </div>`).join("");
}

function selectOpp(i){
  const o=opportunities[i]; if(!o)return;
  document.querySelectorAll(".opp").forEach(x=>x.classList.remove("selected"));
  const card=document.getElementById(`opp-${i}`); if(card) card.classList.add("selected");
  setText("detailTitle",o.accountName||o.account||o.agency);
  setText("detailWhy",o.why||"");
  setText("detailMotion",o.motion||"—");
  setText("detailDeal",o.detected_spend||"—");
  setText("detailWindow",o.evidence_window||o.window||"—");
  setText("detailStatus",o.status_label||"—");
  setText("detailAction",o.recommended_action||"No action generated yet.");
  const evidence=o.evidence||o.signals||[];
  document.getElementById("detailSignals").className=evidence.length?"":"empty";
  document.getElementById("detailSignals").innerHTML=evidence.length ? evidence.map(s=>`
    <div class="signal"><span class="dot ${s.status||"amber"}"></span><div><b>${s.source||s.label||"Evidence"}</b><span>${s.detail||"Evidence item available."}</span></div></div>
  `).join("") : "No evidence loaded.";
}

async function runScan(event){
  if(event) event.preventDefault();
  const btn=document.getElementById("runBuyerScanButton");
  btn.disabled=true; btn.classList.add("is-running"); btn.textContent="Scanning...";
  setText("scanStatus","Active");
  setText("scanMessage","Running buyer scan across configured sources...");
  const stages=["Checking config","Querying USAspending","Searching Federal Register","Checking SAM.gov","Merging evidence","Ranking accounts"];
  let idx=0; setStep(0,stages[0]);
  const timer=setInterval(()=>{idx=Math.min(idx+1,stages.length-1);setStep(idx,stages[idx]);},650);
  try{
    const res=await fetch("/api/market-scan",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({workspace:"Scale AI",business_unit:document.getElementById("businessUnit").value,market:document.getElementById("market").value})});
    if(!res.ok) throw new Error(`Market scan failed ${res.status}: ${await res.text()}`);
    const data=await res.json();
    clearInterval(timer);
    document.getElementById("scanBarFill").style.width="100%";
    setText("scanProgressState","Complete");
    setText("scanMessage",data.message||"Buyer scan complete.");
    setText("countSignals",data.count ?? (data.opportunities||[]).length);
    setText("activeSources",data.active_sources||"3/3");
    setText("topScore",data.top_score||"—");
    setText("scanStatus","Active");
    const fs=data.filter_stats||{};
    setText("filterStats",`Filter: ${fs.records_retained ?? (data.opportunities||[]).length} retained / ${fs.records_fetched ?? "N/A"} fetched · ${(fs.records_excluded ?? 0)} weak matches excluded · ${(fs.records_excluded_old ?? 0)} old records excluded · cutoff ${fs.cutoff_date ?? "last 24 months"} · Rule: ${fs.filter_rule ?? "AI/T&E evidence match"}`);
    opportunities=data.opportunities||[];
    renderOpps(opportunities);
    renderSources(data.source_status||[]);
    if(opportunities.length) selectOpp(0);
    setTimeout(()=>document.getElementById("scanProgress").classList.remove("active"),1200);
  }catch(err){
    clearInterval(timer);
    setText("scanProgressState","Scan failed");
    setText("scanMessage",`Scan failed: ${err.message||err}`);
  }finally{
    btn.disabled=false; btn.classList.remove("is-running"); btn.textContent="Run Buyer Scan";
  }
}
window.runScan=runScan;
document.addEventListener("DOMContentLoaded",()=>{document.getElementById("runBuyerScanButton").onclick=runScan;});
</script>
</body>
</html>
""")
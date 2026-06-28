async def home():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>HossAgent Core</title>
<style>
:root{--bg:#020203;--panel:#080808;--panel2:#11100d;--line:#232832;--line2:#3b4654;--text:#f8fbff;--muted:#c9d3df;--faint:#7f8b99;--green:#9bd67a;--amber:#f0b45a;--red:#d66a5f;--blue:#e6f3ff}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(circle at top left,#101722 0,#020203 44%);color:var(--text);font-family:Inter,Arial,sans-serif}
.app{display:grid;grid-template-columns:340px minmax(560px,1fr) 460px;gap:18px;min-height:100vh;padding:22px}
.rail,.main,.detail{background:rgba(8,8,8,.91);border:1px solid var(--line);border-radius:26px;box-shadow:0 24px 90px rgba(0,0,0,.55)}
.rail{padding:22px}.main{padding:28px}.detail{padding:24px;overflow:auto}
.logo{font-size:28px;font-weight:900;letter-spacing:-.05em;margin-bottom:24px}
.label{color:var(--faint);font-size:11px;letter-spacing:.14em;text-transform:uppercase;margin:20px 0 8px}
.workspace{background:linear-gradient(180deg,#111720,#090b10);border:1px solid var(--line2);border-radius:16px;padding:14px}
.workspace strong{display:block;font-size:18px}.workspace span{color:var(--muted);font-size:13px}
select,input,textarea,button{width:100%;border-radius:14px;padding:13px 14px;font-weight:800}
select,input,textarea{background:var(--panel2);border:1px solid var(--line2);color:var(--text)}
button{background:#f8fbff;border:0;color:#05070d;cursor:pointer;margin-top:12px}
.navitem{padding:11px 12px;border-radius:12px;color:var(--muted);margin:4px 0}.navitem.active{background:rgba(34,197,94,.12);color:var(--text);border:1px solid rgba(34,197,94,.25)}
h1{font-size:42px;line-height:.98;letter-spacing:-.06em;margin:0}.sub{color:var(--muted);line-height:1.55;max-width:760px;margin-top:12px}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:22px 0}.kpi{background:var(--panel2);border:1px solid var(--line);border-radius:20px;padding:16px}.kpi strong{font-size:28px}.kpi span{display:block;color:var(--faint);font-size:11px;text-transform:uppercase;letter-spacing:.12em;margin-top:7px}
.box,.empty,.source{background:var(--panel2);border:1px solid var(--line);border-radius:18px;padding:16px}.box h3,.source h3{margin:0 0 8px}.muted{color:var(--muted);line-height:1.55}.faint{color:var(--faint)}
.eyebrow{color:var(--blue);font-weight:900;text-transform:uppercase;letter-spacing:.14em;font-size:11px}
.feedtitle{display:flex;justify-content:space-between;align-items:center;margin-top:24px}.feedtitle h2{margin:0;font-size:20px}
.statuskey{display:flex;gap:12px;color:var(--muted);font-size:12px}.key{display:flex;gap:6px;align-items:center}.dot{width:10px;height:10px;border-radius:50%;display:inline-block}.green{background:var(--green)}.amber{background:var(--amber)}.red{background:var(--red)}.off{background:var(--faint)}
.empty{border-style:dashed;text-align:center;padding:34px 22px}.empty strong{display:block;font-size:20px;margin-bottom:8px}
.source{margin:10px 0;display:grid;grid-template-columns:1fr auto;gap:10px;align-items:start}.badge{border:1px solid var(--line2);border-radius:999px;color:var(--muted);font-size:12px;padding:7px 10px;white-space:nowrap}.badge.live{color:var(--green);border-color:rgba(34,197,94,.4)}.badge.error{color:var(--red);border-color:rgba(239,68,68,.4)}
.opp{display:grid;grid-template-columns:48px 1fr 94px;gap:14px;align-items:center;background:var(--panel2);border:1px solid var(--line);border-left-width:4px;border-radius:18px;padding:15px;margin:12px 0;cursor:pointer}.opp:hover{border-color:var(--line2);transform:translateY(-1px)}.opp.selected{box-shadow:0 0 0 1px rgba(34,197,94,.35),0 22px 80px #0005}.opp.green{border-left-color:var(--green)}.opp.amber{border-left-color:var(--amber)}.opp.red{border-left-color:var(--red)}
.score{font-size:25px;font-weight:900}.oppname{font-weight:900;font-size:17px}.reason{color:var(--muted);font-size:13px;margin-top:4px;line-height:1.35}.pill{font-size:12px;border:1px solid var(--line2);border-radius:999px;color:var(--muted);padding:8px 10px;text-align:center}
.detail h2{font-size:28px;letter-spacing:-.04em;margin:8px 0 10px}.signal{display:flex;gap:11px;padding:12px 0;border-bottom:1px solid var(--line)}.signal:last-child{border-bottom:0}.signal b{display:block}.signal span{color:var(--muted);font-size:13px;line-height:1.45}.bigaction{border:1px solid rgba(34,197,94,.35);background:rgba(34,197,94,.08)}
@media(max-width:1180px){.app{grid-template-columns:1fr}.kpis{grid-template-columns:1fr 1fr}}

/* HossAgent UI repair: wider rail, wrapped market lens, visible scan animation */
.rail{min-width:340px}
#market{
  width:100%;
  min-height:72px;
  resize:vertical;
  line-height:1.25;
  white-space:normal;
  overflow-wrap:anywhere;
  font-size:13px;
}
#scanProgress{
  display:none;
  margin-top:14px;
  padding:14px;
  border:1px solid var(--line2);
  border-radius:16px;
  background:linear-gradient(180deg,rgba(255,255,255,.06),rgba(255,255,255,.025));
}
#scanProgress.active{display:block}
#scanProgressState{
  font-weight:900;
  margin-bottom:10px;
}
.scan-track{
  height:8px;
  border-radius:999px;
  background:rgba(255,255,255,.10);
  overflow:hidden;
  margin-bottom:12px;
}
#scanBarFill{
  width:0%;
  height:100%;
  border-radius:999px;
  background:linear-gradient(90deg,#f8fbff,#9bd67a);
  transition:width .35s ease;
}
.scan-steps{
  display:grid;
  gap:7px;
  font-size:12px;
  color:var(--muted);
}
.scan-step{
  display:flex;
  align-items:center;
  gap:8px;
  opacity:.72;
}
.scan-step.active{opacity:1;color:var(--text);font-weight:900}
.scan-step.done{opacity:1;color:var(--green)}
.scan-step .glyph{
  width:18px;
  height:18px;
  display:inline-grid;
  place-items:center;
  border-radius:50%;
  border:1px solid var(--line2);
  font-size:11px;
}
button.is-running{
  opacity:.78;
  cursor:wait;
}
@media (max-width:1180px){
  .app{grid-template-columns:1fr}
  .rail,.main,.detail{min-width:0}
}

</style>
</head>
<body>
<div class="app">
<aside class="rail">
<div class="logo">HossAgent</div>
<div class="label">Workspace</div><div class="workspace"><strong>Scale AI</strong><span>Opportunity Intelligence</span></div>
<div class="label">Business Unit</div><select id="businessUnit"><option>Public Sector</option><option>Commercial Enterprise</option></select>
<div class="label">Market Lens</div><textarea id="market">Federal AI Evaluation Model Assurance</textarea>
<button onclick="runScan()">Run Buyer Scan</button>
<button id="evalConsoleButton" type="button" onclick="window.location.href='/eval?v=te-stack'" style="margin-top:10px;background:rgba(255,255,255,.06);border:1px solid var(--line2);color:var(--text);">
  Evaluation Console →
</button>


</aside>
<main class="main">
<h1>Opportunity intelligence for AI test and evaluation.</h1>
<p class="sub">HossAgent scans public-sector data, identifies accounts with evidence of AI test-and-evaluation demand, and explains the source evidence behind each recommendation.</p>
<section class="kpis"><div class="kpi"><strong id="kpiOpps">0</strong><span>Account Signals</span></div><div class="kpi"><strong id="kpiSources">1</strong><span>Active Sources</span></div><div class="kpi"><strong id="kpiTop">—</strong><span>Top Score</span></div><div class="kpi"><strong id="kpiMode">Empty</strong><span>Status</span></div></section>
<div class="box"><div class="eyebrow">Scan Summary</div><h3 id="scanMessage">Ready</h3><p class="muted">Sources: USAspending award history, Federal Register policy signals, and SAM.gov opportunity validation.</p><p class="muted"><b>Scoring:</b> Evidence-based account ranking.</p><p id="filterStats" class="muted"></p>
<div id="scanProgress">
  <div id="scanProgressState">Ready</div>
  <div class="scan-track"><div id="scanBarFill"></div></div>
  <div class="scan-steps">
    <div class="scan-step" data-step="0"><span class="glyph">○</span>Checking config</div>
    <div class="scan-step" data-step="1"><span class="glyph">○</span>Querying USAspending</div>
    <div class="scan-step" data-step="2"><span class="glyph">○</span>Searching Federal Register</div>
    <div class="scan-step" data-step="3"><span class="glyph">○</span>Checking SAM.gov</div>
    <div class="scan-step" data-step="4"><span class="glyph">○</span>Merging evidence</div>
    <div class="scan-step" data-step="5"><span class="glyph">○</span>Ranking accounts</div>
  </div>
</div>
</div>
<div class="feedtitle"><h2>Recommended Accounts</h2><div class="statuskey"><div class="key"><span class="dot green"></span>High</div><div class="key"><span class="dot amber"></span>Medium</div><div class="key"><span class="dot red"></span>Watch</div></div></div>
<div id="opportunities" class="empty"><strong>No account signals yet</strong><p class="muted">Run buyer scan.</p></div>
<div class="feedtitle"><h2>Data Sources</h2></div><div id="sources"></div>
</main>
<aside class="detail">
<div class="eyebrow">Account Detail</div><h2 id="detailTitle">Select an account</h2><p id="detailWhy" class="muted">Run a scan and select an account to see evidence, scoring rationale, and recommended action.</p>
<div class="box"><h3>Opportunity Profile</h3><p class="muted"><b>Motion:</b> <span id="detailMotion">—</span></p><p class="muted"><b>Detected relevant spend:</b> <span id="detailDeal">—</span></p><p class="muted"><b>Evidence window:</b> <span id="detailWindow">—</span></p><p class="muted"><b>Status:</b> <span id="detailStatus">—</span></p></div>
<div class="box"><h3>Evidence Trace</h3><div id="detailSignals" class="empty">No evidence loaded.</div></div>
<div class="box bigaction"><h3>Recommended Action</h3><p id="detailAction" class="muted">No action generated yet.</p></div>
</aside>
</div>
<script>
let current=[];
async function runScan(){
 const business_unit=document.getElementById("businessUnit").value;
 const market=document.getElementById("market").value;
 document.getElementById("scanMessage").textContent="Fetching live USAspending data...";
 const res=await fetch("/api/market-scan",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({workspace:"Scale AI",business_unit,market})});
 const data=await res.json();
 current=data.opportunities || [];
 document.getElementById("scanMessage").textContent=data.message;
 const fs=data.filter_stats;
 document.getElementById("filterStats").textContent=fs ? `Filter: ${fs.records_retained} retained / ${fs.records_fetched} fetched · ${fs.records_excluded} weak matches excluded · ${fs.records_excluded_old || 0} old records excluded · cutoff ${fs.cutoff_date} · Rule: ${fs.filter_rule}` : "";
 document.getElementById("kpiOpps").textContent=current.length;
 document.getElementById("kpiSources").textContent=(data.source_status||[]).filter(s=>s.status==="live").length + "/" + (data.source_status||[]).length;
 document.getElementById("kpiTop").textContent=current.length ? Math.max(...current.map(o=>o.score)) : "—";
 document.getElementById("kpiMode").textContent=data.status;
 document.getElementById("sources").innerHTML=(data.source_status||[]).filter(source => source.status === 'live').map(s=>`<div class="source"><div><h3>${s.name}</h3><p class="muted">${s.job}</p></div><div class="badge ${s.status}">${s.status}</div></div>`).join("");
 if(!current.length){
   document.getElementById("opportunities").innerHTML=`<strong>No ranked opportunities returned</strong><p class="muted">${data.message}</p>`;
   return;
 }
 document.getElementById("opportunities").innerHTML=current.map((o,i)=>`<div class="opp ${o.status}" onclick="selectOpp(${i})" id="opp-${i}"><div class="score">${o.score}</div><div><div class="oppname">${o.account}</div><div class="reason">${o.why}</div></div><div class="pill">${o.status_label}</div></div>`).join("");
 selectOpp(0);
}
function selectOpp(i){
 const o=current[i]; if(!o)return;
 document.querySelectorAll(".opp").forEach(x=>x.classList.remove("selected"));
 document.getElementById("opp-"+i).classList.add("selected");
 document.getElementById("detailTitle").textContent=o.account;
 document.getElementById("detailWhy").textContent=o.why;
 document.getElementById("detailMotion").textContent=o.motion || "—";
 document.getElementById("detailDeal").textContent=o.detected_spend || "—";
 document.getElementById("detailWindow").textContent=o.window;
 document.getElementById("detailStatus").textContent=o.status_label;
 document.getElementById("detailAction").textContent=o.recommended_action;
 document.getElementById("detailSignals").innerHTML=o.evidence.map(s=>`<div class="signal"><span class="dot ${s.status}"></span><div><b>${s.source}</b><span>${s.detail}</span></div></div>`).join("");
}
</script>

<script id="hossagent-customer-ui-cleanup">
(function () {
  function replaceTextNode(node) {
    if (!node || !node.nodeValue) return;

    let text = node.nodeValue;

    const exact = new Map([
      ["Buyer-propensity intelligence cockpit. Noir edition.", "Opportunity intelligence for AI test and evaluation."],
      ["HossAgent scans real public data, ranks buyer-propensity accounts, and explains why an account may deserve GTM attention. Current coverage: Public Sector / USAspending only. Commercial Enterprise connectors are not wired yet.", "HossAgent scans public-sector data, identifies accounts with evidence of AI test-and-evaluation demand, and explains the source evidence behind each recommendation."],
      ["Buyer Signals Found", "Account Signals"],
      ["Sources Wired", "Active Sources"],
      ["Top Propensity Score", "Top Score"],
      ["Scan State", "Status"],
      ["Scan Output", "Scan Summary"],
      ["Account Activity Signals by Agency / Sub-Agency", "Recommended Accounts"],
      ["Source Readiness", "Data Sources"],
      ["Opportunity Detail", "Account Detail"],
      ["Commercial Shape", "Opportunity Profile"],
      ["New Account Activity", "New Account Signal"],
      ["Watchlist", "Watch"],
      ["live", "Active"],
      ["not wired", "Planned"]
    ]);

    if (exact.has(text.trim())) {
      node.nodeValue = text.replace(text.trim(), exact.get(text.trim()));
      return;
    }

    text = text.replaceAll("buyer-propensity", "account");
    text = text.replaceAll("Buyer-propensity", "Account");
    text = text.replaceAll("Hard AI evidence", "Matched evidence");
    text = text.replaceAll("Adjacent evidence", "Supporting evidence");
    text = text.replaceAll("hard AI/model/data language", "relevant AI/data language");
    text = text.replaceAll("Reasoning mode: Deterministic rules. AI synthesis is not wired yet.", "Scoring: Evidence-based account ranking. Truth audit: connectors and diagnostics are live; account narratives may include curated demo fallback text until raw evidence rows are fully expanded.");

    if (text.includes("Filter:") && text.includes("Generic test-and-evaluation alone is excluded")) {
      const match = text.match(/Filter:\s*(\d+\s+retained\s*\/\s*\d+\s+fetched)/i);
      text = match ? "Filter: " + match[1] : "Filter: evidence relevance applied";
    }

    node.nodeValue = text;
  }

  function removeUnwiredSavedViews() {
    const savedViews = Array.from(document.querySelectorAll("h3"))
      .filter(h => h.textContent.trim() === "Saved Views");

    for (const heading of savedViews) {
      const box = heading.closest(".box");
      if (box) {
        box.remove();
        continue;
      }

      heading.remove();

      const labels = new Set([
        "Federal AI Evaluation",
        "DoD Modernization",
        "Civilian Agencies",
        "Risk Watch"
      ]);

      Array.from(document.querySelectorAll("button")).forEach(button => {
        if (labels.has(button.textContent.trim())) button.remove();
      });
    }
  }

  function cleanup() {
    removeUnwiredSavedViews();

    const walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT,
      null
    );

    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(replaceTextNode);
  }

  document.addEventListener("DOMContentLoaded", cleanup);
  window.addEventListener("load", cleanup);

  const originalFetch = window.fetch;
  window.fetch = async function () {
    const response = await originalFetch.apply(this, arguments);
    setTimeout(cleanup, 50);
    setTimeout(cleanup, 250);
    return response;
  };

  setInterval(cleanup, 1000);
})();
</script>


<script id="hossagent-eval-ingress-hard-binding">
window.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("evalConsoleButton");
  if (btn) {
    btn.onclick = function (event) {
      event.preventDefault();
      window.location.assign("/eval?v=te-stack");
    };
  }
});
</script>


<script id="hossagent-run-scan-hard-global">
window.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("runBuyerScanButton") || Array.from(document.querySelectorAll("button")).find(b => b.textContent.trim() === "Run Buyer Scan");
  const scanMessage = document.getElementById("scanMessage");
  const progress = document.getElementById("scanProgress");
  const progressState = document.getElementById("scanProgressState");
  const bar = document.getElementById("scanBarFill");
  const steps = Array.from(document.querySelectorAll(".scan-step"));

  function setStep(idx, label) {
    if (progress) progress.classList.add("active");
    if (progressState) progressState.textContent = label;
    if (bar) bar.style.width = `${Math.min(96, 10 + idx * 16)}%`;
    steps.forEach((step, i) => {
      step.classList.toggle("done", i < idx);
      step.classList.toggle("active", i === idx);
      const glyph = step.querySelector(".glyph");
      if (glyph) glyph.textContent = i < idx ? "✓" : (i === idx ? "→" : "○");
    });
  }

  async function hossRunBuyerScan(event) {
    if (event) event.preventDefault();

    const button = btn;
    const businessUnit = document.getElementById("businessUnit")?.value || "Public Sector";
    const market = document.getElementById("market")?.value || "Federal AI Evaluation Model Assurance";

    if (button) {
      button.disabled = true;
      button.classList.add("is-running");
      button.textContent = "Scanning...";
    }

    if (scanMessage) scanMessage.textContent = "Running buyer scan across configured sources...";

    const stages = [
      [0, "Checking config"],
      [1, "Querying USAspending"],
      [2, "Searching Federal Register"],
      [3, "Checking SAM.gov"],
      [4, "Merging evidence"],
      [5, "Ranking accounts"]
    ];

    let stage = 0;
    setStep(0, "Checking config");
    const timer = setInterval(() => {
      stage = Math.min(stage + 1, stages.length - 1);
      setStep(stages[stage][0], stages[stage][1]);
    }, 650);

    try {
      const res = await fetch("/api/market-scan", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({workspace:"Scale AI", business_unit: businessUnit, market})
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Market scan failed ${res.status}: ${text.slice(0, 220)}`);
      }

      const data = await res.json();

      clearInterval(timer);
      if (bar) bar.style.width = "100%";
      if (progressState) progressState.textContent = "Complete";
      steps.forEach(step => {
        step.classList.remove("active");
        step.classList.add("done");
        const glyph = step.querySelector(".glyph");
        if (glyph) glyph.textContent = "✓";
      });

      const setText = (id, value) => {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
      };

      setText("scanMessage", data.message || "Buyer scan complete.");
      setText("countSignals", data.count ?? (data.opportunities || []).length ?? 0);
      setText("activeSources", data.active_sources || "3/3");
      setText("topScore", data.top_score || (data.opportunities?.[0]?.score ?? "—"));

      const fs = data.filter_stats || {};
      setText("filterStats",
        `Filter: ${fs.records_retained ?? fs.retained ?? (data.opportunities || []).length} retained / ${fs.records_fetched ?? fs.fetched ?? "N/A"} fetched · ${(fs.records_excluded ?? fs.weak_matches_excluded ?? 0)} weak matches excluded · ${(fs.records_excluded_old ?? fs.old_records_excluded ?? 0)} old records excluded · cutoff ${(fs.cutoff_date ?? "last 24 months")} · Rule: ${(fs.filter_rule ?? "AI/T&E evidence match")}`
      );

      if (typeof renderOpps === "function") {
        window.opportunities = data.opportunities || [];
        renderOpps(window.opportunities);
        if (window.opportunities.length && typeof selectOpp === "function") selectOpp(0);
      } else {
        console.warn("renderOpps not found; scan API succeeded but UI renderer is missing.");
      }

      setTimeout(() => {
        if (progress) progress.classList.remove("active");
      }, 1000);

    } catch (err) {
      clearInterval(timer);
      if (progressState) progressState.textContent = "Scan failed";
      if (scanMessage) scanMessage.textContent = `Scan failed: ${err.message || err}`;
      console.error(err);
    } finally {
      if (button) {
        button.disabled = false;
        button.classList.remove("is-running");
        button.textContent = "Run Buyer Scan";
      }
    }
  }

  window.runScan = hossRunBuyerScan;
  if (btn) {
    btn.id = "runBuyerScanButton";
    btn.onclick = hossRunBuyerScan;
    btn.disabled = false;
    btn.textContent = "Run Buyer Scan";
  }
});
</script>


<script id="hossagent-eval-self-test-hard-binding">
window.addEventListener("DOMContentLoaded", () => {
  const isEval = window.location.pathname.includes("/eval");
  if (!isEval) return;

  const buttons = Array.from(document.querySelectorAll("button"));
  const selfTestButton = buttons.find(b => /run self test|self test|test/i.test(b.textContent || ""));
  if (!selfTestButton) return;

  let output = document.getElementById("selfTestOutput") || document.getElementById("evalSelfTestOutput");
  if (!output) {
    output = document.createElement("pre");
    output.id = "selfTestOutput";
    output.style.whiteSpace = "pre-wrap";
    output.style.marginTop = "16px";
    output.style.padding = "16px";
    output.style.border = "1px solid rgba(255,255,255,.18)";
    output.style.borderRadius = "16px";
    output.style.background = "rgba(255,255,255,.05)";
    output.style.color = "inherit";
    selfTestButton.insertAdjacentElement("afterend", output);
  }

  selfTestButton.onclick = async (event) => {
    event.preventDefault();
    selfTestButton.disabled = true;
    const original = selfTestButton.textContent;
    selfTestButton.textContent = "Running Self Test...";
    output.textContent = "Running evaluation console self-test...";

    const candidates = [
      "/api/eval/self-test-v6",
      "/api/eval/self-test-v5",
      "/api/eval/self-test-v4",
      "/api/eval/self-test-v3"
    ];

    try {
      let data = null;
      let used = null;
      let lastErr = null;

      for (const path of candidates) {
        try {
          const res = await fetch(`${path}?ts=${Date.now()}`);
          if (!res.ok) {
            lastErr = `${path} returned ${res.status}`;
            continue;
          }
          data = await res.json();
          used = path;
          break;
        } catch (err) {
          lastErr = `${path}: ${err.message || err}`;
        }
      }

      if (!data) throw new Error(lastErr || "No self-test endpoint responded.");

      const checks = data.checks || data.results || [];
      const lines = [];
      lines.push(`Self-test endpoint: ${used}`);
      lines.push(`Status: ${data.status || data.overall_status || "complete"}`);
      lines.push("");

      if (Array.isArray(checks) && checks.length) {
        for (const c of checks) {
          const name = c.name || c.check || c.title || "Check";
          const pass = c.pass ?? c.passed ?? c.ok ?? c.success;
          const detail = c.detail || c.message || c.summary || "";
          lines.push(`${pass ? "✓" : "✕"} ${name}${detail ? " — " + detail : ""}`);
        }
      } else {
        lines.push(JSON.stringify(data, null, 2));
      }

      output.textContent = lines.join("\n");
    } catch (err) {
      output.textContent = `Self-test failed: ${err.message || err}`;
      console.error(err);
    } finally {
      selfTestButton.disabled = false;
      selfTestButton.textContent = original || "Run Self Test";
    }
  };
});
</script>

</body>
</html>"""
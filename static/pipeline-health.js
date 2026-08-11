(() => {
  const root = document.querySelector("[data-pipeline-repair]");
  if (!root) return;

  const stageButtons = Array.from(document.querySelectorAll("[data-repair-stage]"));
  const repairAll = document.getElementById("repair-all");
  const repairReset = document.getElementById("repair-reset");
  const approve = document.getElementById("approve-repaired");
  const repairLog = document.getElementById("repair-log");
  const repairStatus = document.getElementById("repair-status");
  const repairCount = document.getElementById("repair-count");
  const releaseState = document.getElementById("release-state");
  const healthScore = document.getElementById("health-score");
  const healthNote = document.getElementById("health-note");
  const healthLabel = document.getElementById("health-label");
  const repairMode = document.getElementById("repair-mode");
  const baseline = Number.parseInt(root.dataset.healthBaseline || "0", 10);
  const storageKey = `hossagent.pipeline-repair.${window.location.pathname}`;
  let running = false;
  let completed = new Set();
  let approved = false;

  const wait = (milliseconds) => new Promise((resolve) => window.setTimeout(resolve, milliseconds));

  function saveState() {
    try {
      window.sessionStorage.setItem(storageKey, JSON.stringify({ completed: Array.from(completed), approved }));
    } catch (_error) {
      // The repair remains functional even when browser storage is unavailable.
    }
  }

  function readState() {
    try {
      const saved = JSON.parse(window.sessionStorage.getItem(storageKey) || "null");
      if (saved && Array.isArray(saved.completed)) completed = new Set(saved.completed);
      approved = Boolean(saved && saved.approved);
    } catch (_error) {
      completed = new Set();
      approved = false;
    }
  }

  function appendLog(stage, action, result, tone = "repaired") {
    repairLog.querySelector(".repair-placeholder")?.remove();
    const item = document.createElement("li");
    item.className = tone;
    const stamp = document.createElement("span");
    stamp.textContent = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    const copy = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = `${stage} · ${action}`;
    const detail = document.createElement("p");
    detail.textContent = result;
    copy.append(title, detail);
    item.append(stamp, copy);
    repairLog.prepend(item);
  }

  function updateCheck() {
    const check = document.querySelector('[data-check]:not([data-state="healthy"])');
    if (!check) return;
    check.dataset.state = "healthy";
    const status = check.querySelector("[data-check-status]");
    const percent = check.querySelector("[data-check-percent]");
    const count = check.querySelector("[data-check-count]");
    if (status) {
      status.className = "healthy";
      status.textContent = "Revalidated";
    }
    if (percent) percent.textContent = "100%";
    if (count) count.textContent = "Eligible set rechecked";
  }

  function applyStageRepair(button, result) {
    const stage = button.dataset.stage;
    const card = document.querySelector(`[data-stage-card][data-stage="${CSS.escape(stage)}"]`);
    if (!card) return;
    card.dataset.state = "healthy";
    card.classList.remove("is-repairing");
    card.classList.add("is-repaired");
    const status = card.querySelector("[data-stage-status]");
    const detail = card.querySelector("[data-stage-detail]");
    const posture = card.querySelector("[data-stage-posture]");
    if (status) {
      status.className = "pipeline-status healthy";
      status.textContent = "Repaired";
    }
    if (detail) detail.textContent = result;
    if (posture) posture.textContent = "Revalidated";
    button.disabled = true;
    button.innerHTML = 'Repaired <span aria-hidden="true">✓</span>';

    document.querySelectorAll(`[data-blocker][data-stage="${CSS.escape(stage)}"]`).forEach((row) => {
      row.classList.add("is-resolved");
      const reason = row.querySelector("[data-blocker-reason]");
      const control = row.querySelector("[data-blocker-repair]");
      if (reason) reason.textContent = result;
      if (control) {
        control.disabled = true;
        control.innerHTML = 'Resolved <span aria-hidden="true">✓</span>';
      }
    });
    updateCheck();
  }

  function updateProgress() {
    const total = stageButtons.length;
    const count = completed.size;
    const percentage = total === 0 ? 100 : Math.min(100, Math.round(baseline + ((100 - baseline) * count / total)));
    if (healthScore) healthScore.textContent = `${percentage}%`;
    if (repairCount) repairCount.textContent = `${count} of ${total} repairs completed`;
    if (count === total) {
      if (healthLabel) healthLabel.textContent = "Revalidated health";
      if (healthNote) healthNote.textContent = "Repairable conditions cleared · operator release decision remains";
      if (repairStatus) repairStatus.textContent = "Pipeline repaired and rechecked";
      if (repairMode) repairMode.textContent = "Repair complete";
      if (releaseState) releaseState.textContent = approved ? "Repaired set approved for decision queue" : "Ready for operator approval";
      if (approve) {
        approve.disabled = approved;
        approve.textContent = approved ? "Approved ✓" : "Approve repaired set";
      }
      if (repairAll) {
        repairAll.disabled = true;
        repairAll.innerHTML = 'Pipeline repaired <span aria-hidden="true">✓</span>';
      }
    } else {
      if (healthNote) healthNote.textContent = `${total - count} bounded repairs remain`;
      if (releaseState) releaseState.textContent = "Held until repairs finish";
      if (approve) approve.disabled = true;
    }
  }

  async function repairStage(button) {
    const stage = button.dataset.stage;
    if (!stage || completed.has(stage)) return;
    const card = document.querySelector(`[data-stage-card][data-stage="${CSS.escape(stage)}"]`);
    const action = button.dataset.repairAction || button.textContent.trim();
    const result = button.dataset.repairResult || "Evidence rechecked and unsafe records held.";
    if (card) card.classList.add("is-repairing");
    const status = card?.querySelector("[data-stage-status]");
    if (status) {
      status.className = "pipeline-status repairing";
      status.textContent = "Repairing";
    }
    button.disabled = true;
    button.textContent = "Repairing…";
    if (repairStatus) repairStatus.textContent = `${action} · ${stage}`;
    await wait(window.matchMedia("(prefers-reduced-motion: reduce)").matches ? 20 : 650);
    completed.add(stage);
    applyStageRepair(button, result);
    appendLog(stage, action, result);
    saveState();
    updateProgress();
  }

  async function runAllRepairs() {
    if (running) return;
    running = true;
    if (repairAll) {
      repairAll.disabled = true;
      repairAll.textContent = "Repairing pipeline…";
    }
    if (repairStatus) repairStatus.textContent = "Executing bounded repair plan";
    for (const button of stageButtons) {
      if (!completed.has(button.dataset.stage)) await repairStage(button);
    }
    running = false;
    updateProgress();
  }

  stageButtons.forEach((button) => button.addEventListener("click", () => repairStage(button)));
  document.querySelectorAll("[data-blocker-repair]").forEach((button) => {
    button.addEventListener("click", () => {
      const stageButton = stageButtons.find((candidate) => candidate.dataset.stage === button.dataset.stage);
      if (stageButton) repairStage(stageButton);
    });
  });
  repairAll?.addEventListener("click", runAllRepairs);
  repairReset?.addEventListener("click", () => {
    try { window.sessionStorage.removeItem(storageKey); } catch (_error) { /* no-op */ }
    window.location.reload();
  });
  approve?.addEventListener("click", () => {
    if (completed.size !== stageButtons.length) return;
    approved = true;
    appendLog("Operator authority", "Approved repaired set", "The repaired evidence set may return to the decision queue; no external action was released.", "approved");
    saveState();
    updateProgress();
  });

  readState();
  completed.forEach((stage) => {
    const button = stageButtons.find((candidate) => candidate.dataset.stage === stage);
    if (button) applyStageRepair(button, button.dataset.repairResult || "Revalidated");
  });
  updateProgress();
  if (completed.size < stageButtons.length) window.setTimeout(runAllRepairs, 900);
})();

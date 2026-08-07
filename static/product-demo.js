(() => {
  const configNode = document.getElementById("hoss-demo-config");
  const demo = configNode ? JSON.parse(configNode.textContent) : null;
  if (!demo || !Array.isArray(demo.steps) || !demo.steps.length) return;

  const escapeHtml = (value) => String(value ?? "").replace(/[&<>'"]/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
  })[character]);

  const steps = demo.steps;
  const stepList = document.getElementById("demo-step-list");
  const stageMount = document.getElementById("demo-stage-mount");
  const captionLabel = document.getElementById("demo-caption-label");
  const caption = document.getElementById("demo-caption");
  const stateLabel = document.getElementById("demo-state-label");
  const stageNumber = document.getElementById("demo-stage-number");
  const stageKicker = document.getElementById("demo-stage-kicker");
  const stageTitle = document.getElementById("demo-stage-title");
  const counter = document.getElementById("demo-counter");
  const cursor = document.getElementById("demo-cursor");
  const toast = document.getElementById("demo-toast");
  const playButton = document.getElementById("demo-play");
  const playIcon = document.getElementById("demo-play-icon");
  const playLabel = document.getElementById("demo-play-label");
  const progress = document.getElementById("demo-timeline-progress");
  const speedSelect = document.getElementById("demo-speed");
  const viewport = document.querySelector(".demo-viewport");

  let currentStep = 0;
  let playing = true;
  let speed = 1;
  let stageTotal = 6900;
  let stageElapsed = 0;
  let stageStarted = 0;
  let advanceTimer = null;
  let frame = null;
  let effectTimers = [];
  let toastTimer = null;

  stepList.innerHTML = steps.map((step, index) => `
    <button type="button" data-step="${index}"${index === 0 ? ' aria-current="step"' : ""}>
      <span>${String(index + 1).padStart(2, "0")}</span>
      <strong>${escapeHtml(step.navTitle)}</strong>
      <small>${escapeHtml(step.navMeta)}</small>
    </button>`).join("");
  const stepButtons = [...stepList.querySelectorAll("[data-step]")];

  const clearEffects = () => {
    effectTimers.forEach(window.clearTimeout);
    effectTimers = [];
    window.clearTimeout(toastTimer);
    toast.classList.remove("show");
    cursor.classList.remove("visible", "clicking");
    document.querySelectorAll(".demo-target-pulse").forEach((node) => node.classList.remove("demo-target-pulse"));
  };

  const later = (callback, delay) => {
    const timer = window.setTimeout(callback, Math.max(100, delay / speed));
    effectTimers.push(timer);
  };

  const showToast = (message) => {
    toast.textContent = message;
    toast.classList.add("show");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove("show"), 2200 / speed);
  };

  const moveCursor = (target, message) => {
    if (!target || window.matchMedia("(max-width: 820px)").matches) return;
    const targetBox = target.getBoundingClientRect();
    const viewportBox = viewport.getBoundingClientRect();
    cursor.style.left = `${targetBox.left - viewportBox.left + Math.min(targetBox.width * .78, targetBox.width - 10)}px`;
    cursor.style.top = `${targetBox.top - viewportBox.top + Math.min(targetBox.height * .64, targetBox.height - 7)}px`;
    cursor.classList.add("visible");
    later(() => {
      cursor.classList.remove("clicking");
      void cursor.offsetWidth;
      cursor.classList.add("clicking");
      target.classList.remove("demo-target-pulse");
      void target.offsetWidth;
      target.classList.add("demo-target-pulse");
      showToast(message);
    }, 850);
  };

  const metricMarkup = (metric) => `<article class="${escapeHtml(metric.tone || "")}"><span>${escapeHtml(metric.label)}</span><strong>${escapeHtml(metric.value)}</strong><p>${escapeHtml(metric.detail)}</p></article>`;
  const sourceMarkup = (source, index) => `<li style="--row-delay:${index * 110}ms"><i>${escapeHtml(source.kind)}</i><div><strong>${escapeHtml(source.name)}</strong><span>${escapeHtml(source.meta)}</span></div><em>${escapeHtml(source.status)}</em></li>`;
  const recordMarkup = (record, index) => `<div class="${escapeHtml(record.tone || "")}" style="--row-delay:${(index + 3) * 110}ms"><span>${escapeHtml(record.label)}</span><strong>${escapeHtml(record.value)}</strong><em>${escapeHtml(record.status)}</em></div>`;

  const artifactMarkup = (artifact) => {
    if (!artifact) return "";
    return `<div class="portfolio-artifact" aria-label="Customer artifact preview">
      <header><span>HOSSAGENT / ${escapeHtml(demo.division).toUpperCase()}</span><em>${escapeHtml(artifact.type)}</em></header>
      <div><p>Recorded disposition</p><strong>${escapeHtml(artifact.decision)}</strong><small>${escapeHtml(demo.workspace)}</small></div>
      <footer><span>Decision owner · ${escapeHtml(artifact.owner)}</span><span>${escapeHtml(artifact.reference)}</span></footer>
    </div>`;
  };

  const renderStage = (step) => {
    const guardrailTone = ["pass", "hold", "block"].includes(step.guardrailTone) ? step.guardrailTone : "hold";
    stageMount.innerHTML = `
      <div class="portfolio-stage-copy">
        <div><p class="demo-section-label">${escapeHtml(step.sourceTitle)}</p><h2>${escapeHtml(step.title)}</h2><p>${escapeHtml(step.description)}</p></div>
        <ul class="portfolio-source-list">${step.sources.map(sourceMarkup).join("")}</ul>
      </div>
      <div class="portfolio-stage-data">
        <div class="portfolio-metrics">${step.metrics.map(metricMarkup).join("")}</div>
        <div class="portfolio-records">${step.records.map(recordMarkup).join("")}</div>
        <div class="portfolio-reasoning">
          <div><span>${escapeHtml(step.recommendationLabel)}</span><strong>${escapeHtml(step.recommendation)}</strong><p>${escapeHtml(step.recommendationDetail)}</p></div>
          <aside class="${guardrailTone}" id="demo-guardrail"><span>${escapeHtml(step.guardrailLabel)}</span><strong>${escapeHtml(step.guardrail)}</strong><p>${escapeHtml(step.guardrailDetail)}</p></aside>
        </div>
        ${artifactMarkup(step.artifact)}
      </div>
      <div class="demo-panel-foot portfolio-stage-foot">
        <span>${escapeHtml(step.caption)}</span>
        <button type="button" class="demo-action" id="demo-primary-action">${escapeHtml(step.actionLabel)} <b>${step.artifact ? "↗" : "→"}</b></button>
      </div>
      ${step.artifact ? `<div class="demo-finish portfolio-finish"><div><span>${escapeHtml(demo.finishLabel)}</span><strong>${escapeHtml(demo.finishTitle)}</strong></div><a href="/request-access">${escapeHtml(demo.finishCta)} →</a></div>` : ""}`;

    document.getElementById("demo-primary-action").addEventListener("click", () => {
      showToast(step.toast);
      if (!step.artifact) later(() => setStep(currentStep + 1), 450);
    });
  };

  const updatePlaybackButton = () => {
    playIcon.textContent = playing ? "Ⅱ" : "▶";
    playLabel.textContent = playing ? "Pause" : "Play";
    playButton.setAttribute("aria-label", playing ? "Pause demo" : "Play demo");
  };

  const updateProgress = (now) => {
    if (!playing) return;
    const elapsed = Math.min(stageTotal, stageElapsed + (now - stageStarted));
    progress.style.width = `${((currentStep + elapsed / stageTotal) / steps.length) * 100}%`;
    frame = window.requestAnimationFrame(updateProgress);
  };

  const scheduleAdvance = () => {
    window.clearTimeout(advanceTimer);
    window.cancelAnimationFrame(frame);
    if (!playing) return;
    const remaining = Math.max(0, stageTotal - stageElapsed);
    stageStarted = performance.now();
    advanceTimer = window.setTimeout(() => setStep(currentStep === steps.length - 1 ? 0 : currentStep + 1), remaining);
    frame = window.requestAnimationFrame(updateProgress);
  };

  const runStageEffects = (step) => {
    later(() => document.getElementById("demo-guardrail")?.classList.add("demo-target-pulse"), 1250);
    later(() => moveCursor(document.getElementById("demo-primary-action"), step.toast), 3350);
  };

  function setStep(index) {
    window.clearTimeout(advanceTimer);
    window.cancelAnimationFrame(frame);
    clearEffects();
    currentStep = (index + steps.length) % steps.length;
    const step = steps[currentStep];
    renderStage(step);
    stepButtons.forEach((button, buttonIndex) => {
      if (buttonIndex === currentStep) button.setAttribute("aria-current", "step");
      else button.removeAttribute("aria-current");
    });
    captionLabel.textContent = step.label;
    caption.textContent = step.caption;
    stateLabel.textContent = step.state;
    stageNumber.textContent = String(currentStep + 1).padStart(2, "0");
    stageKicker.textContent = step.kicker;
    stageTitle.textContent = step.title;
    counter.textContent = `${currentStep + 1} / ${steps.length}`;
    stageTotal = (step.artifact ? 9200 : 6900) / speed;
    stageElapsed = 0;
    progress.style.width = `${(currentStep / steps.length) * 100}%`;
    if (playing) runStageEffects(step);
    scheduleAdvance();
  }

  const pause = () => {
    if (!playing) return;
    stageElapsed = Math.min(stageTotal, stageElapsed + (performance.now() - stageStarted));
    playing = false;
    window.clearTimeout(advanceTimer);
    window.cancelAnimationFrame(frame);
    clearEffects();
    updatePlaybackButton();
  };

  const play = () => {
    if (playing) return;
    if (stageElapsed >= stageTotal) stageElapsed = 0;
    playing = true;
    updatePlaybackButton();
    runStageEffects(steps[currentStep]);
    scheduleAdvance();
  };

  playButton.addEventListener("click", () => playing ? pause() : play());
  document.getElementById("demo-restart").addEventListener("click", () => {
    playing = true;
    updatePlaybackButton();
    setStep(0);
  });
  document.getElementById("demo-next").addEventListener("click", () => setStep(currentStep + 1));
  speedSelect.addEventListener("change", () => {
    speed = Number(speedSelect.value) || 1;
    setStep(currentStep);
  });
  stepButtons.forEach((button) => button.addEventListener("click", () => setStep(Number(button.dataset.step))));

  document.addEventListener("keydown", (event) => {
    if (["INPUT", "SELECT", "TEXTAREA"].includes(document.activeElement.tagName)) return;
    if (event.code === "Space") {
      event.preventDefault();
      playing ? pause() : play();
    } else if (event.key === "ArrowRight") setStep(currentStep + 1);
    else if (event.key === "ArrowLeft") setStep(currentStep - 1);
  });
  document.addEventListener("visibilitychange", () => { if (document.hidden) pause(); });

  updatePlaybackButton();
  window.setTimeout(() => setStep(0), 450);
})();

(() => {
  const steps = [
    {
      label: "01 · Define",
      caption: "Start with the consequential question—not a generic analytics dashboard.",
      state: "Configuring",
      kicker: "Evaluation definition",
      title: "Freeze the question before run one.",
      target: "#demo-freeze",
      toast: "Evaluation frozen · HA-EVAL-001",
      duration: 6200,
    },
    {
      label: "02 · Evidence",
      caption: "A small mission-aware event contract connects release exposure to workflow, outcome, and guardrail evidence.",
      state: "Importing",
      kicker: "Evidence intake",
      title: "Bring pseudonymous run evidence into the customer boundary.",
      target: "#demo-import",
      toast: "32 normalized events ready for validation",
      duration: 5900,
    },
    {
      label: "03 · Validate",
      caption: "Bad or incomplete evidence is blocked before analysis. Accepted runs keep their release and analysis lineage.",
      state: "Validating",
      kicker: "Contract review",
      title: "Prove the evidence is fit for the declared decision.",
      target: "#demo-analyze",
      toast: "Evidence contract accepted · 97.8% complete",
      duration: 5700,
    },
    {
      label: "04 · Analyze",
      caption: "The overall release looks faster, but cohort review exposes unacceptable trainee false escalation.",
      state: "Analyzing",
      kicker: "Cohort comparison",
      title: "Let guardrails outrank the attractive average.",
      target: "#demo-trainee",
      toast: "Trainee guardrail crossed · 37.5% observed",
      duration: 7200,
    },
    {
      label: "05 · Decide",
      caption: "HossAgent recommends an action with limitations. The named mission owner records the actual disposition.",
      state: "Reviewing",
      kicker: "Human decision",
      title: "Retain authority and capture the rationale.",
      target: "#demo-modify",
      toast: "Decision signed by Mission Product Owner",
      duration: 6800,
    },
    {
      label: "06 · Brief",
      caption: "The result leaves the dashboard as a reproducible evidence package for product, test, and authorization review.",
      state: "Complete",
      kicker: "Evidence package",
      title: "Export the decision, lineage, findings, and claim boundary.",
      target: "#demo-brief",
      toast: "PDF and HTML evidence briefs ready",
      duration: 9000,
    },
  ];

  const panels = [...document.querySelectorAll("[data-panel]")];
  const stepButtons = [...document.querySelectorAll("[data-step]")];
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
  let stageTotal = steps[0].duration;
  let stageElapsed = 0;
  let stageStarted = 0;
  let advanceTimer = null;
  let frame = null;
  let effectTimers = [];
  let toastTimer = null;

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

  const moveCursor = (selector, message, options = {}) => {
    const target = document.querySelector(selector);
    if (!target || window.matchMedia("(max-width: 820px)").matches) return;
    const targetBox = target.getBoundingClientRect();
    const viewportBox = viewport.getBoundingClientRect();
    cursor.style.left = `${targetBox.left - viewportBox.left + Math.min(targetBox.width * .72, targetBox.width - 8)}px`;
    cursor.style.top = `${targetBox.top - viewportBox.top + Math.min(targetBox.height * .62, targetBox.height - 6)}px`;
    cursor.classList.add("visible");
    later(() => {
      cursor.classList.remove("clicking");
      void cursor.offsetWidth;
      cursor.classList.add("clicking");
      target.classList.remove("demo-target-pulse");
      void target.offsetWidth;
      target.classList.add("demo-target-pulse");
      if (options.select) target.classList.add("selected");
      if (options.highlight) target.classList.add("demo-highlight");
      if (message) showToast(message);
    }, 850);
  };

  const updatePlaybackButton = () => {
    playIcon.textContent = playing ? "Ⅱ" : "▶";
    playLabel.textContent = playing ? "Pause" : "Play";
    playButton.setAttribute("aria-label", playing ? "Pause demo" : "Play demo");
  };

  const updateProgress = (now) => {
    if (playing) {
      const elapsed = Math.min(stageTotal, stageElapsed + (now - stageStarted));
      const totalProgress = ((currentStep + elapsed / stageTotal) / steps.length) * 100;
      progress.style.width = `${totalProgress}%`;
      frame = window.requestAnimationFrame(updateProgress);
    }
  };

  const scheduleAdvance = () => {
    window.clearTimeout(advanceTimer);
    window.cancelAnimationFrame(frame);
    if (!playing) return;
    const remaining = Math.max(0, stageTotal - stageElapsed);
    stageStarted = performance.now();
    advanceTimer = window.setTimeout(() => {
      if (currentStep === steps.length - 1) setStep(0);
      else setStep(currentStep + 1);
    }, remaining);
    frame = window.requestAnimationFrame(updateProgress);
  };

  const runStageEffects = (index) => {
    const step = steps[index];
    document.getElementById("demo-modify").classList.remove("selected");
    document.getElementById("demo-trainee").classList.remove("demo-highlight");
    if (index === 0) {
      later(() => moveCursor(step.target, step.toast), 3400);
    } else if (index === 1) {
      later(() => {
        document.getElementById("demo-dropzone").classList.add("demo-target-pulse");
        showToast("Synthetic event file detected · 8.4 KB");
      }, 850);
      later(() => moveCursor(step.target, step.toast), 3000);
    } else if (index === 2) {
      later(() => moveCursor(step.target, step.toast), 3000);
    } else if (index === 3) {
      later(() => moveCursor(step.target, step.toast, { highlight: true }), 1800);
      later(() => moveCursor("#demo-review", "Recommendation: modify before broader exposure"), 4700);
    } else if (index === 4) {
      later(() => moveCursor(step.target, "Modify selected · guardrail precedence", { select: true }), 1200);
      later(() => moveCursor("#demo-sign", step.toast), 3900);
    } else if (index === 5) {
      later(() => moveCursor(step.target, step.toast), 2800);
    }
  };

  function setStep(index) {
    window.clearTimeout(advanceTimer);
    window.cancelAnimationFrame(frame);
    clearEffects();
    currentStep = (index + steps.length) % steps.length;
    const step = steps[currentStep];
    panels.forEach((panel, panelIndex) => panel.classList.toggle("active", panelIndex === currentStep));
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
    stageTotal = step.duration / speed;
    stageElapsed = 0;
    progress.style.width = `${(currentStep / steps.length) * 100}%`;
    if (playing) runStageEffects(currentStep);
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
    runStageEffects(currentStep);
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

  const nextTargets = ["demo-freeze", "demo-import", "demo-analyze", "demo-review", "demo-sign"];
  nextTargets.forEach((id, index) => document.getElementById(id).addEventListener("click", () => setStep(index + 1)));
  document.getElementById("demo-trainee").addEventListener("click", (event) => event.currentTarget.classList.toggle("demo-highlight"));
  document.getElementById("demo-modify").addEventListener("click", (event) => event.currentTarget.classList.toggle("selected"));
  document.getElementById("demo-brief").addEventListener("click", () => showToast("Demo evidence brief generated · no file written"));

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
  window.setTimeout(() => setStep(0), 650);
})();

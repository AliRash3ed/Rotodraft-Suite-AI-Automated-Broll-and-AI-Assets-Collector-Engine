/* ==========================================================================
   ROTODRAFT SUITE - INTERACTIVE CONTROLLER & STREAMING ENGINE
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const form = document.getElementById("generateForm");
  const scriptInput = document.getElementById("scriptInput");
  const durationInput = document.getElementById("durationInput");
  const clipDurationInput = document.getElementById("clipDurationInput");
  const clipCalcBadge = document.getElementById("clipCalcBadge");
  const wordCountBadge = document.getElementById("wordCountBadge");
  const modeSelect = document.getElementById("modeSelect");
  const voiceGroup = document.getElementById("voiceGroup");
  const submitBtn = document.getElementById("submitBtn");
  
  // Progress & Terminal
  const progressBar = document.getElementById("progressBar");
  const progressText = document.getElementById("progressText");
  const terminal = document.getElementById("terminal");
  const clipsGrid = document.getElementById("clipsGrid");
  const masterContainer = document.getElementById("masterContainer");
  const masterVideo = document.getElementById("masterVideo");
  const exportActions = document.getElementById("exportActions");
  const downloadZipBtn = document.getElementById("downloadZipBtn");
  const openFolderBtn = document.getElementById("openFolderBtn");
  const downloadXmlBtn = document.getElementById("downloadXmlBtn");

  // Modals & Settings
  const settingsModal = document.getElementById("settingsModal");
  const openSettingsBtn = document.getElementById("openSettingsBtn");
  const closeSettingsBtn = document.getElementById("closeSettingsBtn");
  const themeToggleBtn = document.getElementById("themeToggleBtn");

  let currentProjectId = null;
  let currentProjectDir = null;
  let currentXmlUrl = null;

  // Theme Initializer
  const savedTheme = localStorage.getItem("rotodraft_theme") || "dark";
  document.documentElement.setAttribute("data-theme", savedTheme);
  updateThemeIcon(savedTheme);

  themeToggleBtn.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("rotodraft_theme", next);
    updateThemeIcon(next);
  });

  function updateThemeIcon(theme) {
    themeToggleBtn.textContent = theme === "dark" ? "☀️ LIGHT" : "🌙 DARK";
  }

  // Live Time Parsing & Calculation Helper
  function parseDurationInput(val) {
    val = (val || "").trim();
    if (val.includes(":")) {
      const parts = val.split(":");
      const mins = parseFloat(parts[0]) || 0;
      const secs = parseFloat(parts[1]) || 0;
      return mins * 60 + secs;
    }
    return parseFloat(val) || 0;
  }

  function updateCalculation() {
    const text = (scriptInput.value || "").trim();
    const words = text ? text.split(/\s+/).length : 0;
    wordCountBadge.textContent = `${words} WORDS`;

    let dur = parseDurationInput(durationInput.value);
    const clipDur = parseFloat(clipDurationInput.value) || 3.0;

    // Estimate duration from word count if empty (avg ~140 wpm = ~2.3 words/sec)
    if (dur <= 0 && words > 0) {
      dur = Math.round(words / 2.3);
    }

    const calculatedClips = Math.max(1, Math.ceil(dur / clipDur));
    clipCalcBadge.textContent = `${dur.toFixed(0)}s TOTAL -> ~${calculatedClips} CLIPS (${clipDur}s EACH)`;
  }

  scriptInput.addEventListener("input", updateCalculation);
  durationInput.addEventListener("input", updateCalculation);
  clipDurationInput.addEventListener("change", updateCalculation);

  // Mode Selection Toggle
  modeSelect.addEventListener("change", () => {
    const mode = modeSelect.value;
    if (mode === "stock_only") {
      voiceGroup.style.display = "none";
    } else {
      voiceGroup.style.display = "flex";
    }
  });

  // Settings Modal Handlers
  openSettingsBtn.addEventListener("click", () => settingsModal.classList.add("active"));
  closeSettingsBtn.addEventListener("click", () => settingsModal.classList.remove("active"));
  window.addEventListener("click", (e) => {
    if (e.target === settingsModal) settingsModal.classList.remove("active");
  });

  // API Key Tester
  document.querySelectorAll(".test-key-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const provider = btn.getAttribute("data-provider");
      const input = document.getElementById(`${provider}KeyInput`);
      const statusSpan = document.getElementById(`${provider}KeyStatus`);
      
      const key = (input.value || "").trim();
      if (!key) {
        statusSpan.textContent = "⚠️ Please enter key first";
        statusSpan.style.color = "#FF3366";
        return;
      }

      statusSpan.textContent = "⏳ Testing...";
      statusSpan.style.color = "#FFE600";

      try {
        const resp = await fetch("/api/test-key", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ provider, api_key: key })
        });
        const data = await resp.json();
        if (data.success) {
          statusSpan.textContent = "✅ Valid & Active";
          statusSpan.style.color = "#00FF66";
        } else {
          statusSpan.textContent = `❌ ${data.message}`;
          statusSpan.style.color = "#FF3366";
        }
      } catch (err) {
        statusSpan.textContent = "❌ Connection failed";
        statusSpan.style.color = "#FF3366";
      }
    });
  });

  // Terminal Logger
  function logTerminal(msg, level = "info") {
    const line = document.createElement("div");
    line.className = `terminal-line ${level}`;
    const time = new Date().toLocaleTimeString();
    line.textContent = `[${time}] ${msg}`;
    terminal.appendChild(line);
    terminal.scrollTop = terminal.scrollHeight;
  }

  function setProgress(pct, text) {
    progressBar.style.width = `${pct}%`;
    progressText.textContent = text || `${Math.round(pct)}%`;
  }

  // Pipeline Execution via SSE Stream
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const script = (scriptInput.value || "").trim();
    if (!script) {
      alert("Please enter a voiceover script.");
      return;
    }

    const duration = parseDurationInput(durationInput.value) || 30.0;
    const clipDuration = parseFloat(clipDurationInput.value) || 3.0;
    const mode = modeSelect.value;
    const aspect_ratio = document.querySelector('input[name="aspect_ratio"]:checked')?.value || "16:9";
    const quality = document.getElementById("qualitySelect").value;
    const voice = document.getElementById("voiceSelect").value;
    const mood = document.getElementById("moodSelect").value;
    const projectName = (document.getElementById("projectNameInput").value || "RotoDraft_Project").trim();

    // BYOK Keys
    const openrouter_key = document.getElementById("openrouterKeyInput")?.value || "";
    const openrouter_model = document.getElementById("openrouterModelSelect")?.value || "openrouter/free";
    const pexels_key = document.getElementById("pexelsKeyInput")?.value || "";
    const pixabay_key = document.getElementById("pixabayKeyInput")?.value || "";

    // Reset UI State
    submitBtn.disabled = true;
    submitBtn.textContent = "⏳ PROCESSING PRODUCTION...";
    terminal.innerHTML = "";
    clipsGrid.innerHTML = "";
    masterContainer.style.display = "none";
    exportActions.style.display = "none";
    setProgress(0, "INITIALIZING...");

    logTerminal(`Starting pipeline in ${mode.toUpperCase()} mode for '${projectName}'...`);

    const payload = {
      mode,
      script,
      duration_seconds: duration,
      clip_duration: clipDuration,
      aspect_ratio,
      quality,
      voice,
      mood,
      project_name: projectName,
      openrouter_key,
      openrouter_model,
      pexels_key,
      pixabay_key
    };

    try {
      const response = await fetch("/api/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split("\n\n");
        buffer = events.pop(); // Keep incomplete chunk

        for (const eventBlock of events) {
          const trimmed = eventBlock.trim();
          if (!trimmed.startsWith("data:")) continue;

          try {
            const data = JSON.parse(trimmed.replace(/^data:\s*/, ""));
            handleStreamEvent(data, aspect_ratio);
          } catch (jsonErr) {
            console.error("JSON parse error on SSE:", jsonErr);
          }
        }
      }
    } catch (err) {
      logTerminal(`Critical Pipeline Error: ${err.message}`, "error");
      setProgress(0, "FAILED");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "🚀 GENERATE & COLLECT ASSETS";
    }
  });

  function handleStreamEvent(data, aspect_ratio) {
    if (data.type === "log") {
      logTerminal(data.message);
      if (data.progress !== undefined) {
        setProgress(data.progress);
      }
    } else if (data.type === "clip_ready") {
      const clip = data.clip;
      const card = document.createElement("div");
      card.className = "clip-card";
      const isVertical = aspect_ratio === "9:16";

      card.innerHTML = `
        <div class="clip-preview ${isVertical ? 'vertical' : ''}">
          <video src="${clip.url}" controls preload="metadata" loop></video>
        </div>
        <div class="clip-info">
          <div class="clip-tag">#${clip.index} • [${clip.time_start}s - ${clip.time_end}s] • ${clip.provider}</div>
          <div class="clip-kw" title="${clip.keyword}">${clip.keyword}</div>
        </div>
      `;
      clipsGrid.appendChild(card);
      logTerminal(`✨ Clip #${clip.index} ready: ${clip.filename}`);
    } else if (data.type === "done") {
      setProgress(100, "COMPLETED");
      logTerminal(data.message, "info");
      
      currentProjectId = data.project_id;
      currentProjectDir = data.project_dir;
      currentXmlUrl = data.xml_url;

      // Master Video Player
      if (data.master_url) {
        masterVideo.src = data.master_url;
        masterContainer.style.display = "flex";
      }

      // Show Export Actions
      exportActions.style.display = "flex";
    } else if (data.type === "error") {
      logTerminal(`ERROR: ${data.message}`, "error");
      setProgress(0, "ERROR OCCURRED");
    }
  }

  // Export Action Handlers
  openFolderBtn.addEventListener("click", async () => {
    if (!currentProjectDir) return;
    try {
      const res = await fetch("/api/open-folder", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: currentProjectDir })
      });
      const data = await res.json();
      if (data.success) {
        logTerminal(`📂 ${data.message}`);
      }
    } catch (e) {
      logTerminal(`Failed to open folder: ${e.message}`, "error");
    }
  });

  downloadZipBtn.addEventListener("click", () => {
    if (!currentProjectId) return;
    window.location.href = `/api/download-zip/${currentProjectId}`;
  });

  downloadXmlBtn.addEventListener("click", () => {
    if (!currentXmlUrl) return;
    window.location.href = currentXmlUrl;
  });

  // Initial Calculation Run
  updateCalculation();
});

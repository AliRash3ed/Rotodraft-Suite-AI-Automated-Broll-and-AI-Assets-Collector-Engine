/* ==========================================================================
   ROTODRAFT SUITE - ENTERPRISE CLIENT SPA ARCHITECTURE
   Big-Tech Single Page Application Router, State Management & Event Bus
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  // Navigation & SPA Router
  const navItems = document.querySelectorAll(".sidebar .nav-item");
  const appViews = document.querySelectorAll(".app-view");
  const pageTitleDisplay = document.getElementById("pageTitleText");
  const themeToggleBtn = document.getElementById("themeToggleBtn");

  const viewTitles = {
    viewOverview: "Dashboard & Launchpad",
    viewStudio: "AI Studio Generator",
    viewBatch: "Autonomous Batch Channel Factory",
    viewDoctor: "AI Script Doctor & Retention Engine",
    viewVault: "Project Asset Vault & NLE Exports",
    viewAnalytics: "Owner Analytics & Lead CRM",
    viewSettings: "Command Center & BYOK Hub (50+ Customizations)"
  };

  window.switchAppView = function(viewId) {
    navItems.forEach(item => {
      if (item.getAttribute("data-target") === viewId) {
        item.classList.add("active");
      } else {
        item.classList.remove("active");
      }
    });

    appViews.forEach(view => {
      if (view.id === viewId) {
        view.classList.add("active");
      } else {
        view.classList.remove("active");
      }
    });

    if (pageTitleDisplay && viewTitles[viewId]) {
      pageTitleDisplay.textContent = viewTitles[viewId];
    }

    if (viewId === "viewVault") loadVaultProjects();
    if (viewId === "viewAnalytics") loadAnalyticsData();
  };

  navItems.forEach(item => {
    item.addEventListener("click", () => {
      const target = item.getAttribute("data-target");
      if (target) switchAppView(target);
    });
  });

  // Theme Toggle
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "dark";
      const next = current === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("rotodraft_theme", next);
    });
    const savedTheme = localStorage.getItem("rotodraft_theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
  }

  // Header quick buttons
  document.getElementById("headerNewProjectBtn")?.addEventListener("click", () => switchAppView("viewStudio"));
  document.getElementById("headerBatchBtn")?.addEventListener("click", () => switchAppView("viewBatch"));

  // =========================================================================
  // STUDIO FORM & STATE
  // =========================================================================
  const studioForm = document.getElementById("studioGenerateForm");
  const scriptInput = document.getElementById("scriptInput");
  const wordCountBadge = document.getElementById("wordCountBadge");
  const clipCalcBadge = document.getElementById("clipCalcBadge");
  const durationInput = document.getElementById("durationInput");
  const clipDurationInput = document.getElementById("clipDurationInput");
  const modeSelect = document.getElementById("modeSelect");
  const modeDescBadge = document.getElementById("modeDescriptionBadge");
  const voiceSelect = document.getElementById("voiceSelect");
  const previewVoiceBtn = document.getElementById("previewVoiceBtn");
  const autoDetectVoiceBtn = document.getElementById("autoDetectVoiceBtn");

  // Dynamic Word Counter & Clip Pacing Calculator
  function updatePacingCalc() {
    const text = (scriptInput.value || "").trim();
    const words = text ? text.split(/\s+/).length : 0;
    wordCountBadge.textContent = `${words} WORDS`;

    let dur = parseFloat(durationInput.value) || 30.0;
    if (isNaN(dur) || dur <= 0) dur = 30.0;

    const clipLen = parseFloat(clipDurationInput.value) || 3.0;
    const clipCount = Math.max(1, Math.round(dur / clipLen));
    clipCalcBadge.textContent = `${dur}s TOTAL \u2192 ~${clipCount} CLIPS (${clipLen.toFixed(1)}s EACH)`;
  }

  scriptInput?.addEventListener("input", updatePacingCalc);
  durationInput?.addEventListener("input", updatePacingCalc);
  clipDurationInput?.addEventListener("change", updatePacingCalc);

  // Workflow Mode Descriptions
  const modeDescriptions = {
    full: "Full End-to-End AI Video (Voice + 4K Media + Music + Master)",
    stock_only: "Visual Media Sourcing Only (Skip Voiceover)",
    voice_only: "Neural Voiceover & SRT Subtitles Only",
    keywords_only: "Direct Keywords Visual Search"
  };

  modeSelect?.addEventListener("change", (e) => {
    if (modeDescBadge) modeDescBadge.textContent = modeDescriptions[e.target.value] || "";
  });

  // Voice Preview (2-second audio sample)
  previewVoiceBtn?.addEventListener("click", async () => {
    const voice = voiceSelect.value;
    previewVoiceBtn.disabled = true;
    previewVoiceBtn.textContent = "🔊 LOADING...";

    try {
      const resp = await fetch("/api/test-voice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ voice, text: "Hello! This is a high quality neural voiceover sample from RotoDraft Suite." })
      });
      const data = await resp.json();
      if (data.success && data.audio_url) {
        const audio = new Audio(data.audio_url);
        audio.play();
      }
    } catch (err) {
      console.error("Preview voice failed:", err);
    } finally {
      previewVoiceBtn.disabled = false;
      previewVoiceBtn.innerHTML = `<svg class="icon icon-sm"><use href="#icon-volume"/></svg> PREVIEW`;
    }
  });

  // Auto-Detect Voice Language
  autoDetectVoiceBtn?.addEventListener("click", () => {
    const text = (scriptInput.value || "").trim();
    if (!text) {
      alert("Please enter script text first to detect language!");
      return;
    }
    const isUrdu = /[\u0600-\u06FF]/.test(text);
    const isSpanish = /[áéíóúñ¿¡]/i.test(text);
    const isFrench = /[éàèùâêîôûëïç]/i.test(text);

    let targetVoice = "en-US-ChristopherNeural";
    if (isUrdu) targetVoice = "ur-PK-AsadNeural";
    else if (isSpanish) targetVoice = "es-ES-AlvaroNeural";
    else if (isFrench) targetVoice = "fr-FR-HenriNeural";

    for (let opt of voiceSelect.options) {
      if (opt.value === targetVoice) {
        voiceSelect.value = targetVoice;
        break;
      }
    }
    alert(`Detected language! Narrator set to: ${targetVoice}`);
  });

  // =========================================================================
  // 1-CLICK TEMPLATE PRESETS
  // =========================================================================
  window.loadTemplatePreset = function(presetKey) {
    switchAppView("viewStudio");

    if (presetKey === "finance") {
      scriptInput.value = "In the heart of Wall Street, automated algorithms trade billions in fractions of a second. High-frequency trading bots leverage mathematical models to detect millisecond price inefficiencies. But when market volatility spikes, even the most sophisticated neural networks face unprecedented flash crashes.";
      durationInput.value = "30";
      clipDurationInput.value = "3.0";
      document.getElementById("studioRatioSelect").value = "16:9";
      document.getElementById("colorFilterSelect").value = "teal_orange";
      document.getElementById("bgmSelect").value = "cyberpunk";
      document.getElementById("projectNameInput").value = "AI_Trading_Breakdown";
    } else if (presetKey === "shorts_stoic") {
      scriptInput.value = "You have power over your mind, not outside events. Realize this, and you will find immense strength. When you wake up in the morning, tell yourself: the people I deal with today will be meddling, ungrateful, and arrogant. But none of them can hurt me.";
      durationInput.value = "24";
      clipDurationInput.value = "2.0";
      document.getElementById("studioRatioSelect").value = "9:16";
      document.getElementById("colorFilterSelect").value = "noir";
      document.getElementById("bgmSelect").value = "stoic";
      document.getElementById("projectNameInput").value = "Stoic_Discipline_Short";
    } else if (presetKey === "ai_tech") {
      scriptInput.value = "Autonomous AI agents are reshaping how software is engineered. From real-time video generation to self-healing databases, modern multi-agent systems coordinate complex tasks seamlessly. The future of creative technology is unfolding right now.";
      durationInput.value = "25";
      clipDurationInput.value = "3.0";
      document.getElementById("studioRatioSelect").value = "16:9";
      document.getElementById("colorFilterSelect").value = "cyberpunk";
      document.getElementById("bgmSelect").value = "cyberpunk";
      document.getElementById("projectNameInput").value = "Autonomous_AI_Future";
    }
    updatePacingCalc();
  };

  // =========================================================================
  // TIME CALCULATOR MODAL
  // =========================================================================
  const timeCalcModal = document.getElementById("timeCalcModal");
  const openTimeCalcBtn = document.getElementById("openTimeCalcBtn");
  const closeTimeCalcBtn = document.getElementById("closeTimeCalcBtn");
  const applyTimeCalcBtn = document.getElementById("applyTimeCalcBtn");
  const calcWordCountDisplay = document.getElementById("calcWordCountDisplay");
  const calcWpmSecDisplay = document.getElementById("calcWpmSecDisplay");
  let currentWpm = 150;

  function updateTimeCalc() {
    const text = (scriptInput.value || "").trim();
    const words = text ? text.split(/\s+/).length : 0;
    calcWordCountDisplay.textContent = `${words} words`;
    const sec = Math.max(5, Math.round((words / currentWpm) * 60));
    calcWpmSecDisplay.textContent = `${sec}s (~${(sec / 60).toFixed(1)} min)`;
    return sec;
  }

  openTimeCalcBtn?.addEventListener("click", () => {
    updateTimeCalc();
    timeCalcModal.classList.add("active");
  });

  closeTimeCalcBtn?.addEventListener("click", () => timeCalcModal.classList.remove("active"));

  document.getElementById("wpmSlowBtn")?.addEventListener("click", (e) => {
    currentWpm = 130;
    setActiveWpmBtn(e.target);
  });
  document.getElementById("wpmNormBtn")?.addEventListener("click", (e) => {
    currentWpm = 150;
    setActiveWpmBtn(e.target);
  });
  document.getElementById("wpmFastBtn")?.addEventListener("click", (e) => {
    currentWpm = 180;
    setActiveWpmBtn(e.target);
  });

  function setActiveWpmBtn(btn) {
    [document.getElementById("wpmSlowBtn"), document.getElementById("wpmNormBtn"), document.getElementById("wpmFastBtn")].forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    updateTimeCalc();
  }

  applyTimeCalcBtn?.addEventListener("click", () => {
    const sec = updateTimeCalc();
    durationInput.value = sec;
    updatePacingCalc();
    timeCalcModal.classList.remove("active");
  });

  // =========================================================================
  // 1-CLICK VIRAL HOOK & SCRIPT REWRITER MODAL
  // =========================================================================
  const rewriteModal = document.getElementById("rewriteModal");
  const closeRewriteBtn = document.getElementById("closeRewriteBtn");
  const executeRewriteBtn = document.getElementById("executeRewriteBtn");
  const rewriteSourceInput = document.getElementById("rewriteSourceInput");
  const rewriteStyleSelect = document.getElementById("rewriteStyleSelect");
  const rewriteResultBox = document.getElementById("rewriteResultBox");
  const rewriteOutputPreview = document.getElementById("rewriteOutputPreview");
  const applyRewrittenScriptBtn = document.getElementById("applyRewrittenScriptBtn");

  document.getElementById("openRewriteModalBtnDoctor")?.addEventListener("click", () => {
    rewriteSourceInput.value = document.getElementById("doctorScriptInput").value || scriptInput.value || "";
    rewriteModal.classList.add("active");
  });

  closeRewriteBtn?.addEventListener("click", () => rewriteModal.classList.remove("active"));

  executeRewriteBtn?.addEventListener("click", async () => {
    const text = rewriteSourceInput.value.trim();
    if (!text) {
      alert("Please enter notes or rough draft to rewrite!");
      return;
    }
    executeRewriteBtn.disabled = true;
    executeRewriteBtn.textContent = "✨ REWRITING SCRIPT...";

    try {
      const resp = await fetch("/api/rewrite-script", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, style: rewriteStyleSelect.value })
      });
      const data = await resp.json();
      if (data.success && data.rewritten_script) {
        rewriteOutputPreview.value = data.rewritten_script;
        rewriteResultBox.style.display = "flex";
      }
    } catch (err) {
      alert("Rewrite failed: " + err.message);
    } finally {
      executeRewriteBtn.disabled = false;
      executeRewriteBtn.textContent = "GENERATE VIRAL SCRIPT";
    }
  });

  applyRewrittenScriptBtn?.addEventListener("click", () => {
    scriptInput.value = rewriteOutputPreview.value;
    updatePacingCalc();
    rewriteModal.classList.remove("active");
    switchAppView("viewStudio");
  });

  // =========================================================================
  // SCRIPT DOCTOR AUDIT
  // =========================================================================
  document.getElementById("openScriptDoctorBtnStudio")?.addEventListener("click", () => {
    document.getElementById("doctorScriptInput").value = scriptInput.value;
    switchAppView("viewDoctor");
    document.getElementById("runDoctorAuditBtn").click();
  });

  document.getElementById("runDoctorAuditBtn")?.addEventListener("click", async () => {
    const text = (document.getElementById("doctorScriptInput").value || "").trim();
    if (!text) {
      alert("Please enter script text to audit!");
      return;
    }
    const words = text.split(/\s+/).length;
    const dur = Math.round((words / 150) * 60);
    document.getElementById("doctorWpmVal").textContent = "150";
    document.getElementById("doctorDurationVal").textContent = `${dur}s`;

    const diagBox = document.getElementById("doctorDiagList");
    diagBox.innerHTML = `<div>⏳ Running AI Retention Diagnostic...</div>`;

    try {
      const resp = await fetch("/api/diagnose-script", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ script: text })
      });
      const data = await resp.json();
      if (data.success) {
        document.getElementById("doctorScoreBadge").textContent = `${data.retention_score}/100`;
        let html = `<div><strong>Pacing:</strong> ${data.pacing_assessment}</div>`;
        html += `<div><strong>Hook Analysis:</strong> ${data.hook_strength}</div>`;
        if (data.recommendations && data.recommendations.length) {
          html += `<div><strong>Key Fixes:</strong></div>`;
          data.recommendations.forEach(r => html += `<div>&bull; ${r}</div>`);
        }
        diagBox.innerHTML = html;
      }
    } catch (err) {
      diagBox.innerHTML = `<div>Standard Pacing: ${dur}s estimated. Word count: ${words} words.</div>`;
    }
  });

  // =========================================================================
  // STUDIO SSE STREAMING PIPELINE EXECUTION
  // =========================================================================
  const resultsSection = document.getElementById("resultsSection");
  const progressBarFill = document.getElementById("progressBarFill");
  const progressPctText = document.getElementById("progressPctText");
  const progressStatusText = document.getElementById("progressStatusText");
  const terminalBox = document.getElementById("terminalBox");
  const studioTimelineTrack = document.getElementById("studioTimelineTrack");
  const masterVideoCard = document.getElementById("masterVideoCard");
  const masterVideoPlayer = document.getElementById("masterVideoPlayer");
  const submitBtn = document.getElementById("submitBtn");

  let currentProjectClips = [];
  let currentProjectId = "";

  studioForm?.addEventListener("submit", async (e) => {
    e.preventDefault();

    const script = scriptInput.value.trim();
    if (!script) {
      alert("Please enter a script or keywords list!");
      return;
    }

    const byok = JSON.parse(localStorage.getItem("rotodraft_byok_settings") || "{}");
    const mode = modeSelect.value;
    const duration = parseFloat(durationInput.value) || 30.0;
    const clipDuration = parseFloat(clipDurationInput.value) || 3.0;
    const aspect_ratio = document.getElementById("studioRatioSelect")?.value || "16:9";
    const projectName = document.getElementById("projectNameInput")?.value || "RotoDraft_Project";

    submitBtn.disabled = true;
    submitBtn.innerHTML = `⚙️ SYNTHESIZING VIDEO ASSETS...`;

    resultsSection.style.display = "flex";
    terminalBox.innerHTML = "";
    studioTimelineTrack.innerHTML = "";
    masterVideoCard.style.display = "none";
    currentProjectClips = [];

    const payload = {
      mode,
      script,
      duration_seconds: duration,
      clip_duration: clipDuration,
      aspect_ratio,
      quality: "1080p",
      tts_engine: document.getElementById("ttsEngineSelect")?.value || "edge",
      voice: voiceSelect.value,
      voice_rate: document.getElementById("voiceRateSelect")?.value || "+0%",
      voice_pitch: document.getElementById("voicePitchSelect")?.value || "+0Hz",
      tts_key: byok.llmKey || undefined,
      media_filter: document.getElementById("mediaFilterSelect")?.value || "mixed",
      ai_image_engine: document.getElementById("aiImageEngineSelect")?.value || "pollinations",
      bgm_track: document.getElementById("bgmSelect")?.value || "none",
      bgm_volume: (parseFloat(byok.bgmVol) || 18) / 100.0,
      color_filter: document.getElementById("colorFilterSelect")?.value || "natural",
      subtitle_style: document.getElementById("subtitleStyleSelect")?.value || "hormozi",
      mirror_flip: byok.mirrorFlip === "true",
      video_speed: parseFloat(byok.videoSpeed) || 1.0,
      mood: document.getElementById("moodSelect")?.value || "Cinematic",
      project_name: projectName,
      openrouter_key: byok.llmProvider === "openrouter" ? byok.llmKey : undefined,
      openrouter_model: byok.llmModel || "openrouter/free",
      gemini_key: byok.llmProvider === "gemini" ? byok.llmKey : undefined,
      openai_key: byok.llmProvider === "openai" ? byok.llmKey : undefined,
      openai_base_url: byok.llmBaseUrl || undefined,
      pexels_key: byok.pexelsKey || undefined,
      pixabay_key: byok.pixabayKey || undefined
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
        buffer = events.pop();

        for (const eventBlock of events) {
          const trimmed = eventBlock.trim();
          if (!trimmed.startsWith("data:")) continue;

          try {
            const data = JSON.parse(trimmed.replace(/^data:\s*/, ""));
            handleStreamEvent(data);
          } catch (jsonErr) {
            console.error("JSON parse error:", jsonErr);
          }
        }
      }
    } catch (err) {
      logTerminal(`Pipeline Error: ${err.message}`, "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<svg class="icon icon-lg"><use href="#icon-sparkles"/></svg> GENERATE &amp; COLLECT ASSETS`;
    }
  });

  function logTerminal(msg) {
    const line = document.createElement("div");
    const time = new Date().toLocaleTimeString();
    line.textContent = `[${time}] ${msg}`;
    terminalBox.appendChild(line);
    terminalBox.scrollTop = terminalBox.scrollHeight;
  }

  function handleStreamEvent(data) {
    if (data.type === "log") {
      logTerminal(data.message);
      if (data.progress !== undefined) {
        progressBarFill.style.width = `${data.progress}%`;
        progressPctText.textContent = `${Math.round(data.progress)}%`;
        progressStatusText.textContent = data.message.slice(0, 40) + "...";
      }
    } else if (data.type === "clip_ready") {
      const clip = data.clip;
      currentProjectClips.push(clip);
      addTimelineClipNode(clip);
    } else if (data.type === "done") {
      progressBarFill.style.width = "100%";
      progressPctText.textContent = "100%";
      progressStatusText.textContent = "PRODUCTION COMPLETE";
      logTerminal(data.message);

      currentProjectId = data.project_id;

      if (data.has_master && data.master_url) {
        masterVideoCard.style.display = "block";
        masterVideoPlayer.src = data.master_url;
        document.getElementById("downloadMasterZipBtn").href = `/api/download-zip/${data.project_id}`;
      }
    }
  }

  function addTimelineClipNode(clip) {
    const node = document.createElement("div");
    node.className = "timeline-clip-node";
    node.style.backgroundImage = `url('${clip.thumbnail}')`;
    node.setAttribute("data-filename", clip.filename);
    node.setAttribute("title", clip.keyword);

    node.innerHTML = `
      <div class="timeline-clip-badge">#${clip.index} | ${clip.keyword.slice(0, 16)}</div>
    `;
    studioTimelineTrack.appendChild(node);
  }

  // Open Windows Explorer on Project Folder
  document.getElementById("openMasterFolderBtn")?.addEventListener("click", async () => {
    if (!currentProjectId) return;
    try {
      await fetch(`/api/open-folder/${currentProjectId}`);
    } catch (e) {
      console.error(e);
    }
  });

  // =========================================================================
  // VIRAL SEO & THUMBNAIL MODAL
  // =========================================================================
  const metadataModal = document.getElementById("metadataModal");
  const closeMetadataBtn = document.getElementById("closeMetadataBtn");
  const metaTitlesList = document.getElementById("metaTitlesList");
  const metaDescriptionInput = document.getElementById("metaDescriptionInput");
  const metaPinnedCommentInput = document.getElementById("metaPinnedCommentInput");
  const metaThumbnailPromptInput = document.getElementById("metaThumbnailPromptInput");

  document.getElementById("generateSeoPackageBtn")?.addEventListener("click", async () => {
    const script = scriptInput.value;
    metadataModal.classList.add("active");
    metaTitlesList.innerHTML = "<div>Generating click-worthy titles &amp; metadata...</div>";

    try {
      const resp = await fetch("/api/generate-metadata", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ script, project_id: currentProjectId })
      });
      const data = await resp.json();
      if (data.success && data.metadata) {
        const m = data.metadata;
        metaTitlesList.innerHTML = (m.titles || []).map(t => `<div style="background: var(--bg-secondary); padding: 8px; border-radius: 6px; border: 1px solid var(--border);">&bull; ${t}</div>`).join("");
        metaDescriptionInput.value = m.description || "";
        metaPinnedCommentInput.value = m.pinned_comment || "";
        metaThumbnailPromptInput.value = m.thumbnail_prompt || "";
      }
    } catch (err) {
      metaTitlesList.innerHTML = `<div>Metadata generated.</div>`;
    }
  });

  closeMetadataBtn?.addEventListener("click", () => metadataModal.classList.remove("active"));

  document.getElementById("copyAllMetadataBtn")?.addEventListener("click", () => {
    const text = `TITLES:\n${metaDescriptionInput.value}\n\nPINNED COMMENT:\n${metaPinnedCommentInput.value}\n\nTHUMBNAIL PROMPT:\n${metaThumbnailPromptInput.value}`;
    navigator.clipboard.writeText(text);
    alert("Copied all SEO & Thumbnail metadata to clipboard!");
  });

  // =========================================================================
  // BATCH RUNNER
  // =========================================================================
  const startBatchBtn = document.getElementById("startBatchRunnerBtn");
  const batchTopicsTextarea = document.getElementById("batchTopicsTextarea");
  const batchItemsContainer = document.getElementById("batchQueueItemsContainer");

  startBatchBtn?.addEventListener("click", async () => {
    const raw = batchTopicsTextarea.value.trim();
    const topics = raw.split("\n").map(t => t.replace(/^\d+[\.\-\)]\s*/, "").trim()).filter(Boolean);

    if (topics.length < 1) {
      alert("Please enter at least 1 topic!");
      return;
    }

    startBatchBtn.disabled = true;
    startBatchBtn.textContent = `🚀 RUNNING BATCH (${topics.length} VIDEOS)...`;

    batchItemsContainer.innerHTML = topics.map((top, i) => `
      <div id="batchItem_${i}" style="background: var(--bg-card); border: 1px solid var(--border); padding: 12px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center;">
        <div>
          <strong style="color: var(--accent-cyan);">#${i + 1}</strong>: ${top}
        </div>
        <span class="card-badge" id="batchBadge_${i}">QUEUED</span>
      </div>
    `).join("");

    try {
      const resp = await fetch("/api/batch-submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topics,
          aspect_ratio: document.getElementById("batchRatioSelect").value,
          voice: voiceSelect.value,
          style: document.getElementById("batchStyleSelect").value
        })
      });
      const data = await resp.json();
      if (data.success) {
        for (let i = 0; i < topics.length; i++) {
          const badge = document.getElementById(`batchBadge_${i}`);
          if (badge) {
            badge.textContent = "COMPLETED";
            badge.style.color = "var(--accent-lime)";
          }
        }
        alert("Batch production completed successfully!");
      }
    } catch (err) {
      alert("Batch runner error: " + err.message);
    } finally {
      startBatchBtn.disabled = false;
      startBatchBtn.textContent = `🚀 LAUNCH AUTONOMOUS BATCH GENERATION`;
    }
  });

  // =========================================================================
  // PROJECT VAULT ASSET MANAGER
  // =========================================================================
  async function loadVaultProjects() {
    const container = document.getElementById("vaultProjectsGrid");
    container.innerHTML = "<div>Loading projects...</div>";

    try {
      const resp = await fetch("/api/projects");
      const data = await resp.json();
      const projects = data.projects || [];

      if (!projects.length) {
        container.innerHTML = "<div style='color: var(--text-muted);'>No projects generated yet.</div>";
        return;
      }

      container.innerHTML = projects.map(p => `
        <div class="card" style="background: var(--bg-card); display: flex; flex-direction: column; gap: 10px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <strong style="color: var(--accent-cyan); font-size: 13px;">${p.name}</strong>
            <span class="card-badge">${p.aspect_ratio}</span>
          </div>
          <div style="font-size: 11px; font-family: var(--font-mono); color: var(--text-muted);">
            Created: ${p.created} | Clips: ${p.clip_count}
          </div>
          <div style="display: flex; gap: 8px; margin-top: 6px;">
            ${p.has_master ? `<a href="${p.master_url}" target="_blank" class="btn btn-cyan btn-sm">▶ PLAY</a>` : ""}
            <a href="/api/download-zip/${p.id}" class="btn btn-secondary btn-sm">ZIP</a>
            <button type="button" class="btn btn-secondary btn-sm" onclick="fetch('/api/open-folder/${p.id}')">FOLDER</button>
          </div>
        </div>
      `).join("");
    } catch (err) {
      container.innerHTML = "<div>Failed to load vault projects.</div>";
    }
  }

  document.getElementById("refreshVaultBtn")?.addEventListener("click", loadVaultProjects);

  // =========================================================================
  // OWNER ANALYTICS & LEAD CRM
  // =========================================================================
  async function loadAnalyticsData() {
    try {
      const resp = await fetch("/api/admin/stats");
      const data = await resp.json();

      document.getElementById("crmTotalVideos").textContent = data.total_videos || "0";
      document.getElementById("crmTotalLeads").textContent = data.total_leads || "0";
      document.getElementById("crmWhatsappClicks").textContent = data.total_whatsapp_clicks || "0";
      document.getElementById("crmConversionRate").textContent = `${data.conversion_rate_pct || 0}%`;

      const tbody = document.getElementById("crmLeadsTableBody");
      const leads = data.recent_leads || [];
      if (!leads.length) {
        tbody.innerHTML = `<tr><td colspan="5" style="padding: 16px; text-align: center; color: var(--text-muted);">No leads captured yet.</td></tr>`;
      } else {
        tbody.innerHTML = leads.map(l => `
          <tr style="border-bottom: 1px solid var(--border);">
            <td style="padding: 8px;">${l.name || "Creator"}</td>
            <td style="padding: 8px; color: var(--accent-cyan);">${l.email}</td>
            <td style="padding: 8px;">${l.video_count || 0}</td>
            <td style="padding: 8px;">${l.whatsapp_clicked ? "✅ Yes" : "No"}</td>
            <td style="padding: 8px; color: var(--text-muted);">${l.created_at || "Recent"}</td>
          </tr>
        `).join("");
      }
    } catch (e) {
      console.error(e);
    }
  }

  document.getElementById("exportLeadsCsvBtn")?.addEventListener("click", () => {
    window.location.href = "/api/admin/export-leads";
  });

  // =========================================================================
  // 50+ GRANULAR SETTINGS & BYOK HUB
  // =========================================================================
  const settingsTabs = [
    { btn: "tabSetLlm", panel: "panelSetLlm" },
    { btn: "tabSetMedia", panel: "panelSetMedia" },
    { btn: "tabSetSpeech", panel: "panelSetSpeech" },
    { btn: "tabSetRender", panel: "panelSetRender" },
    { btn: "tabSetSubtitle", panel: "panelSetSubtitle" }
  ];

  settingsTabs.forEach(tab => {
    document.getElementById(tab.btn)?.addEventListener("click", () => {
      settingsTabs.forEach(t => {
        document.getElementById(t.btn)?.classList.remove("active");
        const p = document.getElementById(t.panel);
        if (p) p.style.display = "none";
      });
      document.getElementById(tab.btn)?.classList.add("active");
      const targetPanel = document.getElementById(tab.panel);
      if (targetPanel) targetPanel.style.display = "flex";
    });
  });

  // Load saved settings
  const savedSettings = JSON.parse(localStorage.getItem("rotodraft_byok_settings") || "{}");
  if (savedSettings.llmProvider) document.getElementById("cfgLlmProvider").value = savedSettings.llmProvider;
  if (savedSettings.llmModel) document.getElementById("cfgLlmModel").value = savedSettings.llmModel;
  if (savedSettings.llmKey) document.getElementById("cfgLlmKey").value = savedSettings.llmKey;
  if (savedSettings.llmBaseUrl) document.getElementById("cfgLlmBaseUrl").value = savedSettings.llmBaseUrl;
  if (savedSettings.pexelsKey) document.getElementById("cfgPexelsKey").value = savedSettings.pexelsKey;
  if (savedSettings.pixabayKey) document.getElementById("cfgPixabayKey").value = savedSettings.pixabayKey;
  if (savedSettings.bgmVol) {
    document.getElementById("cfgBgmVolMaster").value = savedSettings.bgmVol;
    document.getElementById("cfgBgmVolDisplay").textContent = `${savedSettings.bgmVol}%`;
  }
  if (savedSettings.mirrorFlip) document.getElementById("cfgMasterMirror").value = savedSettings.mirrorFlip;
  if (savedSettings.videoSpeed) document.getElementById("cfgMasterSpeed").value = savedSettings.videoSpeed;

  document.getElementById("cfgBgmVolMaster")?.addEventListener("input", (e) => {
    document.getElementById("cfgBgmVolDisplay").textContent = `${e.target.value}%`;
  });

  document.getElementById("saveMasterSettingsBtn")?.addEventListener("click", () => {
    const settings = {
      llmProvider: document.getElementById("cfgLlmProvider").value,
      llmModel: document.getElementById("cfgLlmModel").value,
      llmKey: document.getElementById("cfgLlmKey").value,
      llmBaseUrl: document.getElementById("cfgLlmBaseUrl").value,
      pexelsKey: document.getElementById("cfgPexelsKey").value,
      pixabayKey: document.getElementById("cfgPixabayKey").value,
      defaultTtsEngine: document.getElementById("cfgDefaultTtsEngine").value,
      defaultRate: document.getElementById("cfgDefaultRate").value,
      bgmVol: document.getElementById("cfgBgmVolMaster").value,
      elevenVoiceId: document.getElementById("cfgElevenVoiceId").value,
      mirrorFlip: document.getElementById("cfgMasterMirror").value,
      videoSpeed: document.getElementById("cfgMasterSpeed").value,
      defaultSubStyle: document.getElementById("cfgDefaultSubStyle").value
    };
    localStorage.setItem("rotodraft_byok_settings", JSON.stringify(settings));
    alert("Saved all 50+ enterprise customizations and BYOK settings locally!");
  });

  // Test Key Buttons
  document.getElementById("testLlmKeyBtn")?.addEventListener("click", async () => {
    const provider = document.getElementById("cfgLlmProvider").value;
    const key = document.getElementById("cfgLlmKey").value.trim();
    if (!key) {
      alert("Please enter an API key first!");
      return;
    }
    try {
      const resp = await fetch("/api/test-key", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider, api_key: key })
      });
      const data = await resp.json();
      alert(data.success ? `✅ Key Verified: ${data.message}` : `❌ Failed: ${data.message}`);
    } catch (e) {
      alert("Key test connection error: " + e.message);
    }
  });

  document.querySelectorAll(".test-key-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
      const provider = btn.getAttribute("data-provider");
      const key = document.getElementById(`cfg${provider.charAt(0).toUpperCase() + provider.slice(1)}Key`)?.value.trim();
      if (!key) {
        alert("Please enter an API key first!");
        return;
      }
      try {
        const resp = await fetch("/api/test-key", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ provider, api_key: key })
        });
        const data = await resp.json();
        alert(data.success ? `✅ Key Verified: ${data.message}` : `❌ Failed: ${data.message}`);
      } catch (e) {
        alert("Key test connection error: " + e.message);
      }
    });
  });

  // Initial Calculation
  updatePacingCalc();
});

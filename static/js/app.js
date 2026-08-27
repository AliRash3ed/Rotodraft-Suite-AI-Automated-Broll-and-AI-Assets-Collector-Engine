/* ==========================================================================
   ROTODRAFT SUITE - INTERACTIVE CONTROLLER & NLE STUDIO V2.1
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const form = document.getElementById("generateForm");
  const scriptInput = document.getElementById("scriptInput");
  const scriptInputLabel = document.getElementById("scriptInputLabel");
  const scriptCardTitle = document.getElementById("scriptCardTitle");
  const durationInput = document.getElementById("durationInput");
  const clipDurationInput = document.getElementById("clipDurationInput");
  const clipCalcBadge = document.getElementById("clipCalcBadge");
  const wordCountBadge = document.getElementById("wordCountBadge");
  const modeSelect = document.getElementById("modeSelect");
  const modeDescriptionBadge = document.getElementById("modeDescriptionBadge");
  const qualitySelect = document.getElementById("qualitySelect");
  const moodSelect = document.getElementById("moodSelect");
  const projectNameInput = document.getElementById("projectNameInput");
  const submitBtn = document.getElementById("submitBtn");

  // Groups for Dynamic Visibility
  const audioDropzoneGroup = document.getElementById("audioDropzoneGroup");
  const timingGroup = document.getElementById("timingGroup");
  const calcBar = document.getElementById("calcBar");
  const aspectRatioGroup = document.getElementById("aspectRatioGroup");
  const voiceoverSettingsGroup = document.getElementById("voiceoverSettingsGroup");
  const videoSpecsGroup = document.getElementById("videoSpecsGroup");
  const videoOutputSection = document.getElementById("videoOutputSection");
  const voiceOnlyOutputCard = document.getElementById("voiceOnlyOutputCard");
  const voiceOnlyAudioPlayer = document.getElementById("voiceOnlyAudioPlayer");
  const srtTranscriptViewer = document.getElementById("srtTranscriptViewer");
  const downloadVoiceMp3Btn = document.getElementById("downloadVoiceMp3Btn");
  const downloadVoiceSrtBtn = document.getElementById("downloadVoiceSrtBtn");
  
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

  // NLE Timeline Elements
  const timelineBoardContainer = document.getElementById("timelineBoardContainer");
  const timelineVideoBlocks = document.getElementById("timelineVideoBlocks");
  const timelineAudioTrack = document.getElementById("timelineAudioTrack");

  // Audio Upload
  const audioDropzone = document.getElementById("audioDropzone");
  const audioFileInput = document.getElementById("audioFileInput");
  const audioUploadStatus = document.getElementById("audioUploadStatus");
  let customAudioPath = null;

  // Tabs & Views
  const studioView = document.getElementById("studioView");
  const vaultView = document.getElementById("vaultView");
  const tabStudioBtn = document.getElementById("tabStudioBtn");
  const tabVaultBtn = document.getElementById("tabVaultBtn");
  const vaultTableBody = document.getElementById("vaultTableBody");

  // Modals & Settings
  const settingsModal = document.getElementById("settingsModal");
  const openSettingsBtn = document.getElementById("openSettingsBtn");
  const closeSettingsBtn = document.getElementById("closeSettingsBtn");
  const themeToggleBtn = document.getElementById("themeToggleBtn");

  // Time Calculator Modal
  const timeCalcModal = document.getElementById("timeCalcModal");
  const openTimeCalcBtn = document.getElementById("openTimeCalcBtn");
  const closeTimeCalcBtn = document.getElementById("closeTimeCalcBtn");
  const applyTimeCalcBtn = document.getElementById("applyTimeCalcBtn");
  const calcMinutesInput = document.getElementById("calcMinutesInput");
  const calcSecondsInput = document.getElementById("calcSecondsInput");
  const calcTotalSecDisplay = document.getElementById("calcTotalSecDisplay");
  const calcWordCountDisplay = document.getElementById("calcWordCountDisplay");
  const calcWpmSecDisplay = document.getElementById("calcWpmSecDisplay");
  const wpmSlowBtn = document.getElementById("wpmSlowBtn");
  const wpmNormBtn = document.getElementById("wpmNormBtn");
  const wpmFastBtn = document.getElementById("wpmFastBtn");
  let currentWpm = 150;

  // Swap Clip Modal
  const swapModal = document.getElementById("swapModal");
  const closeSwapBtn = document.getElementById("closeSwapBtn");
  const swapForm = document.getElementById("swapForm");
  const swapClipIndexInput = document.getElementById("swapClipIndexInput");
  const swapKeywordInput = document.getElementById("swapKeywordInput");
  const swapPageInput = document.getElementById("swapPageInput");

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
    themeToggleBtn.innerHTML = theme === "dark" 
      ? `<svg class="icon icon-sm"><use href="#icon-sun"/></svg> LIGHT` 
      : `<svg class="icon icon-sm"><use href="#icon-moon"/></svg> DARK`;
  }

  // Dynamic Mode Visibility Switcher
  function updateModeVisibility() {
    const mode = modeSelect.value;
    
    // Reset defaults
    audioDropzoneGroup.style.display = "none";
    timingGroup.style.display = "grid";
    calcBar.style.display = "flex";
    aspectRatioGroup.style.display = "flex";
    voiceoverSettingsGroup.style.display = "flex";
    videoSpecsGroup.style.display = "grid";
    videoOutputSection.style.display = "grid";
    voiceOnlyOutputCard.style.display = "none";

    if (mode === "full") {
      modeDescriptionBadge.textContent = "Full Automation (Voiceover + B-Roll Clips + Master Video)";
      scriptCardTitle.innerHTML = `<svg class="icon"><use href="#icon-film"/></svg> 1. SCRIPT &amp; TIMING`;
      scriptInputLabel.textContent = "Voiceover Script Content";
      scriptInput.placeholder = "Paste your voiceover script here...";
      audioDropzoneGroup.style.display = "flex";
      if (timelineAudioTrack) timelineAudioTrack.style.display = "flex";
    } 
    else if (mode === "stock_only") {
      modeDescriptionBadge.textContent = "Stock B-Rolls Only (Decompose Script -> Download 3s Clips)";
      scriptCardTitle.innerHTML = `<svg class="icon"><use href="#icon-film"/></svg> 1. SCRIPT FOR B-ROLL DECOMPOSITION`;
      scriptInputLabel.textContent = "Script / Story Narrative";
      scriptInput.placeholder = "Paste script here. AI will analyze the story and collect 3.0s b-roll scenes...";
      audioDropzoneGroup.style.display = "none"; // NO AUDIO
      voiceoverSettingsGroup.style.display = "none"; // NO TTS
      if (timelineAudioTrack) timelineAudioTrack.style.display = "none";
    } 
    else if (mode === "keywords_only") {
      modeDescriptionBadge.textContent = "Direct Keywords List (Download 3s Clips For Your Custom Keywords)";
      scriptCardTitle.innerHTML = `<svg class="icon"><use href="#icon-film"/></svg> 1. PASTE RAW SEARCH KEYWORDS (1 PER LINE)`;
      scriptInputLabel.textContent = "Custom Keywords List";
      scriptInput.placeholder = "1. Wall street trading floor\n2. Server room flashing lights\n3. High speed city traffic timelapse\n4. Digital money animation";
      audioDropzoneGroup.style.display = "none";
      voiceoverSettingsGroup.style.display = "none";
      timingGroup.style.display = "none"; // Duration is auto computed from line count
      if (timelineAudioTrack) timelineAudioTrack.style.display = "none";
    } 
    else if (mode === "voice_only") {
      modeDescriptionBadge.textContent = "AI Voiceover Only (Edge-TTS Neural Audio + Subtitles)";
      scriptCardTitle.innerHTML = `<svg class="icon"><use href="#icon-mic"/></svg> 1. SCRIPT FOR NEURAL VOICEOVER`;
      scriptInputLabel.textContent = "Voiceover Script";
      scriptInput.placeholder = "Paste text to convert into crystal clear natural voiceover and subtitles...";
      audioDropzoneGroup.style.display = "none";
      timingGroup.style.display = "none";
      calcBar.style.display = "none";
      aspectRatioGroup.style.display = "none";
      videoSpecsGroup.style.display = "none";
      videoOutputSection.style.display = "none";
    }

    updateCalculation();
  }

  modeSelect.addEventListener("change", updateModeVisibility);

  // Time Calculator Modal Interactivity
  openTimeCalcBtn.addEventListener("click", () => {
    const dur = parseDurationInput(durationInput.value) || 30;
    calcMinutesInput.value = Math.floor(dur / 60);
    calcSecondsInput.value = Math.floor(dur % 60);
    updateTimeCalcDisplays();
    timeCalcModal.classList.add("active");
  });

  closeTimeCalcBtn.addEventListener("click", () => timeCalcModal.classList.remove("active"));
  
  function updateTimeCalcDisplays() {
    const mins = parseInt(calcMinutesInput.value, 10) || 0;
    const secs = parseInt(calcSecondsInput.value, 10) || 0;
    const total = mins * 60 + secs;
    calcTotalSecDisplay.textContent = total;

    const words = (scriptInput.value || "").trim().split(/\s+/).filter(Boolean).length;
    calcWordCountDisplay.textContent = `${words} words`;
    const wpmSecs = words > 0 ? Math.round((words / currentWpm) * 60) : 0;
    calcWpmSecDisplay.textContent = `${wpmSecs}s (at ${currentWpm} WPM)`;
  }

  calcMinutesInput.addEventListener("input", updateTimeCalcDisplays);
  calcSecondsInput.addEventListener("input", updateTimeCalcDisplays);

  wpmSlowBtn.addEventListener("click", () => {
    currentWpm = 130;
    wpmSlowBtn.style.background = "var(--accent-yellow)";
    wpmSlowBtn.style.color = "#000";
    wpmNormBtn.style.background = "var(--bg-card)";
    wpmNormBtn.style.color = "var(--text-primary)";
    wpmFastBtn.style.background = "var(--bg-card)";
    wpmFastBtn.style.color = "var(--text-primary)";
    const words = (scriptInput.value || "").trim().split(/\s+/).filter(Boolean).length;
    const total = words > 0 ? Math.round((words / currentWpm) * 60) : 30;
    calcMinutesInput.value = Math.floor(total / 60);
    calcSecondsInput.value = total % 60;
    updateTimeCalcDisplays();
  });

  wpmNormBtn.addEventListener("click", () => {
    currentWpm = 150;
    wpmNormBtn.style.background = "var(--accent-yellow)";
    wpmNormBtn.style.color = "#000";
    wpmSlowBtn.style.background = "var(--bg-card)";
    wpmSlowBtn.style.color = "var(--text-primary)";
    wpmFastBtn.style.background = "var(--bg-card)";
    wpmFastBtn.style.color = "var(--text-primary)";
    const words = (scriptInput.value || "").trim().split(/\s+/).filter(Boolean).length;
    const total = words > 0 ? Math.round((words / currentWpm) * 60) : 30;
    calcMinutesInput.value = Math.floor(total / 60);
    calcSecondsInput.value = total % 60;
    updateTimeCalcDisplays();
  });

  wpmFastBtn.addEventListener("click", () => {
    currentWpm = 180;
    wpmFastBtn.style.background = "var(--accent-yellow)";
    wpmFastBtn.style.color = "#000";
    wpmSlowBtn.style.background = "var(--bg-card)";
    wpmSlowBtn.style.color = "var(--text-primary)";
    wpmNormBtn.style.background = "var(--bg-card)";
    wpmNormBtn.style.color = "var(--text-primary)";
    const words = (scriptInput.value || "").trim().split(/\s+/).filter(Boolean).length;
    const total = words > 0 ? Math.round((words / currentWpm) * 60) : 30;
    calcMinutesInput.value = Math.floor(total / 60);
    calcSecondsInput.value = total % 60;
    updateTimeCalcDisplays();
  });

  applyTimeCalcBtn.addEventListener("click", () => {
    const mins = parseInt(calcMinutesInput.value, 10) || 0;
    const secs = parseInt(calcSecondsInput.value, 10) || 0;
    const total = mins * 60 + secs;
    durationInput.value = total > 0 ? total : 30;
    updateCalculation();
    timeCalcModal.classList.remove("active");
    logTerminal(`Time Converter: Set narrative duration to ${total}s`);
  });

  // Tab Switcher
  tabStudioBtn.addEventListener("click", () => {
    tabStudioBtn.classList.add("active");
    tabVaultBtn.classList.remove("active");
    studioView.style.display = "flex";
    vaultView.style.display = "none";
  });

  tabVaultBtn.addEventListener("click", () => {
    tabVaultBtn.classList.add("active");
    tabStudioBtn.classList.remove("active");
    studioView.style.display = "none";
    vaultView.style.display = "flex";
    loadProjectVault();
  });

  // Template Quick-Select Chips
  document.querySelectorAll(".chip-btn[data-template-id]").forEach((chip) => {
    chip.addEventListener("click", () => {
      const tId = chip.getAttribute("data-template-id");
      fetch("/api/templates")
        .then((r) => r.json())
        .then((data) => {
          const t = data.templates.find((x) => x.id === tId);
          if (t) {
            scriptInput.value = t.script;
            durationInput.value = t.duration;
            clipDurationInput.value = t.clip_len.toFixed(1);
            moodSelect.value = t.mood;
            const ratioRadio = document.querySelector(`input[name="aspect_ratio"][value="${t.ratio}"]`);
            if (ratioRadio) ratioRadio.checked = true;
            projectNameInput.value = `Demo_${t.id}`;
            updateCalculation();
            logTerminal(`Loaded preset template: '${t.title}'`);
          }
        });
    });
  });

  // Custom Audio File Upload
  audioDropzone.addEventListener("click", () => audioFileInput.click());
  audioFileInput.addEventListener("change", async () => {
    const file = audioFileInput.files[0];
    if (!file) return;

    audioUploadStatus.textContent = `Uploading & measuring ${file.name}...`;
    const formData = new FormData();
    formData.append("file", file);

    try {
      const resp = await fetch("/api/upload-audio", { method: "POST", body: formData });
      const data = await resp.json();
      if (data.success) {
        customAudioPath = data.file_path;
        durationInput.value = data.duration;
        audioUploadStatus.textContent = `Attached: ${data.filename} (${data.duration}s)`;
        updateCalculation();
        logTerminal(`Custom Audio Attached: ${data.filename} -> ${data.duration}s detected`);
      } else {
        audioUploadStatus.textContent = "Failed to read audio duration";
      }
    } catch (e) {
      audioUploadStatus.textContent = `Upload error: ${e.message}`;
    }
  });

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
    const words = text ? text.split(/\s+/).filter(Boolean).length : 0;
    const mode = modeSelect.value;

    wordCountBadge.textContent = `${words} WORDS`;

    if (mode === "keywords_only") {
      const lines = text.split("\n").filter((l) => l.trim().length > 0);
      const clipDur = parseFloat(clipDurationInput.value) || 3.0;
      const totalSec = lines.length * clipDur;
      clipCalcBadge.textContent = `${lines.length} CUSTOM KEYWORDS -> ${totalSec.toFixed(0)}s VIDEO (${clipDur}s EACH)`;
      return;
    }

    let dur = parseDurationInput(durationInput.value);
    const clipDur = parseFloat(clipDurationInput.value) || 3.0;

    if (dur <= 0 && words > 0) {
      dur = Math.round(words / 2.3);
    }

    const calculatedClips = Math.max(1, Math.ceil(dur / clipDur));
    clipCalcBadge.textContent = `${dur.toFixed(0)}s TOTAL -> ~${calculatedClips} CLIPS (${clipDur}s EACH)`;
  }

  scriptInput.addEventListener("input", updateCalculation);
  durationInput.addEventListener("input", updateCalculation);
  clipDurationInput.addEventListener("change", updateCalculation);

  // Settings Modal Handlers
  openSettingsBtn.addEventListener("click", () => settingsModal.classList.add("active"));
  closeSettingsBtn.addEventListener("click", () => settingsModal.classList.remove("active"));
  window.addEventListener("click", (e) => {
    if (e.target === settingsModal) settingsModal.classList.remove("active");
    if (e.target === swapModal) swapModal.classList.remove("active");
    if (e.target === timeCalcModal) timeCalcModal.classList.remove("active");
  });

  closeSwapBtn.addEventListener("click", () => swapModal.classList.remove("active"));

  // API Key Tester
  document.querySelectorAll(".test-key-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const provider = btn.getAttribute("data-provider");
      const input = document.getElementById(`${provider}KeyInput`);
      const statusSpan = document.getElementById(`${provider}KeyStatus`);
      
      const key = (input.value || "").trim();
      if (!key) {
        statusSpan.textContent = "Please enter key first";
        statusSpan.style.color = "#FF3366";
        return;
      }

      statusSpan.textContent = "Testing...";
      statusSpan.style.color = "#FFE600";

      try {
        const resp = await fetch("/api/test-key", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ provider, api_key: key })
        });
        const data = await resp.json();
        if (data.success) {
          statusSpan.textContent = "Valid & Active";
          statusSpan.style.color = "#00FF66";
        } else {
          statusSpan.textContent = `${data.message}`;
          statusSpan.style.color = "#FF3366";
        }
      } catch (err) {
        statusSpan.textContent = "Connection failed";
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
      alert("Please enter a voiceover script or keywords.");
      return;
    }

    const duration = parseDurationInput(durationInput.value) || 30.0;
    const clipDuration = parseFloat(clipDurationInput.value) || 3.0;
    const mode = modeSelect.value;
    const aspect_ratio = document.querySelector('input[name="aspect_ratio"]:checked')?.value || "16:9";
    const quality = qualitySelect.value;
    const voice = document.getElementById("voiceSelect").value;
    const voice_rate = document.getElementById("voiceRateSelect")?.value || "+0%";
    const voice_pitch = document.getElementById("voicePitchSelect")?.value || "+0Hz";
    const mood = moodSelect.value;
    const projectName = (projectNameInput.value || "RotoDraft_Project").trim();

    // BYOK Keys
    const openrouter_key = document.getElementById("openrouterKeyInput")?.value || "";
    const openrouter_model = document.getElementById("openrouterModelSelect")?.value || "openrouter/free";
    const pexels_key = document.getElementById("pexelsKeyInput")?.value || "";
    const pixabay_key = document.getElementById("pixabayKeyInput")?.value || "";

    // Reset UI State
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<svg class="icon"><use href="#icon-refresh"/></svg> PROCESSING PRODUCTION...`;
    terminal.innerHTML = "";
    clipsGrid.innerHTML = "";
    if (timelineVideoBlocks) timelineVideoBlocks.innerHTML = "";
    if (timelineBoardContainer) timelineBoardContainer.style.display = "none";
    masterContainer.style.display = "none";
    exportActions.style.display = "none";
    voiceOnlyOutputCard.style.display = "none";
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
      voice_rate,
      voice_pitch,
      mood,
      project_name: projectName,
      custom_audio_path: customAudioPath,
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
        buffer = events.pop();

        for (const eventBlock of events) {
          const trimmed = eventBlock.trim();
          if (!trimmed.startsWith("data:")) continue;

          try {
            const data = JSON.parse(trimmed.replace(/^data:\s*/, ""));
            handleStreamEvent(data, aspect_ratio, clipDuration, quality);
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
      submitBtn.innerHTML = `<svg class="icon icon-lg"><use href="#icon-sparkles"/></svg> GENERATE &amp; COLLECT ASSETS`;
    }
  });

  function handleStreamEvent(data, aspect_ratio, clipDuration, quality) {
    if (data.type === "log") {
      logTerminal(data.message);
      if (data.progress !== undefined) {
        setProgress(data.progress);
      }
    } else if (data.type === "clip_ready") {
      const clip = data.clip;
      renderClipCard(clip, aspect_ratio, clipDuration, quality);
      addTimelineBlock(clip, clipDuration);
      logTerminal(`Clip #${clip.index} ready: ${clip.filename}`);
    } else if (data.type === "done") {
      setProgress(100, "COMPLETED");
      logTerminal(data.message, "info");
      
      currentProjectId = data.project_id;
      currentProjectDir = data.project_dir;
      currentXmlUrl = data.xml_url;

      // Handle Voice Only Output
      if (data.audio_url) {
        voiceOnlyAudioPlayer.src = data.audio_url;
        downloadVoiceMp3Btn.href = data.audio_url;
        if (data.srt_url) {
          downloadVoiceSrtBtn.href = data.srt_url;
          srtTranscriptViewer.value = data.srt_content || "SRT subtitles generated.";
        }
        voiceOnlyOutputCard.style.display = "flex";
      }

      if (data.master_url) {
        masterVideo.src = data.master_url;
        masterContainer.style.display = "flex";
      }

      if (data.clips && data.clips.length > 0) {
        exportActions.style.display = "flex";
        if (timelineBoardContainer) timelineBoardContainer.style.display = "flex";
      }
    } else if (data.type === "error") {
      logTerminal(`ERROR: ${data.message}`, "error");
      setProgress(0, "ERROR OCCURRED");
    }
  }

  function addTimelineBlock(clip, clipDuration) {
    if (!timelineVideoBlocks) return;
    if (timelineBoardContainer) timelineBoardContainer.style.display = "flex";

    const node = document.createElement("div");
    node.className = "timeline-clip-node";
    node.innerHTML = `<span>#${clip.index}</span> <span>${clipDuration.toFixed(1)}s</span>`;
    node.title = `Clip #${clip.index}: ${clip.keyword} (${clip.time_start}s - ${clip.time_end}s)`;
    node.addEventListener("click", () => {
      const targetCard = document.getElementById(`clip-card-${clip.index}`);
      if (targetCard) {
        targetCard.scrollIntoView({ behavior: "smooth", block: "center" });
        targetCard.style.borderColor = "var(--accent-yellow)";
        setTimeout(() => (targetCard.style.borderColor = "var(--border)"), 2000);
      }
    });
    timelineVideoBlocks.appendChild(node);
  }

  function renderClipCard(clip, aspect_ratio, clipDuration, quality) {
    const card = document.createElement("div");
    card.className = "clip-card";
    card.id = `clip-card-${clip.index}`;
    const isVertical = aspect_ratio === "9:16";

    card.innerHTML = `
      <div class="clip-preview ${isVertical ? 'vertical' : ''}">
        <video src="${clip.url}" controls preload="metadata" loop onmouseenter="this.play()" onmouseleave="this.pause()"></video>
      </div>
      <div class="clip-info">
        <div class="clip-tag">#${clip.index} • [${clip.time_start}s - ${clip.time_end}s] • ${clip.provider}</div>
        <div class="clip-kw" title="${clip.keyword}">${clip.keyword}</div>
        <div class="clip-actions">
          <button type="button" class="btn btn-dark btn-sm swap-clip-btn" data-index="${clip.index}" data-kw="${clip.keyword}" title="Swap with next stock result or custom query">
            <svg class="icon icon-sm"><use href="#icon-refresh"/></svg> SWAP
          </button>
          <a href="${clip.url}" download="${clip.filename}" class="btn btn-yellow btn-sm" title="Download Clip MP4">
            <svg class="icon icon-sm"><use href="#icon-download"/></svg> MP4
          </a>
          <button type="button" class="btn btn-cyan btn-sm copy-path-btn" data-path="${clip.path}" title="Copy Path">
            <svg class="icon icon-sm"><use href="#icon-copy"/></svg> PATH
          </button>
        </div>
      </div>
    `;

    card.querySelector(".swap-clip-btn").addEventListener("click", () => {
      swapClipIndexInput.value = clip.index;
      swapKeywordInput.value = clip.keyword;
      swapPageInput.value = "2";
      swapModal.classList.add("active");
    });

    card.querySelector(".copy-path-btn").addEventListener("click", (e) => {
      navigator.clipboard.writeText(clip.path);
      const btn = e.currentTarget;
      btn.innerHTML = `<svg class="icon icon-sm"><use href="#icon-check"/></svg> COPIED!`;
      setTimeout(() => (btn.innerHTML = `<svg class="icon icon-sm"><use href="#icon-copy"/></svg> PATH`), 1500);
    });

    clipsGrid.appendChild(card);
  }

  // Swap Clip Form Handler
  swapForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const clipIndex = parseInt(swapClipIndexInput.value, 10);
    const newKw = swapKeywordInput.value.trim();
    const page = parseInt(swapPageInput.value, 10) || 2;
    const aspect_ratio = document.querySelector('input[name="aspect_ratio"]:checked')?.value || "16:9";
    const quality = qualitySelect.value;
    const clipDuration = parseFloat(clipDurationInput.value) || 3.0;

    if (!currentProjectId) {
      alert("No active project ID found.");
      return;
    }

    swapModal.classList.remove("active");
    logTerminal(`Swapping Clip #${clipIndex} with query: '${newKw}' (Page ${page})...`);

    try {
      const resp = await fetch("/api/regenerate-clip", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: currentProjectId,
          clip_index: clipIndex,
          keyword: newKw,
          aspect_ratio,
          quality,
          duration: clipDuration,
          page
        })
      });
      const data = await resp.json();
      if (data.success) {
        logTerminal(`Clip #${clipIndex} replaced successfully with: ${data.filename}`);
        const card = document.getElementById(`clip-card-${clipIndex}`);
        if (card) {
          const video = card.querySelector("video");
          video.src = `${data.url}?t=${Date.now()}`;
          card.querySelector(".clip-kw").textContent = data.keyword;
        }
      } else {
        logTerminal(`Failed to swap clip: ${data.message}`, "error");
      }
    } catch (err) {
      logTerminal(`Swap error: ${err.message}`, "error");
    }
  });

  // Project Vault Loader
  async function loadProjectVault() {
    vaultTableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; font-family:var(--font-mono);">Loading past projects...</td></tr>`;
    try {
      const resp = await fetch("/api/projects");
      const data = await resp.json();
      const projects = data.projects || [];
      if (projects.length === 0) {
        vaultTableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; font-family:var(--font-mono); color:var(--text-muted);">No past projects found in downloads directory.</td></tr>`;
        return;
      }

      vaultTableBody.innerHTML = "";
      projects.forEach((p) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td style="font-weight:800;">${p.name}</td>
          <td class="mono">${p.created}</td>
          <td class="mono">${p.clip_count} clips (${p.duration}s)</td>
          <td class="mono">${p.aspect_ratio}</td>
          <td>
            ${p.has_master ? `<a href="${p.master_url}" target="_blank" class="btn btn-yellow btn-sm"><svg class="icon icon-sm"><use href="#icon-play"/></svg> PLAY</a>` : `<span style="color:var(--text-muted); font-size:11px;">Clips only</span>`}
          </td>
          <td>
            <div style="display:flex; gap:6px;">
              <button type="button" class="btn btn-lime btn-sm vault-open-btn" data-path="${p.path}">
                <svg class="icon icon-sm"><use href="#icon-folder"/></svg> EXPLORER
              </button>
              <a href="/api/download-zip/${p.id}" class="btn btn-cyan btn-sm">
                <svg class="icon icon-sm"><use href="#icon-download"/></svg> ZIP
              </a>
              <button type="button" class="btn btn-pink btn-sm vault-del-btn" data-id="${p.id}">
                <svg class="icon icon-sm"><use href="#icon-trash"/></svg>
              </button>
            </div>
          </td>
        `;

        tr.querySelector(".vault-open-btn").addEventListener("click", () => {
          fetch("/api/open-folder", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ path: p.path })
          });
        });

        tr.querySelector(".vault-del-btn").addEventListener("click", async () => {
          if (confirm(`Delete project '${p.name}'?`)) {
            await fetch("/api/delete-project", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ project_id: p.id })
            });
            loadProjectVault();
          }
        });

        vaultTableBody.appendChild(tr);
      });
    } catch (e) {
      vaultTableBody.innerHTML = `<tr><td colspan="6" style="color:#FF3366;">Error loading vault: ${e.message}</td></tr>`;
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
        logTerminal(`${data.message}`);
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

  // Initial Visibility Setup
  updateModeVisibility();
});

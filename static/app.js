// Global State
let eventSource = null;
let currentFilter = 'ALL';
let activeProjectData = null;
let activeClips = [];

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initSSE();
  fetchHardwareProfile();
  checkSystemHealth();
  initAudioDropzone();
  recalculateClips();
  recalculateETA();
  loadSettings();
  updateUsageSummary();

  setInterval(checkSystemHealth, 30000);
  setInterval(updateUsageSummary, 15000);
});

// ═══════════════════════════════════════════════════════════════
// 1. MULTI-PAGE SPA NAVIGATION
// ═══════════════════════════════════════════════════════════════

function switchPageView(pageId) {
  document.querySelectorAll('.page-view').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-tab-link').forEach(btn => btn.classList.remove('active'));

  const targetPage = document.getElementById(pageId);
  if (targetPage) targetPage.classList.add('active');

  const btnMap = {
    'page-studio': 'nav-btn-studio',
    'page-features': 'nav-btn-features',
    'page-about': 'nav-btn-about',
    'page-contact': 'nav-btn-contact'
  };

  const activeBtnId = btnMap[pageId];
  if (activeBtnId) {
    const btn = document.getElementById(activeBtnId);
    if (btn) btn.classList.add('active');
  }

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

window.switchPageView = switchPageView;

// ═══════════════════════════════════════════════════════════════
// 2. DUOLINGO-STYLE MASCOT ENGINE
// ═══════════════════════════════════════════════════════════════

function setMascotState(state, message) {
  const mascotMsg = document.getElementById('mascot-msg');
  const mascotTitle = document.getElementById('mascot-title');
  if (!mascotMsg) return;

  if (state === 'SEARCHING') {
    mascotTitle.innerText = 'Felix • Searching 9 Vaults...';
    mascotMsg.innerText = message || 'Analyzing your script and searching millions of 1080p stock footage clips in parallel across 9 sources!';
  } else if (state === 'SUCCESS') {
    mascotTitle.innerText = 'Felix • Scene Wrap! 🎬';
    mascotMsg.innerText = message || 'All 3.0s clips are rendered and timeline-ready! Export to Premiere, DaVinci, or CapCut below.';
  } else if (state === 'DOCTOR') {
    mascotTitle.innerText = 'Felix • AI Doctor 🩺';
    mascotMsg.innerText = message || 'I detected a pipeline issue. Let me diagnose what happened and guide you through the fix!';
  } else {
    mascotTitle.innerText = 'Felix • AI B-Roll Director';
    mascotMsg.innerText = message || 'Paste your voiceover script and let me collect exact 3.0s visual b-roll scenes!';
  }
}

window.setMascotState = setMascotState;

// ═══════════════════════════════════════════════════════════════
// 3. THEME SWITCHER
// ═══════════════════════════════════════════════════════════════

function initTheme() {
  const savedTheme = localStorage.getItem('app-theme') || 'light';
  applyTheme(savedTheme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  const target = current === 'dark' ? 'light' : 'dark';
  applyTheme(target);
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('app-theme', theme);

  const btnIcon = document.getElementById('theme-btn-icon');
  const btnLabel = document.getElementById('theme-btn-label');
  if (btnIcon && btnLabel) {
    btnIcon.innerText = theme === 'dark' ? '☀️' : '🌙';
    btnLabel.innerText = theme === 'dark' ? 'Light' : 'Dark';
  }
}

window.toggleTheme = toggleTheme;
window.applyTheme = applyTheme;

// ═══════════════════════════════════════════════════════════════
// 4. DURATION & ETA CALCULATION
// ═══════════════════════════════════════════════════════════════

function parseDurationToSeconds(input) {
  const raw = String(input).trim();
  if (raw.includes(':')) {
    const parts = raw.split(':');
    if (parts.length === 2) {
      const mins = parseInt(parts[0], 10) || 0;
      const secs = parseFloat(parts[1]) || 0;
      return (mins * 60) + secs;
    } else if (parts.length === 3) {
      const hrs = parseInt(parts[0], 10) || 0;
      const mins = parseInt(parts[1], 10) || 0;
      const secs = parseFloat(parts[2]) || 0;
      return (hrs * 3600) + (mins * 60) + secs;
    }
  }
  return parseFloat(raw) || 90;
}

function formatSecondsToMMSS(seconds) {
  const totalSecs = Math.max(0, Math.round(seconds));
  const mins = Math.floor(totalSecs / 60);
  const secs = totalSecs % 60;
  return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

function recalculateClips() {
  const durationInput = document.getElementById('duration_input').value;
  const clipDuration = parseFloat(document.getElementById('clip_duration').value) || 3.0;
  
  const totalSeconds = parseDurationToSeconds(durationInput);
  const formattedMMSS = formatSecondsToMMSS(totalSeconds);
  const clipCount = Math.max(1, Math.round(totalSeconds / clipDuration));

  const badge = document.getElementById('calc-summary-badge');
  badge.innerHTML = `<strong>${totalSeconds}s (${formattedMMSS}) total</strong> &nbsp;|&nbsp; <strong>${clipCount} clips</strong> @ ${clipDuration}s each`;

  recalculateETA();
}

async function recalculateETA() {
  const durationInput = document.getElementById('duration_input').value;
  const clipDuration = parseFloat(document.getElementById('clip_duration').value) || 3.0;
  const quality = document.getElementById('quality_select').value || '1080p';

  try {
    const res = await fetch('/api/calculate-eta', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        duration_input: durationInput,
        clip_duration: clipDuration,
        quality
      })
    });
    const data = await res.json();
    const badge = document.getElementById('eta-badge');
    badge.innerHTML = `⚡ Estimated Time: ~<strong>${data.formatted_eta}</strong> (${data.speed_rating} &bull; ${data.parallel_workers}-core FFmpeg)`;
  } catch (e) {}
}

let uploadedAudioFile = null;
let estimatedWordDurationSecs = 0;

function handleAudioUpload(file) {
  if (!file) return;
  uploadedAudioFile = file;

  const audio = new Audio();
  const objectUrl = URL.createObjectURL(file);
  audio.src = objectUrl;

  audio.onloadedmetadata = () => {
    const duration = Math.round(audio.duration);
    const mmss = formatSecondsToMMSS(duration);
    
    document.getElementById('duration_input').value = mmss;
    document.getElementById('audio-file-label').innerHTML = `✅ ${escapeHtml(file.name)} <span class="audio-detected-badge">${duration}s (${mmss})</span>`;
    document.getElementById('audio-file-subtext').innerText = `Duration detected! Audio will be automatically muxed into master video.`;
    document.getElementById('clear-audio-btn').style.display = 'inline-block';
    
    recalculateClips();
  };

  audio.onerror = () => {
    alert('Could not read audio duration. Please check file format.');
  };
}

function clearAudioUpload() {
  uploadedAudioFile = null;
  document.getElementById('voiceover_file_input').value = '';
  document.getElementById('audio-file-label').innerText = 'Upload / Drop Voiceover Audio (Optional)';
  document.getElementById('audio-file-subtext').innerText = 'Auto-detects timing & automatically merges audio into your master MP4';
  document.getElementById('clear-audio-btn').style.display = 'none';
}

function autoCalculateWordsEstimate() {
  const text = document.getElementById('script_text').value.trim();
  const words = text ? text.split(/\s+/).filter(w => w.length > 0).length : 0;
  
  document.getElementById('script-char-count').innerText = `${text.length} chars (${words} words)`;
  
  const estimateBtn = document.getElementById('btn-auto-estimate');
  if (words >= 5) {
    const estSecs = Math.max(6, Math.round(words / 2.5));
    estimatedWordDurationSecs = estSecs;
    const mmss = formatSecondsToMMSS(estSecs);
    estimateBtn.innerText = `⚡ Auto-Estimate: ~${estSecs}s (${mmss})`;
    estimateBtn.style.display = 'inline-block';
  } else {
    estimateBtn.style.display = 'none';
  }
}

function applyWordEstimate() {
  if (estimatedWordDurationSecs > 0) {
    document.getElementById('duration_input').value = formatSecondsToMMSS(estimatedWordDurationSecs);
    recalculateClips();
  }
}

function initAudioDropzone() {
  const dropzone = document.getElementById('audio-dropzone');
  if (!dropzone) return;

  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('dragover');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('dragover');
    }, false);
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files && files.length > 0) {
      handleAudioUpload(files[0]);
    }
  }, false);
}

window.handleAudioUpload = handleAudioUpload;
window.clearAudioUpload = clearAudioUpload;
window.autoCalculateWordsEstimate = autoCalculateWordsEstimate;
window.applyWordEstimate = applyWordEstimate;

function updateCharCount() {
  autoCalculateWordsEstimate();
}

function loadSampleScript() {
  const sample = `Artificial intelligence is transforming global computing at breakneck speed.
Inside modern high-tech research laboratories, engineers and roboticists design autonomous systems.
From busy bustling metropolis streets with electric transportation to high-speed fiber-optic data centers, digital networks process petabytes of real-time data every single second.
Businesses collaborate in sleek modern glass offices, looking at rising financial market analytics and cyber security graphs.
The future belongs to those who adapt to this relentless wave of autonomous technology.`;
  document.getElementById('script_text').value = sample;
  updateCharCount();
  applyWordEstimate();
}

window.recalculateClips = recalculateClips;
window.recalculateETA = recalculateETA;
window.updateCharCount = updateCharCount;
window.loadSampleScript = loadSampleScript;

// ═══════════════════════════════════════════════════════════════
// 5. USAGE & QUOTA POLLING
// ═══════════════════════════════════════════════════════════════

async function updateUsageSummary() {
  try {
    const res = await fetch('/api/usage-summary');
    const data = await res.json();

    const pex = data.pexels || {};
    const pix = data.pixabay || {};
    const ai = data.ai || {};

    const navPill = document.getElementById('nav-quota-text');
    if (navPill) {
      navPill.innerText = `Pexels: ${pex.remaining || 200}/hr | Pixabay: ${pix.remaining || 5000}/hr | Coverr/Mixkit/Storyblocks Ready`;
    }

    const pexInfo = document.getElementById('quota-pexels-info');
    if (pexInfo) {
      pexInfo.innerText = `Quota: ${pex.limit || 200} req/hr | Used: ${pex.used || 0} | Remaining: ${pex.remaining || 200} | Resets in ${pex.reset_in_mins || 60}m`;
    }

    const pixInfo = document.getElementById('quota-pixabay-info');
    if (pixInfo) {
      pixInfo.innerText = `Quota: ${pix.limit || 5000} req/hr | Used: ${pix.used || 0} | Remaining: ${pix.remaining || 5000}`;
    }
  } catch (e) {}
}

// ═══════════════════════════════════════════════════════════════
// 6. REAL-TIME EVENT STREAM & TERMINAL
// ═══════════════════════════════════════════════════════════════

function initSSE() {
  if (eventSource) eventSource.close();
  eventSource = new EventSource('/api/events');

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      appendLogLine(data);
    } catch (e) {}
  };
}

function selectAspectRatio(ratio) {
  document.getElementById('aspect_ratio_select').value = ratio;
  document.querySelectorAll('#aspect-ratio-group .toggle-item').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.value === ratio);
  });
}

function selectQuality(quality) {
  document.getElementById('quality_select').value = quality;
  document.querySelectorAll('#quality-group .toggle-item').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.value === quality);
  });
  recalculateETA();
}

function showToast(title, message, type = 'success', duration = 3500) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const icons = {
    success: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#000" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>',
    info: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#000" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
    warning: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#000" stroke-width="2.5"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    error: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#000" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>'
  };

  const toast = document.createElement('div');
  toast.className = `toast-card toast-${type}`;
  toast.innerHTML = `
    <div class="toast-icon-box">${icons[type] || icons.info}</div>
    <div class="toast-content">
      <div class="toast-title">${escapeHtml(title)}</div>
      <div class="toast-message">${escapeHtml(message)}</div>
    </div>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.transition = 'all 200ms ease-out';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 250);
  }, duration);
}

let currentClipsView = 'grid';

function switchClipsView(mode) {
  currentClipsView = mode;
  const gridContainer = document.getElementById('clips-grid-container');
  const tableWrapper = document.getElementById('clips-table-wrapper');
  const btnGrid = document.getElementById('tab-grid-view');
  const btnTable = document.getElementById('tab-table-view');

  if (mode === 'grid') {
    gridContainer.style.display = 'grid';
    tableWrapper.style.display = 'none';
    btnGrid.classList.add('active');
    btnTable.classList.remove('active');
  } else {
    gridContainer.style.display = 'none';
    tableWrapper.style.display = 'block';
    btnTable.classList.add('active');
    btnGrid.classList.remove('active');
  }
}

window.selectAspectRatio = selectAspectRatio;
window.selectQuality = selectQuality;
window.showToast = showToast;
window.switchClipsView = switchClipsView;

function resetProgressAndTable() {
  document.getElementById('main-progress-bar').style.width = '5%';
  document.getElementById('progress-pct-text').innerText = '5%';
  document.getElementById('progress-step-text').innerText = 'Starting pipeline...';
  document.getElementById('job-status-badge').className = 'status-badge RUNNING';
  document.getElementById('job-status-badge').innerText = 'RUNNING';

  document.getElementById('ms-ai-val').innerText = '0';
  document.getElementById('ms-search-val').innerText = '0';
  document.getElementById('ms-dl-val').innerText = '0';
  document.getElementById('ms-proc-val').innerText = '0';

  document.getElementById('result-actions').style.display = 'none';
  renderSkeletonCards(6);
  document.getElementById('clips-table-body').innerHTML = '<tr class="empty-row"><td colspan="8">Initializing and generating keywords...</td></tr>';
}

function renderSkeletonCards(count = 6) {
  const container = document.getElementById('clips-grid-container');
  if (!container) return;
  container.innerHTML = '';
  for (let i = 1; i <= count; i++) {
    const sk = document.createElement('div');
    sk.className = 'skeleton-card';
    sk.innerHTML = `
      <div class="skeleton-box" style="height: 100px;"></div>
      <div class="skeleton-box" style="height: 14px; width: 75%;"></div>
      <div class="skeleton-box" style="height: 10px; width: 45%;"></div>
    `;
    container.appendChild(sk);
  }
}

function appendLogLine(data) {
  const terminal = document.getElementById('terminal-body');
  const line = document.createElement('div');
  line.className = `log-line log-${data.level.toLowerCase()} log-${data.category.toLowerCase()}`;
  line.dataset.category = data.category.toUpperCase();
  line.dataset.level = data.level.toUpperCase();

  line.innerText = `[${data.timestamp}] [${data.category}] ${data.message}`;

  if (!shouldShowLogLine(line.dataset.category, line.dataset.level)) {
    line.style.display = 'none';
  }

  terminal.appendChild(line);
  terminal.scrollTop = terminal.scrollHeight;
}

function shouldShowLogLine(cat, lvl) {
  if (currentFilter === 'ALL') return true;
  if (currentFilter === 'ERROR' && lvl === 'ERROR') return true;
  if (currentFilter === cat) return true;
  return false;
}

function setLogFilter(filter) {
  currentFilter = filter;
  document.querySelectorAll('.log-filter-chips .chip').forEach(c => {
    c.classList.toggle('active', c.innerText.toUpperCase() === filter);
  });

  document.querySelectorAll('#terminal-body .log-line').forEach(line => {
    const cat = line.dataset.category || '';
    const lvl = line.dataset.level || '';
    line.style.display = shouldShowLogLine(cat, lvl) ? 'block' : 'none';
  });
}

function copyTerminalLogs() {
  const terminal = document.getElementById('terminal-body');
  navigator.clipboard.writeText(terminal.innerText).then(() => {
    alert('Logs copied to clipboard!');
  });
}

function clearTerminalLogs() {
  document.getElementById('terminal-body').innerHTML = '<div class="log-line log-system">[SYSTEM] Console cleared.</div>';
}

window.setLogFilter = setLogFilter;
window.copyTerminalLogs = copyTerminalLogs;
window.clearTerminalLogs = clearTerminalLogs;

// ═══════════════════════════════════════════════════════════════
// 7. PIPELINE LAUNCH & MONITOR (9 STOCK SOURCES)
// ═══════════════════════════════════════════════════════════════

async function handleStartCollection(e) {
  e.preventDefault();

  const script = document.getElementById('script_text').value.trim();
  if (!script) {
    alert('Please enter a script.');
    return;
  }

  const durationInput = document.getElementById('duration_input').value;
  const clipDuration = parseFloat(document.getElementById('clip_duration').value);
  const projectName = document.getElementById('project_name').value.trim() || 'broll_project';
  const quality = document.getElementById('quality_select').value;
  const aspectRatio = document.getElementById('aspect_ratio_select').value;
  const mediaType = document.getElementById('media_type_select').value;
  const aiProvider = document.getElementById('ai_provider_select').value;
  const transition = document.getElementById('transition_select').value;
  const colorPreset = document.getElementById('color_preset_select').value;
  const enableKenBurns = document.getElementById('enable_ken_burns').checked;
  const exportFullVideo = document.getElementById('export_full_video_toggle').checked;

  const providers = [];
  if (document.getElementById('provider_pexels')?.checked) providers.push('pexels');
  if (document.getElementById('provider_pixabay')?.checked) providers.push('pixabay');
  if (document.getElementById('provider_coverr')?.checked) providers.push('coverr');
  if (document.getElementById('provider_mixkit')?.checked) providers.push('mixkit');
  if (document.getElementById('provider_storyblocks')?.checked) providers.push('storyblocks');
  if (document.getElementById('provider_videvo')?.checked) providers.push('videvo');
  if (document.getElementById('provider_pinterest')?.checked) providers.push('pinterest');
  if (document.getElementById('provider_unsplash')?.checked) providers.push('unsplash');
  if (document.getElementById('provider_wikimedia')?.checked) providers.push('wikimedia');

  const enableFallback = document.getElementById('enable_fallback').checked;

  const payload = {
    script,
    duration_input: durationInput,
    clip_duration: clipDuration,
    project_name: projectName,
    quality,
    aspect_ratio: aspectRatio,
    media_type: mediaType,
    providers,
    enable_fallback: enableFallback,
    ai_provider: aiProvider,
    transition,
    color_preset: colorPreset,
    enable_ken_burns: enableKenBurns,
    export_full_video: exportFullVideo
  };

  setUIWorking(true);
  resetProgressAndTable();
  dismissErrorDoctor();
  setMascotState('SEARCHING', 'Searching across 9 stock media vaults in parallel...');

  try {
    const res = await fetch('/api/collect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (!res.ok) {
      triggerErrorDoctor(data.detail || 'Unknown error');
      setUIWorking(false);
    } else {
      showToast('Pipeline Started', `Collecting scenes across 9 vaults in parallel...`, 'info');
      pollJobStatus();
    }
  } catch (err) {
    triggerErrorDoctor(err.message);
    setUIWorking(false);
  }
}

let pollTimer = null;
function pollJobStatus() {
  if (pollTimer) clearInterval(pollTimer);

  pollTimer = setInterval(async () => {
    try {
      const res = await fetch('/api/job-status');
      const job = await res.json();
      updateDashboardFromJob(job);

      if (job.status === 'COMPLETED') {
        clearInterval(pollTimer);
        setUIWorking(false);
        updateUsageSummary();
        showToast('Pipeline Complete', `${job.completed_clips} clips rendered successfully!`, 'success');
        setMascotState('SUCCESS', `Directing complete! ${job.completed_clips} clips rendered into ${job.folder_name}/clips/`);
      } else if (job.status === 'FAILED') {
        clearInterval(pollTimer);
        setUIWorking(false);
        showToast('Pipeline Failed', job.error || 'Check error doctor', 'error');
        triggerErrorDoctor(job.error || 'Pipeline job failed');
      }
    } catch (e) {}
  }, 1000);
}

function updateDashboardFromJob(job) {
  const pct = job.percent || 0;
  document.getElementById('main-progress-bar').style.width = `${pct}%`;
  document.getElementById('progress-pct-text').innerText = `${pct}%`;
  document.getElementById('progress-step-text').innerText = job.current_step || 'Processing...';

  const badge = document.getElementById('job-status-badge');
  badge.className = `status-badge ${job.status}`;
  badge.innerText = job.status;

  if (job.clips && job.clips.length > 0) {
    activeClips = job.clips;
    renderClipsGrid(job.clips);
    renderClipsTable(job.clips);

    document.getElementById('ms-ai-val').innerText = job.clips.length;
    document.getElementById('ms-search-val').innerText = job.clips.filter(c => c.found).length;
    document.getElementById('ms-dl-val').innerText = job.clips.filter(c => c.download_success).length;
    document.getElementById('ms-proc-val').innerText = job.clips.filter(c => c.process_success).length;
  }

  if (job.status === 'COMPLETED') {
    activeProjectData = job;
    document.getElementById('result-actions').style.display = 'block';
    document.getElementById('result-summary-text').innerText =
      `🎉 Collection Complete! ${job.completed_clips} / ${job.total_clips} clips ready in ${job.folder_name}/clips/`;
  }
}

function renderClipsGrid(clips) {
  const container = document.getElementById('clips-grid-container');
  if (!container) return;

  if (!clips || clips.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; padding: 2.5rem 1rem; text-align: center; color: var(--text-muted, #666); font-size: 0.85rem; font-weight: 700;">
        No clips yet. Enter your voiceover script on the left and click <strong>Start B-Roll Collection</strong>.
      </div>
    `;
    return;
  }

  container.innerHTML = '';
  clips.forEach(c => {
    const card = document.createElement('div');
    card.className = 'clip-gallery-card';

    let clipUrl = '';
    if (activeProjectData && activeProjectData.folder_name && c.output_filename) {
      clipUrl = `/downloads/${activeProjectData.folder_name}/clips/${c.output_filename}`;
    } else if (c.video_url) {
      clipUrl = c.video_url;
    }

    const thumbSrc = c.thumbnail_url || '/static/assets/placeholder_video.png';

    card.innerHTML = `
      <div class="clip-card-thumb-wrapper" onclick="previewClip(${c.index})" title="Click to play preview">
        <img src="${thumbSrc}" class="clip-card-thumb" alt="Clip ${c.index}" onerror="this.src='data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'100%\\' height=\\'100%\\' viewBox=\\'0 0 24 24\\'><rect fill=\\'%23111\\' width=\\'24\\' height=\\'24\\'/><text fill=\\'%23fff\\' x=\\'50%\\' y=\\'50%\\' text-anchor=\\'middle\\' font-size=\\'3\\' font-weight=\\'bold\\'>CLIP #${c.index}</text></svg>'">
        <span class="clip-index-tag">#${c.index.toString().padStart(2, '0')}</span>
        <span class="clip-provider-tag">${(c.provider || 'AUTO').toUpperCase()}</span>
      </div>
      <div class="clip-card-info">
        <div class="clip-keyword-title">${escapeHtml(c.keyword || 'Generating keyword...')}</div>
        <div style="font-size: 0.72rem; color: var(--text-muted, #666); margin-bottom: 0.4rem;">
          ⏱ ${c.final_duration || 3.0}s &bull; ${c.resolution || c.quality || '1080p'}
        </div>
        <div class="clip-card-footer">
          <button class="btn btn-secondary btn-xs" onclick="previewClip(${c.index})" title="Preview clip" style="flex: 1;">▶ Play</button>
          <button class="btn btn-warning btn-xs" onclick="openSwapDrawer(${c.index})" title="Swap Clip" style="flex: 1; background:#ffff00; color:#000; font-weight:800; border:1.5px solid #000;">🔄 Swap</button>
          ${clipUrl ? `<a href="${clipUrl}" download="${c.output_filename || 'clip_' + c.index + '.mp4'}" class="btn btn-primary btn-xs" title="Download" style="text-decoration:none; padding: 2px 6px;">⬇</a>` : ''}
        </div>
      </div>
    `;

    container.appendChild(card);
  });
}

function setUIWorking(working) {
  const btn = document.getElementById('btn-submit');
  btn.disabled = working;
  btn.innerHTML = working
    ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> Directing Video Pipeline...'
    : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> Start B-Roll Collection';

  const cancelBtn = document.getElementById('btn-cancel-job');
  if (cancelBtn) {
    cancelBtn.style.display = working ? 'inline-block' : 'none';
  }
}

async function cancelActiveJob() {
  if (!confirm('Are you sure you want to stop the generation?')) return;
  try {
    const res = await fetch('/api/job/cancel', { method: 'POST' });
    const data = await res.json();
    setUIWorking(false);
    document.getElementById('job-status-badge').innerText = 'CANCELLED';
    document.getElementById('job-status-badge').className = 'status-badge FAILED';
    document.getElementById('progress-step-text').innerText = 'Job stopped by user.';
    const cancelBtn = document.getElementById('btn-cancel-job');
    if (cancelBtn) cancelBtn.style.display = 'none';
  } catch (e) {
    alert('Failed to cancel job: ' + e.message);
  }
}

async function fetchHardwareProfile() {
  try {
    const res = await fetch('/api/system/profile');
    const data = await res.json();
    const pill = document.getElementById('nav-hw-text');
    if (pill) {
      pill.innerText = data.label || '💻 Hardware Ready';
    }
  } catch (e) {}
}

let currentSwapIndex = null;

function openSwapDrawer(index) {
  currentSwapIndex = index;
  const clip = activeClips.find(c => c.index === index);
  if (!clip) return;

  document.getElementById('swap-badge-text').innerText = `CLIP #${index.toString().padStart(2, '0')}`;
  document.getElementById('swap-title-text').innerText = `Swap Clip #${index}`;
  document.getElementById('swap-keyword-input').value = clip.keyword || '';
  document.getElementById('swap-status-box').style.display = 'none';
  document.getElementById('swap-drawer').style.display = 'flex';
  document.getElementById('swap-drawer-overlay').style.display = 'block';
}

function closeSwapDrawer() {
  document.getElementById('swap-drawer').style.display = 'none';
  document.getElementById('swap-drawer-overlay').style.display = 'none';
  currentSwapIndex = null;
}

async function executeSingleClipSwap() {
  if (!currentSwapIndex || !activeProjectData || !activeProjectData.folder_name) {
    alert('Please wait until project is loaded.');
    return;
  }
  const newKw = document.getElementById('swap-keyword-input').value.trim();
  if (!newKw) {
    alert('Please enter a keyword.');
    return;
  }

  const btn = document.getElementById('btn-execute-swap');
  const statusBox = document.getElementById('swap-status-box');
  btn.disabled = true;
  btn.innerText = '⚡ Searching & Rendering (~2s)...';
  statusBox.style.display = 'block';
  statusBox.innerText = '🔍 Fetching stock media & rendering with FFmpeg...';

  try {
    const res = await fetch('/api/clip/swap', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        folder_name: activeProjectData.folder_name,
        clip_index: currentSwapIndex,
        new_keyword: newKw
      })
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.detail || 'Swap failed.');
    }

    // Update in-memory clips
    const idx = activeClips.findIndex(c => c.index === currentSwapIndex);
    if (idx !== -1) {
      activeClips[idx] = data.clip;
      renderClipsTable(activeClips);
    }

    statusBox.innerText = `✅ Clip #${currentSwapIndex} successfully swapped!`;
    setTimeout(() => {
      closeSwapDrawer();
      btn.disabled = false;
      btn.innerText = '⚡ Regenerate Clip (~2s)';
    }, 1200);

  } catch (err) {
    statusBox.innerText = `❌ Error: ${err.message}`;
    btn.disabled = false;
    btn.innerText = '⚡ Try Again';
  }
}

window.cancelActiveJob = cancelActiveJob;
window.openSwapDrawer = openSwapDrawer;
window.closeSwapDrawer = closeSwapDrawer;
window.executeSingleClipSwap = executeSingleClipSwap;

function renderClipsTable(clips) {
  const tbody = document.getElementById('clips-table-body');
  document.getElementById('clips-summary-label').innerText = `${clips.length} Clips`;

  tbody.innerHTML = '';
  clips.forEach(c => {
    const tr = document.createElement('tr');
    
    let thumbHtml = '<div class="clip-thumb"></div>';
    if (c.thumbnail_url) {
      thumbHtml = `<img src="${c.thumbnail_url}" class="clip-thumb" onclick="previewClip(${c.index})" title="Click to preview" />`;
    }

    let statusClass = 'PENDING';
    let statusText = 'Waiting';
    if (c.process_success) {
      statusClass = 'COMPLETED';
      statusText = '✓ Ready';
    } else if (c.download_success) {
      statusClass = 'DOWNLOADED';
      statusText = '⟳ Proc';
    } else if (c.found) {
      statusClass = 'FOUND';
      statusText = 'Found';
    } else if (c.status === 'FAILED' || c.download_error || c.process_error) {
      statusClass = 'FAILED';
      statusText = '✕ Fail';
    }

    let actionButtons = '';
    let clipUrl = '';
    if (activeProjectData && activeProjectData.folder_name && c.output_filename) {
      clipUrl = `/downloads/${activeProjectData.folder_name}/clips/${c.output_filename}`;
    } else if (c.video_url) {
      clipUrl = c.video_url;
    }

    actionButtons = `
      <div style="display: flex; gap: 4px;">
        <button class="btn btn-secondary btn-xs" onclick="previewClip(${c.index})" title="Preview clip">▶</button>
        <button class="btn btn-warning btn-xs" onclick="openSwapDrawer(${c.index})" title="Swap / Regenerate this single clip" style="background:#ffd700; color:#000; font-weight:700; border:1px solid #000;">🔄</button>
        ${clipUrl ? `<a href="${clipUrl}" download="${c.output_filename || 'clip_' + c.index + '.mp4'}" class="btn btn-primary btn-xs" title="Download MP4" style="text-decoration:none; padding: 2px 6px;">⬇</a>` : ''}
      </div>
    `;

    tr.innerHTML = `
      <td><strong>#${c.index}</strong></td>
      <td>${thumbHtml}</td>
      <td><strong>${escapeHtml(c.keyword || '')}</strong></td>
      <td><span class="status-badge COMPLETED">${(c.provider || 'auto').toUpperCase()}</span></td>
      <td>${c.resolution || c.quality || '1080p'}</td>
      <td>${c.final_duration ? c.final_duration + 's' : '3.0s'}</td>
      <td><span class="clip-status-tag ${statusClass}">${statusText}</span></td>
      <td>${actionButtons}</td>
    `;
    tbody.appendChild(tr);
  });
}

let currentPreviewClipIndex = null;

function previewClip(index) {
  currentPreviewClipIndex = index;
  const clip = activeClips.find(c => c.index === index);
  if (!clip) return;

  const modal = document.getElementById('video-preview-modal');
  const player = document.getElementById('modal-video-player');
  const title = document.getElementById('modal-video-title');
  const meta = document.getElementById('modal-video-meta');
  const dlBtn = document.getElementById('modal-video-download-btn');

  title.innerText = `Clip #${clip.index}: ${clip.keyword}`;

  let srcUrl = '';
  if (activeProjectData && activeProjectData.folder_name && clip.output_filename) {
    srcUrl = `/downloads/${activeProjectData.folder_name}/clips/${clip.output_filename}`;
  } else if (clip.video_url) {
    srcUrl = clip.video_url;
  }

  if (srcUrl) {
    player.src = srcUrl;
    player.play().catch(() => {});
    modal.classList.add('active');
    meta.innerText = `Provider: ${(clip.provider || 'auto').toUpperCase()} | Resolution: ${clip.resolution || '1080p'} | Duration: ${clip.final_duration || 3.0}s`;
    if (dlBtn) {
      dlBtn.href = srcUrl;
      dlBtn.download = clip.output_filename || `clip_${clip.index}.mp4`;
    }
  }
}

function closeVideoModal(e) {
  const modal = document.getElementById('video-preview-modal');
  if (!modal) return;
  const player = document.getElementById('modal-video-player');
  if (player) {
    player.pause();
    player.src = '';
  }
  modal.classList.remove('active');
  currentPreviewClipIndex = null;
}

document.addEventListener('keydown', (e) => {
  const modal = document.getElementById('video-preview-modal');
  if (modal && modal.classList.contains('active')) {
    if (e.key === 'Escape') {
      closeVideoModal();
    } else if (e.key === ' ' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
      e.preventDefault();
      const player = document.getElementById('modal-video-player');
      if (player.paused) player.play();
      else player.pause();
    }
  }
});

window.handleStartCollection = handleStartCollection;
window.previewClip = previewClip;
window.closeVideoModal = closeVideoModal;

// ═══════════════════════════════════════════════════════════════
// 8. NLE TIMELINE & FULL VIDEO EXPORTERS
// ═══════════════════════════════════════════════════════════════

function downloadNLE(format) {
  if (!activeProjectData || !activeProjectData.folder_name) {
    alert('Please run a b-roll collection job first.');
    return;
  }
  window.location.href = `/api/export-nle/${activeProjectData.folder_name}/${format}`;
}

async function triggerStitchFullVideo() {
  if (!activeProjectData || !activeProjectData.folder_name) {
    alert('Please run a b-roll collection job first.');
    return;
  }

  const resActions = document.getElementById('result-summary-text');
  resActions.innerText = '🎬 Stitching full master video... Please wait...';

  try {
    const res = await fetch('/api/export-full-video', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ folder_name: activeProjectData.folder_name })
    });
    const data = await res.json();
    if (data.success && data.master_url) {
      resActions.innerText = `🎉 Master video ready: ${data.filename}!`;
      // Open preview modal with full video
      const modal = document.getElementById('video-preview-modal');
      const player = document.getElementById('modal-video-player');
      const title = document.getElementById('modal-video-title');
      title.innerText = `Full Master Video: ${data.filename}`;
      player.src = data.master_url;
      player.play().catch(() => {});
      modal.classList.add('active');
    } else {
      alert('Failed to stitch video.');
    }
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
}

window.downloadNLE = downloadNLE;
window.triggerStitchFullVideo = triggerStitchFullVideo;

// ═══════════════════════════════════════════════════════════════
// 9. SELF-HEALING AI ERROR DOCTOR
// ═══════════════════════════════════════════════════════════════

async function triggerErrorDoctor(errorMessage) {
  setMascotState('DOCTOR', 'I caught an error! Let me diagnose the exact solution for your system.');

  const card = document.getElementById('error-doctor-card');
  const title = document.getElementById('err-doc-title');
  const expl = document.getElementById('err-doc-expl');
  const list = document.getElementById('err-doc-steps-list');

  card.classList.add('active');
  title.innerText = 'Diagnosing with AI Error Doctor...';
  expl.innerText = errorMessage;

  try {
    const res = await fetch('/api/ai-diagnose-error', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error_message: errorMessage })
    });
    const diag = await res.json();
    title.innerText = `${diag.category}: ${diag.title}`;
    expl.innerText = diag.explanation;

    list.innerHTML = '';
    (diag.solution_steps || []).forEach(s => {
      const li = document.createElement('li');
      li.innerText = s;
      list.appendChild(li);
    });
  } catch (e) {
    title.innerText = 'Pipeline Execution Issue';
    list.innerHTML = '<li>Check your internet connection and API keys in Settings.</li>';
  }
}

function dismissErrorDoctor() {
  document.getElementById('error-doctor-card').classList.remove('active');
  setMascotState('IDLE');
}

function retryActiveJob() {
  dismissErrorDoctor();
  const form = document.getElementById('collector-form');
  form.dispatchEvent(new Event('submit'));
}

window.triggerErrorDoctor = triggerErrorDoctor;
window.dismissErrorDoctor = dismissErrorDoctor;
window.retryActiveJob = retryActiveJob;

// ═══════════════════════════════════════════════════════════════
// 10. EXPLORER & ZIP
// ═══════════════════════════════════════════════════════════════

async function openActiveClipsFolder() {
  if (!activeProjectData || !activeProjectData.folder_name) return;
  const path = `downloads/${activeProjectData.folder_name}/clips`;
  await fetch('/api/open-folder', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path })
  });
}

function downloadZip() {
  if (!activeProjectData || !activeProjectData.folder_name) return;
  window.location.href = `/api/download-zip/${activeProjectData.folder_name}`;
}

window.openActiveClipsFolder = openActiveClipsFolder;
window.downloadZip = downloadZip;

// ═══════════════════════════════════════════════════════════════
// 11. SETTINGS & CODE COPIER (WITH STORYBLOCKS & COVERR)
// ═══════════════════════════════════════════════════════════════

async function checkSystemHealth() {
  try {
    const res = await fetch('/api/health');
    const h = await res.json();
  } catch (e) {}
}

function openSettingsModal(defaultTab) {
  document.getElementById('settings-modal').classList.add('active');
  if (defaultTab) switchSettingsTab(defaultTab);
  loadSettings();
}

function closeSettingsModal(e) {
  if (!e || e.target.id === 'settings-modal' || e.target.className === 'btn-close' || e.target.innerText === 'Close') {
    document.getElementById('settings-modal').classList.remove('active');
  }
}

function switchSettingsTab(tabId) {
  document.querySelectorAll('.settings-tabs .tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('onclick').includes(tabId));
  });
  document.querySelectorAll('.tab-pane').forEach(pane => {
    pane.classList.toggle('active', pane.id === tabId);
  });
}

async function loadSettings() {
  try {
    const res = await fetch('/api/settings');
    const s = await res.json();

    document.getElementById('set_openrouter_key').value = s.OPENROUTER_API_KEY || '';
    document.getElementById('set_openrouter_model').value = s.OPENROUTER_MODEL || 'openrouter/free';

    document.getElementById('set_deepseek_key').value = s.DEEPSEEK_API_KEY || '';
    document.getElementById('set_deepseek_model').value = s.DEEPSEEK_MODEL || 'deepseek-chat';

    document.getElementById('set_groq_key').value = s.GROQ_API_KEY || '';
    document.getElementById('set_groq_model').value = s.GROQ_MODEL || 'llama-3.3-70b-versatile';

    document.getElementById('set_gemini_key').value = s.GEMINI_API_KEY || '';
    document.getElementById('set_gemini_model').value = s.GEMINI_MODEL || 'gemini-1.5-flash';

    document.getElementById('set_openai_key').value = s.OPENAI_API_KEY || '';
    document.getElementById('set_openai_model').value = s.OPENAI_MODEL || 'gpt-4o-mini';

    document.getElementById('set_anthropic_key').value = s.ANTHROPIC_API_KEY || '';
    document.getElementById('set_anthropic_model').value = s.ANTHROPIC_MODEL || 'claude-3-5-sonnet-20241022';

    document.getElementById('set_ollama_endpoint').value = s.OLLAMA_ENDPOINT || 'http://localhost:11434/v1/chat/completions';
    document.getElementById('set_ollama_model').value = s.OLLAMA_MODEL || 'llama3.2';

    // Custom AI Builder
    document.getElementById('set_custom_name').value = s.CUSTOM_AI_NAME || 'Custom LLM';
    document.getElementById('set_custom_endpoint').value = s.CUSTOM_AI_ENDPOINT || '';
    document.getElementById('set_custom_key').value = s.CUSTOM_AI_KEY || '';
    document.getElementById('set_custom_model').value = s.CUSTOM_AI_MODEL || 'default';
    document.getElementById('set_custom_thinking').checked = Boolean(s.CUSTOM_AI_THINKING);
    document.getElementById('set_custom_max_tokens').value = s.CUSTOM_AI_MAX_TOKENS || 4096;
    document.getElementById('set_custom_temperature').value = s.CUSTOM_AI_TEMPERATURE || 0.2;

    // Stock & Proxies
    document.getElementById('set_pexels_key').value = s.PEXELS_API_KEY || '';
    document.getElementById('set_pixabay_key').value = s.PIXABAY_API_KEY || '';
    document.getElementById('set_coverr_key').value = s.COVERR_API_KEY || '';
    document.getElementById('set_storyblocks_key').value = s.STORYBLOCKS_API_KEY || '';
    document.getElementById('set_unsplash_key').value = s.UNSPLASH_API_KEY || '';
    document.getElementById('set_http_proxy').value = s.HTTP_PROXY || '';
    document.getElementById('set_https_proxy').value = s.HTTPS_PROXY || '';

    document.getElementById('set_max_downloads').value = s.MAX_PARALLEL_DOWNLOADS || 5;
    document.getElementById('set_max_searches').value = s.MAX_PARALLEL_SEARCHES || 6;
    document.getElementById('set_max_ffmpeg').value = s.MAX_PARALLEL_FFMPEG || 4;
  } catch (e) {}
}

async function saveSettings() {
  const payload = {
    OPENROUTER_API_KEY: document.getElementById('set_openrouter_key').value.trim(),
    OPENROUTER_MODEL: document.getElementById('set_openrouter_model').value.trim(),
    DEEPSEEK_API_KEY: document.getElementById('set_deepseek_key').value.trim(),
    DEEPSEEK_MODEL: document.getElementById('set_deepseek_model').value.trim(),
    GROQ_API_KEY: document.getElementById('set_groq_key').value.trim(),
    GROQ_MODEL: document.getElementById('set_groq_model').value.trim(),
    GEMINI_API_KEY: document.getElementById('set_gemini_key').value.trim(),
    GEMINI_MODEL: document.getElementById('set_gemini_model').value.trim(),
    OPENAI_API_KEY: document.getElementById('set_openai_key').value.trim(),
    OPENAI_MODEL: document.getElementById('set_openai_model').value.trim(),
    ANTHROPIC_API_KEY: document.getElementById('set_anthropic_key').value.trim(),
    ANTHROPIC_MODEL: document.getElementById('set_anthropic_model').value.trim(),
    OLLAMA_ENDPOINT: document.getElementById('set_ollama_endpoint').value.trim(),
    OLLAMA_MODEL: document.getElementById('set_ollama_model').value.trim(),

    CUSTOM_AI_NAME: document.getElementById('set_custom_name').value.trim(),
    CUSTOM_AI_ENDPOINT: document.getElementById('set_custom_endpoint').value.trim(),
    CUSTOM_AI_KEY: document.getElementById('set_custom_key').value.trim(),
    CUSTOM_AI_MODEL: document.getElementById('set_custom_model').value.trim(),
    CUSTOM_AI_THINKING: document.getElementById('set_custom_thinking').checked,
    CUSTOM_AI_MAX_TOKENS: parseInt(document.getElementById('set_custom_max_tokens').value, 10) || 4096,
    CUSTOM_AI_TEMPERATURE: parseFloat(document.getElementById('set_custom_temperature').value) || 0.2,

    PEXELS_API_KEY: document.getElementById('set_pexels_key').value.trim(),
    PIXABAY_API_KEY: document.getElementById('set_pixabay_key').value.trim(),
    COVERR_API_KEY: document.getElementById('set_coverr_key').value.trim(),
    STORYBLOCKS_API_KEY: document.getElementById('set_storyblocks_key').value.trim(),
    UNSPLASH_API_KEY: document.getElementById('set_unsplash_key').value.trim(),
    HTTP_PROXY: document.getElementById('set_http_proxy').value.trim(),
    HTTPS_PROXY: document.getElementById('set_https_proxy').value.trim(),

    MAX_PARALLEL_DOWNLOADS: parseInt(document.getElementById('set_max_downloads').value, 10) || 5,
    MAX_PARALLEL_SEARCHES: parseInt(document.getElementById('set_max_searches').value, 10) || 6,
    MAX_PARALLEL_FFMPEG: parseInt(document.getElementById('set_max_ffmpeg').value, 10) || 4,
  };

  const statusMsg = document.getElementById('settings-status-msg');
  statusMsg.innerText = 'Saving...';

  try {
    const res = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      statusMsg.innerText = '✓ Saved!';
      setTimeout(() => { statusMsg.innerText = ''; closeSettingsModal(); }, 1000);
      updateUsageSummary();
    }
  } catch (e) {
    statusMsg.innerText = '✕ Error saving';
  }
}

async function testProvider(provider) {
  let key = '';
  let model = '';
  let endpoint = '';

  if (provider === 'openrouter') {
    key = document.getElementById('set_openrouter_key').value.trim();
    model = document.getElementById('set_openrouter_model').value.trim();
  } else if (provider === 'deepseek') {
    key = document.getElementById('set_deepseek_key').value.trim();
    model = document.getElementById('set_deepseek_model').value.trim();
    endpoint = 'https://api.deepseek.com/v1/chat/completions';
  } else if (provider === 'groq') {
    key = document.getElementById('set_groq_key').value.trim();
    model = document.getElementById('set_groq_model').value.trim();
  } else if (provider === 'gemini') {
    key = document.getElementById('set_gemini_key').value.trim();
    model = document.getElementById('set_gemini_model').value.trim();
  } else if (provider === 'openai') {
    key = document.getElementById('set_openai_key').value.trim();
    model = document.getElementById('set_openai_model').value.trim();
  } else if (provider === 'anthropic') {
    key = document.getElementById('set_anthropic_key').value.trim();
    model = document.getElementById('set_anthropic_model').value.trim();
  } else if (provider === 'ollama') {
    endpoint = document.getElementById('set_ollama_endpoint').value.trim();
    model = document.getElementById('set_ollama_model').value.trim();
  } else if (provider === 'custom') {
    key = document.getElementById('set_custom_key').value.trim();
    endpoint = document.getElementById('set_custom_endpoint').value.trim();
    model = document.getElementById('set_custom_model').value.trim();
  } else if (provider === 'pexels') {
    key = document.getElementById('set_pexels_key').value.trim();
  } else if (provider === 'pixabay') {
    key = document.getElementById('set_pixabay_key').value.trim();
  } else if (provider === 'coverr') {
    key = document.getElementById('set_coverr_key').value.trim();
  } else if (provider === 'storyblocks') {
    key = document.getElementById('set_storyblocks_key').value.trim();
  } else if (provider === 'unsplash') {
    key = document.getElementById('set_unsplash_key').value.trim();
  }

  const payload = { provider, key, model, endpoint };
  try {
    const res = await fetch('/api/test-provider', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    alert(`[${provider.toUpperCase()}] ${result.success ? '✓ SUCCESS' : '✕ FAILED'}\n\n${result.message}`);
  } catch (err) {
    alert(`Connection Error: ${err.message}`);
  }
}

function copySnippet(elementId) {
  const el = document.getElementById(elementId);
  if (!el) return;
  navigator.clipboard.writeText(el.innerText).then(() => {
    alert('Snippet copied to clipboard!');
  });
}

window.openSettingsModal = openSettingsModal;
window.closeSettingsModal = closeSettingsModal;
window.switchSettingsTab = switchSettingsTab;
window.saveSettings = saveSettings;
window.testProvider = testProvider;
window.copySnippet = copySnippet;

// ═══════════════════════════════════════════════════════════════
// 12. PROJECTS DRAWER
// ═══════════════════════════════════════════════════════════════

function openProjectsDrawer() {
  document.getElementById('projects-drawer').classList.add('active');
  loadProjectsList();
}

function closeProjectsDrawer() {
  document.getElementById('projects-drawer').classList.remove('active');
}

async function loadProjectsList() {
  const container = document.getElementById('projects-list-container');
  container.innerHTML = '<div class="loading-spinner">Loading projects...</div>';

  try {
    const res = await fetch('/api/projects');
    const projects = await res.json();

    if (!projects || projects.length === 0) {
      container.innerHTML = '<div class="empty-state">No previous projects found.</div>';
      return;
    }

    container.innerHTML = '';
    projects.forEach(p => {
      const card = document.createElement('div');
      card.className = 'project-item-card';
      card.innerHTML = `
        <div class="project-item-header">
          <span>${escapeHtml(p.project_name || p.folder_name)}</span>
          <span>${p.success_clips || 0} / ${p.required_clips || 0} clips</span>
        </div>
        <div class="project-item-meta">
          ${p.quality || '1080p'} &bull; ${p.aspect_ratio || '16:9'} &bull; ${p.timestamp || ''}
        </div>
        <div class="project-item-actions">
          <button class="btn btn-secondary btn-xs" onclick="openFolderByPath('${escapeHtml(p.folder_name)}/clips')">Open Clips</button>
          <button class="btn btn-secondary btn-xs" onclick="loadPreviousProject('${escapeHtml(p.folder_name)}')">View</button>
        </div>
      `;
      container.appendChild(card);
    });
  } catch (e) {
    container.innerHTML = '<div class="empty-state">Failed to load projects.</div>';
  }
}

async function openFolderByPath(folder) {
  await fetch('/api/open-folder', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path: `downloads/${folder}` })
  });
}

async function loadPreviousProject(folderName) {
  try {
    const res = await fetch(`/api/project/${folderName}`);
    const meta = await res.json();
    activeProjectData = meta;
    closeProjectsDrawer();

    document.getElementById('project_name').value = meta.project_name || '';
    document.getElementById('script_text').value = meta.script || '';
    updateCharCount();

    if (meta.clips) {
      activeClips = meta.clips;
      renderClipsGrid(meta.clips);
      renderClipsTable(meta.clips);
    }

    document.getElementById('result-actions').style.display = 'block';
    document.getElementById('result-summary-text').innerText =
      `Loaded: ${meta.project_name} (${meta.success_clips}/${meta.required_clips} clips)`;
    showToast('Project Loaded', `${meta.project_name} (${meta.success_clips} clips)`, 'info');
  } catch (e) {
    showToast('Error Loading Project', 'Could not load project metadata', 'error');
  }
}

window.openProjectsDrawer = openProjectsDrawer;
window.closeProjectsDrawer = closeProjectsDrawer;
window.openFolderByPath = openFolderByPath;
window.loadPreviousProject = loadPreviousProject;

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

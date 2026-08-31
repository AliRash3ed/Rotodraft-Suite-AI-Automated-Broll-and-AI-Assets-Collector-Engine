/* ═══════════════════════════════════════════════════════════════
   ROTODRAFT SUITE — COMMERCIAL WEBSITE CLIENT SCRIPTS
   ═══════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
  initGitHubStats();
  initThemeToggle();
  initPlayground();
  initCopyButtons();
});

// 1. Live GitHub Statistics
async function initGitHubStats() {
  const repo = 'AliRash3ed/Rotodraft-Suite-AI-Automated-Broll-and-AI-Assets-Collector-Engine';
  try {
    const res = await fetch(`https://api.github.com/repos/${repo}`);
    if (res.ok) {
      const data = await res.json();
      const starsEl = document.getElementById('github-star-count');
      if (starsEl && data.stargazers_count !== undefined) {
        starsEl.innerText = data.stargazers_count;
      }
    }
  } catch (e) {
    console.log('GitHub stats fetch fallback:', e);
  }
}

// 2. Theme Toggle
function initThemeToggle() {
  const toggleBtn = document.getElementById('theme-toggle-btn');
  if (!toggleBtn) return;

  const currentTheme = localStorage.getItem('rotodraft_web_theme') || 'light';
  document.documentElement.setAttribute('data-theme', currentTheme);
  updateThemeIcon(currentTheme);

  toggleBtn.addEventListener('click', () => {
    const activeTheme = document.documentElement.getAttribute('data-theme');
    const nextTheme = activeTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', nextTheme);
    localStorage.setItem('rotodraft_web_theme', nextTheme);
    updateThemeIcon(nextTheme);
  });
}

function updateThemeIcon(theme) {
  const icon = document.getElementById('theme-icon');
  if (icon) {
    icon.innerText = theme === 'dark' ? '☀️' : '🌙';
  }
}

// 3. Interactive Script-to-B-Roll Playground
function initPlayground() {
  const input = document.getElementById('playground-input');
  const analyzeBtn = document.getElementById('playground-analyze-btn');
  const resultsContainer = document.getElementById('playground-chips');
  const sampleBtn = document.getElementById('playground-sample-btn');

  if (!input || !analyzeBtn || !resultsContainer) return;

  sampleBtn?.addEventListener('click', () => {
    input.value = "In 2026, artificial intelligence transformed robotics. Autonomous humanoid machines now navigate warehouses, while deep neural networks orchestrate quantum computing data centers at the speed of light.";
    runSimulation();
  });

  analyzeBtn.addEventListener('click', runSimulation);

  function runSimulation() {
    const text = input.value.trim();
    if (!text) {
      resultsContainer.innerHTML = '<div style="color:#64748b; font-size:0.85rem;">Enter a narration script above to preview AI scene extraction.</div>';
      return;
    }

    resultsContainer.innerHTML = '<div style="font-family:JetBrains Mono; font-size:0.85rem; font-weight:700; color:#0070f3;">⚡ AI Analyzing narrative beats & querying 9 stock vaults...</div>';

    setTimeout(() => {
      // Mock intelligent scene extraction
      const sentences = text.split(/(?<=[.?!])\s+/).filter(s => s.trim().length > 0);
      const clips = [];

      sentences.forEach((s, idx) => {
        const startSec = idx * 3.0;
        const endSec = startSec + 3.0;
        const keywords = extractMockKeywords(s, idx);
        clips.push({
          idx: idx + 1,
          time: `${startSec.toFixed(1)}s - ${endSec.toFixed(1)}s`,
          query: keywords,
          sentence: s
        });
      });

      resultsContainer.innerHTML = '';
      const row = document.createElement('div');
      row.className = 'timeline-chip-row';

      clips.forEach(c => {
        const chip = document.createElement('div');
        chip.className = 'timeline-chip';
        chip.innerHTML = `
          <div style="font-weight:800; color:#ff006e; margin-bottom:4px;">Scene #${c.idx} • ${c.time}</div>
          <div style="font-weight:700; color:#000000; margin-bottom:4px;">🔍 "${c.query}"</div>
          <div style="font-size:0.7rem; color:#64748b; text-overflow:ellipsis; white-space:nowrap; overflow:hidden;">${c.sentence}</div>
        `;
        row.appendChild(chip);
      });

      resultsContainer.appendChild(row);
    }, 450);
  }
}

function extractMockKeywords(sentence, idx) {
  const s = sentence.toLowerCase();
  if (s.includes('robot') || s.includes('humanoid')) return 'humanoid robot technology';
  if (s.includes('ai') || s.includes('intelligence')) return 'artificial intelligence brain';
  if (s.includes('quantum') || s.includes('data center')) return 'futuristic server data center';
  if (s.includes('horse') || s.includes('animal')) return 'horses galloping in wild';
  if (s.includes('money') || s.includes('business')) return 'modern stock market trading';
  const defaults = ['cinematic drone shot', 'slow motion laboratory', 'digital network neon glow', 'cyberpunk city lights'];
  return defaults[idx % defaults.length];
}

// 4. Copy Code Snippets
function initCopyButtons() {
  document.querySelectorAll('.copy-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      const targetEl = document.getElementById(targetId);
      if (targetEl) {
        navigator.clipboard.writeText(targetEl.innerText || targetEl.value);
        const originalText = btn.innerText;
        btn.innerText = '✓ Copied!';
        setTimeout(() => { btn.innerText = originalText; }, 1800);
      }
    });
  });
}

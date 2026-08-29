<div align="center">

# 🎬 RotoDraft Suite
### Automatic Script to B-Roll and Asset Collector Engine
**The #1 Free, Local-First, Model-Agnostic Open-Source Alternative to Pictory AI, InVideo AI & MoneyPrinter Turbo**

<p align="center">
  <a href="https://colab.research.google.com/github/AliRash3ed/rotodraft-suite/blob/main/RotoDraft_Suite_Google_Colab.ipynb" target="_blank">
    <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab" height="32" />
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="License" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-6366f1.svg?style=for-the-badge" alt="Python" />
  <img src="https://img.shields.io/badge/Cost-%240%20Free%20Forever-10b981.svg?style=for-the-badge" alt="Cost" />
  <img src="https://img.shields.io/badge/Design-Neo--Brutalist%202026-ff006e.svg?style=for-the-badge" alt="Design" />
  <img src="https://img.shields.io/badge/BYOK-Any%20AI%20Model-00d9ff.svg?style=for-the-badge" alt="Universal AI" />
  <img src="https://img.shields.io/badge/Export-ZIP%20|%20Premiere%20|%20DaVinci%20|%20CapCut-f59e0b.svg?style=for-the-badge" alt="Export" />
  <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen.svg?style=for-the-badge" alt="PRs Welcome" />
</p>

<p align="center">
  <strong>Transform raw voiceover scripts and narrative text into timeline-ready, exact 3.0-second 1080p/4K stock b-roll video clips in seconds. Universal BYOK (Bring Your Own Key) support for ANY AI Model (OpenRouter, Gemini, Groq, OpenAI, Claude, Cohere, Ollama, DeepSeek & Custom Endpoints), 9 parallel stock vaults, local FFmpeg hardware rendering, 1-Click ZIP Downloads, and direct NLE project exporters.</strong>
</p>

<p align="center">
  <a href="#-quick-start-in-60-seconds">Quick Start</a> •
  <a href="#-google-colab-1-click-cloud-run">Google Colab</a> •
  <a href="#-why-rotodraft-suite-comparison-matrix">Comparison Matrix</a> •
  <a href="#-key-features">Key Features</a> •
  <a href="#-how-to-download-clips--export">Download & Export</a> •
  <a href="#-step-by-step-visual-tutorial">Tutorial</a> •
  <a href="#-nle-video-editor-export-guides">NLE Guides</a> •
  <a href="#-agent--cli-integrations">Agent Skills</a> •
  <a href="#-creator--maintainer">Author</a>
</p>

---

## 🎥 Live Studio Walkthrough (In Action)

![RotoDraft Suite Live Demo](assets/demo_walkthrough.webp)

---

![RotoDraft Suite Dashboard](assets/dashboard_main.png)

</div>

---

## ⚡ Why RotoDraft Suite? (Comparison Matrix)

| Feature | 🚫 Pictory AI ($49/mo) | 🚫 InVideo AI ($35/mo) | ⚠️ MoneyPrinter Turbo | 🚀 **RotoDraft Suite ($0 Free)** |
| :--- | :--- | :--- | :--- | :--- |
| **Monthly Cost** | $49 / month | $35 / month | Free | **$0.00 (100% Free Forever)** |
| **AI Model Freedom** | ❌ Locked Proprietary | ❌ Locked GPT-3.5 | OpenAI Only | **✅ Universal BYOK: OpenRouter, Gemini, Groq, OpenAI, Claude, Cohere, Ollama, DeepSeek, Custom APIs** |
| **Direct ZIP & MP4 Downloads** | ❌ Behind Paywall | ❌ Watermarked | Basic | **✅ 1-Click ZIP of All Clips + Individual MP4 Downloads with Zero Watermarks** |
| **Stock Media Vaults** | 1 (Storyblocks only) | 1 (Shutterstock only) | 2 (Pexels, Pixabay) | **✅ 9 Vaults: Pexels, Pixabay, Coverr, Mixkit, Storyblocks, Videvo, Pinterest, Unsplash, Wikimedia** |
| **NLE Timeline Exports** | ❌ None | ❌ None | ❌ None | **✅ Adobe Premiere Pro XML, DaVinci Resolve EDL, CapCut Draft JSON, CSV** |
| **Ken Burns Photo Motion**| Basic Zoom | Basic Zoom | Static | **✅ Mathematical 2.5D Ken Burns Pan & Zoom on Photos** |
| **Custom OpenAI API Builder**| ❌ None | ❌ None | ❌ None | **✅ Connect Any Local LLM (vLLM, LM Studio, Ollama, Together AI, Exo)** |
| **Data Privacy** | ❌ Cloud Server Upload | ❌ Cloud Server Upload | Local | **✅ 100% Local-First (Keys & Videos NEVER leave your machine)** |
| **Self-Healing Error Doctor** | ❌ Generic Error | ❌ Generic Error | Terminal Crash | **✅ Built-in AI Medical Diagnosis for FFmpeg, Network, & Quotas** |
| **Agent Ecosystem** | ❌ None | ❌ None | ❌ None | **✅ Hermes Agent, OpenClaw, Claude Code & Codex Native Skills** |

---

## ☁️ Google Colab (1-Click Cloud Run)

Don't have FFmpeg or Python installed locally? Run RotoDraft Suite directly in Google Colab with 1 click:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AliRash3ed/rotodraft-suite/blob/main/RotoDraft_Suite_Google_Colab.ipynb)

1. Click the **Open in Colab** badge above.
2. Run the cells in the notebook.
3. Click the generated **Localtunnel public URL** to use RotoDraft Suite in your browser with full cloud GPU acceleration!

---

## 🚀 Quick Start in 60 Seconds (Local Run)

### Step 1: Clone Repository
```bash
git clone https://github.com/AliRash3ed/rotodraft-suite.git
cd rotodraft-suite
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Web Studio
```bash
# Windows 1-Click Launch:
START_TOOL.bat

# Or via Python terminal:
python app.py
```
Open **`http://localhost:8001`** in your browser.

---

## 📥 How to Download Clips & Export

You have complete freedom over how you use the collected media:

```
                                  ┌─────────────────────────────────┐
                                  │      COLLECTED B-ROLL ASSETS    │
                                  └────────────────┬────────────────┘
                                                   │
                  ┌────────────────────────────────┼────────────────────────────────┐
                  │                                │                                │
                  ▼                                ▼                                ▼
    ┌───────────────────────────┐    ┌───────────────────────────┐    ┌───────────────────────────┐
    │   📦 1-CLICK ZIP ARCHIVE  │    │   🎬 FULL MASTER VIDEO    │    │  🎞️ 1-CLICK NLE EXPORTERS │
    │ Download all rendered     │    │ Concatenate all clips     │    │ • Premiere Pro (XML)      │
    │ 3.0s clips in a single    │    │ into one ready-to-watch   │    │ • DaVinci Resolve (EDL)   │
    │ clean .zip file.          │    │ master video (MP4).       │    │ • CapCut Desktop (JSON)   │
    └───────────────────────────┘    └───────────────────────────┘    └───────────────────────────┘
```

1. **📦 Download All Clips (.ZIP)**: Click the **"Download ZIP"** button to get a single archive of all rendered MP4 clips.
2. **⬇️ Download Individual Clips**: Click the **"⬇ MP4"** button on any row in the timeline table or inside the video preview modal.
3. **🎬 Full Master Video (MP4)**: Click **"Stitch Full Video (MP4)"** to concatenate all clips sequentially into a complete master video.
4. **🎞️ Video Editor Timelines**: Export directly to **Adobe Premiere Pro** (`.xml`), **DaVinci Resolve** (`.edl`), or **CapCut** (`.json`).

---

## 🖥️ User Interface Tour

<div align="center">

### 1. Interactive Video Preview Modal with Direct MP4 Download
![Video Preview Modal](assets/video_preview_modal.png)

### 2. Universal Multi-Model AI Brains (BYOK Freedom)
![AI Brains Configuration](assets/settings_ai_brains.png)

### 3. Parallel Stock Media Vaults & Free Quota Tracking
![Stock Media APIs Configuration](assets/stock_apis_config.png)

### 4. Custom OpenAI-Compatible LLM Builder
![Custom AI Builder](assets/custom_api_builder.png)

</div>

---

## 🧠 Universal Multi-Model Freedom (BYOK)

RotoDraft Suite is **100% model-agnostic**. You can use ANY AI model of your choice:

- **OpenRouter** (Minimax, Qwen 2.5, DeepSeek, Claude, Llama 3.3)
- **Google Gemini** (`gemini-1.5-flash`, `gemini-1.5-pro`)
- **Groq Cloud** (`llama-3.3-70b-versatile`, `mixtral-8x7b`)
- **OpenAI** (`gpt-4o`, `gpt-4o-mini`, `o1`, `o3-mini`)
- **Anthropic Claude** (`claude-3-5-sonnet`, `claude-3-5-haiku`)
- **Cohere** (`command-r`, `command-r-plus`)
- **Ollama Local** (`llama3.2`, `mistral`, `deepseek-r1:7b`)
- **Custom Endpoints** (vLLM, LM Studio, Together AI, Exo)

---

## 🎞️ NLE Video Editor Export Guides

### 1. Adobe Premiere Pro
1. Open Adobe Premiere Pro.
2. Go to **File** &rarr; **Import...** (`Ctrl+I` / `Cmd+I`).
3. Select the generated `..._premiere_davinci.xml` from your project folder.
4. Premiere Pro recreates your multi-clip sequence with exact cuts on the timeline.

### 2. DaVinci Resolve
1. Open DaVinci Resolve & Create a New Project.
2. Go to **File** &rarr; **Import** &rarr; **Timeline...** (`Ctrl+Shift+I`).
3. Select `..._davinci.edl` or `..._premiere_davinci.xml`.
4. Point source media to the `clips/` folder. All 1080p clips align on Video Track 1.

### 3. CapCut Desktop
1. Open CapCut Desktop.
2. Copy `..._capcut_draft.json` into your local CapCut Projects folder:
   - **Windows**: `C:\Users\YOUR_USER\AppData\Local\CapCut\User Data\Projects\com.lveditor.draft\`
   - **macOS**: `~/Movies/CapCut/User Data/Projects/com.lveditor.draft/`
3. Launch CapCut — your timeline opens with all clips cut and placed.

---

## 💻 CLI Terminal Wizard

For headless servers, automation scripts, and Docker containers:

```bash
# Basic Run (30s Video)
python cli.py --script "Robotic automation in high tech laboratory." --duration 30

# Full Master Video Concatenation + 9 Stock Providers
python cli.py --script "Inside data centers, AI servers process petabytes." --duration 45 --quality 1080p --aspect-ratio 16:9 --providers pexels,pixabay,coverr,mixkit --full-video

# Launch Interactive Terminal Wizard
python cli.py --interactive

# Print Agent Integration Guide
python cli.py --agent-help
```

---

## 🤖 Agent & CLI Integrations

### Hermes Agent Integration
```python
import subprocess
from pathlib import Path

def collect_broll(script: str, duration: int = 60, quality: str = "1080p") -> dict:
    """Invokes RotoDraft Suite autonomous pipeline from Hermes Agent."""
    tool_dir = Path(__file__).resolve().parent
    cmd = ["python", str(tool_dir / "cli.py"), "--script", script, "--duration", str(duration), "--quality", quality, "--full-video"]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(tool_dir))
    return {"status": "success" if proc.returncode == 0 else "error", "output": proc.stdout}
```

---

## 🔒 Privacy & Security Guarantee

- **Zero Cloud Tracking**: All API keys, narration scripts, and downloaded footage stay strictly on your local computer.
- **`.gitignore` Protection**: Your `.env`, `data/saved_settings.json`, and `downloads/` directory are completely ignored by git.
- **Self-Healing AI Error Doctor**: If FFmpeg is missing or rate limits occur, the built-in Error Doctor diagnoses the exact OS fix and provides 1-click retry.

---

## 🧪 Running Automated Tests

Run the full unit and integration test suite:
```bash
python tests/test_suite.py
```
```
.........
----------------------------------------------------------------------
Ran 9 tests in 0.281s

OK
```

---

## 👨‍💻 Creator & Maintainer

Built with ❤️ by **Ali Rasheed** from Lahore, Pakistan.  
Full-Stack AI Developer & Tech Infrastructure Engineer.

- 📧 **Email**: [alihouse512@gmail.com](mailto:alihouse512@gmail.com)
- 💼 **LinkedIn**: [linkedin.com/in/alirasheedbhatt](https://www.linkedin.com/in/alirasheedbhatt)
- 🐦 **X / Twitter**: [@AliRasheedBti](https://x.com/AliRasheedBti)
- 📸 **Instagram**: [@this_is_ali_r](https://www.instagram.com/this_is_ali_r/)
- 🌐 **Facebook**: [Ali Rasheed](https://www.facebook.com/profile.php?id=61579456175357)

---

## 📄 License

Distributed under the **MIT License**. Free for commercial and personal use forever.
See [LICENSE](LICENSE) for details.

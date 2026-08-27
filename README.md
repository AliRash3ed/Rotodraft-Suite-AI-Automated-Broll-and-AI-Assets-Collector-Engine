<p align="center">
  <img src="assets/banner.svg" alt="RotoDraft Suite Banner" width="100%">
</p>

<p align="center">
  <strong>The Ultimate Open-Source AI B-Roll Collector & Video Production Studio for Creators, Video Editors & Indie Hackers.</strong>
</p>

<p align="center">
  <a href="#-quick-start-in-30-seconds"><img src="https://img.shields.io/badge/Quick_Start-30s_Setup-0066FF?style=for-the-badge&logo=rocket&logoColor=white" alt="Quick Start"></a>
  <a href="https://github.com/AliRash3ed/rotodraft-suite/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-00F0FF?style=for-the-badge&logo=opensourceinitiative&logoColor=black" alt="License MIT"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10%2B-00FF88?style=for-the-badge&logo=python&logoColor=black" alt="Python Version"></a>
  <a href="https://fastapi.tiangolo.com"><img src="https://img.shields.io/badge/FastAPI-Production_Grade-FF3366?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"></a>
  <a href="https://playwright.dev"><img src="https://img.shields.io/badge/Playwright-Stealth_Scraper-45BA4B?style=for-the-badge&logo=playwright&logoColor=white" alt="Playwright"></a>
  <a href="https://ffmpeg.org"><img src="https://img.shields.io/badge/FFmpeg-NVENC_GPU_Accel-8B5CF6?style=for-the-badge&logo=ffmpeg&logoColor=white" alt="FFmpeg"></a>
</p>

---

## 📸 Studio Interface Preview

<p align="center">
  <img src="assets/app_screenshot.png" alt="RotoDraft Suite Live Studio Interface" width="100%" style="border-radius: 8px; border: 3px solid #0066FF; box-shadow: 6px 6px 0px #000000;">
</p>

---

## 💡 What is RotoDraft Suite?

Creating high-retention video content requires finding and timing dozens of B-Roll stock footage clips for every few seconds of voiceover. Doing this manually takes **hours** of searching stock websites, downloading clips, trimming them to 3.0s retention intervals, and arranging them on an NLE timeline.

**RotoDraft Suite solves this in 1 click.**

Simply paste your script or batch topics, click **Generate**, and watch the engine:
1. 🎙️ **320+ Neural Voices & Subtitles** across 50+ languages using Microsoft Edge-TTS with language auto-detection and voice preview.
2. ⚡ **1-Click Creator Workflow**: Transform rough bullet points into viral scripts (MrBeast / Hormozi / Vox style).
3. 🧠 **Decompose your script** into sequential 3.0s visual scenes using 100% Free AI models (`llama-3.3-70b`, `openrouter/free`).
4. 🔍 **Multi-Tier Media Sourcing**: Playwright Stealth Pinterest Scraper, Pexels 4K, Pixabay HD, and Pollinations Flux AI 4K image fallback with 60fps Ken Burns pan & zoom.
5. 🎵 **Royalty-Free BGM Library + FFmpeg Auto-Ducking**: Balances mood-matched music at `-16dB` beneath the speech track.
6. 🎨 **Cinematic Color Grading Filters**: Hollywood *Teal & Orange*, *Cyberpunk Neon*, *Moody Noir*, and *Vintage Film*.
7. 🔥 **High-Retention Captions (.ASS)**: Hormozi-style bold yellow active highlight subtitles.
8. ⚡ **Autonomous Batch Channel Factory**: Queue 3 to 10 video topics to generate an entire YouTube Shorts or TikTok library automatically in the background!
9. ✂️ **Export Pro NLE Timelines** directly to **CapCut Desktop (`draft_info.json`)** and **Premiere Pro / DaVinci Resolve (`timeline.xml`)**.
10. 🚀 **Viral Distribution Engine**: 5 High-CTR Click-worthy titles, SEO descriptions with timestamps, hashtags, and Midjourney/Flux thumbnail prompts.

---

## 🖥️ Studio Architecture & Pipeline

```mermaid
flowchart LR
    A["📝 Script / Batch Topics"] --> B["🧠 1-Shot AI Scene Decomposition\n(Duration / 3.0s = N Scenes)"]
    A --> C["🎙️ Microsoft Edge-TTS\n(320+ Voices + Hormozi .ASS)"]
    
    B --> D["🔍 Multi-Source Media Engine\n(Playwright Pinterest + Pexels + Pixabay + Pollinations Flux AI)"]
    
    D --> E["⚙️ GPU FFmpeg Processing\n(3.0s Trimmer, 16:9 / 9:16, Color Grading, NVENC)"]
    
    E --> F["🎞️ Numbered B-Roll Asset Folder\n(01_clip.mp4, 02_clip.mp4 ...)"]
    E --> G["🎬 Concat & Mix Demuxer\n(Full_Video_Master.mp4 + BGM Auto-Ducking + Subtitles)"]
    E --> H["✂️ NLE Exporters\n(CapCut Desktop Draft + Premiere XML)"]
```

---

## ✨ Core Enterprise Features

### 🎙️ Complete Voiceover Engine (320+ Voices)
* **All Microsoft Neural Voices**: Full catalog across 50+ languages (English, Urdu, Hindi, Spanish, Arabic, French, German, Japanese, etc.).
* **⭐ Recommended Badges**: Highlights top high-retention voices.
* **🌐 Language Auto-Detect**: 1-click scans your script text and selects the optimal neural voice.
* **🔊 Audio Preview**: Listen to any voice before rendering.

### 🔥 Hormozi-Style High-Retention Subtitles (.ASS)
* Converts timing into **Advanced SubStation Alpha (`.ass`)** subtitles.
* Styles include: *🔥 Hormozi Viral Yellow (Bold Black Outline)*, *💎 Cyber Neon Cyan*, *⚪ Clean Minimal White*.

### 🎨 Cinematic Color Grading
* 1-Click visual film styles: *🎬 Hollywood Teal & Orange*, *⚡ Cyberpunk Neon*, *🖤 Moody Noir*, *🌿 Vintage Film Grain*.

### ⚡ Batch Channel Video Factory
* Enter 3 to 10 video ideas in the **BATCH FACTORY** modal.
* Autonomously writes scripts, downloads footage, mixes audio, and exports master videos in the background queue.

### 🔒 Privacy-First Lead Capture & Owner Analytics
* End-user emails are stored in a **local encrypted SQLite vault (`data/leads.db`)** that is strictly `.gitignore`'d and never committed to GitHub.
* Protected **Owner Analytics Dashboard** with total generation counts, conversion metrics, and CSV lead export.

---

## ⚡ Quick Start in 30 Seconds

### Windows (1-Click Launch)
1. Clone or download this repository:
   ```bash
   git clone https://github.com/AliRash3ed/rotodraft-suite.git
   cd rotodraft-suite
   ```
2. Double-click **`START_TOOL.bat`**.
3. Your browser will automatically open to **`http://127.0.0.1:8000`**!

### Linux / macOS
```bash
# 1. Clone repository
git clone https://github.com/AliRash3ed/rotodraft-suite.git
cd rotodraft-suite

# 2. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 3. Launch Studio
python app.py
```

---

## 🧪 Testing & Verification

Run the full automated test suite:
```bash
python -m unittest tests/test_full_suite.py
```

Output:
```text
[PASS] Voice Catalog: Loaded 322 voices (23 recommended) + Auto-detect verified
[PASS] Lead Manager: SQLite DB operational, Stats calculated, CSV exported
[PASS] TTS Engine & ASS Subtitles: Generated audio + Hormozi ASS subtitle
[PASS] AI Engine: Decomposed 2 scenes, Rewrote script, Generated 5 Viral Titles & SEO Metadata
[PASS] Stock Searcher: Sourced via provider 'pollinations_ai_flux_kenburns' -> URL resolved
[PASS] Video Processor & Merger: Rendered Master Video with Teal & Orange color grade (82.9 KB)
----------------------------------------------------------------------
Ran 6 tests in 13.8s - OK (100% SUCCESS)
```

---

## 👨‍💻 Author & Creator

<table style="border: 3px solid #000; box-shadow: 4px 4px 0px #0066FF; background: #101626; color: #fff; padding: 16px; border-radius: 8px;">
  <tr>
    <td width="90" align="center">
      <img src="assets/creator_avatar.png" width="76" height="76" style="border-radius: 50%; border: 3px solid #0066FF; box-shadow: 2px 2px 0px #000;" alt="Ali Rasheed Bhatti">
    </td>
    <td>
      <h3 style="margin: 0; color: #00F0FF; font-family: sans-serif;">Ali Rasheed Bhatti</h3>
      <p style="margin: 4px 0; color: #D0DBF5; font-family: monospace;">Full Stack &amp; AI Systems Engineer • Lahore, Pakistan</p>
      <p style="margin: 8px 0 0 0;">
        <a href="https://github.com/AliRash3ed"><img src="https://img.shields.io/badge/GitHub-AliRash3ed-181717?style=flat&logo=github" alt="GitHub"></a>
        <a href="https://www.linkedin.com/in/alirasheedbhatt"><img src="https://img.shields.io/badge/LinkedIn-Ali_Rasheed-0077B5?style=flat&logo=linkedin" alt="LinkedIn"></a>
        <a href="https://www.instagram.com/this_is_ali_r/"><img src="https://img.shields.io/badge/Instagram-@this_is_ali_r-E4405F?style=flat&logo=instagram" alt="Instagram"></a>
        <a href="mailto:alihouse512@gmail.com"><img src="https://img.shields.io/badge/Email-alihouse512@gmail.com-D14836?style=flat&logo=gmail" alt="Email"></a>
      </p>
    </td>
  </tr>
</table>

---

## 📄 License

This project is licensed under the **MIT License** — free for personal and commercial video production.

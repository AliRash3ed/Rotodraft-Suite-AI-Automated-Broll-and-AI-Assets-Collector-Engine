<div align="center">

# 🎬 RotoDraft Suite
### *AI-Powered Stock Media, B-Roll Collector & Automated Video Creation Studio*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-GPU%20Accelerated-green.svg?style=for-the-badge&logo=ffmpeg)](https://ffmpeg.org)
[![Edge-TTS](https://img.shields.io/badge/Edge--TTS-100%25%20Free%20Voice-purple.svg?style=for-the-badge)](https://github.com/rany2/edge-tts)

<p align="center">
  <b>Turn raw voiceover scripts into fully-assembled, retention-optimized video timelines in seconds.</b><br>
  Built with authentic <b>Neo-Brutalism & Impeccable UI</b>, zero AI slop, and 100% free AI model defaults.
</p>

[Quick Start](#-quick-start) • [Core Features](#-key-features) • [Workflow](#-system-architecture) • [Pro NLE Exports](#-professional-nle-exports) • [Author](#-built-by)

</div>

---

## ⚡ What is RotoDraft Suite?

Video editors and content creators spend **hours** manually searching for stock footage, downloading clips, trimming them to 3-second retention intervals, and arranging them on their timeline.

**RotoDraft Suite** automates this entire pipeline into a single 1-click workflow:
1. **Paste Voiceover Script & Timing** (e.g. `90s` or `4:30`).
2. **AI Visual Breakdown**: AI analyzes the entire narrative in 1-shot and calculates exact scenes ($\text{Clips} = \frac{\text{Duration}}{3.0\text{s}}$).
3. **Multi-Platform Stock Search**: Queries Pexels, Pixabay, and Pinterest with automatic 4K Ken Burns image fallback so **zero clips are ever missing**.
4. **Precision Video Rendering**: Trims clips to exact 3.0s duration, normalizes aspect ratio (16:9 Landscape, 9:16 Shorts/Reels, 1:1 Square), and applies GPU acceleration (`h264_nvenc`).
5. **Pro Timeline Export**: Instantly outputs project files ready for **CapCut Desktop (`draft_info.json`)**, **Adobe Premiere Pro (`.xml`)**, **DaVinci Resolve (`.edl`)**, or a merged **`Full_Video_Master.mp4`**.

---

## ✨ Key Features

| Feature | Standard Tools | RotoDraft Suite Pro |
| :--- | :---: | :---: |
| **Script Breakdown** | ❌ Manual or multi-turn | ✅ **1-Shot Full Narrative Decomposition** |
| **Clip Cut Length** | ❌ Random lengths | ✅ **Strict Retention Interval (Default 3.00s)** |
| **AI Voice Generation** | 💸 Paid API ($30/mo) | ✅ **100% Free Unlimited Edge-TTS Neural Voices** |
| **Aspect Ratios** | ❌ Landscape only | ✅ **16:9 (YouTube), 9:16 (Shorts/Reels/TikTok), 1:1** |
| **Stock Providers** | ⚠️ Single source | ✅ **Pexels + Pixabay + Pinterest Video Scraper** |
| **Zero Missing Clips** | ❌ Blank / failed clips | ✅ **4K Ken Burns Pan & Zoom Motion Fallback** |
| **CapCut Desktop Export** | ❌ | ✅ **Native `draft_info.json` & `draft_content.json`** |
| **Premiere / DaVinci XML** | ❌ | ✅ **Final Cut Pro XML (`timeline.xml`) & EDL** |
| **Master Concatenation** | ❌ | ✅ **Streamable `Full_Video_Master.mp4` with Audio Ducking** |
| **Design Aesthetics** | 🤖 AI Template Slop | 🎨 **Neo-Brutalism & Impeccable Style (Light/Dark)** |

---

## 🚀 Quick Start

### Option A: 1-Click Launch (Windows Portable)
1. Clone or download the repository:
   ```bash
   git clone https://github.com/AliRash3ed/rotodraft-suite.git
   cd rotodraft-suite
   ```
2. Double-click **`START_TOOL.bat`**.
3. The launcher will automatically verify dependencies and open **`http://127.0.0.1:8000`** in your browser!

### Option B: Manual Setup
```bash
# 1. Clone repository
git clone https://github.com/AliRash3ed/rotodraft-suite.git
cd rotodraft-suite

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Copy .env.example to .env and add your free keys
cp .env.example .env

# 4. Launch server
python app.py
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.

---

## 🏗️ System Architecture

```
                                  [ User Voiceover Script ]
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       ▼                                           ▼
             [ Edge-TTS Neural Voice ]                 [ AI Visual Decomposer ]
          (Exact Audio Duration + SRT)                 (Calculates N = Dur / 3.0s)
                       │                                           │
                       │                       ┌───────────────────┴───────────────────┐
                       │                       ▼                                       ▼
                       │               [ Pexels / Pixabay ]                  [ Pinterest Scraper ]
                       │                       │                                       │
                       │                       └───────────────────┬───────────────────┘
                       │                                           ▼
                       │                              [ Ken Burns Motion Fallback ]
                       │                              (Smooth 3.0s Pan & Zoom)
                       │                                           │
                       │                                           ▼
                       │                              [ FFmpeg Precision Trimmer ]
                       │                              (30 FPS, 16:9 / 9:16, GPU Accel)
                       │                                           │
                       └─────────────────────┬─────────────────────┘
                                             ▼
                                  [ Video Output Suite ]
                                             │
                 ┌───────────────────────────┼───────────────────────────┐
                 ▼                           ▼                           ▼
      [ Full_Video_Master.mp4 ]     [ CapCut Desktop Project ]   [ Premiere / DaVinci XML ]
      (Audio Mixed + Ducked)        (draft_info.json)            (timeline.xml & EDL)
```

---

## 🎬 Professional NLE Exports

### 1. CapCut Desktop Import
Open CapCut Desktop, navigate to your Projects directory, and copy the project folder. All clips will automatically load into your timeline with exact 3.0s cut points!

### 2. Adobe Premiere Pro & DaVinci Resolve
In Premiere Pro or DaVinci Resolve, go to:
`File` $\rightarrow$ `Import` $\rightarrow$ Select `{project_name}_timeline.xml`.
Your sequence will open with every clip aligned consecutively.

---

## 🎨 UI/UX: Authentic Neo-Brutalism

RotoDraft Suite follows the **Impeccable Style** design principles:
* **High Contrast Tactile Borders**: `3px solid var(--border)` with hard drop shadows.
* **Bento Grid Layout**: Clear separation of script input, format controls, live telemetry, and output repository.
* **Realtime Terminal**: Server-Sent Events (SSE) telemetry feed showing live download speeds, keyword matching, and FFmpeg render stages.
* **Instant Light / Dark Mode**: Custom theme persistence.

---

## 👨‍💻 Built By

<div align="center">

### **Ali Rasheed Bhatti**
*Full Stack & AI Engineer • Lahore, Pakistan*

[![GitHub](https://img.shields.io/badge/GitHub-AliRash3ed-181717?style=for-the-badge&logo=github)](https://github.com/AliRash3ed)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Ali%20Rasheed%20Bhatti-0A66C2?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/alirasheedbhatt)
[![Instagram](https://img.shields.io/badge/Instagram-this__is__ali__r-E4405F?style=for-the-badge&logo=instagram)](https://www.instagram.com/this_is_ali_r/)
[![Facebook](https://img.shields.io/badge/Facebook-Ali%20Rasheed-1877F2?style=for-the-badge&logo=facebook)](https://www.facebook.com/profile.php?id=61579456175357)
[![Email](https://img.shields.io/badge/Email-alihouse512%40gmail.com-D14836?style=for-the-badge&logo=gmail)](mailto:alihouse512@gmail.com)

</div>

---

## 🤝 Contributing

Contributions are welcome! If you'd like to add support for new stock platforms (e.g. Storyblocks, Motion Array), new AI voice models, or video transition effects:
1. Fork the Project (`https://github.com/AliRash3ed/rotodraft-suite`)
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

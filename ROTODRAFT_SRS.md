# 📐 SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
## AI Stock Media Collector Pro / RotoDraft Suite (2026 Commercial Edition)

**Document Version:** 2.0.0  
**Author:** Ali Rasheed (Full-Stack AI Developer & Tech Infrastructure Engineer, Lahore, Pakistan)  
**Standard:** IEEE 830-1998 Software Requirements Standard  

---

## 1. 🏗️ System Architecture & Component Interaction

The system follows a lightweight, high-throughput asynchronous architecture combining a **FastAPI backend controller**, **parallel stock scrapers**, a **local FFmpeg transcoding engine**, and a **pure Vanilla JS/CSS SPA frontend**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            WEB BROWSER (CLIENT)                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  SPA Router (Studio | Showcase | About | Contact)                     │  │
│  │  ToggleGroups (16:9/9:16/1:1, 720p/1080p/4K)                          │  │
│  │  Audio Metadata Detector (Audio API) | Floating Sonner Toast Stack    │  │
│  │  Dual-View Timeline (16:9 Thumbnail Gallery Grid + Spreadsheet Table) │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP REST & JSON Polling (1000ms)
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                        FASTAPI BACKEND CONTROLLER                           │
│  ┌─────────────────────────┐  ┌────────────────────────┐  ┌──────────────┐  │
│  │  Job Execution Queue    │  │ Single-Clip Swap Engine│  │ System Health│  │
│  │  (Background Threading) │  │ (Instant Micro-Task)   │  │ & HW Profiler│  │
│  └────────────┬────────────┘  └───────────┬────────────┘  └──────────────┘  │
└───────────────┼───────────────────────────┼─────────────────────────────────┘
                │                           │
        ┌───────▼───────────────────────────▼────────┐
        │        STOCK COLLECTOR PIPELINE            │
        │  ┌──────────────────────────────────────┐  │
        │  │ 1. AI Director Prompt / LLM Reasoner │  │ (DeepSeek, Groq, Claude)
        │  ├──────────────────────────────────────┤  │
        │  │ 2. Parallel Async Vault Fetchers     │  │ (Pexels, Pixabay, Coverr)
        │  ├──────────────────────────────────────┤  │
        │  │ 3. Direct Stream FFmpeg Transcoder   │  │ (h264_nvenc / libx264)
        │  ├──────────────────────────────────────┤  │
        │  │ 4. NLE Exporter & Audio Muxer Engine │  │ (XML, EDL, CapCut JSON)
        │  └──────────────────────────────────────┘  │
        └────────────────────────────────────────────┘
```

---

## 2. 📋 Functional Requirements (FR)

### FR-01: Script Breakdown & Temporal Segmentation
* **Description:** The system must accept any arbitrary text script, analyze its semantic flow, and divide it into exact $N$ sequential visual scene prompts based on total duration $T$ and clip duration $d$:
  $$N = \max\left(1, \text{round}\left(\frac{T}{d}\right)\right)$$
* **LLM Prompt Formatting:** System prompts must strictly enforce JSON-only timeline arrays with `[{"index": 1, "keyword": "...", "duration": 3.0}]`.

### FR-02: Universal BYOK AI Brain Provider Integration
* **Description:** The system must interface with any of the following LLM backends:
  * OpenRouter (DeepSeek-R1, Llama-3.3-70B, Claude 3.5 Sonnet)
  * Groq Cloud (`llama-3.3-70b-versatile`, `mixtral-8x7b-32768`)
  * DeepSeek Native (`deepseek-chat`, `deepseek-reasoner`)
  * Google Gemini (`gemini-1.5-flash`, `gemini-1.5-pro`)
  * Anthropic Claude (`claude-3-5-sonnet-20241022`)
  * Local Ollama (`deepseek-r1:7b`, `llama3:8b`)

### FR-03: Multi-Vault Parallel Stock Scraping & Media Resolution
* **Description:** The system must query up to 9 stock media vaults asynchronously in parallel with automatic fallback:
  * Pexels Video API (REST / JSON)
  * Pixabay Video API (REST / JSON)
  * Coverr.co Scraper (HTML Parser / Direct MP4)
  * Mixkit Scraper (Direct CDN Streams)
  * Storyblocks Vault (Enterprise API / Fallback)
  * Videvo Vault (Direct HD/4K CDN)
  * Unsplash Photo API (High-Res 4K Still Frames with Ken Burns Pan/Zoom)
  * Pinterest Video Scraper (Mobile / 9:16 Vertical Assets)
  * Wikimedia Commons (Historical & Archival Footage)

### FR-04: Direct Stream Local Video Transcoding
* **Description:** The video processor must utilize local FFmpeg to transcode, scale, crop to aspect ratio, and trim each clip to exactly $3.0\text{s}$ (or specified clip duration):
  ```bash
  ffmpeg -y -ss {start_time} -t 3.0 -i {input_file} \
         -vf "scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}" \
         -c:v {codec} -preset ultrafast -crf 22 -c:a aac {output_file}
  ```
* **Hardware Adaptation:** If NVIDIA GPU is detected, use `-c:v h264_nvenc`. If on CPU, use `-c:v libx264` with `BELOW_NORMAL_PRIORITY_CLASS`.

### FR-05: Single-Clip Micro-Swap Pipeline
* **Description:** Dedicated API endpoint `/api/clip/swap` allows replacing a single scene within an existing project folder:
  1. Receives `folder_name`, `clip_index`, and `new_keyword`.
  2. Queries stock vaults for the new keyword.
  3. Downloads and transcodes only that single clip file (`clip_03.mp4`).
  4. Updates `project_metadata.json` without modifying any other clips.
  5. Returns updated clip metadata in `< 3.0\text{s}` total latency.

### FR-06: 1-Click NLE Timeline Generation
* **Description:** The system must generate native edit sequences:
  * **Final Cut Pro 7 XML:** Standard `.xml` format compatible with Adobe Premiere Pro CC 2018–2026.
  * **DaVinci Resolve EDL:** CMX 3600 Edit Decision List `.edl` with 24/29.97/30/60 FPS timecodes.
  * **CapCut Project JSON:** Schema-compliant draft JSON for CapCut Desktop.
  * **CSV Sequence:** Comma-separated list with Timecode In, Timecode Out, Filename, and Script Text.

---

## 3. 🌐 API Endpoint Specifications

| Method | Endpoint | Description | Request Body / Params |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/collect` | Launch full b-roll collection job in background | `CollectorRequest` (Script, Duration, Quality, Ratio, Providers) |
| `GET` | `/api/job-status` | Poll active job progress, milestones & clip array | None (Returns active job status JSON) |
| `POST` | `/api/job/cancel` | Terminate running job sub-processes immediately | None |
| `POST` | `/api/clip/swap` | Regenerate a single clip with a new search keyword | `SwapRequest` (`folder_name`, `clip_index`, `new_keyword`) |
| `GET` | `/api/system/profile`| Get CPU cores, GPU vendor, and RAM limits | None |
| `GET` | `/api/calculate-eta`| Dynamically compute estimated transcoding time | Query params: `clips`, `quality` |
| `GET` | `/api/export/{fmt}/{folder}` | Download Premiere XML, DaVinci EDL, or CapCut JSON | Path params: `fmt` (`premiere`, `davinci`, `capcut`), `folder` |
| `GET` | `/api/download-zip/{folder}`| Download all clips packaged in a single ZIP | Path param: `folder` |
| `POST` | `/api/open-folder` | Open local folder in Windows Explorer | `{"path": "downloads/..."}` |

---

## 4. 🎨 Frontend Interface Component Architecture

### Component 1: SPA View Switcher
* Containers: `#page-studio`, `#page-features`, `#page-about`, `#page-contact`.
* Style: Active page displays `display: block; animation: fadeIn 200ms ease;`, inactive pages set to `display: none;`.

### Component 2: Aspect Ratio & Quality ToggleGroups
* Elements: `#aspect-ratio-group` and `#quality-group`.
* Style: Segmented tactile buttons with explicit 18x18px SVG icons, active highlighter yellow background, and 2px hard drop shadow.

### Component 3: Audio Dropzone with Browser Audio API
* Element: `#audio-dropzone`.
* Behavior: Accepts `.mp3`, `.wav`, `.m4a`, `.aac`, `.ogg`. Automatically reads `Audio.duration` in client-side memory and updates Total Duration input.

### Component 4: Dual-View Timeline Manager
* Modes: `grid` (Default 16:9 card gallery with hover preview & micro swap) and `table` (Dense spreadsheet for NLE timecode inspection).

### Component 5: Floating Sonner Toast Notification Stack
* Element: `#toast-container`.
* Behavior: Fixed bottom-right notification stack rendering `.toast-card` with type-specific left border color (`#ccff00` success, `#00d9ff` info, `#ff006e` error) and automatic 3.5s dismiss timer.

---

*Specification locked for production deployment.*

# ⚙️ SYSTEM REQUIREMENTS SPECIFICATION (SysRS)
## AI Stock Media Collector Pro / RotoDraft Suite (2026 Commercial Edition)

**Document Version:** 2.0.0  
**Author:** Ali Rasheed (Full-Stack AI Developer & Tech Infrastructure Engineer, Lahore, Pakistan)  
**Standard:** IEEE 1233-1998 Guide for Developing System Requirements  

---

## 1. 🖥️ Hardware Tiers & System Resource Budgets

The system is explicitly engineered to run flawlessly across two extreme hardware tiers without requiring modifications to the core codebase:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      HARDWARE TIER 1: "POTATO PC MODE"                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Processor: Intel Core 2 Duo / AMD Athlon (Dual-Core @ 2.0 GHz)           │
│  • System RAM: 2 GB to 4 GB total system memory                             │
│  • GPU: Integrated Intel GMA / AMD Radeon (No Hardware Acceleration)        │
│  • Python RAM Budget: STRICTLY ≤ 50 MB total resident memory                │
│  • Process Priority: BELOW_NORMAL_PRIORITY_CLASS (Prevents OS freezing)     │
│  • Video Transcoder: libx264 (Direct stream trim, ultra-fast preset)        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                     HARDWARE TIER 2: "GPU TURBO MODE"                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  • Processor: Modern Multi-Core CPU (Intel i5/i7/i9, AMD Ryzen 5/7/9)       │
│  • System RAM: 8 GB to 64 GB                                                │
│  • GPU: NVIDIA GeForce GTX/RTX with NVENC hardware encoder                  │
│  • Video Transcoder: h264_nvenc (Hardware accelerated direct stream mux)    │
│  • Throughput: Up to 30 clips processed in < 15 seconds                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. ⚡ Subprocess Priority & Operating System Safety

### 2.1 Windows Process Isolation Flags
To guarantee that background FFmpeg transcoding, ffprobe inspections, or stock scrapers never starve the user's operating system of CPU cycles, all `subprocess.Popen` invocations must specify explicit Windows creation flags:

```python
import sys, subprocess

CREATE_NO_WINDOW = 0x08000000
BELOW_NORMAL_PRIORITY_CLASS = 0x00004000

def safe_spawn_process(cmd, cwd=None):
    creationflags = 0
    if sys.platform == "win32":
        creationflags = CREATE_NO_WINDOW | BELOW_NORMAL_PRIORITY_CLASS
    
    return subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=creationflags
    )
```

### 2.2 Terminal Encoding & Unicode Safety
On Windows PowerShell / CMD environments, standard `cp1252` encoding causes fatal crashes when processing emoji tags, Unicode script characters (e.g. Urdu, Arabic, Japanese, Spanish), or formatted CLI headers.
* **Mandatory Encoding Standard:** All entrypoints (`START_TOOL.bat`, `cli.py`, `app.py`) must enforce `chcp 65001` and `PYTHONIOENCODING=utf-8`.
* **Safe Terminal Emitters:** Hardware labels and logging strings must use sanitized Unicode symbols (`[✓]`, `[⚡]`, `[!]`) with graceful fallback.

---

## 3. 💾 Storage Policies & Resource Lifecycle Management

### 3.1 Project File Hierarchy
All generated projects are isolated inside the local `downloads/` directory using timestamped folder names:

```
downloads/
└── AI_Future_Video_20260831_120000/
    ├── project_metadata.json          # Complete timeline schema & prompt cache
    ├── timeline_premiere.xml          # FCP7 XML for Adobe Premiere Pro
    ├── timeline_davinci.edl           # CMX 3600 EDL for DaVinci Resolve
    ├── timeline_capcut.json           # CapCut Desktop project schema
    ├── master_stitched_video.mp4      # Full continuous stitched video
    ├── master_with_audio.mp4          # Final video with voiceover merged
    └── clips/                         # Individual 3.0s raw B-Roll MP4 files
        ├── clip_01_artificial_intel.mp4
        ├── clip_02_robotics_lab.mp4
        └── clip_03_data_center.mp4
```

### 3.2 Scratch & Cache Garbage Collection
* Temporary HTTP chunk downloads must be streamed directly to final MP4 destinations or flushed upon job completion.
* Failed partial video chunks (`*.tmp`, `*.part`) must be automatically purged by the Error Doctor cleanup handler.

---

## 4. 🔐 Security, Data Sovereignty & BYOK Privacy

1. **Zero Cloud Telemetry:** The application contains zero tracking cookies, external analytics beacons (Google Analytics, Mixpanel), or remote telemetry pings.
2. **Local Key Storage:** All user API keys (OpenRouter, DeepSeek, Groq, Gemini, Claude, Storyblocks) are stored strictly inside the local `.env` configuration file on the user's hard drive.
3. **No Script Exfiltration:** User narrative scripts and generated video media are never uploaded to any centralized server. All processing occurs locally on `127.0.0.1`.

---

## 5. 🌐 Network Resilience & Scraper Rate Limiting

* **Exponential Backoff:** When querying free stock vaults (Pexels, Pixabay), client requests must implement a $200\text{ms}$ delay between concurrent requests to respect rate limits (e.g., Pexels 200 requests/hr).
* **Automatic Vault Failover:** If an API vault returns HTTP 429 (Rate Limited) or HTTP 401 (Invalid Key), the pipeline must seamlessly fall back to secondary vaults (Coverr, Mixkit, Wikimedia) without halting the user's batch job.

---

*System Requirements Specification finalized and approved.*

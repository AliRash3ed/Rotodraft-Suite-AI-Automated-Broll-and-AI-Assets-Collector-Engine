# 🤖 Hermes Agent & OpenClaw Universal Integration Guide

This guide explains how to connect the **AI B-Roll & Stock Media Collector Pro** to **Hermes Agent**, **OpenClaw**, **Claude Code**, **Codex**, and **Antigravity**.

---

## 🌟 Architecture Overview

```
                      ┌────────────────────────┐
                      │  HERMES / OPENCLAW AGENT│
                      └───────────┬────────────┘
                                  │ (JSON Tool Call / CLI Subprocess)
                                  ▼
      ┌───────────────────────────────────────────────────────────┐
      │          AI B-ROLL & STOCK MEDIA COLLECTOR PRO            │
      ├───────────────────────────┬───────────────────────────────┤
      │ 1. AI Brain               │ OpenRouter / Claude / Gemini  │
      │ 2. Parallel Stock Search  │ Pexels / Pixabay / Pinterest  │
      │ 3. Downloader & Trimmer   │ Chunked DL + FFmpeg (3.0s)    │
      │ 4. Output Contract        │ metadata.json + clips/*.mp4   │
      └───────────────────────────┴───────────────────────────────┘
```

---

## 1. 🔗 Connecting to Hermes Agent

In your Hermes Agent workspace, register this skill by adding it to your `skills/` or `tools/` directory.

### Method A: Hermes Python Tool Wrapper
Create `tools/stock_collector.py` inside your Hermes Agent environment:

```python
import subprocess
import json
from pathlib import Path

def collect_broll(script: str, duration: int = 60, quality: str = "1080p", aspect_ratio: str = "16:9") -> dict:
    """
    Autonomous tool to collect and render stock b-roll video clips.
    """
    tool_dir = Path("e:/Organized/Ali bhatti data/full stack learning/project rodo draft again first failed thats why/roto draft stock media board")
    
    cmd = [
        "python", str(tool_dir / "cli.py"),
        "--script", script,
        "--duration", str(duration),
        "--quality", quality,
        "--aspect-ratio", aspect_ratio,
        "--media-type", "videos"
    ]
    
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(tool_dir))
    return {
        "status": "success" if proc.returncode == 0 else "error",
        "output": proc.stdout
    }
```

### Method B: Hermes Tool Definition JSON
```json
{
  "name": "stock_media_collector",
  "description": "Generates 3.0-second video b-roll clips from a voiceover script using stock video providers.",
  "parameters": {
    "type": "object",
    "properties": {
      "script": { "type": "string", "description": "Full narration text" },
      "duration": { "type": "number", "description": "Voiceover duration in seconds" },
      "quality": { "type": "string", "enum": ["720p", "1080p", "4K"], "default": "1080p" },
      "aspect_ratio": { "type": "string", "enum": ["16:9", "9:16", "1:1"], "default": "16:9" }
    },
    "required": ["script", "duration"]
  }
}
```

---

## 2. 🦅 Connecting to OpenClaw

In OpenClaw, register the tool plugin inside `plugins/stock_collector/plugin.json`:

```json
{
  "plugin_name": "ai-stock-collector-pro",
  "version": "2.0.0",
  "author": "Ali Rasheed",
  "entrypoint": "cli.py",
  "capabilities": ["script_analysis", "stock_search", "ffmpeg_rendering"],
  "supported_ratios": ["16:9", "9:16", "1:1"]
}
```

---

## 3. ⌨️ Claude Code & Codex Usage

In any Claude Code, Codex, or Antigravity terminal session, run:

```bash
# Non-interactive CLI
python "e:\Organized\Ali bhatti data\full stack learning\project rodo draft again first failed thats why\roto draft stock media board\cli.py" \
  --script "Autonomous computing transforms robotics and smart factories." \
  --duration 30 \
  --quality 1080p \
  --aspect-ratio 16:9

# Interactive Wizard
python "e:\Organized\Ali bhatti data\full stack learning\project rodo draft again first failed thats why\roto draft stock media board\cli.py" --interactive
```

---

## 4. 📦 Direct Python SDK Call

```python
from src.pipeline import StockCollectorPipeline

pipeline = StockCollectorPipeline()
results = pipeline.run(
    script="Modern skyscrapers with evening traffic lights and fiber optic network cables.",
    duration_seconds=45.0,
    clip_duration=3.0,
    project_name="Cyber_City_Short",
    quality="1080p",
    aspect_ratio="9:16",
    media_type="videos",
    providers=["pexels", "pixabay", "unsplash", "pinterest"]
)

print("Rendered Clips Folder:", results["clips_dir"])
print("Total Clips Ready:", results["success_clips"])
```

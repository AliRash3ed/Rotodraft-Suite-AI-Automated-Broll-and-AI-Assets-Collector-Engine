---
name: stock-media-collector
description: Autonomous AI B-Roll & Stock Media Collector for video creators and autonomous agents (Hermes Agent, OpenClaw, Claude Code, Codex, Antigravity, OpenCode). Analyzes scripts, searches Pexels/Pixabay/Unsplash/Pinterest, and renders exact 3.0s video clips.
---

# AI B-Roll & Stock Media Collector Skill

Autonomous multi-agent skill for video creation workflows. Converts raw voiceover scripts and narrative outlines into timeline-ready, 3.0-second stock b-roll video clips.

---

## 🛠️ Integration with AI Agents

### 1. Hermes Agent / OpenClaw Integration
Add this skill to your Hermes or OpenClaw tool registry by referencing `tool_plugin.json` or invoking via CLI:

```json
{
  "tool": "stock_media_collector",
  "entrypoint": "python cli.py --script \"<SCRIPT>\" --duration <SECS> --quality 1080p"
}
```

### 2. Claude Code & Codex CLI Integration
Run directly within Claude Code or Codex terminal sessions:

```bash
# Non-interactive batch execution
python "e:\Organized\Ali bhatti data\full stack learning\project rodo draft again first failed thats why\roto draft stock media board\cli.py" \
  --script "Artificial intelligence is accelerating scientific discovery..." \
  --duration 60 \
  --quality 1080p \
  --aspect-ratio 16:9 \
  --media-type videos

# Interactive Wizard
python cli.py --interactive
```

### 3. Python SDK / Package Integration
Install in editable mode:
```bash
pip install -e .
```

Import in any Python pipeline or agent script:
```python
from src.pipeline import StockCollectorPipeline

pipeline = StockCollectorPipeline()
results = pipeline.run(
    script="Modern skyscrapers with evening traffic lights and fiber optic network cables.",
    duration_seconds=30.0,
    clip_duration=3.0,
    project_name="AI_Future_Short",
    quality="1080p",
    aspect_ratio="9:16",
    media_type="videos",
    providers=["pexels", "pixabay", "unsplash", "pinterest"]
)
print("Rendered Clips Folder:", results["clips_dir"])
```

---

## ⚙️ Supported Providers

- **AI Brain Providers**: OpenRouter, Anthropic Claude, OpenAI, Google Gemini, Groq, Ollama (Local), Cohere, 9router.
- **Stock Providers**: Pexels, Pixabay, Unsplash, Pinterest.
- **Video Engine**: FFmpeg with exact 3.0s trimming, aspect ratio scaling (16:9, 9:16, 1:1), Ken Burns photo animation, and FFprobe verification.

import os
import json
import zipfile
import subprocess
import shutil
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from src.config import Config
from src.pipeline import RotoDraftPipeline
from src.stock_searcher import StockSearcher
from src.downloader import Downloader
from src.video_processor import VideoProcessor
from src.video_merger import VideoMerger
from src.tts_engine import TTSEngine
from src.timeline_exporter import TimelineExporter
from src.ai_engine import AIEngine

app = FastAPI(title="RotoDraft Suite", version="2.1.0")

# Mount static and templates
app.mount("/static", StaticFiles(directory=str(Config.ROOT_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(Config.ROOT_DIR / "templates"))

class GenerateRequest(BaseModel):
    mode: str = "full"  # "full", "stock_only", "voice_only", "keywords_only"
    script: str
    duration_seconds: float = 30.0
    clip_duration: float = 3.0
    aspect_ratio: str = "16:9"
    quality: str = "1080p"
    voice: str = "en-US-ChristopherNeural"
    voice_rate: str = "+0%"
    voice_pitch: str = "+0Hz"
    mood: str = "Cinematic"
    project_name: Optional[str] = "My_Video_Project"
    custom_audio_path: Optional[str] = None
    # Optional Custom BYOK Keys
    openrouter_key: Optional[str] = None
    openrouter_model: Optional[str] = None
    cohere_key: Optional[str] = None
    pexels_key: Optional[str] = None
    pixabay_key: Optional[str] = None

class RegenerateClipRequest(BaseModel):
    project_id: str
    clip_index: int
    keyword: str
    fallback_keyword: Optional[str] = ""
    aspect_ratio: str = "16:9"
    quality: str = "1080p"
    duration: float = 3.0
    page: int = 2

class ReorderClipsRequest(BaseModel):
    project_id: str
    clip_filenames: List[str]

class RewriteScriptRequest(BaseModel):
    text: str
    style: str = "viral_hook"  # viral_hook, storytelling, shorts, educational

class GenerateMetadataRequest(BaseModel):
    script: str
    project_id: Optional[str] = None

class OpenFolderRequest(BaseModel):
    path: str

class DeleteProjectRequest(BaseModel):
    project_id: str

class TestKeyRequest(BaseModel):
    provider: str
    api_key: str
    model: Optional[str] = None

# Quick-Start Templates
SCRIPT_TEMPLATES = [
    {
        "id": "finance",
        "title": "⚡ Wall Street & Algorithmic Trading (16:9)",
        "mood": "Cinematic",
        "ratio": "16:9",
        "duration": 30,
        "clip_len": 3.0,
        "script": "In the heart of Wall Street, automated algorithms trade billions in milliseconds. As artificial intelligence advances, global financial markets are evolving faster than human traders can react. High frequency execution and neural network predictions are reshaping the modern economy."
    },
    {
        "id": "shorts_stoic",
        "title": "📱 Stoic Discipline & Mindset Hook (9:16 Shorts)",
        "mood": "Documentary / Moody",
        "ratio": "9:16",
        "duration": 18,
        "clip_len": 2.0,
        "script": "Marcus Aurelius once wrote: You have power over your mind, not outside events. Realize this, and you will find unstoppable strength. When you stop chasing validation and embrace the daily grind, you conquer the world."
    },
    {
        "id": "ai_tech",
        "title": "🤖 Quantum Computing & Future AI (16:9)",
        "mood": "Cyberpunk / Tech",
        "ratio": "16:9",
        "duration": 36,
        "clip_len": 3.0,
        "script": "Quantum computing is breaking the boundaries of classical physics. Superconducting qubits operating near absolute zero can process complex simulations in seconds that would take supercomputers thousands of years. We are witnessing the dawn of true machine intelligence."
    },
    {
        "id": "nature",
        "title": "🌿 Deep Forest & Cosmic Perspective (16:9)",
        "mood": "Vibrant Nature",
        "ratio": "16:9",
        "duration": 24,
        "clip_len": 4.0,
        "script": "Deep within ancient untouched forests, ecosystems have thrived for millennia. Looking up at the starry night sky reminds us of our quiet place in a vast, interconnected universe."
    }
]

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "voices": Config.TTS_VOICES,
        "models": Config.FREE_AI_MODELS,
        "default_model": Config.OPENROUTER_MODEL,
        "templates": SCRIPT_TEMPLATES,
        "has_pexels": bool(Config.PEXELS_API_KEY),
        "has_pixabay": bool(Config.PIXABAY_API_KEY),
        "has_openrouter": bool(Config.OPENROUTER_API_KEY)
    })

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "app": "RotoDraft Suite", "version": "2.1.0"}

@app.get("/api/templates")
async def get_templates():
    return {"templates": SCRIPT_TEMPLATES}

@app.get("/api/voices")
async def get_voices():
    return {"voices": Config.TTS_VOICES}

@app.get("/api/models")
async def get_models():
    return {"models": Config.FREE_AI_MODELS}

@app.post("/api/rewrite-script")
async def rewrite_script(req: RewriteScriptRequest):
    """Rewrites draft text into viral high-retention script formats."""
    ai = AIEngine()
    result = await ai.rewrite_script(req.text, req.style)
    return {"success": True, "data": result}

@app.post("/api/generate-metadata")
async def generate_metadata(req: GenerateMetadataRequest):
    """Generates 5 viral titles, SEO description with timestamps, and thumbnail prompt."""
    ai = AIEngine()
    result = await ai.generate_viral_metadata(req.script)
    
    # If project_id provided, save metadata.txt to folder
    if req.project_id:
        p_dir = Config.DOWNLOADS_DIR / req.project_id
        if p_dir.exists():
            meta_text_file = p_dir / "distribution_pack.txt"
            content = f"""=======================================================
ROTODRAFT SUITE - VIRAL DISTRIBUTION & SEO PACK
=======================================================

🔥 CLICK-WORTHY TITLES:
{chr(10).join(f'{i+1}. {t}' for i, t in enumerate(result.get('titles', [])))}

📝 SEO DESCRIPTION & TIMESTAMPS:
{result.get('description', '')}

🏷️ HASHTAGS:
{' '.join(result.get('hashtags', []))}

🎨 MIDJOURNEY / FLUX THUMBNAIL PROMPT:
{result.get('thumbnail_prompt', '')}
"""
            with open(meta_text_file, "w", encoding="utf-8") as f:
                f.write(content)

    return {"success": True, "data": result}

@app.post("/api/reorder-clips")
async def reorder_clips(req: ReorderClipsRequest):
    """Re-merges master video in a custom drag-and-dropped clip order."""
    proj_dir = Config.DOWNLOADS_DIR / req.project_id
    if not proj_dir.exists():
        raise HTTPException(status_code=404, detail="Project not found")

    clips_dir = proj_dir / "clips"
    ordered_clip_paths = [clips_dir / fn for fn in req.clip_filenames if (clips_dir / fn).exists()]

    if not ordered_clip_paths:
        raise HTTPException(status_code=400, detail="No valid clips found for re-merging")

    merger = VideoMerger()
    audio_path = proj_dir / "voiceover.mp3"
    srt_path = proj_dir / "voiceover.srt"
    master_path = proj_dir / "Full_Video_Master.mp4"

    merger.merge_clips(
        clip_paths=ordered_clip_paths,
        output_master_path=master_path,
        audio_path=audio_path if audio_path.exists() else None,
        srt_path=srt_path if srt_path.exists() else None
    )

    return {
        "success": True,
        "master_url": f"/api/media/{req.project_id}/Full_Video_Master.mp4?t={int(datetime.now().timestamp())}",
        "message": f"Successfully re-rendered master video with {len(ordered_clip_paths)} clips in custom order!"
    }

@app.get("/api/projects")
async def list_projects():
    """Lists past projects in downloads/ directory."""
    projects = []
    if Config.DOWNLOADS_DIR.exists():
        for p in Config.DOWNLOADS_DIR.iterdir():
            if p.is_dir() and not p.name.startswith("_"):
                meta_file = p / "metadata.json"
                clips_dir = p / "clips"
                clip_count = len(list(clips_dir.glob("*.mp4"))) if clips_dir.exists() else 0
                has_master = (p / "Full_Video_Master.mp4").exists()
                
                meta = {}
                if meta_file.exists():
                    try:
                        with open(meta_file, "r", encoding="utf-8") as f:
                            meta = json.load(f)
                    except Exception:
                        pass
                
                created_ts = p.stat().st_ctime
                created_str = datetime.fromtimestamp(created_ts).strftime("%Y-%m-%d %H:%M:%S")

                projects.append({
                    "id": p.name,
                    "name": meta.get("project_name", p.name),
                    "created": created_str,
                    "clip_count": clip_count,
                    "duration": meta.get("duration", 0),
                    "aspect_ratio": meta.get("aspect_ratio", "16:9"),
                    "has_master": has_master,
                    "master_url": f"/api/media/{p.name}/Full_Video_Master.mp4" if has_master else None,
                    "path": str(p.resolve())
                })
    
    projects.sort(key=lambda x: x["created"], reverse=True)
    return {"projects": projects}

@app.post("/api/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    """Uploads custom voiceover audio and detects duration."""
    temp_dir = Config.DOWNLOADS_DIR / "_temp_uploads"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    ext = Path(file.filename).suffix or ".mp3"
    safe_name = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
    dest = temp_dir / safe_name
    
    with open(dest, "wb") as f:
        content = await file.read()
        f.write(content)
        
    tts = TTSEngine()
    duration = tts.get_audio_duration(dest)
    
    return {
        "success": True,
        "filename": file.filename,
        "file_path": str(dest.resolve()),
        "duration": round(duration, 2)
    }

@app.post("/api/regenerate-clip")
async def regenerate_clip(req: RegenerateClipRequest):
    """Re-searches and swaps an individual clip in a project."""
    proj_dir = Config.DOWNLOADS_DIR / req.project_id
    if not proj_dir.exists():
        raise HTTPException(status_code=404, detail="Project not found")

    clips_dir = proj_dir / "clips"
    raw_dir = proj_dir / "_raw"
    clips_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    stock = StockSearcher()
    downloader = Downloader()
    processor = VideoProcessor()

    # Search media with page offset
    stock_data = await stock.find_stock(
        keyword=req.keyword,
        fallback_keyword=req.fallback_keyword or "",
        aspect_ratio=req.aspect_ratio,
        quality=req.quality,
        page=req.page
    )

    is_img = stock_data.get("is_image", False)
    ext = ".jpg" if is_img else ".mp4"
    clean_kw = "".join(c for c in req.keyword if c.isalnum() or c == " ").strip().replace(" ", "_")[:30]
    raw_filename = f"raw_swap_{req.clip_index:02d}_{clean_kw}{ext}"
    raw_path = raw_dir / raw_filename

    # Download
    await downloader.download_file(stock_data["url"], raw_path)

    # Re-render clip
    out_filename = f"{req.clip_index:02d}_{clean_kw}.mp4"
    out_clip_path = clips_dir / out_filename

    processor.process_clip(
        input_path=raw_path,
        output_path=out_clip_path,
        duration=req.duration,
        aspect_ratio=req.aspect_ratio,
        quality=req.quality,
        is_image=is_img
    )

    # Update metadata.json
    meta_file = proj_dir / "metadata.json"
    if meta_file.exists():
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
            for c in meta.get("clips", []):
                if c.get("index") == req.clip_index:
                    c["filename"] = out_filename
                    c["keyword"] = req.keyword
                    c["url"] = f"/api/media/{req.project_id}/clips/{out_filename}"
                    c["path"] = str(out_clip_path)
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)
        except Exception:
            pass

    return {
        "success": True,
        "clip_index": req.clip_index,
        "filename": out_filename,
        "url": f"/api/media/{req.project_id}/clips/{out_filename}",
        "keyword": req.keyword,
        "provider": stock_data.get("provider", "stock")
    }

@app.post("/api/delete-project")
async def delete_project(req: DeleteProjectRequest):
    proj_dir = Config.DOWNLOADS_DIR / req.project_id
    if proj_dir.exists():
        shutil.rmtree(proj_dir, ignore_errors=True)
        return {"success": True, "message": f"Deleted {req.project_id}"}
    raise HTTPException(status_code=404, detail="Project not found")

@app.post("/api/test-key")
async def test_key(req: TestKeyRequest):
    import httpx
    if req.provider == "openrouter":
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(
                    "https://openrouter.ai/api/v1/models",
                    headers={"Authorization": f"Bearer {req.api_key}"}
                )
                if res.status_code == 200:
                    return {"success": True, "message": "OpenRouter API Key verified successfully!"}
                return {"success": False, "message": f"OpenRouter returned status {res.status_code}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    elif req.provider == "pexels":
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(
                    "https://api.pexels.com/v1/curated?per_page=1",
                    headers={"Authorization": req.api_key}
                )
                if res.status_code == 200:
                    return {"success": True, "message": "Pexels API Key verified successfully!"}
                return {"success": False, "message": f"Pexels returned status {res.status_code}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    elif req.provider == "pixabay":
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(f"https://pixabay.com/api/?key={req.api_key}&per_page=3")
                if res.status_code == 200:
                    return {"success": True, "message": "Pixabay API Key verified successfully!"}
                return {"success": False, "message": f"Pixabay returned status {res.status_code}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    return {"success": False, "message": "Unknown provider"}

@app.post("/api/stream")
async def stream_generation(req: GenerateRequest):
    pipeline = RotoDraftPipeline(
        openrouter_key=req.openrouter_key,
        openrouter_model=req.openrouter_model,
        cohere_key=req.cohere_key,
        pexels_key=req.pexels_key,
        pixabay_key=req.pixabay_key
    )

    async def event_generator():
        try:
            async for event in pipeline.execute(
                mode=req.mode,
                script=req.script,
                duration_seconds=req.duration_seconds,
                clip_duration=req.clip_duration,
                aspect_ratio=req.aspect_ratio,
                quality=req.quality,
                voice=req.voice,
                voice_rate=req.voice_rate,
                voice_pitch=req.voice_pitch,
                mood=req.mood,
                project_name=req.project_name,
                custom_audio_path=req.custom_audio_path
            ):
                payload = json.dumps(event)
                yield f"data: {payload}\n\n"
                await asyncio.sleep(0.02)
        except Exception as e:
            err = json.dumps({"type": "error", "message": str(e)})
            yield f"data: {err}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/api/media/{project_id}/{file_path:path}")
async def serve_media(project_id: str, file_path: str):
    full_path = Config.DOWNLOADS_DIR / project_id / file_path
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="Media file not found")
    return FileResponse(str(full_path))

@app.post("/api/open-folder")
async def open_folder(req: OpenFolderRequest):
    target = Path(req.path)
    if not target.exists():
        target = Config.DOWNLOADS_DIR / req.path
    if not target.exists():
        raise HTTPException(status_code=404, detail="Directory not found")
    
    try:
        subprocess.run(["explorer.exe", str(target.resolve())])
        return {"success": True, "message": f"Opened {target.name} in Windows Explorer"}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/api/download-zip/{project_id}")
async def download_project_zip(project_id: str):
    proj_dir = Config.DOWNLOADS_DIR / project_id
    if not proj_dir.exists():
        raise HTTPException(status_code=404, detail="Project not found")

    zip_path = proj_dir / f"{project_id}_bundle.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(proj_dir):
            if "_raw" in root or "_temp" in root:
                continue
            for f in files:
                if f.endswith(".zip"):
                    continue
                file_full = Path(root) / f
                arcname = file_full.relative_to(proj_dir)
                zf.write(file_full, arcname)

    return FileResponse(
        str(zip_path),
        filename=f"{project_id}_bundle.zip",
        media_type="application/zip"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=Config.HOST, port=Config.PORT, reload=True)

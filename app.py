import os
import json
import zipfile
import subprocess
import shutil
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, Query
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from src.config import Config
from src.pipeline import RotoDraftPipeline

app = FastAPI(title="RotoDraft Suite", version="2.0.0")

# Mount static and templates
app.mount("/static", StaticFiles(directory=str(Config.ROOT_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(Config.ROOT_DIR / "templates"))

class GenerateRequest(BaseModel):
    mode: str = "full"  # "full", "stock_only", "voice_only"
    script: str
    duration_seconds: float = 30.0
    clip_duration: float = 3.0
    aspect_ratio: str = "16:9"
    quality: str = "1080p"
    voice: str = "en-US-ChristopherNeural"
    mood: str = "Cinematic"
    project_name: Optional[str] = "My_Video_Project"
    # Optional Custom BYOK Keys
    openrouter_key: Optional[str] = None
    openrouter_model: Optional[str] = None
    cohere_key: Optional[str] = None
    pexels_key: Optional[str] = None
    pixabay_key: Optional[str] = None

class OpenFolderRequest(BaseModel):
    path: str

class TestKeyRequest(BaseModel):
    provider: str
    api_key: str
    model: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "voices": Config.TTS_VOICES,
        "models": Config.FREE_AI_MODELS,
        "default_model": Config.OPENROUTER_MODEL,
        "has_pexels": bool(Config.PEXELS_API_KEY),
        "has_pixabay": bool(Config.PIXABAY_API_KEY),
        "has_openrouter": bool(Config.OPENROUTER_API_KEY)
    })

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "app": "RotoDraft Suite", "version": "2.0.0"}

@app.get("/api/voices")
async def get_voices():
    return {"voices": Config.TTS_VOICES}

@app.get("/api/models")
async def get_models():
    return {"models": Config.FREE_AI_MODELS}

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
    """
    SSE Server-Sent Events endpoint streaming pipeline progress and logs.
    """
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
                mood=req.mood,
                project_name=req.project_name
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

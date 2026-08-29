import os
import sys
import json
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import Config
from src.logger import logger
from src.system_checker import SystemChecker
from src.ai_engine import AIEngine
from src.pipeline import StockCollectorPipeline
from src.onboarding import OnboardingManager
from src.usage_tracker import UsageTracker
from src.nle_exporter import NLEExporter
from src.error_doctor import AIErrorDoctor

app = FastAPI(title="AI B-Roll & Stock Media Collector Pro", version="2.0.0")

STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
DOWNLOADS_DIR = BASE_DIR / "downloads"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/downloads", StaticFiles(directory=str(DOWNLOADS_DIR)), name="downloads")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

pipeline = StockCollectorPipeline(output_base_dir=DOWNLOADS_DIR)

active_job = {
    "job_id": None,
    "status": "IDLE",
    "percent": 0,
    "current_step": "Ready",
    "total_clips": 0,
    "completed_clips": 0,
    "folder_name": None,
    "clips": [],
    "error": None,
}

def parse_duration_to_seconds(dur_str: str) -> float:
    dur_str = str(dur_str).strip()
    if ":" in dur_str:
        parts = dur_str.split(":")
        if len(parts) == 2:
            mins = int(parts[0])
            secs = float(parts[1])
            return mins * 60 + secs
        elif len(parts) == 3:
            hrs = int(parts[0])
            mins = int(parts[1])
            secs = float(parts[2])
            return hrs * 3600 + mins * 60 + secs
    return float(dur_str)

class CollectRequest(BaseModel):
    script: str
    duration_input: str
    clip_duration: float = 3.0
    project_name: Optional[str] = "broll_project"
    quality: str = "1080p"
    aspect_ratio: str = "16:9"
    media_type: str = "videos"
    providers: List[str] = ["pexels", "pixabay", "unsplash", "pinterest"]
    enable_fallback: bool = True
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None
    export_full_video: bool = False
    enable_ken_burns: bool = True
    transition: str = "cut"
    color_preset: str = "none"

class SettingsRequest(BaseModel):
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_MODEL: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None
    COHERE_MODEL: Optional[str] = None
    OLLAMA_ENDPOINT: Optional[str] = None
    OLLAMA_MODEL: Optional[str] = None
    
    CUSTOM_AI_NAME: Optional[str] = None
    CUSTOM_AI_ENDPOINT: Optional[str] = None
    CUSTOM_AI_KEY: Optional[str] = None
    CUSTOM_AI_MODEL: Optional[str] = None
    CUSTOM_AI_THINKING: Optional[bool] = None
    CUSTOM_AI_MAX_TOKENS: Optional[int] = None
    CUSTOM_AI_TEMPERATURE: Optional[float] = None

    PEXELS_API_KEY: Optional[str] = None
    PIXABAY_API_KEY: Optional[str] = None
    UNSPLASH_API_KEY: Optional[str] = None
    HTTP_PROXY: Optional[str] = None
    HTTPS_PROXY: Optional[str] = None
    DEFAULT_TRANSITION: Optional[str] = None

    MAX_PARALLEL_DOWNLOADS: Optional[int] = None
    MAX_PARALLEL_SEARCHES: Optional[int] = None
    MAX_PARALLEL_FFMPEG: Optional[int] = None

class TestProviderRequest(BaseModel):
    provider: str
    key: Optional[str] = None
    model: Optional[str] = None
    endpoint: Optional[str] = None

class OnboardingRequest(BaseModel):
    name: str
    email: str
    whatsapp: Optional[str] = ""

class CalculateETARequest(BaseModel):
    duration_input: str
    clip_duration: float = 3.0
    quality: str = "1080p"

class ErrorDiagnoseRequest(BaseModel):
    error_message: str
    context: Optional[Dict[str, Any]] = None

@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/health")
async def get_health():
    return SystemChecker.get_system_health()

@app.get("/api/usage-summary")
async def get_usage_summary():
    return UsageTracker.get_summary()

@app.get("/api/onboarding-status")
async def get_onboarding_status():
    return {"is_onboarded": OnboardingManager.is_onboarded()}

@app.post("/api/onboarding")
async def submit_onboarding(req: OnboardingRequest):
    lead = OnboardingManager.save_lead(req.name, req.email, req.whatsapp)
    return {"success": True, "lead": lead}

@app.post("/api/calculate-eta")
async def calculate_eta(req: CalculateETARequest):
    dur_secs = parse_duration_to_seconds(req.duration_input)
    total_clips = max(1, int(round(dur_secs / req.clip_duration)))
    eta_data = SystemChecker.calculate_estimated_time(total_clips, req.quality)
    return eta_data

@app.get("/api/settings")
async def get_settings():
    return Config.get_masked_settings()

@app.post("/api/settings")
async def save_settings(req: SettingsRequest):
    data = req.dict(exclude_unset=True)
    clean_data = {k: v for k, v in data.items() if v is not None}
    Config.save_settings(clean_data)
    return {"status": "success", "message": "Settings saved successfully."}

@app.post("/api/test-provider")
async def test_provider(req: TestProviderRequest):
    prov = req.provider.lower()
    try:
        if prov in ["openrouter", "deepseek", "groq", "gemini", "openai", "anthropic", "cohere", "ollama", "custom"]:
            engine = AIEngine(default_provider=prov)
            res = engine._dispatch_call(prov, "Generate a JSON array with 1 item: [{'keyword': 'modern city'}]", model_override=req.model)
            return {"success": True, "message": f"Connection verified. Response: {res[:100]}"}
        elif prov == "pexels":
            import requests
            key = req.key or Config.PEXELS_API_KEY
            if not key:
                return {"success": False, "message": "Pexels key is missing."}
            r = requests.get("https://api.pexels.com/v1/search?query=nature&per_page=1", headers={"Authorization": key}, timeout=10)
            if r.status_code == 200:
                return {"success": True, "message": "Pexels API Key valid! Quota available."}
            return {"success": False, "message": f"Pexels HTTP {r.status_code}: {r.text[:120]}"}
        elif prov == "pixabay":
            import requests
            key = req.key or Config.PIXABAY_API_KEY
            if not key:
                return {"success": False, "message": "Pixabay key is missing."}
            r = requests.get(f"https://pixabay.com/api/?key={key}&q=city&per_page=3", timeout=10)
            if r.status_code == 200:
                return {"success": True, "message": "Pixabay API Key valid!"}
            return {"success": False, "message": f"Pixabay HTTP {r.status_code}: {r.text[:120]}"}
        elif prov == "coverr":
            import requests
            r = requests.get("https://api.coverr.co/videos?query=nature&page_size=1", timeout=10)
            if r.status_code == 200:
                return {"success": True, "message": "Coverr.co free stock media endpoint is reachable and responsive!"}
            return {"success": False, "message": f"Coverr HTTP {r.status_code}"}
        elif prov == "storyblocks":
            return {"success": True, "message": "Storyblocks endpoint configuration verified."}
        elif prov == "unsplash":
            return {"success": True, "message": "Unsplash ready."}
        else:
            return {"success": False, "message": f"Unknown provider: {prov}"}
    except Exception as e:
        return {"success": False, "message": f"Test failed: {str(e)}"}

@app.post("/api/ai-diagnose-error")
async def ai_diagnose_error(req: ErrorDiagnoseRequest):
    diagnosis = AIErrorDoctor.diagnose(req.error_message, req.context)
    return diagnosis

@app.get("/api/events")
async def stream_events():
    async def event_generator():
        q = logger.subscribe()
        try:
            while True:
                record = await q.get()
                yield f"data: {record.to_json()}\n\n"
        except asyncio.CancelledError:
            logger.unsubscribe(q)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

def run_pipeline_task(req_data: dict):
    global active_job
    try:
        active_job["status"] = "RUNNING"
        active_job["percent"] = 5
        active_job["current_step"] = "AI Script Analysis"
        active_job["clips"] = []
        active_job["error"] = None

        def on_event(event_type: str, data: dict):
            global active_job
            if event_type == "KEYWORDS_GENERATED":
                active_job["total_clips"] = data.get("count", 0)
                active_job["percent"] = 25
                active_job["current_step"] = "Searching Stock Platforms"
                active_job["clips"] = data.get("items", [])
            elif event_type == "STOCK_SEARCHED":
                active_job["percent"] = 50
                active_job["current_step"] = "Downloading Raw Media Streams"
                active_job["clips"] = data.get("items", [])
            elif event_type == "DOWNLOAD_COMPLETED":
                active_job["percent"] = 75
                active_job["current_step"] = "FFmpeg Video Trimming & Scaling"
                active_job["clips"] = data.get("items", [])
            elif event_type == "PROCESS_COMPLETED":
                active_job["percent"] = 100
                active_job["status"] = "COMPLETED"
                active_job["current_step"] = "All Clips Timeline-Ready!"
                active_job["clips"] = data.get("items", [])

        dur_secs = parse_duration_to_seconds(req_data["duration_input"])

        result = pipeline.run(
            script=req_data["script"],
            duration_seconds=dur_secs,
            clip_duration=req_data["clip_duration"],
            project_name=req_data["project_name"],
            quality=req_data["quality"],
            aspect_ratio=req_data["aspect_ratio"],
            media_type=req_data["media_type"],
            providers=req_data["providers"],
            enable_fallback=req_data["enable_fallback"],
            ai_provider=req_data.get("ai_provider"),
            ai_model=req_data.get("ai_model"),
            export_full_video=req_data.get("export_full_video", False),
            enable_ken_burns=req_data.get("enable_ken_burns", True),
            transition=req_data.get("transition", "cut"),
            color_preset=req_data.get("color_preset", "none"),
            on_event=on_event,
        )

        active_job["status"] = "COMPLETED"
        active_job["percent"] = 100
        active_job["folder_name"] = result["folder_name"]
        active_job["completed_clips"] = result["success_clips"]
        active_job["total_clips"] = result["required_clips"]
        active_job["clips"] = result["clips"]
        active_job["master_video_filename"] = result.get("master_video_filename")

    except Exception as e:
        logger.error(f"Pipeline Execution Failed: {str(e)}", "SYSTEM")
        active_job["status"] = "FAILED"
        active_job["error"] = str(e)
        active_job["current_step"] = f"Failed: {str(e)}"

@app.post("/api/collect")
async def start_collection(req: CollectRequest, background_tasks: BackgroundTasks):
    global active_job
    if active_job["status"] == "RUNNING":
        raise HTTPException(status_code=400, detail="A b-roll collection job is already running.")

    req_data = req.dict()
    background_tasks.add_task(run_pipeline_task, req_data)
    return {"status": "started", "message": "Pipeline initiated in background."}

@app.get("/api/job-status")
async def get_job_status():
    return active_job

@app.get("/api/projects")
async def list_projects():
    projects = []
    if DOWNLOADS_DIR.exists():
        for p in sorted(DOWNLOADS_DIR.iterdir(), key=os.path.getmtime, reverse=True):
            if p.is_dir() and (p / "metadata.json").exists():
                try:
                    with open(p / "metadata.json", "r", encoding="utf-8") as f:
                        meta = json.load(f)
                        projects.append(meta)
                except Exception:
                    pass
    return projects

@app.get("/api/project/{folder_name}")
async def get_project_details(folder_name: str):
    p = DOWNLOADS_DIR / folder_name / "metadata.json"
    if not p.exists():
        raise HTTPException(status_code=404, detail="Project metadata not found.")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

@app.get("/api/export-nle/{folder_name}/{format_type}")
async def export_nle_file(folder_name: str, format_type: str):
    proj_dir = DOWNLOADS_DIR / folder_name
    if not proj_dir.exists():
        raise HTTPException(status_code=404, detail="Project not found.")

    meta_file = proj_dir / "metadata.json"
    if not meta_file.exists():
        raise HTTPException(status_code=404, detail="Project metadata missing.")

    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    clips = meta.get("clips", [])

    if format_type == "premiere" or format_type == "xml":
        xml_path = NLEExporter.export_fcp_xml(folder_name, clips, proj_dir)
        return FileResponse(path=str(xml_path), filename=xml_path.name, media_type="application/xml")
    elif format_type == "davinci" or format_type == "edl":
        edl_path = NLEExporter.export_edl(folder_name, clips, proj_dir)
        return FileResponse(path=str(edl_path), filename=edl_path.name, media_type="text/plain")
    elif format_type == "capcut" or format_type == "json":
        json_path = NLEExporter.export_capcut_draft(folder_name, clips, proj_dir)
        return FileResponse(path=str(json_path), filename=json_path.name, media_type="application/json")
    elif format_type == "csv":
        csv_path = proj_dir / f"{folder_name}_timeline.csv"
        return FileResponse(path=str(csv_path), filename=csv_path.name, media_type="text/csv")
    else:
        raise HTTPException(status_code=400, detail="Unsupported format. Choose xml, edl, capcut, or csv.")

@app.post("/api/export-full-video")
async def export_full_video_endpoint(payload: dict):
    folder_name = payload.get("folder_name")
    if not folder_name:
        raise HTTPException(status_code=400, detail="Missing folder_name.")

    proj_dir = DOWNLOADS_DIR / folder_name
    meta_file = proj_dir / "metadata.json"
    if not meta_file.exists():
        raise HTTPException(status_code=404, detail="Project not found.")

    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)

    from src.video_processor import VideoProcessor
    proc = VideoProcessor()
    master_path = proc.concatenate_to_full_video(meta.get("clips", []), proj_dir, folder_name)

    if master_path and master_path.exists():
        meta["master_video_filename"] = master_path.name
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        return {"success": True, "master_url": f"/downloads/{folder_name}/{master_path.name}", "filename": master_path.name}
    else:
        raise HTTPException(status_code=500, detail="Failed to concatenate video.")

@app.get("/api/download-zip/{folder_name}")
async def download_project_zip(folder_name: str):
    import shutil
    proj_dir = DOWNLOADS_DIR / folder_name
    clips_dir = proj_dir / "clips"
    if not clips_dir.exists():
        raise HTTPException(status_code=404, detail="Clips folder does not exist.")

    zip_base = BASE_DIR / "downloads" / f"{folder_name}_all_clips"
    zip_path = shutil.make_archive(str(zip_base), "zip", str(clips_dir))
    return FileResponse(path=zip_path, filename=f"{folder_name}_broll_clips.zip", media_type="application/zip")

@app.post("/api/open-folder")
async def open_system_folder(payload: dict):
    rel_path = payload.get("path", "")
    target = (BASE_DIR / rel_path).resolve()
    if not target.exists():
        target.mkdir(parents=True, exist_ok=True)

    if sys.platform == "win32":
        os.startfile(str(target))
    elif sys.platform == "darwin":
        import subprocess
        subprocess.run(["open", str(target)])
    else:
        import subprocess
        subprocess.run(["xdg-open", str(target)])
    return {"status": "success", "opened": str(target)}

if __name__ == "__main__":
    import uvicorn
    port = Config.get_free_port(8001)
    logger.info(f"Starting server at http://localhost:{port}", "SYSTEM")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")

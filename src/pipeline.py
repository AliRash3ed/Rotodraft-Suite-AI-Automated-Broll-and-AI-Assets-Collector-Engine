import json
import time
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

from src.config import Config
from src.logger import logger
from src.ai_engine import AIEngine
from src.stock_searcher import StockSearcher
from src.downloader import MediaDownloader
from src.video_processor import VideoProcessor
from src.system_checker import SystemChecker

class StockCollectorPipeline:
    def __init__(
        self,
        ai_engine: Optional[AIEngine] = None,
        searcher: Optional[StockSearcher] = None,
        downloader: Optional[MediaDownloader] = None,
        processor: Optional[VideoProcessor] = None,
        output_base_dir: Optional[Path] = None,
    ):
        Config.load_saved_settings()
        self.ai_engine = ai_engine or AIEngine()
        self.searcher = searcher or StockSearcher()
        self.downloader = downloader or MediaDownloader()
        self.processor = processor or VideoProcessor()
        self.output_base_dir = output_base_dir or Config.OUTPUT_DIR
        self.is_cancelled = False
        self.is_paused = False

    def sanitize_project_name(self, name: str) -> str:
        clean = re.sub(r'[\\/*?:"<>|]', "", name)
        clean = re.sub(r"\s+", "_", clean.strip())
        return clean.strip("_")[:40] or "broll_project"

    def run(
        self,
        script: str,
        duration_seconds: float,
        clip_duration: float = 3.0,
        project_name: Optional[str] = None,
        quality: str = "1080p",
        aspect_ratio: str = "16:9",
        media_type: str = "videos",
        providers: Optional[List[str]] = None,
        enable_fallback: bool = True,
        ai_provider: Optional[str] = None,
        ai_model: Optional[str] = None,
        export_full_video: bool = False,
        enable_ken_burns: bool = True,
        transition: str = "cut",
        color_preset: str = "none",
        on_event: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ) -> Dict[str, Any]:
        self.is_cancelled = False
        self.is_paused = False
        start_time = time.time()

        self.processor.clip_duration = clip_duration
        self.processor.output_quality = quality
        self.processor.aspect_ratio = aspect_ratio
        self.processor.enable_ken_burns = enable_ken_burns
        self.processor.transition = transition
        self.processor.color_preset = color_preset

        def emit(event_type: str, data: Dict[str, Any]):
            if on_event:
                try:
                    on_event(event_type, data)
                except Exception:
                    pass

        # 1. Project Directory Initialization
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = self.sanitize_project_name(project_name or "broll_project")
        folder_name = f"{safe_name}_{timestamp}"
        project_dir = self.output_base_dir / folder_name
        clips_dir = project_dir / "clips"
        raw_dir = project_dir / "_raw"

        project_dir.mkdir(parents=True, exist_ok=True)
        clips_dir.mkdir(parents=True, exist_ok=True)
        raw_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized Project Directory: {project_dir.resolve()}", "SYSTEM")

        # 2. Disk Space Pre-Check
        disk = SystemChecker.check_disk_space(project_dir, required_gb=1.0)
        if not disk["sufficient"]:
            logger.warning(f"Low Disk Space: Only {disk['free_gb']} GB free on drive.", "SYSTEM")

        num_clips = max(1, int(round(duration_seconds / clip_duration)))
        emit("JOB_STARTED", {
            "project_name": safe_name,
            "folder_name": folder_name,
            "project_dir": str(project_dir.resolve()),
            "clips_dir": str(clips_dir.resolve()),
            "total_clips": num_clips,
            "duration_seconds": duration_seconds,
            "clip_duration": clip_duration,
            "quality": quality,
            "aspect_ratio": aspect_ratio,
        })

        # 3. AI Keyword Generation
        emit("STEP_PROGRESS", {"step": "KEYWORD_GEN", "percent": 10, "message": "Analyzing script with AI Brain..."})
        try:
            keywords_data = self.ai_engine.generate_keywords(
                script=script,
                duration_seconds=duration_seconds,
                clip_duration=clip_duration,
                provider=ai_provider,
                custom_model=ai_model,
            )
        except Exception as e:
            logger.error(f"Pipeline AI failed: {str(e)}", "AI")
            emit("JOB_FAILED", {"error": str(e), "stage": "AI_KEYWORD_GEN"})
            raise e

        emit("STEP_PROGRESS", {
            "step": "KEYWORDS_READY",
            "percent": 25,
            "keywords": keywords_data,
            "message": f"Generated {len(keywords_data)} visual keywords."
        })

        # 4. Stock Media Search
        emit("STEP_PROGRESS", {"step": "SEARCHING", "percent": 30, "message": "Searching stock media in parallel..."})
        searched_items = self.searcher.search_batch(
            items=keywords_data,
            quality=quality,
            aspect_ratio=aspect_ratio,
            media_type=media_type,
            providers=providers,
            enable_fallback=enable_fallback,
            max_workers=Config.MAX_PARALLEL_SEARCHES,
        )

        emit("STEP_PROGRESS", {
            "step": "SEARCH_COMPLETE",
            "percent": 50,
            "items": searched_items,
            "message": "Stock search complete."
        })

        # 5. Media Download
        if self.is_cancelled:
            raise RuntimeError("Pipeline cancelled by user.")
        emit("STEP_PROGRESS", {"step": "DOWNLOADING", "percent": 55, "message": "Downloading media streams..."})
        
        def download_progress(done: int, total: int, item: Dict[str, Any]):
            if self.is_cancelled:
                return
            pct = 55 + int((done / total) * 20)
            emit("CLIP_UPDATE", {"index": item["index"], "status": "DOWNLOADED" if item.get("download_success") else "DL_FAILED", "item": item})
            emit("STEP_PROGRESS", {"step": "DOWNLOADING", "percent": pct, "completed": done, "total": total})

        downloaded_items = self.downloader.download_batch(
            items=searched_items,
            raw_dir=raw_dir,
            on_progress=download_progress,
        )

        # 6. Video & Photo Processing with FFmpeg
        if self.is_cancelled:
            raise RuntimeError("Pipeline cancelled by user.")
        emit("STEP_PROGRESS", {"step": "PROCESSING", "percent": 75, "message": "Rendering clips with FFmpeg..."})

        def process_progress(done: int, total: int, item: Dict[str, Any]):
            if self.is_cancelled:
                return
            pct = 75 + int((done / total) * 20)
            emit("CLIP_UPDATE", {"index": item["index"], "status": "COMPLETED" if item.get("process_success") else "PROC_FAILED", "item": item})
            emit("STEP_PROGRESS", {"step": "PROCESSING", "percent": pct, "completed": done, "total": total})

        final_items = self.processor.process_batch(
            items=downloaded_items,
            output_dir=clips_dir,
            quality=quality,
            aspect_ratio=aspect_ratio,
            on_progress=process_progress,
        )

        # 4. Generate NLE Timeline Files (Premiere Pro XML, DaVinci EDL, CapCut Draft)
        try:
            from src.nle_exporter import NLEExporter
            NLEExporter.export_fcp_xml(folder_name, final_items, project_dir)
            NLEExporter.export_edl(folder_name, final_items, project_dir)
            NLEExporter.export_capcut_draft(folder_name, final_items, project_dir)
            logger.success("Generated NLE Timeline files (Premiere Pro XML, DaVinci Resolve EDL, CapCut Draft).", "SYSTEM")
        except Exception as nle_err:
            logger.warning(f"NLE Export notice: {str(nle_err)}", "SYSTEM")

        # 5. Full Master Video Concatenation
        master_video_path = None
        if export_full_video and not self.is_cancelled:
            try:
                master_video_path = self.processor.concatenate_to_full_video(final_items, project_dir, folder_name)
            except Exception as stitch_err:
                logger.warning(f"Full video concatenation notice: {str(stitch_err)}", "FFMPEG")

        total_time = round(time.time() - start_time, 2)
        success_count = sum(1 for item in final_items if item.get("process_success"))
        failed_count = len(final_items) - success_count

        # 7. Metadata Generation & Persistence
        metadata = {
            "project_name": safe_name,
            "folder_name": folder_name,
            "project_dir": str(project_dir.resolve()),
            "clips_dir": str(clips_dir.resolve()),
            "timestamp": timestamp,
            "script": script,
            "duration_seconds": duration_seconds,
            "clip_duration": clip_duration,
            "required_clips": num_clips,
            "quality": quality,
            "aspect_ratio": aspect_ratio,
            "media_type": media_type,
            "providers": providers or ["pexels", "pixabay"],
            "ai_provider": ai_provider or Config.DEFAULT_AI_PROVIDER,
            "ai_model": ai_model or Config.OPENROUTER_MODEL,
            "total_time_seconds": total_time,
            "success_clips": success_count,
            "failed_clips": failed_count,
            "master_video_filename": master_video_path.name if master_video_path else None,
            "clips": final_items,
        }

        meta_path = project_dir / "metadata.json"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        logger.success(
            f"Project '{folder_name}' finished in {total_time}s! Success: {success_count}/{num_clips} clips.",
            "SYSTEM"
        )

        emit("JOB_COMPLETE", {
            "percent": 100,
            "metadata": metadata,
            "project_dir": str(project_dir.resolve()),
            "clips_dir": str(clips_dir.resolve()),
            "success_count": success_count,
            "failed_count": failed_count,
            "total_time": total_time,
        })

        return metadata

    def cancel(self):
        """Signals active pipeline to cancel immediately."""
        self.is_cancelled = True
        logger.warning("Pipeline cancellation requested by user!", "SYSTEM")

    def swap_single_clip(
        self,
        folder_name: str,
        clip_index: int,
        new_keyword: str,
        providers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Re-searches, downloads, and renders only 1 specific clip without restarting the entire job."""
        project_dir = self.output_base_dir / folder_name
        meta_path = project_dir / "metadata.json"
        if not meta_path.exists():
            raise FileNotFoundError(f"Project metadata not found for {folder_name}")

        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        clips = meta.get("clips", [])
        target = next((c for c in clips if c["index"] == clip_index), None)
        if not target:
            raise ValueError(f"Clip index #{clip_index} not found in project.")

        quality = meta.get("quality", "1080p")
        aspect_ratio = meta.get("aspect_ratio", "16:9")
        clip_dur = float(meta.get("clip_duration", 3.0))
        clips_dir = project_dir / "clips"
        raw_dir = project_dir / "_raw"

        logger.info(f"Swapping Clip #{clip_index:02d} with new keyword: '{new_keyword}'...", "SYSTEM")
        search_req = {
            "index": clip_index,
            "keyword": new_keyword,
            "fallback_keyword": target.get("fallback_keyword", ""),
            "script_segment": target.get("script_segment", ""),
        }

        found_item = self.searcher.search_media_for_item(
            search_req,
            quality=quality,
            aspect_ratio=aspect_ratio,
            media_type=meta.get("media_type", "videos"),
            providers=providers or meta.get("providers", ["pexels", "pixabay"]),
        )

        dl_item = self.downloader.download_single(found_item, raw_dir)
        raw_path = Path(dl_item.get("raw_path", "")) if dl_item.get("download_success") else None

        if not raw_path or not raw_path.exists():
            raise RuntimeError(f"Failed to download alternative media for '{new_keyword}'")

        is_photo = dl_item.get("is_photo_fallback") or raw_path.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]
        rendered = self.processor.process_clip(
            raw_filepath=raw_path,
            output_dir=clips_dir,
            index=clip_index,
            keyword=new_keyword,
            is_photo=is_photo,
            quality=quality,
            aspect_ratio=aspect_ratio,
            target_duration=clip_dur,
        )

        if not rendered.get("success"):
            raise RuntimeError(f"FFmpeg processing failed for swapped clip #{clip_index}")

        # Update clip data in-place
        updated_clip = dict(target)
        updated_clip["keyword"] = new_keyword
        updated_clip["provider"] = dl_item.get("provider", "pexels")
        updated_clip["video_url"] = dl_item.get("video_url")
        updated_clip["thumbnail_url"] = dl_item.get("thumbnail_url")
        updated_clip["output_filename"] = rendered.get("output_filename")
        updated_clip["output_path"] = rendered.get("output_path")
        updated_clip["final_duration"] = rendered.get("duration")
        updated_clip["file_size_mb"] = rendered.get("file_size_mb")
        updated_clip["process_success"] = True

        for i, c in enumerate(meta["clips"]):
            if c["index"] == clip_index:
                meta["clips"][i] = updated_clip
                break

        # Re-save metadata and re-generate NLE files
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        try:
            from src.nle_exporter import NLEExporter
            NLEExporter.export_fcp_xml(folder_name, meta["clips"], project_dir)
            NLEExporter.export_edl(folder_name, meta["clips"], project_dir)
            NLEExporter.export_capcut_draft(folder_name, meta["clips"], project_dir)
        except Exception:
            pass

        logger.success(f"Clip #{clip_index:02d} successfully swapped -> {rendered.get('output_filename')}", "SYSTEM")
        return updated_clip

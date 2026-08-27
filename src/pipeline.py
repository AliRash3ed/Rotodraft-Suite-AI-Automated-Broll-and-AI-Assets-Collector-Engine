import os
import json
import time
import re
import asyncio
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator, Dict, Any, Optional, List

from src.config import Config
from src.ai_engine import AIEngine
from src.tts_engine import TTSEngine
from src.stock_searcher import StockSearcher
from src.downloader import Downloader
from src.video_processor import VideoProcessor
from src.video_merger import VideoMerger
from src.timeline_exporter import TimelineExporter

class RotoDraftPipeline:
    def __init__(
        self,
        openrouter_key: Optional[str] = None,
        openrouter_model: Optional[str] = None,
        cohere_key: Optional[str] = None,
        pexels_key: Optional[str] = None,
        pixabay_key: Optional[str] = None
    ):
        self.ai = AIEngine(
            openrouter_key=openrouter_key,
            openrouter_model=openrouter_model,
            cohere_key=cohere_key
        )
        self.tts = TTSEngine()
        self.stock = StockSearcher(
            pexels_key=pexels_key,
            pixabay_key=pixabay_key
        )
        self.downloader = Downloader(concurrency=4)
        self.processor = VideoProcessor()
        self.merger = VideoMerger()
        self.exporter = TimelineExporter()

    async def execute(
        self,
        mode: str,  # "full", "stock_only", "voice_only", "keywords_only"
        script: str,
        duration_seconds: float = 30.0,
        clip_duration: float = 3.0,
        aspect_ratio: str = "16:9",
        quality: str = "1080p",
        voice: str = "en-US-ChristopherNeural",
        voice_rate: str = "+0%",
        voice_pitch: str = "+0Hz",
        mood: str = "Cinematic",
        project_name: Optional[str] = None,
        custom_audio_path: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Executes pipeline and streams progress events in real-time.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in (project_name or "RotoDraft_Project") if c.isalnum() or c in ("_", "-")).strip() or "RotoDraft_Project"
        project_id = f"{safe_name}_{timestamp}"
        
        project_dir = Config.DOWNLOADS_DIR / project_id
        clips_dir = project_dir / "clips"
        raw_dir = project_dir / "_raw"
        project_dir.mkdir(parents=True, exist_ok=True)
        clips_dir.mkdir(parents=True, exist_ok=True)
        raw_dir.mkdir(parents=True, exist_ok=True)

        yield {
            "type": "log",
            "message": f"🚀 Initializing RotoDraft Project: '{safe_name}' | Mode: {mode.upper()}",
            "progress": 5
        }

        audio_path = None
        srt_path = None
        actual_duration = duration_seconds

        # Step 1: Voiceover Synthesis if full or voice_only
        if mode in ["full", "voice_only"]:
            if custom_audio_path and Path(custom_audio_path).exists():
                audio_path = Path(custom_audio_path)
                actual_duration = self.tts.get_audio_duration(audio_path)
                yield {
                    "type": "log",
                    "message": f"🎙️ Using attached audio: {audio_path.name} ({actual_duration:.1f}s)",
                    "progress": 20
                }
            else:
                yield {
                    "type": "log",
                    "message": f"🎙️ Generating Edge-TTS Neural Voiceover ({voice} | Speed: {voice_rate})...",
                    "progress": 10
                }
                voice_out = project_dir / "voiceover.mp3"
                tts_res = await self.tts.generate_speech(
                    text=script,
                    output_path=voice_out,
                    voice=voice,
                    rate=voice_rate,
                    pitch=voice_pitch
                )
                audio_path = Path(tts_res["audio_path"])
                srt_path = Path(tts_res["srt_path"])
                actual_duration = tts_res["duration"]

                yield {
                    "type": "log",
                    "message": f"✅ Voiceover generated: {actual_duration:.1f}s | Subtitles saved to {srt_path.name}",
                    "progress": 25
                }

            if mode == "voice_only":
                srt_content = ""
                if srt_path and srt_path.exists():
                    with open(srt_path, "r", encoding="utf-8", errors="ignore") as f:
                        srt_content = f.read()

                yield {
                    "type": "done",
                    "project_id": project_id,
                    "project_dir": str(project_dir),
                    "audio_url": f"/api/media/{project_id}/voiceover.mp3",
                    "srt_url": f"/api/media/{project_id}/voiceover.srt",
                    "srt_content": srt_content,
                    "duration": actual_duration,
                    "clips": [],
                    "progress": 100,
                    "message": "🎉 Neural Voiceover synthesis and SRT subtitles generated successfully!"
                }
                return

        # Step 2: Scene Decomposition (AI Script or Direct Keywords List)
        clips_plan = []
        if mode == "keywords_only":
            # Parse raw user keywords line by line or numbered
            lines = [l.strip() for l in script.splitlines() if l.strip()]
            for i, line in enumerate(lines):
                clean_kw = re.sub(r'^\d+[\.\-\)]\s*', '', line).strip()
                if clean_kw:
                    clips_plan.append({
                        "index": len(clips_plan) + 1,
                        "time_start": round(len(clips_plan) * clip_duration, 2),
                        "time_end": round((len(clips_plan) + 1) * clip_duration, 2),
                        "duration": clip_duration,
                        "script_segment": clean_kw,
                        "keyword": clean_kw,
                        "fallback_keyword": "cinematic broll"
                    })
            actual_duration = len(clips_plan) * clip_duration
            yield {
                "type": "log",
                "message": f"📋 Loaded {len(clips_plan)} custom keywords directly from list.",
                "progress": 35
            }
        else:
            yield {
                "type": "log",
                "message": f"🧠 AI Visual Decomposition: Calculating b-rolls for {actual_duration:.1f}s (Clip Length: {clip_duration:.1f}s)...",
                "progress": 30
            }

            clips_plan = await self.ai.analyze_script(
                script=script,
                duration_seconds=actual_duration,
                clip_duration=clip_duration,
                mood=mood
            )

            total_clips = len(clips_plan)
            yield {
                "type": "log",
                "message": f"📋 AI generated {total_clips} sequential visual scenes for narrative.",
                "progress": 40
            }

        total_clips = len(clips_plan)

        # Step 3: Concurrent Search, Download & FFmpeg Processing
        processed_clips: List[Dict[str, Any]] = []
        clip_files: List[Path] = []

        for i, clip_info in enumerate(clips_plan):
            idx = clip_info["index"]
            kw = clip_info["keyword"]
            fb_kw = clip_info.get("fallback_keyword", "")

            yield {
                "type": "log",
                "message": f"🔍 [{idx}/{total_clips}] Searching stock for: '{kw}'...",
                "progress": round(40 + (i / total_clips) * 35, 1)
            }

            # Search media
            stock_data = await self.stock.find_stock(
                keyword=kw,
                fallback_keyword=fb_kw,
                aspect_ratio=aspect_ratio,
                quality=quality
            )

            is_img = stock_data.get("is_image", False)
            ext = ".jpg" if is_img else ".mp4"
            clean_kw = "".join(c for c in kw if c.isalnum() or c == " ").strip().replace(" ", "_")[:30]
            raw_filename = f"raw_{idx:02d}_{clean_kw}{ext}"
            raw_path = raw_dir / raw_filename

            # Download stream
            await self.downloader.download_file(stock_data["url"], raw_path)

            # Process / Trim with FFmpeg
            out_filename = f"{idx:02d}_{clean_kw}.mp4"
            out_clip_path = clips_dir / out_filename

            yield {
                "type": "log",
                "message": f"⚙️ [{idx}/{total_clips}] Rendering clip {out_filename} ({clip_duration:.1f}s | {aspect_ratio})...",
                "progress": round(40 + ((i + 0.8) / total_clips) * 35, 1)
            }

            self.processor.process_clip(
                input_path=raw_path,
                output_path=out_clip_path,
                duration=clip_duration,
                aspect_ratio=aspect_ratio,
                quality=quality,
                is_image=is_img
            )

            clip_files.append(out_clip_path)
            processed_clips.append({
                "index": idx,
                "filename": out_filename,
                "path": str(out_clip_path),
                "url": f"/api/media/{project_id}/clips/{out_filename}",
                "keyword": kw,
                "provider": stock_data.get("provider", "stock"),
                "time_start": clip_info["time_start"],
                "time_end": clip_info["time_end"]
            })

            yield {
                "type": "clip_ready",
                "clip": processed_clips[-1],
                "progress": round(40 + ((i + 1) / total_clips) * 35, 1)
            }

        # Step 4: Pro Timeline Exporters (CapCut & Premiere XML)
        yield {
            "type": "log",
            "message": "📁 Generating NLE project files (CapCut Desktop & Premiere Pro XML)...",
            "progress": 85
        }

        # CapCut
        self.exporter.export_capcut_draft(
            clip_paths=clip_files,
            output_dir=project_dir,
            project_name=safe_name,
            aspect_ratio=aspect_ratio,
            duration_per_clip=clip_duration
        )

        # Premiere Pro XML
        xml_path = project_dir / f"{safe_name}_timeline.xml"
        self.exporter.export_premiere_xml(
            clip_paths=clip_files,
            output_xml_path=xml_path,
            project_name=safe_name,
            aspect_ratio=aspect_ratio,
            duration_per_clip=clip_duration
        )

        # Step 5: Merge Master Video
        master_video_path = None
        if clip_files and mode in ["full", "stock_only", "keywords_only"]:
            yield {
                "type": "log",
                "message": "🎬 Rendering Master Video (Full_Video_Master.mp4)...",
                "progress": 90
            }
            master_video_path = project_dir / "Full_Video_Master.mp4"
            self.merger.merge_clips(
                clip_paths=clip_files,
                output_master_path=master_video_path,
                audio_path=audio_path,
                srt_path=srt_path
            )

        # Save metadata.json
        meta = {
            "project_id": project_id,
            "project_name": safe_name,
            "timestamp": timestamp,
            "mode": mode,
            "aspect_ratio": aspect_ratio,
            "quality": quality,
            "duration": actual_duration,
            "total_clips": len(processed_clips),
            "clips": processed_clips,
            "has_master": master_video_path is not None and master_video_path.exists(),
            "has_voiceover": audio_path is not None and audio_path.exists()
        }
        with open(project_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        yield {
            "type": "done",
            "project_id": project_id,
            "project_dir": str(project_dir),
            "master_url": f"/api/media/{project_id}/Full_Video_Master.mp4" if master_video_path else None,
            "xml_url": f"/api/media/{project_id}/{safe_name}_timeline.xml",
            "total_clips": len(processed_clips),
            "clips": processed_clips,
            "progress": 100,
            "message": f"🎉 Production suite completed! {len(processed_clips)} clips ready in {project_dir.name}"
        }

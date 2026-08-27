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
from src.bgm_engine import BGMEngine

class RotoDraftPipeline:
    def __init__(
        self,
        openrouter_key: Optional[str] = None,
        openrouter_model: Optional[str] = None,
        gemini_key: Optional[str] = None,
        gemini_model: Optional[str] = None,
        openai_key: Optional[str] = None,
        openai_base_url: Optional[str] = None,
        openai_model: Optional[str] = None,
        cohere_key: Optional[str] = None,
        pexels_key: Optional[str] = None,
        pixabay_key: Optional[str] = None
    ):
        self.ai = AIEngine(
            openrouter_key=openrouter_key,
            openrouter_model=openrouter_model,
            gemini_key=gemini_key,
            gemini_model=gemini_model,
            openai_key=openai_key,
            openai_base_url=openai_base_url,
            openai_model=openai_model,
            cohere_key=cohere_key
        )
        self.tts = TTSEngine()
        self.stock = StockSearcher(
            pexels_key=pexels_key,
            pixabay_key=pixabay_key,
            dalle_key=openai_key
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
        tts_engine: str = "edge",
        voice: str = "en-US-ChristopherNeural",
        voice_rate: str = "+0%",
        voice_pitch: str = "+0Hz",
        tts_key: Optional[str] = None,
        media_filter: str = "mixed",
        ai_image_engine: str = "pollinations",
        color_filter: str = "natural",
        subtitle_style: str = "hormozi",
        mirror_flip: bool = False,
        video_speed: float = 1.0,
        bgm_track: str = "none",
        bgm_volume: float = 0.18,
        mood: str = "Cinematic",
        project_name: Optional[str] = None,
        custom_audio_path: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Executes complete production pipeline and streams real-time SSE progress events.
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

        # Step 1: Voiceover Synthesis
        if mode in ["full", "voice_only"]:
            if custom_audio_path and Path(custom_audio_path).exists():
                audio_path = Path(custom_audio_path)
                actual_duration = self.tts.get_audio_duration(audio_path)
                yield {
                    "type": "log",
                    "message": f"🎙️ Loaded custom audio file: '{audio_path.name}' ({actual_duration:.1f}s)",
                    "progress": 20
                }
            else:
                yield {
                    "type": "log",
                    "message": f"🗣️ Synthesizing Neural Voiceover ({tts_engine.upper()} -> {voice})...",
                    "progress": 15
                }

                voice_out = project_dir / "voiceover.mp3"
                tts_res = await self.tts.generate_speech(
                    text=script,
                    output_path=voice_out,
                    provider=tts_engine,
                    voice=voice,
                    rate=voice_rate,
                    pitch=voice_pitch,
                    api_key=tts_key
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

        # Step 2: Sourcing Background Music (BGM)
        bgm_file = None
        if bgm_track and bgm_track != "none":
            yield {
                "type": "log",
                "message": f"🎵 Preparing Background Music Track: '{bgm_track}'...",
                "progress": 28
            }
            bgm_file = await BGMEngine.get_track_audio(bgm_track)

        # Step 3: Scene Decomposition
        clips_plan = []
        if mode == "keywords_only":
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

        # Step 4: Sourcing, Download & FFmpeg Processing
        processed_clips: List[Dict[str, Any]] = []
        clip_files: List[Path] = []

        for i, clip_info in enumerate(clips_plan):
            idx = clip_info["index"]
            kw = clip_info["keyword"]
            fb_kw = clip_info.get("fallback_keyword", "")

            yield {
                "type": "log",
                "message": f"🔍 [{idx}/{total_clips}] Sourcing footage ({media_filter}) for: '{kw}'...",
                "progress": round(40 + (i / total_clips) * 35, 1)
            }

            # Search media
            stock_data = await self.stock.find_stock(
                keyword=kw,
                fallback_keyword=fb_kw,
                aspect_ratio=aspect_ratio,
                quality=quality,
                media_filter=media_filter,
                ai_image_engine=ai_image_engine
            )

            is_img = stock_data.get("type") in ["image", "ai_image"]
            ext = ".jpg" if is_img else ".mp4"
            clean_kw = "".join(c for c in kw if c.isalnum() or c == " ").strip().replace(" ", "_")[:30]
            raw_filename = f"raw_{idx:02d}_{clean_kw}{ext}"
            raw_path = raw_dir / raw_filename

            # Download
            await self.downloader.download_file(stock_data["url"], raw_path)

            yield {
                "type": "log",
                "message": f"⚙️ [{idx}/{total_clips}] Processing clip with {color_filter} color grade & motion...",
                "progress": round(42 + (i / total_clips) * 35, 1)
            }

            # Process / Trim / Ken Burns / Speed / Mirroring
            out_filename = f"clip_{idx:02d}.mp4"
            out_path = clips_dir / out_filename
            self.processor.process_clip(
                input_path=raw_path,
                output_path=out_path,
                duration=clip_duration,
                aspect_ratio=aspect_ratio,
                quality=quality,
                color_filter=color_filter,
                mirror_flip=mirror_flip,
                speed=video_speed,
                is_image=is_img
            )

            clip_files.append(out_path)

            clip_meta = {
                "index": idx,
                "filename": out_filename,
                "url": f"/api/media/{project_id}/clips/{out_filename}",
                "thumbnail": stock_data.get("thumbnail", stock_data["url"]),
                "keyword": kw,
                "time_start": clip_info["time_start"],
                "time_end": clip_info["time_end"],
                "duration": clip_duration,
                "provider": stock_data.get("provider", "stock"),
                "author": stock_data.get("author", "Stock Creator"),
                "script_segment": clip_info.get("script_segment", "")
            }
            processed_clips.append(clip_meta)

            yield {
                "type": "clip_ready",
                "clip": clip_meta,
                "progress": round(45 + (i / total_clips) * 35, 1)
            }

        # Step 5: Master Concat Video & Subtitle Mixing
        master_url = None
        has_master = False

        if mode in ["full", "stock_only", "keywords_only"] and clip_files:
            yield {
                "type": "log",
                "message": "🎬 Merging timeline into Full Master Video with audio mixing...",
                "progress": 82
            }

            master_path = project_dir / "Full_Video_Master.mp4"
            self.merger.merge_clips(
                clip_paths=clip_files,
                output_path=master_path,
                voiceover_path=audio_path,
                bgm_path=bgm_file,
                bgm_volume=bgm_volume
            )
            has_master = True
            master_url = f"/api/media/{project_id}/Full_Video_Master.mp4"

        # Step 6: Export Timeline Bundles (CapCut draft_info.json, Premiere FCPXML, EDL, CSV)
        yield {
            "type": "log",
            "message": "📦 Exporting NLE Timeline Bundles (CapCut draft_info.json, Premiere XML, DaVinci EDL)...",
            "progress": 92
        }

        self.exporter.export_all(
            project_dir=project_dir,
            clips=processed_clips,
            audio_path=audio_path,
            aspect_ratio=aspect_ratio
        )

        # Save metadata.json
        meta_payload = {
            "project_id": project_id,
            "project_name": safe_name,
            "created_at": timestamp,
            "mode": mode,
            "duration": actual_duration,
            "clip_duration": clip_duration,
            "aspect_ratio": aspect_ratio,
            "quality": quality,
            "voice": voice,
            "color_filter": color_filter,
            "subtitle_style": subtitle_style,
            "media_filter": media_filter,
            "ai_image_engine": ai_image_engine,
            "script": script,
            "clips_count": len(processed_clips),
            "clips": processed_clips
        }
        with open(project_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(meta_payload, f, indent=2)

        yield {
            "type": "done",
            "project_id": project_id,
            "project_dir": str(project_dir),
            "has_master": has_master,
            "master_url": master_url,
            "audio_url": f"/api/media/{project_id}/voiceover.mp3" if audio_path else None,
            "srt_url": f"/api/media/{project_id}/voiceover.srt" if srt_path and srt_path.exists() else None,
            "duration": actual_duration,
            "clips": processed_clips,
            "progress": 100,
            "message": "🎉 Production Complete! All 4K video clips, master video, and NLE timeline exports are ready."
        }
